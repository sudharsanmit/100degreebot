import time
from ModelBootstrap import ModelBootstrap
import ModelManager
import threading

def bootstrap(_filename):
#Model Bootstrap
    mb = ModelBootstrap(filename=_filename)

t = threading.Thread(target=bootstrap,args=('Top100.conf',))
t.setDaemon(False)
while True:
    t.start()
    time.sleep(1*60*60*24)
    print('Thread stopped')
    break
