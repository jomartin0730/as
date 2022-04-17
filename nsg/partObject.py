import copy
import math
from re import S
import numpy as np
import time


# G Object (generic object)
class GObject:
    def __init__(self, name):
        self.name = name
        self.className = 'object'
        self.rpn = 0
        self.age = 0
        self.born = time.time()
        self.rtime = time.time()
        self.r1time = time.time()
        self.partId = name
        self.cur_pos_x = 0.0
        self.cur_pos_y = 0.0
        self.cur_pos_z = 0.0
        self.rho = 0.0

    def setPartID(self, partId):
        self.partId = partId

    def setRecordNo(self, no):
        self.rpn = no

    def setCurPosition(self, x, y, z):
        self.cur_pos_x = x
        self.cur_pos_y = y
        self.cur_pos_z = z

    def set2Dpos(self, x4):
        self.twoD_x1 = x4[0]
        self.twoD_y1 = x4[1]
        self.twoD_x2 = x4[2]
        self.twoD_y2 = x4[3]
        self.twoD_w = x4[2] - x4[0]  # width
        self.twoD_h = x4[3] - x4[1]  # height
        self.twoD_cx = x4[0] + (self.twoD_w) / 2  # center x
        self.twoD_cy = x4[1] + (self.twoD_h) / 2  # center x


