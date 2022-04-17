from tracemalloc import start
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
import time
import datetime
import cv2
from numpy.lib.function_base import msort
from partObject import *
import cModel
import lineDetector
import partClassInfo
from transitions import Machine
import csv


STEP_NO = 48
Detect_LINE = 330
palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

class StepSignal(QObject):
    report_signal = pyqtSignal(str)
    step_signal = pyqtSignal(int, float, str)
    rst_signal = pyqtSignal(np.ndarray)
    clsStep_signal = pyqtSignal(int, int, int)
    colorImg_signal = pyqtSignal(np.ndarray)
    depthImg_signal = pyqtSignal(np.ndarray)
    tObjSig = pyqtSignal(partObject)
    tact_time_signal = pyqtSignal(str)
    print('create step signal')

class nodeStepChecker(QThread):
    def __init__(self, r_no, parent=None):
        super(self.__class__, self).__init__(parent)
        self.working = True
        self.objList = ObjectList ()
        self.nsig = StepSignal()
        self.partID = 'default'
        self.state = 'report'
        self.text = '1'
        self.value = int(STEP_NO)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerEvent)
        print('nodeStepChecker robot no = ' + str(r_no))
        self.sourceImage = None
        self.srcImgOrg = None
        self.flag = False
        self.resultDraw = False
        self.rno = r_no  # default 1호기
        self.xs = 0  # start x position
        self.st = 10  # step weith
        self.rc = STEP_NO # recicle count
        self.ys = 20
        self.ye = 200 
        if self.rno == 1:
            self.margin = 280 # 140
        else:
            self.margin = 200 

        self.yE_line = 500
        self.cThHold = 100  # threshhold value nc
        self.min_area = 1500  # 2**9=512
        self.z_rate = 1.57
        self.arcRate = 0.012
        self.pstate = 48 
        self.lifeTime = 100  # 수명
        self.speedCnt = 0
        self.speedAvg = 0
        self.spSum = 0
        self.speed = -1
        self.prevFrame = None
        self.newTime = None
        self.oldTime = None
        self.obj = None
        self.tobj = None  # 추적 목표물 d객체
        self.fobj = None  # first 목표물 d객체                
        self.trect = None
        self.isTarget = False  # 추적목표물이 존재 하는가?
        self.isTracking = False  # 지금 추적중인가?
        self.drawTrackFlag = False
        self.logfileFlag = False
        self.start_flag = False
        self.tcList = [] 
        self.startBoxLB = (660, 80)
        self.startBoxRT = (820, 400)
        self.countNo = 0
        self.sqIdx = 0  # sequence index 
        self.FPS = 0

        self.startState = 0
        self.readyState = 0
        self.endState = 0

        self.startTime = 0
        self.endTime = 0

        self.runStartX = 0
        self.runEndX = 0
        self.oldTx = -1

        self.tracks = []
        self.speedQueue = []
        self.speedPermit = True # 추적을 쓸것인지
        
        self.detect_working = False
        self.depthImage = None
        self.lineDetecotor = lineDetector.lineDetector()        
        self.pInfo = partClassInfo.partClassInfo()        
        self.oldPartClass = 'old'
        state_of_step = ['detect', 'flow','out', 'act']  #탐지, 추적, 놓침, 대기
        self.cmodel = cModel.cModel()

        self.step_machine = Machine(model=self.cmodel, states=state_of_step, initial='detect')
        self.step_machine.add_transition('detection','out','detect')
        self.step_machine.add_transition('tracking','detect','flow',conditions='detect')
        self.step_machine.add_transition('action','flow','act',conditions='check')
        self.step_machine.add_transition('inspection','act','out')
        self.fileCSV = open('./log/startLine.csv', 'w', encoding='utf-8', newline='')
        self.fcsv = csv.writer(self.fileCSV)
    

    def __del__(self):
        print(".....end thread.")

    def timerEvent(self):
        print('Time out!!!!!!!')

    def setColorImage(self, cv_img):
        # cv_img = cv2.resize(cv_img, dsize=(480, 270), interpolation=cv2.INTER_AREA)
        self.sourceImage = cv_img
        self.srcImgOrg = cv_img.copy()
        self.flag = True
        self.sqIdx+= 1
        self.resultDraw = False
        #print('nstep set image '+ str(self.sqIdx))

    def setDepthImage(self, cv_img):
        self.depthImage = cv_img
        #self.flag = True

    def setTimerInterval(self, inv):
        #print('nodeStepChecker set timer interval' + str(inv))
        self.timer.start(inv)

    def setThreshold(self, th):
        self.cThHold = th

    def setLineNo(self, rno):
        self.rno = rno
        self.detector.detect_set(self.rno)
        self.tracker.setLineNo(self.rno)

    def detectObject(self, image):  # 갹체 탐지 함수
        self.src  = image
        reportMsg = 'detectObject '
        xyxy, rimg, clsname, detect_check = self.detector.detect(image)
        obj =None
        if clsname is not None:
            pCls = self.pInfo.getClass(clsname + '#' + str(self.rno))
            if xyxy is not None:
                obj = partObject.partObject(clsname)
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
                    reportMsg += ' obj set width & height fail'
            else :
                reportMsg += ' xyxy is None'
        else : 
            reportMsg += ' Not detect'     
            pCls = None
            obj = None

        return reportMsg, obj, pCls 



    def compute_color_for_labels(self, label):
        """
        Simple function that adds fixed color depending on the class
        """
        color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
        return tuple(color)

    def addSpeedData(self, sp):
        self.speedCnt += 1
        self.spSum += sp
        self.speedAvg = int(self.spSum/self.speedCnt)

    def checkInRect(self, bl, tr, p):
        if (p[0] > bl[0] and p[0] < tr[0] and p[1] > bl[1] and p[1] < tr[1]):
            return True
        else:
            return False



    # 확인 하는 스텝
    def checkStep(self, ob):
        stepV = -1
        startx = 0

        if self.rno == 1 :
            cp = ob.x
        else :
            cp = ob.x2

        for i in range(self.rc):
            x1 = self.xs + i * self.st + self.margin
            x2 = self.xs + (i + 1) * self.st + self.margin
            if i == 0:
                startx = x1
            if x1 < cp and x2 >= cp:
                stepV = i
                #print('nodeStepChecker: ' + str(cp) + ' stepv = ' + str(stepV) + ' sx=' + str(startx) + ' x1=[' + str(x1) + '] x2= [' + str(x2) + ']')
        if stepV < 0:
            stepV = 0

        if self.rno == 1 :
            rv = STEP_NO - stepV
        else :
            rv = stepV
        return rv

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

    def drawRun(self, img, color):
        if self.runStartX > 0:
            cv2.line(img, (self.runStartX, 50), (self.runStartX, 180), color, 2)
        if self.runEndX > 0:
            cv2.line(img, (self.runEndX, 50), (self.runEndX, 180), color, 2)

    #  스텝상태를 그림으로 그림
    def drawStep(self, src_img, stv):
        color = (255, 135, 0)
        thickness = 1

        for i in range(self.rc):
            # zone = thresh2_img[50:450, xs - (i + 1) * st:xs - i * st]
            x1 = self.xs + i * self.st + self.margin
            x2 = self.xs + (i + 1) * self.st - 1 + self.margin
            pts1 = (x1, 10)
            pts2 = (x2, 20)
            cv2.rectangle(src_img, pts1, pts2, color, thickness)
            if self.rno == 1:
                if i == STEP_NO - self.startState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, (0,255,255), 2)
                elif i == STEP_NO - self.readyState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, color, thickness)
                elif i == STEP_NO - self.endState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, color, thickness)
            else:
                if i == self.startState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, (0,255,255), 2)
                elif i == self.readyState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, color, thickness)
                elif i == self.endState:
                    pts2 = (x1, self.yE_line)
                    cv2.line(src_img, pts1, pts2, color, thickness)

        if self.rno == 1:
            cv2.line(src_img, (Detect_LINE, 20), (Detect_LINE, 250), (255, 255, 255), 1)
        else:
            cv2.line(src_img, (100, 20), (100, self.yE_line), (255, 255, 255), 1)
        cv2.putText(src_img,'['+ str(self.sqIdx) + '] ', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,  cv2.LINE_AA)            
        cv2.putText(src_img, 'speed=' + str(self.speed) + ' FPS='+ str(self.FPS), (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(src_img, 'step=' + str(stv) + ' '+self.state, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(src_img, 'len= ' + str(self.objList.size()), (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)                    


        nobjcolor = (9,0,255)
        tcolor = (0,234,120)
        for obj in self.objList.objlist:
            if obj.isTarget :
                self.drawTargetObj(obj,tcolor)
                if self.rno == 1 :
                    pts1 = (obj.x, 10)
                    pts2 = (obj.x, self.yE_line-50)  
                else :                 
                    pts1 = (obj.x2, 10)
                    pts2 = (obj.x2, self.yE_line-50)   
                cv2.line(src_img, pts1, pts2, nobjcolor, 2)  
                cv2.putText(src_img, 'x=' + str(pts2[0]) , (pts2[0], self.yE_line-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)                 
            elif obj.state == 'm':
                self.drawTargetObj(obj,nobjcolor) 
                if self.rno == 1 :
                    pts1 = (obj.x, 10)
                    pts2 = (obj.x, self.yE_line-50)  
                else :                 
                    pts1 = (obj.x2, 10)
                    pts2 = (obj.x2, self.yE_line-50)    
                cv2.line(src_img, pts1, pts2, nobjcolor, 2)     
                cv2.putText(src_img, 'x=' + str(pts2[0]) , (pts2[0], self.yE_line-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)       
            #else :
            #    self.drawTargetObj(obj,objcolor) 
        if self.tobj is not None:
            pt1, pt2 = self.tobj.getSAreaPts()
            cv2.rectangle(src_img, pt1, pt2, (255, 255, 255), 3)
            cv2.putText(src_img, str(self.tobj.rpn), self.tobj.getLT(), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2,
                        cv2.LINE_AA) 

        if len(self.tracks) > 0:            
            for co in self.tracks:
                if co is not None and self.sourceImage is not None:
                    color = (28,128,200)
                    r  = co.getBRect()                            
                    self.objList.checkSameAreaReplace(co)            
                    label = '{}{:d}'.format("", co.uID)
                    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 2 , 2)[0]
                    cv2.rectangle(self.sourceImage,r,color,2)
                    cv2.rectangle(self.sourceImage,(r[0], r[1]),(r[0]+t_size[0]+3,r[1]+t_size[1]+4), color,-1)
                    cv2.putText(self.sourceImage,label,(r[0],r[1]+t_size[1]+4), cv2.FONT_HERSHEY_PLAIN, 2, [255,255,255], 2)
            self.tracks = []
        
        self.resultDraw = True

    def setObject(self, tobj):
        self.obj = tobj
        self.isTarget = True
        self.flag = True
        self.obj.step = 0
        #print('  +nodeStepChecker: set target '+str(self.obj.rpn))

    def stopTracking(self):
        if self.tobj is not None:
            self.runEndX = self.tobj.getCenter()[0]
            self.drawTrackFlag = False
            #print('nodeStepChecker : stop tracking')
        # pass
    def setStateStart(self, sno):
        self.startState = sno

    def setStateReady(self, dno):
        self.readyState = dno

    def setStateEnd(self, eno):
        self.endState = eno

    def setSpeed(self, s, r):        
        self.speed = int(s)    
        self.flag = True 
        print('  +setSpeed   '+ str(self.speed ))


    def setDT(self, outs):  # set Deep Sort Tracking
        self.tracks = outs
        #if len(self.tracks) < 1: 
        self.moveStep(self.speedAvg)                     
        #print('  +setDT  detect length = '+ str(len(outs) ))


    def drawTargetObj(self, obj, color):
        if obj.rpn == 0 :
            rect  = obj.getBRect()
        else :
            rect = obj.getRect()            
        cv2.rectangle(self.sourceImage, rect, color, 2)
        if obj.hasAngel :
            a, b = np.cos(obj.angle), np.sin(obj.angle)
            x0, y0 = a * obj.rho, b * obj.rho
            scale = 200
            x1 = int(x0 + scale * -b)
            y1 = int(y0 + scale * a)
            x2 = int(x0 - scale * -b)
            y2 = int(y0 - scale * a)
            dy = y2 - y1
            dx = x2 - x1
            mx = int(rect[0])
            my = int(rect[1])
            if dx != 0 and dy != 0:
                slope = (y2 - y1) / (x2 - x1)
                angle = np.rad2deg(np.arctan(slope))
            else:
                angle = 0
            cv2.circle(self.sourceImage, (mx + int(x0), my + int(y0)), 6, (255, 0, 255), 2, cv2.FILLED)
            #print('x1 = '+ str(x1) + '  y1='+str(y1) + ' x2='+str(x2)+ ' y2='+str(y2) + ' mx='+str(rect[0]) + ' my='+str(rect[1]))
            cv2.line(self.sourceImage, (mx + int(x0), my + int(y0)), (mx+x1 , my - y2), (0, 0, 255), 2)
            
            cv2.putText(self.sourceImage, '{0:0.2f}'.format(angle), (mx+3, my+190), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 255), 2, cv2.LINE_AA)        

        if obj.rpn > 0 :
            cv2.putText(self.sourceImage, str(obj.rpn), obj.getLT(), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2,
                        cv2.LINE_AA)            
        
#객체를 가지고 움직이는 작업을 진행함. SP 는 스피드를 의미함.
    def moveStep(self, sp):            
        maxStep = 0
        maxObj= None
        #print('\t moveStep '+str(sp)+' --------------------------')
        if sp > 50 or sp <-50 :
            return maxStep

        for obj in self.objList.objlist:
                      
            if obj.state == 'm': #max step object               
                obj.moveTo(sp)  
                maxStep = obj.getStep()
                maxObj = obj
            elif obj.state == 'f':
                obj.moveTo(sp)      
                st = self.checkStep(obj)
                obj.setStep(st)
                if st > maxStep :
                    maxStep = st
                    maxObj = obj
                    #print('maxStep =  ' +str(maxStep))
            elif obj.state == 'o' :  #target
                obj.moveTo(sp)  
            else :  # t 인경우  안움직여도 됨
                self.oldTx = obj.x

            obj.setStep(self.checkStep(obj))
            if obj.step > self.startState +2 : # 지나간 상태
                obj.state = 'o'
                obj.isTarget = False
                
           
                      

                
        if maxObj is not None and maxObj.state != 'o':  #제일 스텝이 높은 객체 이므로..first OBJECT
            maxObj.state = 'm'    
            self.fobj =  maxObj               
            #print (' * maxobj = '+str(maxObj.rpn) +' 상태 = '+maxObj.state + ' step = '+ str(maxObj.getStep()))            
        return maxStep
        
    def setTargetObj(self, obj):  # d외부에서 호출되는 함수 
        dx = obj.x - self.tobj.x
        #print('\t @@ dx ='+ str(dx))
        self.tobj.setRectA(obj.getRect())
        self.tobj.setStep(self.checkStep(self.tobj))
        #if self.rno == 1 :
        #    self.moveStep(dx)
        #else :
        self.speed  = dx
        self.addSpeedData(dx)
        self.moveStep(self.speed )
        
    def newTargetObj(self, obj):  
        if self.objList.checkLowNew(obj, self.rno) :
            step = self.checkStep(obj)
            if step >= self.startState :
                #print(' obj step = '+ str(step))
                return

            if self.tobj is not None and self.tobj.state != 'o':
                self.tobj.state = 'f'

            obj.reBorn(200)
            self.countNo = self.objList.appear(self.countNo, obj) 
            self.tobj = obj                               
            self.tobj.state = 't'
            self.tobj.step = step
            self.tobj.isTarget = True
            self.tobj.setRecordNo(self.countNo)             
            #print('  @@@ New Target count no = '+ str(self.countNo) + ' step =' + str(step))   
        else :
            # 가장낮은 놈을 찾아서 그걸 매칭 해야 한다. 
            #print('  @@@ New Object is high '+ str(obj.getCenterX()) + ' old='+str(self.tobj.getCenterX()))   
            self.setTargetObj(obj)
        self.nsig.tObjSig.emit(obj)


    def out(self):
        if self.fobj is not None:
            self.fobj.state = 'o'
            if self.objList.countFinal()  < 1 : # 
                self.fobj = None
        
    def startRun(self,s_value):
        if self.startTime == 0:
            self.startTime = time.time()
        else:
            self.endTime = time.time() - self.startTime
            times = str(datetime.timedelta(seconds=self.endTime))
            self.startTime = 0
            if times[5] == "0":
                print("Cycle Time : ",times[6:10],"s",sep='')                  
                #self.nsig.tact_time_signal.emit(self.obj.getPartID() + " Tact Time : " + times[6:10] + "s" ) # self.obj.getPartID()를 한 번씩 가져오지 못함, 프로그램 안정화 이후 사용 
                self.nsig.tact_time_signal.emit("Tact Time : " + times[6:10] + "s" )
            else:
                print("Cycle Time : ",times[5:10],"s",sep='')
                #self.nsig.tact_time_signal.emit(self.obj.getPartID() + " Tact Time : " + times[5:10] + "s" ) # self.obj.getPartID()를 한 번씩 가져오지 못함, 프로그램 안정화 이후 사용 
                self.nsig.tact_time_signal.emit("Tact Time : " + times[5:10] + "s" )

        if self.rno == 1:
            start_line = self.margin + ((self.rc-s_value)*self.st) +5
        else :
            start_line = self.margin + (s_value*self.st) + 5

        self.start_flag = False
        stNo = -1
        if self.sourceImage is not None: # and self.logfileFlag:   
            img_time = datetime.datetime.now().strftime("%H%M%S%f")
            fileName = './log/startShot'+str(self.tobj.rpn )+'_'+img_time+'_.jpg' 
            #cv2.imwrite(fileName, self.sourceImage)  
            self.nsig.depthImg_signal.emit(self.sourceImage)
            #print('>> start log ' +fileName )
         
        if self.fobj is not None:
            if self.rno == 1:
                self.runStartX = self.fobj.x
            else :
                self.runStartX = self.fobj.x2
            stNo = self.objList.findFinalAndChange()
            #print('>>>fobj start line :' +str(start_line) + ' = ' +str(self.runStartX))
            if stNo < 0 :
                stNo = self.fobj.rpn
            self.fcsv.writerow([stNo,self.runStartX,'f'])
            self.fobj.state = 'o'

            
            if self.objList.countFinal()  < 1 : # 
                self.fobj = None
                print ('fobj is None!!!!!!!')

        elif self.tobj is not None :
            stNo = self.tobj.rpn 
            if self.rno == 1:
                self.runStartX = self.tobj.x
            else :
                self.runStartX = self.tobj.x2
            #print('>>>tobj start line :' +str(start_line) + ' = ' +str(self.runStartX))
            self.fcsv.writerow([stNo,self.runStartX,'t'])

            self.tobj.state = 'o'
            self.tobj.isTarget = False

  
        if self.runStartX >= (start_line-10) and self.runStartX <= start_line + 10 :
            self.start_flag = True
        else:
            self.start_flag = False
              
        return stNo, self.runStartX,self.start_flag

    def setReady(self):
        self.value = STEP_NO
        self.oldPartClass = 'default'

    def printTime(self):
        now = datetime.datetime.now()
        #strTemp = now.strftime("%m/%d/%Y, %H:%M:%S.%f")
        strTemp = now.strftime("%H:%M:%S.%f")
        return strTemp

    def run(self):
        print('step checker ON')
        self.working = True
        self.objList.setMax(10)  # 관리가능 한 객체의 갯수
        self.newTime = time.time()
        while self.working:
            if self.flag:
                reportMsg = 't['+ str(self.sqIdx) + '] '
                print('------ speed ='+str(self.speed))
                if self.obj is not None:# 초기영역윈도우를 벗어나지 않았다면. 생하지 않고 벗어났다면 다른 객체로 인식!!!!                    
                    self.drawTargetObj(self.obj,(255,255,255))
                    if self.tobj is not None and self.tobj.state == 't' : # 이미 있는 경우 위치를 바꾸어 준다.
                        diff = self.tobj.diffFromX(self.obj.getCenterX())
                        if self.tobj.checkArea(self.obj): 
                            if diff > self.tobj.harfW or diff < -self.tobj.harfW : #
                                self.state = 'obj miss newTargetObj'
                                self.fobj = self.tobj
                                self.fobj.state = 'f'
                                self.fobj.isTarget = False
                                self.newTargetObj(self.obj)                                  
                                #print('  -new taget obj center = ' + str(self.obj.x ) + ' DIFF =['+str(diff)+ '] speed = '+ str(self.speed) )
                            else :
                                self.setTargetObj(self.obj)
                                #self.nsig.tObjSig.emit(self.obj)
                                self.tobj.setSpeed(diff)
                                #print('  -set taget obj center no = '+str(self.tobj.rpn)) 
                                self.state = 'setTargetObj'
                        else : # t obj가 체크 에리아에 없다면 ,, 새로운 오브젝트가 생겼지만. 기존에 있는 타겟과 겹치지 않는디
                            self.obj.setStep(self.checkStep(self.obj)) 
                            if self.obj.getStep() > 0 : # 체크 스텝을 했는데 0 스텝보타 크다면 타겟을 바꾸어줌
                                if self.objList.checkSameArea(self.obj) :
                                    self.fobj = self.tobj
                                    self.fobj.state = 'f'
                                    self.fobj.isTarget = False                          
                                    self.newTargetObj(self.obj) 
                                    self.state = 'newTargetObj'
                                    #print('  change target = ' + str(self.obj.x ) + ' DIFF =['+str(diff)+ '] speed = '+ str(self.speed) )                                
                            else :   # 영역밖에 오브젝트 임
                                if diff < 20 and diff > -20 :           
                                    self.setTargetObj(self.obj)
                                    #self.nsig.tObjSig.emit(self.obj) 
                                    self.tobj.setSpeed(diff)   
                                    self.state = 'obj move = ' + str(diff)
                                else : 
                                    if self.objList.checkSameAreaReplace(self.obj) : #영역밖의 오브젝트인데 겹침이 있       
                                        self.state = 'big move obj move = ' + str(diff)
                                    else : # 영역밖인데 겹칩이 없다면 새로운 객체로 생성                                 
                                        self.newTargetObj(self.obj) 
                                        self.state = 'new obj ==> f '                              
                                #print(' out object !' +self.state+'  No = '+str(self.tobj.rpn) +' *  check Same Area')
                                self.tobj.setStep(self.checkStep(self.tobj))      
# 추적하는 물체가 없는 경우 
                    else :                         
                        if self.objList.checkSameArea(self.obj) :                                                                    
                            self.newTargetObj(self.obj)      #객체등록  NEW target
                            self.state = 'obj regist'    
                        else :
                            self.state = 'old target'                                                                                     
                    #print('\t + object detect: '+self.printTime())
                    self.nsig.report_signal.emit('object detect: ' +  self.obj.getPartID() )
# 탐지된 물체가 없는 경우 object is None
                else :
                    if self.tobj is not None and self.tobj.state == 't' :          
                        self.state = 'tobj is tracking'  
                    else :      
                        self.state = 'None'  
                        self.fobj = None
 

# 이동시킨 최종상태를 스텝을 리포트 함.
                if self.fobj is not None:                 
                    self.value = self.fobj.getStep()
                    self.nsig.step_signal.emit(self.value ,self.speed, self.tobj.getPartID())       
                elif self.tobj is not None and self.tobj.state == 't':                    
                    self.value =   self.tobj.getStep()
                    self.nsig.step_signal.emit(self.value ,self.speed, self.tobj.getPartID())   

# 객체리스트를 정리하고 화면에 그림                
                reportMsg += self.state+ " step="+ str(self.value)
                self.objList.checkLife()
                self.objList.checkMax()  # obj 수량이 많은 경우 하나를 줄임
                self.objList.update()  # 객체 상태를 정리 
                if self.resultDraw :
                    self.sourceImage = self.srcImgOrg.copy()
                self.drawStep(self.sourceImage, self.value)  # 화면엔 step을 표시 함.

                deltaT = time.time() - self.newTime 
                self.newTime = time.time()
                self.FPS = int(1/ deltaT)
                reportTime = " : "+ str(deltaT)
                reportMsg = reportMsg + reportTime
                print(reportMsg)
#  화면  데이터 전송           
                if self.sourceImage is not None:    
                    self.nsig.colorImg_signal.emit(self.sourceImage)
                self.obj = None
                self.flag = False

            time.sleep(0.01)
            

    def stop(self):
        self.working = False
        self.frame_idx = 0
        self.fileCSV.close()

    def resume(self):
        self.working = True
