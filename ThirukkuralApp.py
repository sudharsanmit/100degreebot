from Twitter import Twitter
import logging
import queue
import random
import time
import unittest
from AppConfig import AppConfig
import datetime
from datetime import timedelta
from Thirukkural import TKSearch
import shelve

class Thirukkural(object):
    def __init__(self,*args,**kwargs):
#Setup log
        self.logger = logging.getLogger(__name__)

# To do: pickApp.
    def pickUser(self,resultQ,*args,**kwargs):
        user=AppConfig('apps.conf').getAppAttributes('Thirukkural').get('user')
        resultQ.put({'user':user})
        self.logger.info('PickUser    : Twitter User picked.')

    def authUser(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        api=Twitter(user)
        resultQ.put({'api':api,'user':user})
        self.logger.info('AuthUser    : User Authorized.')

    def feedBackRandomKural(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        api=kwargs.get('api')
        resultQ.put({'user':user,'api':api})

    def getRandomKural(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        api=kwargs.get('api')
        langs=['TA','EN']
        num=random.randint(1,1330)
        lang=langs[random.randint(0,1)]
        tkSearch=TKSearch()
        result=tkSearch.multi_filter(lang=lang,num=num)
        replies=[]
        for i in result:
            desc=str(i[0]) + '.' + ' ' + i[4]
            max_len=135
            offset=0
            if len(desc) > 140:
                offset=desc[:max_len][::-1].index(' ')+1
                replies.append(desc[max_len-offset+1:].strip())
                replies.append(desc[:max_len-offset+1].strip())
            else:
                replies.append(str(i[0]) + '.' + ' ' + i[4])
 
            desc=i[2] + '\n' + str(i[0]) + '.' + i[3]
            max_len=135
            offset=0
            if len(desc) > 140:
                offset=desc[:max_len][::-1].index(' ')+1
                replies.append(desc[max_len-offset+1:].strip())
                replies.append(desc[:max_len-offset+1].strip())
            else:
                replies.append(i[2] + '\n' + str(i[0]) + '.' + i[3])
        for i in replies:
            resultQ.put({'api':api,'user':user,'tweet':None,'reply':i})

    def postDummyTweet(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        api=kwargs.get('api')
        to=AppConfig('apps.conf').getAppAttributes('Thirukkural').get('user')
        msg='@'+to+' Hello ' + str(random.randint(1,999)) + '!'
        api.update_status(msg)
        resultQ.put({'api':api,'user':user,'msg':msg})

    def getMentionsTimeline(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        max_id=kwargs.get('max_id')
        since_id=kwargs.get('since_id') 
        tweets=[]
        try:
            timeline=api.mentions_timeline(max_id=max_id,since_id=since_id)
            for tweet in timeline:
# Slow down the read. 
                max_id=tweet.id
                if tweet.favorited:
                    since_id=None
                    max_id=None
                else:
                    tweets = tweets + [tweet]
    
            resultQ.put({'api':api,'user':user,'max_id':max_id,'since_id':since_id,'tweets':tweets})
            self.logger.info('GetMentionsTimeline: Mentions read.')
            #time.sleep(60.0)
        except:
            resultQ.put({'user':user,'OnFailure':True})
            self.logger.info('GetMentionsTimeline: Error in Mentions read. FeedBackAuth sent.')

    def feedBackAuth(self,resultQ,*args,**kwargs):
        user=kwargs.get('user')
        resultQ.put({'user':user})

    def feedBackMentionsTimeline(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        max_id=kwargs.get('max_id')
        since_id=kwargs.get('since_id')
        resultQ.put({'api':api,'user':user,'max_id':max_id,'since_id':since_id})
        
    def getTweet(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        user=kwargs.get('user')
        tweets=kwargs.get('tweets')
        for tweet in tweets:
            if not tweet.favorited:
                resultQ.put({'api':api,'user':user,'tweet':tweet})
        self.logger.info('GETTWEET   :Got ' + str(len(tweets)) + ' tweets.')

    def checkFriendship(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        if api.show_friendship(source_screen_name=tweet.user.screen_name,target_screen_name=user)[0].following:
            resultQ.put({'api':api,'user':user,'tweet':tweet})
    
    def favoriteTweet(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        api.create_favorite(id=tweet.id)

    def formatReply(self,reply,**kwargs):
        tweet=kwargs.get('tweet')
        replies=[]
        if reply.get('error'):
            replies.append('@' + tweet.user.screen_name + ' ' + reply.get('head') + '\n ' + reply.get('error'))
        elif reply.get('result'):
            for i in reply.get('result'):
                #replies.append('@' + tweet.user.screen_name + ' ' + i[2] + '\n' + str(i[0]) + '.' + i[3])
                desc='@' + tweet.user.screen_name + ' ' + str(i[0]) + '.' + ' ' + i[4]
                max_len=135
                offset=0
                if len(desc) > 140:
                    offset=desc[:max_len][::-1].index(' ')+1
                    replies.append('@' + tweet.user.screen_name + ' ' + desc[max_len-offset+1:].strip())
                    replies.append(desc[:max_len-offset+1].strip())
                else:
                    replies.append('@' + tweet.user.screen_name + ' ' + str(i[0]) + '.' + ' ' + i[4])

                desc='@' + tweet.user.screen_name + ' ' + i[2] + '\n' + str(i[0]) + '.' + i[3]
                max_len=135
                offset=0
                if len(desc) > 140:
                    offset=desc[:max_len][::-1].index(' ')+1
                    replies.append('@' + tweet.user.screen_name + ' ' + desc[max_len-offset+1:].strip())
                    replies.append(desc[:max_len-offset+1].strip())
                else:
                    replies.append('@' + tweet.user.screen_name + ' ' + i[2] + '\n' + str(i[0]) + '.' + i[3])

        else:
            replies.append('@' + tweet.user.screen_name + ' ' + reply.get('head') + '\n ' + reply.get('body'))
        return replies

    def searchStrategy(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        in_reply_to=tweet.in_reply_to_status_id

        if in_reply_to:
            reply=self.searchKurals(*args,**kwargs)
        else:
            reply=self.welcome()

        media_ids=reply.get('media_ids')
        for i in self.formatReply(reply,**kwargs):
            resultQ.put({'api':api,'user':user,'tweet':tweet,'reply':i,'media_ids':media_ids})

    def welcome(self,*args,**kwargs):
        stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage0')
        head=AppConfig('apps.conf').getAppAttributes('Thirukkural_Header')
        head_sel=head.get('head_sel2')
        head_res=head.get('head_res2')
#  
        reply={}
        reply['head']=head_sel + ',,,,,' + head_res 
        reply['body']= stage_params.get('options')
        return reply

    def searchKurals(self,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        in_reply_to=tweet.in_reply_to_status_id
        parent_tweet=api.statuses_lookup(id=[tweet.in_reply_to_status_id])[0].text
        selections = parent_tweet.split('::')[1]
        reply=self.getReplyForStage(selections,*args,**kwargs)
        return reply

    def getMediaIds(self,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        media_ids=[]
        db=shelve.open('db/thirukkural')
        for i in range(1,5):
            twitter_media_id=db.get(user+'adhi_' + str(i) + '.jpg')
            if not twitter_media_id: 
                twitter_media_id=api.media_upload('img/adhi_' + str(i) + '.jpg').media_id
                db[user+'adhi_'+ str(i) + '.jpg'] = twitter_media_id
            media_ids.append(twitter_media_id)
        db.close()
        return media_ids

    def getReplyForStage(self,selections,*args,**kwargs):
        reply={}
# Input Section
        selected_values=selections.split(':')[1].split(',')
        user_option=kwargs.get('tweet').text.strip().split(' ')[1]
        stage=len(list(filter(lambda x:x != '',selected_values)))
        api_arr=['' for _ in range(0,7)]
#
        # TKSearch API variables
        tkSearch=TKSearch()
        num=None
        pal=None
        adhi=None
        start=None
        end=None
        has=None
        lang=None
        # API variables end.

        for i in range(0,stage+1):
            if i > 6:
                break 
            elif selected_values[i] != '':
                if i == 0:
                    stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(i))
                else:
                    stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(api_arr[0])+str(i))
                if stage_params.get('option_type') == 'NUMERIC':
                    api_arr[i]=int(selected_values[i])

                if stage_params.get('option_type') == 'ALPHANUMERIC':
                    api_arr[i]=selected_values[i]

                #api_arr[i]=selected_values[i]
            else:
                head=AppConfig('apps.conf').getAppAttributes('Thirukkural_Header')
                if i == 0:
                    stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(i))
                else:
                    stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(api_arr[0])+str(i))
                if stage_params.get('option_type') == 'NUMERIC':
                    if not user_option.isdigit():
                        reply['error']=stage_params.get('error')
                        api_arr[i]=user_option
                    elif (int(user_option) < int(stage_params.get('option_min')) or int(user_option) > int(stage_params.get('option_max'))):
                        reply['error']=stage_params.get('error')
                    else:
                        api_arr[i]=int(user_option)

                if stage_params.get('option_type') == 'ALPHANUMERIC':
                    if user_option in ['',None]:
                        reply['error']=stage_params.get('error')
                    else:
                        api_arr[i]=user_option

                if i < 6:
                    head_sel=head.get('head_sel' + str(api_arr[0]))
                    head_res=head.get('head_res' + str(api_arr[0]))
                    stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(api_arr[0])+str(stage+1))

                    values=''
                    for j in range(0,6):
                        if str(api_arr[j]):
                            values=values + str(api_arr[j])+','
                        else:
                            values=values + ','
                    header=head_sel + values + head_res
                    footer=stage_params.get('options')
                break
     
 
        if not reply.get('error'):
            if api_arr[0] and api_arr[0] > 0:
                if api_arr[0] == 1:
                    lang='TA'
                else:
                    lang='EN'

            if stage == 2:
                try:
                    reply['media_ids']=self.getMediaIds(*args,**kwargs)
                except:
                    pass


            if api_arr[1] and api_arr[1] > 0:
                num=api_arr[1]
    
            if api_arr[2] and api_arr[2] > 0:
                pal=api_arr[2]

            if api_arr[3] and api_arr[3] > 0:
                adhi=api_arr[3]

            if api_arr[4] and api_arr[5] and api_arr[4] == 1:
                start=api_arr[5]

            if api_arr[4] and api_arr[5] and api_arr[4] == 2:
                end=api_arr[5]

            if api_arr[4] and api_arr[5] and api_arr[4] == 3:
                has=api_arr[5]

            result=tkSearch.multi_filter(lang=lang,num=num,pal=pal,adhi=adhi,start=start,end=end,has=has)

        if reply.get('error'):
            reply['head']=header
        elif stage == 5 or (stage == 4 and int(user_option) == 4) or (stage == 1 and int(user_option) > 0): 
            if len(result) > 25: #int(stage_params.get('option_max')):
                reply['head']=header+str(len(result))
                reply['body']=stage_params.get('error')
            elif len(result) == 0:
                print(len(result))
                reply['head']=header+str(len(result))
                reply['error']=stage_params=AppConfig('apps.conf').getAppAttributes('Thirukkural_Stage'+str(api_arr[0])+str(5)).get('error')
            else:
                print('nonz'+len(result))
                reply['result'] = result
        else:
            reply['head']=header+str(len(result))
            reply['body']=footer

        return reply

    def sendReply(self,resultQ,*args,**kwargs):
        api=kwargs.get('api')
        tweet=kwargs.get('tweet')
        user=kwargs.get('user')
        reply=kwargs.get('reply')
        media_ids=kwargs.get('media_ids')
        if tweet:
            api.update_status(reply,in_reply_to_status_id=tweet.id,media_ids=media_ids) 
        else:
            api.update_status(reply) 
        self.logger.info('sendReply   : Reply sent.')
        time.sleep(5.0)

class mUnitTest(unittest.TestCase):
    def setUp(self):
        self.thirukkural = Thirukkural()
        self.resultQ = queue.Queue()
        self.test_user=AppConfig('apps.conf').getAppAttributes('Thirukkural').get('test_user')

    def pickUserMock(self):
        self.thirukkural.pickUser(self.resultQ)
        return self.resultQ.get_nowait()

    def testpickUser(self):
        result = self.pickUserMock()
        self.assertIsNotNone(result)

    def authTestUserMock(self):
        user=self.test_user
        self.thirukkural.authUser(self.resultQ,**user)
        return self.resultQ.get_nowait()

    def authUserMock(self):
        user=self.pickUserMock()
        self.thirukkural.authUser(self.resultQ,**user)
        return self.resultQ.get_nowait()

    def testauthUser(self):
        result = self.authUserMock()
        self.assertIsNotNone(result)

    def postDummyTweetMock(self):
        self.thirukkural.authUser(self.resultQ,**{'user': self.test_user})
        api=self.resultQ.get_nowait()
        self.thirukkural.postDummyTweet(self.resultQ,**api)
        return self.resultQ.get_nowait()

    def testpostDummyTweet(self):
        result = self.postDummyTweetMock().get('msg')
        self.assertIsNotNone(result)

    def getMentionsTimelineMock(self):
        api=self.authUserMock()
        self.thirukkural.getMentionsTimeline(self.resultQ,**api)
        return self.resultQ.get_nowait()
        
    def testgetMentionsTimeline(self):
        result=self.getMentionsTimelineMock()
        self.assertGreater(len(result),0)

    def feedBackMentionsTimelineMock(self):
        tweets=self.getMentionsTimelineMock()
        self.thirukkural.feedBackMentionsTimeline(self.resultQ,**tweets)
        return self.resultQ.get_nowait()

    def testfeedBackMentionsTimeline(self):
        result = self.feedBackMentionsTimelineMock()
        self.assertIsNotNone(result)

    def getTweetMock(self):
        tweets=self.getMentionsTimelineMock()
        self.thirukkural.getTweet(self.resultQ,**tweets)
        return self.resultQ.get_nowait()

    def testgetTweet(self):
        result = self.getTweetMock()
        self.assertIsNotNone(result)
        self.resultQ = queue.Queue()

    def checkFriendshipMock(self):
        tweet=self.getTweetMock()
        self.thirukkural.checkFriendship(self.resultQ,**tweet)
        return self.resultQ.get_nowait()    

    def testcheckFriendship(self):
        result = self.checkFriendshipMock()
        self.assertIsNotNone(result)

    def searchStrategyMock(self):
        tweet=self.checkFriendshipMock()
        self.thirukkural.searchStrategy(self.resultQ,**tweet)
        return self.resultQ.get_nowait()    

    def testsearchStrategy(self):
        result = self.searchStrategyMock()
        self.assertIsNotNone(result)

    def sendReplyMock(self):
        reply=self.searchStrategyMock()
        self.thirukkural.sendReply(self.resultQ,**reply)
        return self.resultQ.get_nowait()    

    def testsendReply(self):
        result = self.sendReplyMock()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main(verbosity=2,warnings='ignore')
