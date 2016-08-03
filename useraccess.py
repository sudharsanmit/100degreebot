import tweepy
import json
from userschema import *
import time
import logging
import logging.config

class UserAccess(object):
    def __init__(self):
        self._credentials = {}
        for j in userdata:
            self._credentials[json.dumps(dict(zip(schema[0:1],j[0:1])))]=json.dumps(dict(zip(schema[1:],j[1:])))


    @property
    def credentials(self):
        """I'm the 'credentails' property."""
        return self._credentials

    @credentials.setter
    def credentials(self, value):
        self._credentials = value

    @credentials.deleter
    def credentails(self):
        del self._credentials

    def getUser(self,handle):
        return json.loads(json.dumps(self._credentials))[json.dumps(dict(zip(['userid'],[handle])))] 

    def getConsumerKey (self,handle):
        return json.loads(self.getUser(handle))['consumer_key']

    def getConsumerSecret (self,handle):
        return json.loads(self.getUser(handle))['consumer_secret']

    def getAccessToken (self,handle):
        return json.loads(self.getUser(handle))['access_token']

    def getAccessTokenSecret (self,handle):
        return json.loads(self.getUser(handle))['access_token_secret']

    def userList(self):
        return [keys for keys in self._credentials]
