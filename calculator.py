import queue
import random
import time
import unittest
class calculator(object):
    def __init__(self,*args,**kwargs):
        self._a = None
        self._b = None
        self._result = None

    def add(self,resultQ,*args,**kwargs):
        self._result = kwargs.get('value1') + kwargs.get('value2')
        resultQ.put({'op1':self._result})

    def input(self,resultQ,*args,**kwargs):
        for i in range(1000):
            self._a = random.randint(0,9999)
            self._b = random.randint(0,9999)
            resultQ.put({'value1':self._a,'value2':self._b})

    def result(self,resultQ,*args,**kwargs):
        resultQ.put({'result':kwargs.get('op1')})
        resultQ.put({'result':kwargs.get('op2')})

    def subtract(self,resultQ,*args,**kwargs):
        self._result = kwargs.get('value1') - kwargs.get('value2')
        resultQ.put({'op2':self._result})

class mUnitTest(unittest.TestCase):
    def setUp(self):
        self.calculator = calculator()
        self.resultQ = queue.Queue()

    def testAdd(self):
        self.calculator.add(self.resultQ,value1=1,value2=2)
        result = self.resultQ.get_nowait()
        self.assertEqual({'op1':3},result)

    def testSubtract(self):
        self.calculator.subtract(self.resultQ,value1=1,value2=2)
        result = self.resultQ.get_nowait()
        self.assertEqual({'op2':-1},result)
 
    def testInput(self):
        self.calculator.input(self.resultQ)
        result = self.resultQ.get_nowait()
        self.assertIsNotNone(result)

#    def tearDown(self):
#        self.calculator.dispose()
#        self.resultQ.dispose()

if __name__ == '__main__':
    unittest.main()
