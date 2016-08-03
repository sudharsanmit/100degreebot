from Twitter import Twitter
import logging
import queue
import random
import time
import unittest
from AppConfig import AppConfig
from Top import Top
import pprint
import datetime
from datetime import timedelta

class Top100(object):
    def __init__(self,*args,**kwargs):
#Setup log
        self.logger = logging.getLogger(__name__)

# To do: pickApp.
    def pickUser(self,resultQ,*args,**kwargs):
        user=AppConfig('apps.conf').getAppAttributes('Top100').get('user')
        resultQ.put({'user':user})
        self.logger.info('PICKUSER    : Twitter User picked.')

    def pickList(self,resultQ,*args,**kwargs):
        list_name=AppConfig('apps.conf').getAppAttributes('Top100').get('list_name')
        resultQ.put({'list_name':list_name})
        self.logger.info('PICKLIST    : Top 100 List Picked.')

    def authUser(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        api=Twitter(user)
        resultQ.put({'api':api,'user':user})
        self.logger.info('AUTHUSER    : User Authorized.')

    def getList(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name')
        try:
            list_id=api.get_list(user,list_name).id
            resultQ.put({'user':user,'api':api,'list_id':list_id,'list_name':list_name})
            self.logger.info('GETLIST    : Got List.')
        except Exception as inst:
            resultQ.put({'api':api,'user':user,'list_name':list_name,'OnFailure':True})
            self.logger.info('GETLIST    : Creating List.')

    def createList(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name')
        api.create_list(list_name)
        resultQ.put({'user':user,'api':api,'list_name':list_name})
        self.logger.info('CREATELIST : List Created.')

    def getListMembers(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name') 
        list_id=kwargs.get('list_id') 
        list_members=api.list_members(user,list_name)
        resultQ.put({'api':api,'user':user,'list_name':list_name,'list_id':list_id,'list_members':list_members})
        self.logger.info('GETLISTMEMBERS:Got list members.')
 
    def getHandlesFromUrl(self,resultQ,*args,**kwargs):
        top=Top()
        handles=top.getTop100()
        resultQ.put({'handles':handles})
        self.logger.info('GETHANDLESFROMURL:Got Handles.')

    def buildList(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        list_members=kwargs.get('list_members')
        list_id=kwargs.get('list_id')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name')
        handles=kwargs.get('handles')
        for handle in handles:
            if not handle in list_members:
                api.add_list_member(slug=list_id,id=api.get_user(handle).id)
        resultQ.put({'api':api,'user':user,'list_name':list_name,'list_id':list_id,'list_members':list_members})
        self.logger.info('BUILDLIST  :List built.')

    def getListTimeline(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        list_members=kwargs.get('list_members')
        list_id=kwargs.get('list_id')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name')
        handles=kwargs.get('handles')
        max_id=kwargs.get('max_id')
        since_id=kwargs.get('since_id') 
        per_page=20
        tweets=[]
        for tweet in api.list_timeline(user,list_name,per_page=per_page,max_id=max_id,since_id=since_id):
# Slow down the read. 
            time.sleep(0.5)
		#created_at=datetime.datetime.fromtimestamp(time.mktime(time.strptime(tweet.created_at,'%Y-%m-%d %H:%M:%S')))
            created_at=tweet.created_at
            #last_24hr=datetime.datetime.now() - timedelta(days=2)
            last_24hr=datetime.datetime.now() - timedelta(hours=15)
            #if since_id == None:
            #since_id=0
            max_id=tweet.id
            if (created_at < last_24hr):
                since_id=None
                max_id=None
                break
            tweets = tweets + [tweet]
# Reset max_id if per_page is less than 50% of set value.
        if len(tweets) < per_page * 0.5:
            max_id=None
        resultQ.put({'api':api,'list_name':list_name,'list_id':list_id,'user':user,'handles':handles,'max_id':max_id,'since_id':since_id,'tweets':tweets})
        self.logger.info('GetListTimeline: Got List Timeline. Now - ' + str(created_at) + '. Target - ' + str(last_24hr))

    def feedBackListTimeline(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        list_members=kwargs.get('list_members')
        list_id=kwargs.get('list_id')
        user=kwargs.get('user')
        list_name=kwargs.get('list_name')
        handles=kwargs.get('handles')
        max_id=kwargs.get('max_id')
        since_id=kwargs.get('since_id')
        resultQ.put({'api':api,'list_name':list_name,'list_id':list_id,'user':user,'handles':handles,'max_id':max_id,'since_id':since_id})
        
    def getTweet(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweets=kwargs.get('tweets')
        for tweet in tweets:
            if not tweet.retweeted:
                #print(tweet.retweeted, tweet.retweet_count, tweet.favorite_count, tweet.user.id, tweet.user.screen_name, tweet.user.followers_count)
                resultQ.put({'api':api,'tweet':tweet})
        self.logger.info('GETTWEET   :Got ' + str(len(tweets)) + ' tweets.')

    def retweetStrategy(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        created_at=tweet.created_at
        now=datetime.datetime.now()
        elapsed_hours=abs(now-created_at).total_seconds()/3600
        if elapsed_hours < 1:
            elapsed_hours=1
# Time factor
        if elapsed_hours <= 1:
            time_factor=2
        if elapsed_hours <= 2:
            time_factor=3
        elif elapsed_hours <= 4:
            time_factor=2
        elif elapsed_hours <= 10:
            time_factor=4
        elif elapsed_hours <= 12:
            time_factor=8
        else:
            time_factor=16

        retweet_factor = 15/elapsed_hours

# If one in 2500 followers liked or retweeted the status, the bot will retweet.
        if (tweet.favorite_count + tweet.retweet_count)*retweet_factor >= (tweet.user.followers_count/5000)*time_factor:
            try:
                api.retweet(tweet.id) 
                self.logger.info('RETWEET     : User  - %-10s, Favorite - %-5s, Retweet - %5s', tweet.user.screen_name, tweet.favorite_count, tweet.retweet_count)
            except:
                self.logger.error('RETWEET    : User  - %-10s, Favorite - %-5s, Retweet - %5s, Retweeted - %-5s', tweet.user.screen_name, tweet.favorite_count, tweet.retweet_count, tweet.retweeted)
                raise


class mUnitTest(unittest.TestCase):
    def setUp(self):
        self.top100 = Top100()
        self.resultQ = queue.Queue()

    def retweetStrategyMock(self):
        self.resultQ = queue.Queue()
        tweet=self.getTweetMock()
        self.top100.retweetStrategy(self.resultQ,**tweet)
        return self.resultQ.get_nowait()

    def testretweetStrategy(self):
        result = self.retweetStrategyMock()
        self.assertIsNotNone(result)
        
    def getTweetMock(self):
        tweets=self.getListTimelineMock()
        self.top100.getTweet(self.resultQ,**tweets)
        return self.resultQ.get_nowait()

    def testgetTweet(self):
        result = self.getTweetMock()
        self.assertIsNotNone(result)
        self.resultQ = queue.Queue()

    def getListTimelineMock(self):
        timeline=self.buildListMock()
        self.top100.getListTimeline(self.resultQ,**timeline)
        return self.resultQ.get_nowait()

    def testgetListTimeline(self):
        result = self.getListTimelineMock()
        self.assertIsNotNone(result)

    def feedBackListTimelineMock(self):
        tweets=self.getListTimelineMock()
        self.top100.feedBackListTimeline(self.resultQ,**tweets)
        return self.resultQ.get_nowait()

    def testfeedBackListTimeline(self):
        result = self.feedBackListTimelineMock()
        self.assertIsNotNone(result)

    def pickUserMock(self):
        self.top100.pickUser(self.resultQ)
        return self.resultQ.get_nowait()

    def testpickUser(self):
        result = self.pickUserMock()
        self.assertIsNotNone(result)

    def pickListMock(self):
        self.top100.pickList(self.resultQ)
        return self.resultQ.get_nowait()

    def testpickList(self):
        result = self.pickListMock()
        self.assertIsNotNone(result)

    def authUserMock(self):
        user=self.pickUserMock()
        self.top100.authUser(self.resultQ,**user)
        return self.resultQ.get_nowait()

    def testauthUser(self):
        result = self.authUserMock()
        self.assertIsNotNone(result)

    def getListMock(self):
        #user=self.pickUserMock()
        api=self.authUserMock()
        list_name=self.pickListMock()
        self.top100.getList(self.resultQ,**api,**list_name)
        return self.resultQ.get_nowait()
        
    def testgetList(self):
        result = self.getListMock()
        self.assertIsNotNone(result)

    def createListMock(self):
        api=self.authUserMock()
        list_name=self.pickListMock()
        #user=self.pickUserMock()
        self.top100.createList(self.resultQ,**api,**list_name)
        return self.resultQ.get_nowait()

    def testcreateList(self):
        result = self.createListMock()
        self.assertIsNotNone(result)

    def buildListMock(self):
        list_members=self.getListMembersMock()
        handles=self.getHandleFromUrlMock()
        self.top100.buildList(self.resultQ,**handles,**list_members)
        return self.resultQ.get_nowait()

    def testbuildList(self):
        result = self.buildListMock()
        self.assertIsNotNone(result)

    def getHandleFromUrlMock(self):
        self.top100.getHandlesFromUrl(self.resultQ)
        return self.resultQ.get_nowait()

    def testgetHandleFromUrl(self):
        result = self.getHandleFromUrlMock()
        self.assertIsNotNone(result)

    def getListMembersMock(self):
        list_id=self.getListMock()
        self.top100.getListMembers(self.resultQ,**list_id)
        return self.resultQ.get_nowait()

    def testgetListMembers(self):
        result = self.getListMembersMock()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main(verbosity=2,warnings='ignore')
