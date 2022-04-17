#  객체추적기
import cv2
#import centroidtracker
#import trackableobject
import numpy as np
from partObject import partObject

class objectTracker():
    def __init__(self):
        self.tImage = None
        self.tWrect = None
        self.mtracker = None
        self.rno = 0
        self.speed = 2
        #self.ct = centroidtracker.CentroidTracker()
        self.trackableObjects = {}
        self.W = 480
        self.H = 270
        # 객체 시작점 튜플
        self.object_start_tuple = ()

    def setLineNo(self, rno):
        print('Object Tracker line set = '+ str(rno))
        self.rno = rno

    def timeTracking(self,obj):
        curTime = obj.checkTimeDistance()
        print(' distance ' + str(curTime))
    
    def trackClear(self):
        self.mtracker = None

    def initialize(self, tImage, trect):
        reportMsg = ' initialize '
        rtnFlag = -1
        self.tImage = tImage
        self.tWrect = trect
        
        if tImage.shape[1] > trect[0] + trect[2] and tImage.shape[0] > trect[1] + trect[3]:
            #self.mtracker = cv2.legacy.TrackerBoosting_create()
            #self.mtracker =cv2.TrackerBoosting_create()
            self.mtracker = cv2.legacy.TrackerCSRT_create() 
            if self.mtracker.init(self.tImage, self.tWrect):
                reportMsg = reportMsg + ' & init targaet'
                rtnFlag = 1
            else:
                reportMsg = reportMsg + ' & init Fail '        
        else :
            reportMsg = 'init (Out of start area)'  
            rtnFlag = 2  
        return reportMsg, rtnFlag 


    def tracking(self, srcImage, obj):
        reportMsg = ' '
        rtnFlag = False
        dx = 0

        rc = [110,10,10,10]
        if self.mtracker is not None :
            success, rc = self.mtracker.update(srcImage)
            if success:                
                rtnFlag = True
                
                rc = tuple([int(_) for _ in rc])
                #print(' ** ' +str(rc[0])+ ' : '+ str(obj.x)) 
                dx = rc[0] - obj.x    
                dxx = obj.x 
                if self.rno == 1 :
                    if dx  < 17 and dx > -40:
                        #obj.setExp(rc[0])
                        reportMsg += ' track success '
                    else :
                        rtnFlag = False
                        rc = [121,100,10,10]
                        reportMsg += '1L dx = '+str(dx)
                        dx = 0
                else :
                    if dx > -17 and dx < 40 :
                        #obj.setExp(rc[0])                                              
                        reportMsg += ' TRACK success '
                    else :
                        rtnFlag = False
                        rc = [121,100,10,10]
                        reportMsg += '2L dx = '+str(dx)
                        dx = 0
            else :
                reportMsg = reportMsg + 'track fail '
                
        return reportMsg, rtnFlag, dx, rc