# part Object
class partObject(GObject):
    def __init__(self, name):
        super().__init__(name)
        self.partname = name
        self.partId = name
        self.uID = -1
        self.pClass = None
        self.state = 'None'
        self.step = 0
        self.speed = 0.0
        self.percent = 0.0
        self.hasCenter = False
        self.hasShape = False
        self.has3D = False
        self.hasAngel = False
        self.isMoveFW = False
        self.isTarget = False
        self.cx = 0
        self.cy = 0
        self.dx = 0
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.harfW = 0
        self.x2 = 0
        self.y2 = 0

        self.ex = 0
        self.ey = 0
        self.ew = 0
        self.eh = 0

        self.oldX = 0

        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.p4 = 0
        self.angle = 0
        self.tWind = None
        self.dtime = None

    def setPartClass(self, pInfo):
        self.pClass = pInfo
        if self.pClass is None:
            pass
            print('setPartClass : pClass is is not set')

    def setBoundingRec(self, p1, p2, p3, p4):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.hasShape = False

    def setBoundingBox(self, box):
        idx = 0
        for p in box:
            # print(f'{idx} = '+str(p))
            if idx == 0:
                self.p1 = p
            elif idx == 1:
                self.p2 = p
            elif idx == 2:
                self.p3 = p
            elif idx == 3:
                self.p4 = p
            idx = idx + 1
        self.clip_pos = np.array(
            [self.p1[0], self.p1[1], self.p2[0], self.p2[1]]).astype(np.int64)
        self.hasShape = False

    def setCentre(self, c):
        self.cx = int(c[0])
        self.cy = int(c[1])
        # self.hasCenter = True

    def isStartArea(self):
        return self.pClass.isStartArea(self.getCenter())

    def setBox(self, box):  # set bounding box
        x1, y1, x2, y2 = [int(i) for i in box]
        width = int(x2 - x1)
        height = int(abs(y2 - y1))
        cx = int(x1 + width / 2)
        cy = int(y1 + height / 2)
        self.setRect(x1, y1, width, height)
        self.ex = x1
        self.ey = y1
        self.ew = width
        self.eh = height

    def setXYXY(self, xyxy):  # 처음 불리는 함수이기 때문에 영역체크를 여기서함.
        width = int(abs(xyxy[2] - xyxy[0]))
        height = int(abs(xyxy[3] - xyxy[1]))
        x_value = int(xyxy[0])
        y_value = int(xyxy[1])
        cx = int(x_value + width / 2)
        cy = int(y_value + height / 2)
        if self.pClass is not None:
            if self.pClass.isStartArea((cx, cy)):
                self.tWind = copy.deepcopy(self.pClass.getTW())
                self.setRect(x_value, y_value, width, height)
                self.ex = x_value
                self.ey = y_value
                self.ew = width
                self.eh = height
                print('cx=' + str(cx) + ' cy=' + str(cy) + ' w=' +
                      str(width) + ' h=' + str(height) + self.pClass.toStr())
                return True
            else:
                print('out of area x=' + str(cx) + ' y=' +
                      str(cy) + ' area=' + self.pClass.toStr())
                return False
        else:
            print('setXYXY : pClass is None')
            return False

    def setTWinImage(self, simg):
        r = self.tWind
        #print('setTWinImage : '+str(r))
        return simg[r[1]:r[3], r[0]:r[2]].copy()

    def getBoxInTwin(self):
        r = self.tWind
        if self.x - r[0] < 1:
            xx = 1
        else:
            xx = self.x - r[0]
        if self.y - r[1] < 1:
            yy = 3
        else:
            yy = self.y - r[1]
        #print (' getBoxInTwin '+ str(xx)+ ' '+ str(yy) + ' '+str(self.width) + ' '+str(self.height))
        return (xx, yy, self.width, self.height)

    def setBoxInTwin(self, rc):  # 타켓윈도우내부의 좌표로 변환
        r = self.tWind
        # print('setBoxInTwin : '+str(r))
        return [rc[0] + r[0], rc[1] + r[1], rc[2], rc[3]]

    def getSAreaPts(self):  # 초기 설정영역의 좌표값
        if self.pClass is not None:
            r = self.pClass.getSA()
            return (r[0], r[1]), (r[2], r[3])
        else:
            return (250, 160), (280, 170)

    def getTWinPts(self):  # 타켓윈도 좌표값
        if self.tWind is not None:
            r = self.tWind
            return (r[0], r[1]), (r[2], r[3])
        else:
            return (240, 150), (270, 180)

    def moveTWin(self, dx):
        self.tWind[0] = self.tWind[0] - dx
        self.tWind[2] = self.tWind[2] - dx

    def moveCenter(self, c):
        self.cx = int(c[0])
        self.cy = int(c[1])

        self.x = int(c[0] - (self.width/2))
        self.y = int(c[1] - (self.height/2))
        dx = int(self.cx - c[0])
        dy = int(self.cy - c[1])
        self.p1[0] = self.p1[0] - dx
        self.p1[1] = self.p1[1] - dy
        self.p2[0] = self.p2[0] - dx
        self.p2[1] = self.p2[1] - dy
        self.p3[0] = self.p3[0] - dx
        self.p3[1] = self.p3[1] - dy
        self.p4[0] = self.p4[0] - dx
        self.p4[1] = self.p4[1] - dy

    def setExp(self, exp):
        self.oldX = self.x
        self.ex = exp
        self.setRect(exp, self.y, self.width, self.height)
        self.isMoveFW = True

    def moveToExp(self, speed):
        self.oldX = self.x
        self.setRect(self.ex - speed, self.ey, self.ew, self.eh)

    def getSpeed(self):
        if self.isMoveFW:
            return 1
        else:
            return 0

    def isMove(self):
        if self.oldX == self.x:
            return False
        else:
            return True

    def setCenter(self, x, y):
        self.cx = int(x)
        self.cy = int(y)
        # self.hasCenter = True

    def set3Info(self, name, st, sp):
        self.partname = name
        self.state = st
        self.speed = sp

    def setStep(self, st):
        self.step = st

    def setState(self, st):
        self.state = st

    def setSpeed(self, sp):
        self.speed = sp

    def setPartName(self, name):
        self.partname = name

    def setPercent(self, p):
        self.percent = p

    def getStep(self):
        return self.step

    def getPartID(self):
        return self.partname

    def getLT(self):
        return (int(self.x + (self.width / 2)), int(self.y + (self.height / 2)))

    def getCenter(self):
        return (self.cx, self.cy)

    def getCenterX(self):
        return self.cx

    def getBoxPoints(self):
        return [self.p1, self.p2, self.p3, self.p4]

    def getBox(self):
        return (self.x, self.y, self.width, self.height)

    def getWH(self):
        return str(self.width) + ' ' + str(self.height)

    def getRectPoints(self):
        return [self.p1[0], self.p1[1], self.p3[0], self.p3[1]]

    def setRectA(self, r):
        self.setRect(r[0], r[1], r[2], r[3])

    def setRect(self, x, y, w, h):
        self.dx = self.x - x
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.harfW = int(w / 2 - 2)
        self.x2 = x+w
        self.y2 = y+h
        self.cx = int(x + self.harfW)
        self.cy = int(y + y / 2)
        self.p1 = [x, y]
        self.p2 = [x + w, y]
        self.p3 = [x + w, y + h]
        self.p4 = [x, y + h]
        # self.hasCenter = True

    def move(self, x, y, w, h):
        self.oldX = self.x
        dx = self.x - x
        dy = self.y - y
        print(' dx = ' + str(dx))
        self.setRect(x, y, w, h)
        if dx < self.speed:
            return False
        else:
            return True

    def moveTo(self, speed):
        self.oldX = self.x
        self.setRect(self.x + speed, self.y, self.width, self.height)

    def moveToCheck(self, speed):
        self.oldX = self.x
        if self.isMoveFW:
            self.isMoveFW = False
        else:
            self.setRect(self.x + speed, self.y, self.width, self.height)

    def moveSelf(self, speed, rc):
        dx = abs(self.x - rc[0])
        if speed > dx:
            self.moveTo(speed)
        else:
            self.move(rc[0], rc[1], rc[2], rc[3])
        #print('dx = ' + str(dx) + '  speed=' + str(speed))

    def getDx(self):
        return self.dx

    def getRect(self):
        return [self.x, self.y, self.width, self.height]

    def getBRect(self):
        return [self.x - 2, self.y - 2, self.width + 4, self.height + 4]

    def checkTimeDistance(self, curX):
        d = self.cx - curX
        return d

    def distanceFrom(self, cp):
        a = self.cx - cp[0]
        b = self.cy - cp[1]
        return math.sqrt((a * a) + (b * b))

    def diffFromX(self, cp):
        return int(self.cx - cp)

    def isInside(self, cp):
        if self.x < cp and cp < self.x+self.width:
            return True
        else:
            return False

    def isContains(self, pt):
        logic = self.x < pt[0] < self.x + \
            self.width and self.y < pt[1] < self.y+self.height
        return logic

    def isLeft(self, xx):
        if self.cx >= xx:
            return True
        else:
            return False

    def setStep(self, st):
        self.step = st

    def getStep(self):
        return self.step

    def roll(self):
        self.r1time = self.rtime
        self.rtime = time.time()

        self.age = self.age + 1

    def reBorn(self, lifeTime):
        self.born = time.time()
        self.age = 0
        self.state = 'reborn'
        self.lifetime = lifeTime

    def getAgeStr(self):
        t = time.time() - self.born
        return str(self.age) + ': {0:0.2f}'.format(t)

    def getDiffRoll(self):
        t = time.time() - self.r1time
        return str(self.age) + ': {0:0.2f}'.format(t)

    def getAgeTime(self):
        return time.time() - self.born

    def getAge(self):
        return self.age

    def isTimeToDie(self):
        if self.age > self.lifetime:
            return True
        else:
            return False

    def setAngle(self, rho, ang):
        self.rho = rho
        self.angle = ang
        self.hasAngel = True

    def itHasAngel(self):
        return self.hasAngel

    def getAngle(self):
        return self.angle

    def checkIntersect(self):
        width = self.calculateIntersection(
            self.tWind[0], self.tWind[2], self.x, self.x + self.width)
        height = self.calculateIntersection(
            self.tWind[1], self.tWind[3], self.y, self.y + self.height)
        area = width * height
        AREA = float(self.width * self.height)
        percent = area / AREA
        # print('percent = ' + str(percent))
        if percent < 1:
            return False
        else:
            return True

    def calculateIntersection(self, a0, a1, b0, b1):
        if a0 >= b0 and a1 <= b1:  # Contained
            intersection = a1 - a0
        elif a0 < b0 and a1 > b1:  # Contains
            intersection = b1 - b0
        elif a0 < b0 and a1 > b0:  # Intersects right
            intersection = a1 - b0
        elif a1 > b1 and a0 < b1:  # Intersects left
            intersection = b1 - a0
        else:  # No intersection (either side)
            intersection = 0
        return intersection

    def checkArea(self, obj):
        xx = self.x - obj.x
        #print('xx = '+str(xx)+'  fw='+str(self.harfW))
        if xx > -self.harfW and xx < self.harfW:  # 거의 같은 위치에 있다.
            return True
        else:
            return False

    def checkDist(self, obj):
        xx = self.x - obj.x
        #print('xx = '+str(xx)+'  fw='+str(self.harfW))
        if xx > -5 and xx < 5:  # 거의 같은 위치에 있다.
            return True
        else:
            return False

    def getInfoStr(self):
        return self.name + ' st =[' + self.state + '] sp =[' + str(self.speed) + '] age = [' + str(
            self.age) + '] x=' + str(self.x) + ' x2 =' + str(self.x2) + ' step=' + str(self.step) + ' #' + str(
            self.rpn)


