import time
from ModelBootstrap import ModelBootstrap
import ModelManager
import threading

#def threadStatus():
#    for modelName, _threads in ModelManager.ModelManager().getModelThreads():
#        for _thread in _threads:
#            print(modelName,_thread.getName(),_thread.is_alive())

def bootstrap(_filename):
#Model Bootstrap
    mb = ModelBootstrap(filename=_filename)

t = threading.Thread(target=bootstrap,args=('models.conf',))
t.setDaemon(False)
while True:
    t.start()
#    for _ in range(10):
#        threadStatus()
#        time.sleep(1)
    time.sleep(15)
#    t.stop()
    print('Thread stopped')
    break
    #pass

