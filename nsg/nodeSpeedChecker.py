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

import scipy as sp
import objectTracker
import lineDetector
import partObject

class SpeedSignal(QObject):
    report_signal = pyqtSignal(str)
    speed_signal = pyqtSignal(float, int)
    rstImg_signal = pyqtSignal(np.ndarray)

class nodeSpeedChecker(QThread):
    def __init__(self, r_no,  parent=None):
        super(self.__class__, self).__init__(parent)
        self.working = True    
        self.rno = r_no        
        self.sig = SpeedSignal()      
        self.partID = 'TestXXX'
        self.state  = 'report'
        self.text = '1'
        self.value = 0  #
        self.sig.report_signal.emit('partDetectNode')
        self.sourceImage = None
        self.tobj = None
        self.rc = None  # 사각형
        self.flag = False
        self.frame_idx = 0
        self.trackMode = False
        self.tracker = objectTracker.objectTracker() 
        self.tracker.setLineNo(self.rno)
        self.lineDetecotor = lineDetector.lineDetector()  
        self.orb = cv2.ORB_create()       
        self.speedCnt = 0
        self.spSum = 0
        self.speedAvg = 0 
        self.rstState = -1
        self.orbMark = False
        self.kp = None
        self.des = None
        self.crop = None
        self.matcher  = cv2.BFMatcher_create()
        self.color = np.random.randint(0,255,(200,3))
        self.lines = None  #추적 선을 그릴 이미지 저장 변수
        self.prevImg = None  # 이전 프레임 저장 변수
        self.prevPt = None
        self.opticalFirst = True
        self.hsv = None
