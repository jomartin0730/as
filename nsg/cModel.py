import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
import time
import cv2
import partObject
from partObject import ObjectList
# import Motion

import objectTracker
import lineDetector
import partClassInfo
from transitions import Machine

class cModel(object):  # step checker model
    def __init__(self):
        self.src = None
        self.rno = -1 # not set 
     
        self.detect_working = True

        self.lifeTime = 100



   
    def input(self):        
        print('input')
        return True

    def detect(self):
        print('is detect')        
        return True

    def check(self):
        print ('condition check')
        return True

