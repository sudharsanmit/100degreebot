from __future__ import print_function
import json
import apiclient
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import verify_id_token
import httplib2
import urllib3

#Alternate method instead of using google built-in api.
#def short_url(url):
#    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key='+API_KEY
#    params = json.dumps({'longUrl': url})
#    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
#    return response

class Firebase(object):
    def __init__(self,keyFile):
        self._API_KEY = 'AIzaSyAwWRMFi_l5PStENHDn1i8QF060T_Hdc-k' 
        self._scopes = ['https://www.googleapis.com/auth/firebase.database','https://www.googleapis.com/auth/userinfo.email']
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile,self._scopes)

        #h = self._credentials.authorize(httplib2.Http())
        #print(h)
        #res,cont = h.request('https://shorturl-1267.firebaseio.com/users.json')
        #print(res,cont)

        h = self._credentials.authorize(urllib3.PoolManager())
        print(h.request)
        res,cont = h.request.get('https://shorturl-1267.firebaseio.com/users.json')
        #print(res,cont)
        

# PRIVATE METHODS
    def getNoAuthService(self):
        return build('urlshortener', 'v1', developerKey=self._API_KEY)

    def getNoAuth(self,shortUrl):
        return self.getNoAuthService().url().get(shortUrl=shortUrl,projection="FULL").execute()

    def getAuthService(self):
        return build('urlshortener', 'v1', credentials=self._credentials) 

    def list(self):
        return self.getAuthService().url().list().execute()

    def get(self,shortUrl):
        return self.getAuthService().url().get(shortUrl=shortUrl,projection="FULL").execute()

# PUBLIC METHODS FOLLOW...
    def insert(self,longUrl):
        return self.getAuthService().url().insert(body=dict(zip(['longUrl'],[longUrl]))).execute()

    def getLongUrl(self,shortUrl):
        return self.get(shortUrl)['longUrl']

    def getShortUrl(self,longUrl):
        return self.insert(longUrl)['id']

    def getUrlList(self):
        return (dict(zip(['shortUrl'],[i['id']])) for i in self.list()['items'])


g=Firebase('config/SHORTURL-71318685345a.json')
#g=ShortUrl('config/gmail-oauth2-498963b603b9.json')
#print(list(i.getUrlList()))