# calcOpticalFlowPyrLK 중지 요건 설정
        self.termcriteria =  (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03) 

    def __del__(self):
        print(".....end thread.")
        
    def addSpeedData(self, sp):
        self.speedCnt += 1
        self.spSum += sp
        self.speedAvg = int(self.spSum/self.speedCnt)

    def setImage(self, src_img):
        self.sourceImage = src_img
        self.flag = True
        self.frame_idx += 1

    def orbf(self, image, h, w) :
        # find the keypoints with ORB
        kp, des = self.orb.detectAndCompute(image,None)
        # compute the descriptors with ORB
        # draw only keypoints location,not size and orientation
        zero = np.zeros((h, w, 3), dtype=np.uint8)
        #img2 = cv2.drawKeypoints(zero,kp,None)            
        img2 = cv2.drawKeypoints(image,kp,None)
        
        return img2

    def setOrbMark(self, img, mr):
        print(mr)
        self.crop = img[mr[1]:mr[1]+mr[3], mr[0]:mr[0]+mr[2]]
        self.kp, self.des = self.orb.detectAndCompute(self.crop,None)   
        print(' kp object = ' + str(len(self.kp)))
        self.orbMark = True   
        

    def findRectOrbMark(self, img):
        dst = img
        k, d = self.orb.detectAndCompute(img,None)
        matches = self.matcher.match(self.des, d)
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches  = matches[:80]
        matCnt = len(good_matches)
        #print('k='+ str(len(k))+ ' matches='+str(len(matches)) +' matCnt='+str(matCnt) )
        if matCnt > 4 :
            pts1 = np.array([self.kp[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2).astype(np.float32)
            pts2 = np.array([k[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2).astype(np.float32)
            H, _ = cv2.findHomography(pts1,pts2, cv2.RANSAC)
            dst = cv2.drawMatches(self.crop,self.kp,img,k,good_matches,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            (h,w) = self.crop.shape[:2]
            corners1 = np.array([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2).astype(np.float32)
            corners2 = cv2.perspectiveTransform(corners1,H)
            corners2 = corners2 + np.float32([w,0])         
            img = cv2.drawKeypoints(img,self.kp,None)
            cv2.polylines(dst,[np.int32(corners2)], True,(0,255,0),2,cv2.LINE_AA)
        else :
            dst = cv2.drawKeypoints(img,k,None)
        return dst

    def opticalFlow(self, img, obj):
        img_draw = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        speed = 0
        # 최초 프레임 경우
        if self.opticalFirst :
            self.prevImg = gray
            self.opticalFirst  = False
            self.hsv = np.zeros_like(img)
            self.hsv[...,1] = 255

        else:            
            # 추적선 그릴 이미지를 프레임 크기에 맞게 생성
            self.lines = np.zeros_like(img)
            # 추적 시작을 위한 코너 검출  ---①
            self.prevPt = cv2.goodFeaturesToTrack(self.prevImg, 200, 0.01, 10)
            nextImg = gray
            # 옵티컬 플로우로 다음 프레임의 코너점  찾기 ---②
            nextPt, status, err = cv2.calcOpticalFlowPyrLK(self.prevImg, nextImg, self.prevPt, None, criteria=self.termcriteria)
            # 대응점이 있는 코너, 움직인 코너 선별 ---③
            prevMv = self.prevPt[status==1]
            nextMv = nextPt[status==1]
            dta = 0
            cnt = 0
            for i,(p, n) in enumerate(zip(prevMv, nextMv)):
                px,py = p.ravel()
                nx,ny = n.ravel()
                
                if obj is not None and obj.state == 't':
                    if obj.isContains([nx,ny]) :
                        # 새로운 코너에 점 그리기
                        cv2.line(self.lines, (px, py), (nx,ny), self.color[i].tolist(), 1)
                        cv2.circle(img_draw, (nx,ny), 5, self.color[i].tolist(), -1)
                        dx = nx-px
                        if self.rno == 1 :
                            if dx < 0 :
                                dta +=  dx
                        else :
                            if dx > 0 :
                                dta += dx

                        cnt += 1
            if dta > 0 or dta < 0:
                if cnt > 2 :
                    speed = dta / cnt

            #result = cv2.bitwise_and(img_draw, img_draw, mask=mask)
            #bgr = cv2.cvtColor(mask,cv2.COLOR_HSV2BGR)
            #img_draw = cv2.add(img_draw, result)
            # 누적된 추적 선을 출력 이미지에 합성 ---⑤
            img_draw = cv2.add(img_draw, self.lines)
            cv2.putText(img_draw,'speed = '+str(speed), (10,500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2,cv2.LINE_AA) 

            # 다음 프레임을 위한 프레임과 코너점 이월
            #self.prevImg = nextImg
            #self.prevPt = nextMv.reshape(-1,1,2)

        return img_draw , speed

    def setObject(self, tobj):
        self.tobj = tobj
        self.trackMode = False
        self.tracker.trackClear()
        #print('nodeSpeedChecker: set target ' + str(self.tobj.rpn))

    def stopTracking(self):
        self.tobj.setState('o') 
        self.trackMode = False
        self.tracker.trackClear()

    def drawResult(self, rstImg, msg, tr):
        color = (10, 235, 30)
        thickness = 2
        #rstImg = cv2.cvtColor(src_img, cv2.COLOR_GRAY2RGB )
# color image translation
        cv2.putText(rstImg, msg, (10,400), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness,cv2.LINE_AA) 
        cv2.putText(rstImg,'['+ str(self.frame_idx) + '] ', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)  
        if self.tobj is not None:
            cv2.putText(rstImg,str( self.tobj.getAngle()), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness,cv2.LINE_AA) 

            pt1, pt2 = self.tobj.getSAreaPts()
            cv2.rectangle(rstImg, pt1, pt2, (255, 255, 255), thickness)
            if tr :
                cv2.rectangle(rstImg, self.tobj.getRect() , (0,255,0), 2)
            else : 
                cv2.rectangle(rstImg, self.rc , (0,255,255), 1)

            cv2.putText(rstImg, str(self.tobj.rpn) + ' '+str(self.tobj.getCenter()[0]), self.tobj.getLT(), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness,
                        cv2.LINE_AA) 
        return rstImg

    # main Thread 
    def run(self):
        self.sig.report_signal.emit('nodeSpeedChecker ON')
        self.working = True

        while self.working :
            self.newTime = time.time()
            reportMsg = 's{'+ str(self.frame_idx) + '} '
            trackingResult = False
            trn = False            
            if self.flag :
                self.value  = 0
                if self.tobj is not None and self.tobj.state =='t':
                    if self.lineDetecotor.isLineDetectModel(self.tobj.getPartID()):
                        try :
                            r, a, c = self.lineDetecotor.checkLine(self.sourceImage, self.tobj.getRect())
                            if c > 0 :
                                self.tobj.setAngle(r, a)                            
                        except Exception as e:
                            print("set angle error : ", e)

                    if self.trackMode :  # 추적 모드 
                        msg, trn, dx, self.rc = self.tracker.tracking(self.sourceImage,self.tobj)                        
                        reportMsg += msg
                        #print('    dx = '+ str(dx))

                        if self.rno == 1 :  # case line 1
                            if dx > 0 :
                                dx = 0 
                                #trn = False
                        else : # line 2
                            if dx < 0 :
                                dx = 0
                                #trn = False

                        if trn :
                            reportMsg += '  tracking sucess '
                            self.value = dx
                            self.addSpeedData(dx)
                            self.rstState  = 1
                            #self.setOrbMark(self.sourceImage,self.rc) 
                            # 일단 추적객체 오알비마킹
                        else :
                            self.trackMode = False
                            if self.rc[0] == 121 :
                                reportMsg += ' out of range '
                            else :                            
                                reportMsg += '  tracking fail '
                                self.tobj = None
                            self.value = 0  # 이전진행속도평균                                
                            self.tracker.trackClear()
                            self.rstState  = -1

                    else : #추적모드가 아닌 경우
                        if self.sourceImage is not None :  #
                             if self.tobj is not None :
                                self.rc = self.tobj.getBox()
                                msg, trn = self.tracker.initialize(self.sourceImage,self.tobj.getBox()) 
                                # orb marking
                                #self.setOrbMark(self.sourceImage,self.tobj.getBox())                           
                                reportMsg += (msg + ' '+str(trn)) 
                                if trn : 
                                    self.trackMode = True
                                    self.rstState  = 2  #  추적설정 상태
                                else :
                                    reportMsg += ' init fail '   
                                    self.rstState  = -2 
                                    self.value = 0 
                        else :
                            reportMsg += ' src imag is None '
                            self.rstState  = 0
                        self.value = 0
                else :
                    reportMsg += ' target is None '
                    self.value = 0 
                    self.rc = [10,10,10,10] 
                    self.rstState  = 0
                   
                if  self.value == 0 :
                    self.value = int(self.speedAvg)                    

                self.drawResult(self.sourceImage,reportMsg,trn) 
                if self.sourceImage is not None :                   
                    self.sig.rstImg_signal.emit(self.sourceImage)
                if self.rno == 1 :  # case line 1
                    if self.value < self.speedAvg*1.5 :
                        self.value = int(self.speedAvg*1.5 )
                else :
                    if self.value > self.speedAvg*1.5 :
                        self.value = int(self.speedAvg*1.5)      
                
                self.sig.speed_signal.emit(self.value, self.rstState)
                reportTime = " : "+ str(time.time() - self.newTime)
                reportMsg = reportMsg    + reportTime + ' send ='+str(self.value) + ' avg='+str(self.speedAvg)
                #print(reportMsg)  
                self.flag = False                     
            time.sleep(0.02)

    def stop(self) :
        pass
