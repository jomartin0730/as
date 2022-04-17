# part id 를 검색해서 code를 리턴하는 Node
# QThred로부터 상속받아 Signal로 동작한다.
import os
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import time
import sys
import cv2
import os
import struct
import datetime
from utils_ds.draw import draw_boxes
#import MovingFilter
import JsonLoader
import partClassInfo
import detect
import detectAndTrack
import MysqlController
from partObject import *


json_data = JsonLoader.JsonLoader().load_data("dsensor")
min_area = json_data['contour']['min_area']  # 2**9=512
arcRate = json_data['contour']['arcRate']
xs = json_data['state']['start_x']
st = json_data['state']['step_width']
rc = json_data['state']['recycle_count']
cThHold = json_data['state']['cThHold']

fps = json_data['speed']['fps']
px2m = json_data['speed']['px2m']
ms2kmh = json_data['speed']['ms2kmh']

class DetectSignal(QObject):
    partObjSig = pyqtSignal(partObject)
    report_signal = pyqtSignal(str)
    clsStep_signal = pyqtSignal(int, int, int)
    dt_signal = pyqtSignal(list)

class nodePartDetector(QThread):
    def __init__(self, r_no, parent=None):
        super(self.__class__, self).__init__(parent)

        #self.detector = detect.Detector()
        self.detector = detectAndTrack.Detector()
        self.detector.detect_set(r_no)
        self.rno = r_no
        self.pInfo = partClassInfo.partClassInfo()
        self.working = True
        self.dsig = DetectSignal()
        self.partID = 'None'
        self.state  = 'report'
        self.oldPartClass = 'default'       
        self.text = '1'
        self.value = 0
        self.sourceImage = None
        self.flag = False
        self.frame_idx = 0
        self.lifeTime = 130

    def __del__(self):
        print(".....end thread.")
    
    def setImage(self, src_img):
        self.sourceImage = src_img
        self.flag = True
        self.frame_idx += 1
        

    def detectObject(self, image):  # 갹체 탐지 함수
        #avg_fps = [], [], []
        self.src  = image
        reportMsg = 'detectObject '
        xyxy, rimg, clsname, detect_check, outputs = self.detector.detect(image)
        obj = None
        if clsname is not None:
            pCls = self.pInfo.getClass(clsname + '#' + str(self.rno))
            #print(pCls.getSA)
            if xyxy is not None:
                obj = partObject(clsname)
                obj.setPartClass(pCls)
                if self.oldPartClass != clsname:                                
                    self.oldPartClass = clsname   

                if obj.setXYXY(xyxy): 
                    obj.reBorn(self.lifeTime)
                    reportMsg += ' obj born'
                    #msg, trn = self.tracker.initialize(obj.setTWinImage(image),obj.getBoxInTwin())
                    #reportMsg += msg
                else :
                    obj = None
                    reportMsg += ' obj set width & height fail '
            else :
                reportMsg += ' xyxy is None '
        else : 
            reportMsg += ' Not detect '     
            pCls = None
            obj = None
        outs = []
        # visualize bbox  ********************************
        if len(outputs) > 0:
            #print(' detect length = '+ str(len(outputs) ))
            bbox_xyxy = outputs[:, :4]
            identities = outputs[:, -1]

            offset=(0,0)
            for i,box in enumerate(bbox_xyxy):
                cobj = partObject(clsname)
                cobj.setBox(box)
                
                # box text and bar
                id = int(identities[i]) if identities is not None else 0    
                cobj.uID = id
                outs.append(cobj)
                
        return reportMsg, obj, pCls , outs    

    def stop(self):
        self.working = False
        self.flag = False

    # main Thread 
    def run(self) :

        self.dsig.report_signal.emit('part Detector ON')
        self.working = True
        while self.working :
            self.newTime = time.time()
            reportMsg = 'p ('+str(self.frame_idx )+ ')  '
            #print('NPD start part detwecttor '+ str(self.newTime))
            # 영상확인
            if self.flag :
                obj = None
                self.newTime = time.time()
                # 객체인식 테스트 코드
                rmsg, obj, pCls, outs = self.detectObject(self.sourceImage)
                
                if pCls is not None and pCls.cname != self.partID:
                    # 새품종인지를 확인해서 새품종일 때문 동작하도록 해야 함.
                    self.dsig.clsStep_signal.emit(pCls['ready'], pCls['start'], pCls['end'])
                    reportMsg = reportMsg + ' ' + pCls.cname
                    self.partID = pCls.cname
                    
                if obj is not None:
                    #part object를 생성하여 전달
                    self.dsig.partObjSig.emit(obj)
                    reportMsg += ' obj detect ! '

                reportTime = " : "+ str(time.time() - self.newTime)                
                reportMsg = reportMsg + rmsg + self.partID + reportTime                
                #print(reportMsg)  
                if outs is not None:    
                    self.dsig.dt_signal.emit(outs)
 

                self.flag = False
            time.sleep(0.01)