# 객체를 보관관리하는 객체 저장소
class ObjectList:
    def __init__(self):
        self.maxNo = 5
        self.objlist = []

    def setMax(self, max):
        self.maxNo = max

    def update(self):  # 시간이 증가했음을 알려주는 함수
        for obj in self.objlist:
            obj.roll()

    def appear(self, key, obj):
        self.objlist.append(obj)
        return key + 1

    def checkLife(self):

        for obj in self.objlist:
            # print(obj.getInfoStr())
            if obj.isTimeToDie():
                print('remove Time to Die =' + str(obj.rpn))
                self.objlist.remove(obj)
            elif obj.x > 900:
                self.objlist.remove(obj)
            elif obj.x < 0:
                self.objlist.remove(obj)
        return len(self.objlist)

    def checkMax(self):
        if len(self.objlist) > self.maxNo:
            obj = self.objlist.pop(0)
            # print('obj list size = '+str(len(self.objlist)))

    def findTarget(self):
        for obj in self.objlist:
            if obj.isStartArea():
                return obj
        return None

    def findFinalAndChange(self):
        for obj in self.objlist:
            if obj.state == 'm':
                obj.state = 'o'
                return obj.rpn
        return -1

    def checkLowNew(self, onj, rno):
        if rno == 1:
            for obj in self.objlist:
                if obj.x > onj.x:
                    #print(' ????? '+ str(obj.x) + ' : '+str(onj.x))
                    return False
        else:
            for obj in self.objlist:
                if obj.x < onj.x:
                    return False

        return True

    def countFinal(self):
        cnt = 0
        for obj in self.objlist:
            if obj.state == 'f':
                cnt = + 1
        return cnt

    def checkSameArea(self, obj):
        for oo in self.objlist:
            if obj.checkArea(oo):
                return False
        return True

    def checkSameAreaReplace(self, obj):
        for oo in self.objlist:
            if obj.checkArea(oo):
                oo.setExp(obj.x)
                #print('*update position* oo'+str(oo.harfW) +' '+oo.getInfoStr())
                #print('*update position* obj'+str(obj.harfW) +' '+obj.getInfoStr())
                return True
        #print('checkSame Area replace FALSE')
        return False

    def disappear(self, key):
        self.objlist.remove(key)
    
    def size(self):
        return len(self.objlist)


