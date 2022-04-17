import os
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
import time
import sys
import cv2
import os
import struct
import datetime
from partObject import partObject
import detect

STEP_NO = 0
Detect_LINE = 200

class StepSignal(QObject):
    report_signal = pyqtSignal(str)
    step_signal = pyqtSignal(int, float,str)
    rst_signal = pyqtSignal(np.ndarray)
    colorImg_signal = pyqtSignal(np.ndarray)
    depthImg_signal = pyqtSignal(np.ndarray)
    print('create step signal')


class nodeStepChecker(QThread):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.working = True
        self.nsig = StepSignal()
        self.partID = 'default'
        self.state = 'report'
        self.text = '1'
        self.value = int(STEP_NO)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        print('nodeStepChecker')
        self.sourceImage = None
        self.flag = False
        self.xs = 0  # start x position
        self.st = 10  # step weith
        self.rc = 25  # recicle count
        self.ys = 20
        self.ye = 80
        self.margin = 130
        self.cThHold = 100  # threshhold value nc
        self.min_area = 1500  # 2**9=512
        self.z_rate = 1.57
        self.arcRate = 0.012
        self.pstate = 22
        self.speedCnt = 0
        self.speedAvg = 0
        self.speed = 0
        self.prevFrame = None
        self.newTime = None
        self.oldTime = None
        self.tobj = None  # 추적 목표물 객체
        self.trect = None
        self.isTarget = False  # 추적목표물이 존재 하는가?
        self.isTracking = False  # 지금 추적중인가?
        self.drawTrackFlag = False
        self.tcList = []
        self.startBoxLB = (90, 80)
        self.startBoxRT = (250, 400)
        self.countNo = 0

        self.runStartX = 0
        self.runEndX = 0
        self.mtracker = None

        # detect관련
        self.detector = detect.Detector()
        self.detector.detect_set()
        self.detect_working = True

    def __del__(self):
        print(".....end thread.")

    def timerEvent(self):
        print('Time out!!!!!!!')

    def setImage(self, src_img, d_img):
        self.sourceImage = src_img
        self.depthImage = d_img
        self.flag = True

    def setColorImage(self, cv_img):
        cv_img = cv2.resize(cv_img, dsize=(480, 270), interpolation=cv2.INTER_AREA)
        self.sourceImage = cv_img
        

    def setDepthImage(self, cv_img):
        cv_img = cv2.resize(cv_img, dsize=(480, 270), interpolation=cv2.INTER_AREA)
        # cv_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2BGR)
        self.depthImage = cv_img
        self.flag = True

    def setTimerInterval(self, inv):
        print('nodeStepChecker set timer interval' + str(inv))
        self.timer.start(inv)

    def setThreshold(self, th):
        self.cThHold = th

    def checkInRect(self, bl, tr, p):
        if (p[0] > bl[0] and p[0] < tr[0] and p[1] > bl[1] and p[1] < tr[1]):
            return True
        else:
            return False

    def detectBoudingBox(self, det_img, out_img):
        contours, hierarchy = cv2.findContours(det_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        idx = 0
        color = (128, 255, 100)
        thickness = 1
        blobList = []
        centerList = []
        for cnt in contours:
            idx += 1
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 30 and h > 100 and h < 400 and x > 100:
                pts1 = (x, y)
                pts2 = (x + w, y + h)
                cv2.rectangle(out_img, pts1, pts2, color, thickness)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                blobList.append(box)
                gateCenter = (int(rect[0][0]), int(rect[0][1]))
                centerList.append(gateCenter)
                cv2.drawContours(out_img, [box], 0, (0, 190, 190), 1)
                cv2.circle(out_img, gateCenter, 6, (0, 155, 155), 1)
        return blobList, centerList


    # 확인 하는 스텝
    def checkStep(self, cp):
        stepV = -1
        startx = 0
        for i in range(self.rc):
            x1 = self.xs + i * self.st + self.margin
            x2 = self.xs + (i + 1) * self.st + self.margin
            if i == 0:
                startx = x1
            if x1 < cp[0] and x2 >= cp[0]:
                stepV = i
        if stepV > -1:
            print('nodeStepChecker: ' + str(cp) + ' stepv = ' + str(stepV) + ' sx=' + str(startx) + ' x1=[' + str(
                x1) + '] x2= [' + str(x2) + ']')
        return stepV

    def drawTracking(self, img, cv, color):
        # for c in cv :
        #    cv2.line(img,self.tobj.getCenter(),(c[0],c[1]),color,1)
        flagFirst = True
        for tc in self.tcList:
            if flagFirst:
                oldC = tc
                flagFirst = False
            else:
                cv2.line(img, oldC, tc, (0, 255, 255), 1)
                cv2.circle(img, tc, 4, color, 1)
                oldC = tc

    def drawTarget(self, img, color):
        trect = self.tobj.getRect()
        if trect is not None:
            pts1 = (trect[0], trect[1])
            pts2 = (trect[0] + trect[2], trect[1] + trect[3])
            cv2.rectangle(img, pts1, pts2, color, 2)

        if self.tobj.hasShape:
            cnt = np.array([self.tobj.getBoxPoints()], np.int32)
            cv2.polylines(img, [cnt], 0, color, 1)
            cp = self.tobj.getCenter()
            cv2.circle(img, cp, 6, color, 2)
            cv2.putText(img, str(self.countNo), (cp[0], 260), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    def drawRun(self, img, color):
        if self.runStartX > 0:
            cv2.line(img, (self.runStartX, 50), (self.runStartX, 180), color, 2)
        if self.runEndX > 0:
            cv2.line(img, (self.runEndX, 50), (self.runEndX, 180), color, 2)

    # 고리를 인식해서 스텝을 그리고
    def drawStep(self, src_img):
        gray = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)
        thresh2_img = cv2.GaussianBlur(gray, (3, 3), 0)
        ov, oc = self.detectBoudingBox(thresh2_img, src_img)
        # check roi countNonZero
        zoneV = np.arange(self.rc)
        for i in range(self.rc):
            # zone = thresh2_img[50:450, xs - (i + 1) * st:xs - i * st]
            x1 = self.xs + i * self.st + self.margin
            x2 = self.xs + (i + 1) * self.st - 1 + self.margin
            pts1 = (x1, 10)
            pts2 = (x2, 40)
            zone = thresh2_img[10:40, x1:x2]
            zzV = cv2.countNonZero(zone)
            zoneV[i] = zzV
            if zzV > self.cThHold:
                color = (0, 255, 0)
                thickness = 1
                cv2.rectangle(src_img, pts1, pts2, color, thickness)
            else:
                color = (0, 255, 255)
                thickness = 1
                cv2.rectangle(src_img, pts1, pts2, color, thickness)
        cv2.line(src_img, (Detect_LINE,20), (Detect_LINE,250), (255, 255, 255), 2)
        cv2.putText(src_img, 'step=' + str(self.value), (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        return zoneV

    def setTarget(self, tobj):
        self.tobj = tobj
        self.isTarget = True
        print('nodeStepChecker: set target')

    def stopTracking(self):
        self.runEndX = self.tobj.getCenter()[0]
        self.drawTrackFlag = False
        print('nodeStepChecker : stop tracking')
        # pass

    def startRun(self):
        self.runStartX = self.tobj.getCenter()[0]
        self.drawTrackFlag = True
        self.tcList.clear()

    def setReady(self):
        self.value = STEP_NO
        self.isTarget = False
        self.isTracking = False
        self.countNo = self.countNo + 1
        print('nodeStepChecker: setReady count = ' + str(self.countNo))

    # main Thread
    def run(self):
        print('step checker ON')
        self.working = True
        while self.working:
            if self.flag:
                reportMsg = 'start'
                stepV = 0
                # speed check
                if self.isTarget is False:  # 추적 상태가 아니라면
                    xyxy, rimg, clsname, detect_check = self.detector.detect(self.sourceImage)
                    if clsname is not None :
                        self.partID = clsname
                    if xyxy is not None:
                        if self.coming_check(xyxy):
                            self.isTarget = True
                            self.tobj = partObject(clsname)
                            width = int(abs(xyxy[2] - xyxy[0]))
                            height = int(abs(xyxy[3] - xyxy[1]))
                            x_value = int(xyxy[0])
                            y_value = int(xyxy[1])
                            print('width= ' + str(width) + ' height= ' + str(height) + ' x_value=[' + str(
                                x_value) + '] y_value= [' + str(y_value) + ']')
                            self.tobj.setRect(x_value, y_value, width, height)
                            box = (x_value, y_value, width, height)
                            self.mtracker = cv2.MultiTracker_create()  # 추적기 생성
                            self.mtracker.add(cv2.TrackerBoosting_create(), self.sourceImage, box)
                            self.drawTarget(self.depthImage, (255, 0, 255))
                            self.isTracking = True
                            self.tobj.setState('present')
                            self.value = STEP_NO  # start position
                            reportMsg = ' target build !  !!!'
                    else:
                        # 시간을 끌기 위한 함수가 필요함  탐지된 객체가 없으므로.
                        pass

                else:
                    if self.isTracking:  # 탐지를 해서 추적할 목표물이 있다면
                        success, bboxes = self.mtracker.update(self.sourceImage)
                        if success:
                            for i, box in enumerate(bboxes):
                                p1 = (int(box[0]), int(box[1]))
                                p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
                                cv2.rectangle(self.sourceImage, p1, p2, (5, 10, 222), 5)
                                cx = int(box[0] + box[2] / 2)
                                cy = int(box[1] + box[3] / 2)
                                self.tobj.moveCenter((cx, cy))
                                self.speed = self.tobj.getSpeed()
                                if i == 0:
                                    self.value = self.checkStep((cx, cy))
                                    #break
                            reportMsg = ' traking !'
                        else:
                            reportMsg = ' traking FAIL'
                            self.isTracking = False
                            self.isTarget = False
                    else:
                        reportMsg = ' I has no traking target '
                        self.isTarget = False

                stepV =  self.value  # 역방향을 순방향 번호로 바꿈

                self.drawStep(self.depthImage)  # 화면엔 step을 표시 함.

                # reportTime = " : "+ str(time.time() - self.newTime)
                self.nsig.report_signal.emit('Step: ' + str(stepV) + reportMsg)
                self.nsig.step_signal.emit(stepV, self.speed, self.partID)
                self.nsig.rst_signal.emit(self.depthImage)
                self.nsig.colorImg_signal.emit(self.sourceImage)
                self.nsig.depthImg_signal.emit(self.depthImage)
                self.flag = False

    def coming_check(self, x):
        center_x = (int(x[2]) + int(x[0])) / 2
        print("센터x 좌표값 : ", center_x)
        if center_x <= Detect_LINE:  # 1,2호기에 따라 달라지므로 변수화 해야함.
            check_flag = True
        else:
            check_flag = False
        return check_flag

    def stop(self):
        self.working = False
        self.frame_idx = 0

    def resume(self):
        self.working = True