import urllib3
from bs4 import BeautifulSoup
import time
import logging
import unittest

class Top(object):
    def __init__(self):
#Setup log
        self.logger = logging.getLogger(__name__)
        self.http=urllib3.PoolManager()
        self.response=None
        self.url=None

    def getUrl(self):
        return self.http.request('GET',self.url)

    def getHtml(self):
        self.response=self.getUrl()
        if self.response.status == 200:
            return BeautifulSoup(self.response.data,'html.parser')
        else:
            return None
 
    def getHandles(self):
        return self.getHtml().find_all('span',{'itemprop':'alternateName'}) 

    def getUsers(self):
        return list(str(handle.string).replace('@','') for handle in self.getHandles())

    def getTop100(self):
        self.url='http://twittercounter.com/pages/100'
        return self.getUsers() 

class mUnitTest(unittest.TestCase):
    def setUp(self):
        self.top = Top()
        self.top.url="http://twittercounter.com/pages/100"

    def testgetUrl(self):
        result=self.top.getUrl()
        self.assertEqual(result.status,200)
        self.assertIsNotNone(result.data)

    def testgetHtml(self):
        result=self.top.getHtml()
        self.assertIsNotNone(result)

    def testgetHandles(self):
        result=self.top.getHandles()
        self.assertEqual(len(result),100)

    def testgetUsers(self):
        result=self.top.getUsers()
        self.assertEqual(len(result),100)

    def testgetUsers(self):
        result=self.top.getUsers()
        self.assertEqual(len(result),100)
        self.top.url="http://www.google.com"
        result=self.top.getUsers()
        self.assertEqual(len(result),0)


if __name__ == '__main__':
    unittest.main(verbosity=2,warnings='ignore')