class Motion:
    # 1.제품코드 2.제품상태 3.현재state 4.start state 5.endstate 6.모션속도 7.연속도장횟수
    def __init__(self):
        # self.partID = "A01-1P-0242"
        self.partID = "default"
        self.p_value = ""
        self.stepV = 0
        self.start_state = 5
        self.end_state = 7
        self.speedV = 7.0
        self.motion_repeat = 0
        self.motionMode = 0
        self.old_stepV = -1

    def setPartID(self, pid):
        self.partID = pid

    def setMotionParam(self, ss, es, sv, mr):
        self.start_state = ss
        self.end_state = es
        self.speedV = sv
        self.motion_repeat = mr

    def setMotionMode(self, mode):
        self.motionMode = mode

    def setStep(self, stepv):
        self.stepV = stepv

    def setstartState(self, start_state):
        self.start_state = start_state

    def setEndState(self, end_state):
        self.end_state = end_state

    def ready(self):
        self.p_value = "R"

    def start(self):
        # self.p_value = "start"
        self.p_value = "P"

    def stop(self):
        self.p_value = 'stop'
        # self.p_value = 'S'

    def getWord(self):
        # if self.p_value != "" :
        # if self.stepV != self.old_stepV :
        str_array = self.partID + ":"
        str_array += str(self.p_value) + ":"
        str_array += str(self.stepV) + ":"
        str_array += str(self.start_state) + ":"
        str_array += str(self.end_state) + ":"
        str_array += str(self.speedV) + ":"
        str_array += str(self.motion_repeat)

        self.old_stepV = self.stepV
        return str_array
        # else :
        # pass
