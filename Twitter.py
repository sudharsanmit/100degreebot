import tweepy
import json
#from userschema import *
import useraccess 
import time
import logging
import logging.config
#import oauth2
import base64
import urllib

class Twitter(object):
    def __init__(self,handle):
        self._api = None
        self._endpoint = None
        self._message=None
        u = useraccess.UserAccess();
        auth = tweepy.OAuthHandler(u.getConsumerKey(handle),u.getConsumerSecret(handle))
        auth.set_access_token(u.getAccessToken(handle),u.getAccessTokenSecret(handle))
        self._api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=3, retry_delay=10)

    @property
    def api(self):
        """I'm the 'api' property."""
        return self._api

    @api.setter
    def api(self, value):
        self._api = value

    @api.deleter
    def api(self):
        del self._api

    def debug(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            elapsed = str(float(te - ts))
            logger = logging.getLogger(__name__)
            logger.debug(str(args) + '. Elapsed time - ' + str(elapsed) + ' secs.')
            return result
        return timed

    def wait(self,secs):
        if secs == 0:
            return
        logging.warning('Limit reached. Waiting for ' + str(secs) + ' seconds.')
        time.sleep(secs)

    def getRateLimit(self,rate_data,endpoint):
        return rate_data['resources'][endpoint.split('/')[1]][endpoint]['limit']

    def getRemaining(self,rate_data,endpoint):
        return rate_data['resources'][endpoint.split('/')[1]][endpoint]['remaining']

    def getResetTime(self,rate_data,endpoint):
        return rate_data['resources'][endpoint.split('/')[1]][endpoint]['reset']

    def check_rate_to_wait(self,rate_data):
        # Rate_limit_Status endpoint
        rate_limit_endpoint = '/application/rate_limit_status'

        endpoint_limit = self.getRateLimit(rate_data,self._endpoint)
        rate_check_limit = self.getRateLimit(rate_data,rate_limit_endpoint)
        endpoint_remain = self.getRemaining(rate_data,self._endpoint)
        rate_check_remain = self.getRemaining(rate_data,rate_limit_endpoint)
        endpoint_reset_time = self.getResetTime(rate_data,self._endpoint)
        rate_check_reset_time = self.getResetTime(rate_data,rate_limit_endpoint)

        print(endpoint_remain, rate_check_remain)
        # Wait if the remaining limit is less than 10% of total limit
        threshold = 0.1
        return
        if (endpoint_remain <= endpoint_limit * threshold):
            self.wait(endpoint_reset_time - int(time.time()) + 1)

        if (rate_check_remain <= rate_check_limit * threshold):
            self.wait(rate_check_reset_time - int(time.time()) + 1)

###### TWITTER PUBLIC API START ##################################################
    def rate_limit_status(self):
        rate_data = self._api.rate_limit_status()
        self._endpoint = '/application/rate_limit_status'
        self.check_rate_to_wait(rate_data)


# 
# API.update_status(status[, in_reply_to_status_id][, lat][, long][, source][, place_id])
# Update the authenticated user’s status. Statuses that are duplicates or too long will be silently ignored.
# 
# Parameters:	
# status – The text of your status update.
# in_reply_to_status_id – The ID of an existing status that the update is in reply to.
# lat – The location’s latitude that this tweet refers to.
# long – The location’s longitude that this tweet refers to.
# source – Source of the update. Only supported by Identi.ca. Twitter ignores this parameter.
# place_id – Twitter ID of location which is listed in the Tweet if geolocation is enabled for the user.
# Return type:	
# Status object

    def update_status(self,status,in_reply_to_status_id=None,lat=None,long=None,source=None,place_id=None,media_ids=None):
        self._api.update_status(status,in_reply_to_status_id,lat,long,source,place_id,media_ids=media_ids)

# API.create_list(name[, mode][, description])
# Creates a new list for the authenticated user. Accounts are limited to 20 lists.
# 
# Parameters:	
# name – The name of the new list.
# mode – Whether your list is public or private. Values can be public or private. Lists are public by default if no mode is specified.
# description – The description of the list you are creating.
# Return type:	
# List object

    def create_list(self,name, mode='private', description=None):
        return self._api.create_list(name,mode,description)

# API.get_list(owner, slug)
# Show the specified list. Private lists will only be shown if the authenticated user owns the specified list.
# 
# Parameters:	
# owner – the screen name of the owner of the list
# slug – the slug name or numerical ID of the list
# Return type:	
# List object
   
    def get_list(self,owner, slug):
        return self._api.get_list(owner_screen_name=owner,slug=slug)

# API.lists([cursor])
# List the lists of the specified user. Private lists will be included if the authenticated users is the same as the user who’s lists are being returned.
# 
# Parameters:	cursor – Breaks the results into pages. Provide a value of -1 to begin paging. Provide values as returned to in the response body’s next_cursor and previous_cursor attributes to page back and forth in the list.
# Return type:	list of List objects

    def lists_all(self,cursor=None):
        return self._api.lists_all()

# 
# API.add_list_member(slug, id)
# Add a member to a list. The authenticated user must own the list to be able to add members to it. Lists are limited to having 500 members.
# 
# Parameters:	
# slug – the slug name or numerical ID of the list
# id – the ID of the user to add as a member
# Return type:	
# List object
# 
    def add_list_member(self,slug,id):
        self._api.add_list_member(list_id=slug,user_id=id)

# API.remove_list_member(slug, id)
# Removes the specified member from the list. The authenticated user must be the list’s owner to remove members from the list.
# 
# Parameters:	
# slug – the slug name or numerical ID of the list
# id – the ID of the user to remove as a member
# Return type:	
# List object
# 
    def remove_list_member(self,slug, id):
        self._api.remove_list_member(slug,id)

# API.list_members(owner, slug, cursor)
# Returns the members of the specified list.
# 
# Parameters:	
# owner – the screen name of the owner of the list
# slug – the slug name or numerical ID of the list
# cursor – Breaks the results into pages. Provide a value of -1 to begin paging. Provide values as returned to in the response body’s next_cursor and previous_cursor attributes to page back and forth in the list.
# Return type:	
# list of User objects
# 
    def list_members(self,owner,slug,cursor=None):
        return list(members.screen_name for members in tweepy.Cursor(self._api.list_members,owner,slug).items())
        #return self._api.list_members(owner,slug,cursor)

# API.is_list_member(owner, slug, id)
# Check if a user is a member of the specified list.
# 
# Parameters:	
# owner – the screen name of the owner of the list
# slug – the slug name or numerical ID of the list
# id – the ID of the user to check
# Return type:	
# User object if user is a member of list, otherwise False.

    def is_list_member(self,owner,slug,id):
        return self._api.is_list_member(owner,slug,id)
 
# API.retweet(id)
# Retweets a tweet. Requires the id of the tweet you are retweeting.
# 
# Parameters:	id – The numerical ID of the status.
# Return type:	Status object

    def retweet(self,id):
        return self._api.retweet(id)

# API.get_user(id/user_id/screen_name)
# Returns information about the specified user.
# 
# Parameters:	
# id – Specifies the ID or screen name of the user.
# user_id – Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.
# screen_name – Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
# Return type:	
# User object

    def get_user(self,screen_name=None):
        return self._api.get_user(screen_name=screen_name)

# API.list_timeline(owner, slug[, since_id][, max_id][, per_page][, page])
# Show tweet timeline for members of the specified list.
# 
# Parameters:	
# owner – the screen name of the owner of the list
# slug – the slug name or numerical ID of the list
# since_id – Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
# max_id – Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
# per_page – Number of results per a page
# page – Specifies the page of results to retrieve. Note: there are pagination limits.
# Return type:	
# list of Status objects

    def list_timeline(self,owner,slug,since_id=None,max_id=None,per_page=None,page=None):
        return self._api.list_timeline(owner,slug,since_id=since_id,max_id=max_id,per_page=per_page)

    def media_upload(self,media,media_data=None):
        return self._api.media_upload(media,media_data)

    def mentions_timeline(self,since_id=None,max_id=None):
        return self._api.mentions_timeline(since_id=since_id,max_id=max_id)

# API.exists_friendship(user_a, user_b)
# Checks if a friendship exists between two users. Will return True if user_a follows user_b, otherwise False.
#
# Parameters:
# user_a – The ID or screen_name of the subject user.
# user_b – The ID or screen_name of the user to test for following.
# Return type:
# True/False

    def show_friendship(self,source_screen_name=None,target_screen_name=None):
        return self._api.show_friendship(source_screen_name=source_screen_name,target_screen_name=target_screen_name)

# API.create_favorite(id)
# Favorites the status specified in the ID parameter as the authenticating user.
# 
# Parameters:	id – The numerical ID of the status.
# Return type:	Status object

    def create_favorite(self,id=None):
        return self._api.create_favorite(id=id)

# API.statuses_lookup(id[, include_entities][, trim_user][, map])
# Returns full Tweet objects for up to 100 tweets per request, specified by the id parameter.
#
# Parameters:
# id – A list of Tweet IDs to lookup, up to 100
# include_entities – A boolean indicating whether or not to include [entities](https://dev.twitter.com/docs/entities) in the returned tweets. Defaults to False.
# trim_user – A boolean indicating if user IDs should be provided, instead of full user information. Defaults to False.
# map – A boolean indicating whether or not to include tweets that cannot be shown, but with a value of None. Defaults to False.
# Return type:
# list of Status objects

    def statuses_lookup(self,id=None,include_entities=None,trim_user=None,map=None):
        return self._api.statuses_lookup(id_=id,include_entities=include_entities,trim_user=trim_user,map_=map)

##  ##################################################################################

#t=Twitter('sudharsanmit')
#t.create_list('test')
#for list in t.lists_all():
#    print (list.slug)
#list_id=t.get_list('sudharsanmit','Top100').id
#t.add_list_member(slug=list_id,id=t.get_user('pughazhchola').id)
#t.add_list_member(slug=list_id,id=t.get_user('swamy39').id)
#for m in t.list_members('sudharsanmit','Top100'):
#    print(m.id,m.screen_name)
#print(t.list_members('sudharsanmit','Top100'))
#print(t.list_timeline('sudharsanmit','Top100',per_page=20))
#for tweet in t.list_timeline('sudharsanmit','Top100',per_page=20,max_id=759217971860504581,since_id=759215706483326976):
#     print(tweet.id)
