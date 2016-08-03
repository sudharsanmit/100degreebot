from __future__ import print_function
import json
import apiclient
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
#from httplib2 import Http

#Alternate method instead of using google built-in api.
#def short_url(url):
#    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key='+API_KEY
#    params = json.dumps({'longUrl': url})
#    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
#    return response

class ShortUrl(object):
    def __init__(self,keyFile):
        print(keyFile)
        self._API_KEY = 'AIzaSyAwWRMFi_l5PStENHDn1i8QF060T_Hdc-k' 
        self._scopes = ['https://www.googleapis.com/auth/urlshortener']
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile,self._scopes)

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

    def insert(self,longUrl):
        return self.getAuthService().url().insert(body=dict(zip(['longUrl'],[longUrl]))).execute()

    def getLongUrl(self,shortUrl):
        return self.get(shortUrl)['longUrl']

    def getShortUrl(self,longUrl):
        return self.insert(longUrl)['id']

    def getUrlList(self):
        return (dict(zip(['shortUrl'],[i['id']])) for i in self.list()['items'])


#    g=ShortUrl('SHORTURL-71318685345a.json')
      
