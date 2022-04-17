# mind processor
# state machine 을 가지고 생각을 하는 장치
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QImage
import time
import sys
import os
import struct
import datetime
import math
from transitions import Machine
from partObject import partObject, ObjectList, Motion


class TModel(object):
    def __init__(self):
        self.sv = 0  # state variable of the model
        self.conditions = {  # each state
            'out': 0,
            'ready': 7,
            'start': 9,
            'end': 15,
        }

    def poll(self):
        if self.sv >= self.conditions[self.state]:
            self.next_state()  # go to next state
            # print('--next_state-')
        else:
            # print('---')
            getattr(self, 'on_%s' % self.state)()

    def info_print(self):
        print(self.conditions)

    def set_s_con(self, step):
        self.conditions['start'] = step

    def set_e_con(self, step):
        self.conditions['end'] = step

    def set_r_con(self, step):
        self.conditions['ready'] = step

    def set_zValue(self, zV):
        self.sv = zV

    def get_s_con(self):
        return self.conditions['start']

    def get_e_con(self):
        return self.conditions['end']

    def get_r_con(self):
        return self.conditions['ready']

    def on_start(self):
        pass

    def on_end(self):
        pass

    def on_start(self):
        pass

    def on_end(self):
        pass

    def on_ready(self):
        pass

    def on_out(self):
        pass


class PModel(object):
    def __init__(self):
        self.partId = 'unknown'
        self.partId_before = 'unknown'

    def set_PartID(self, pid):
        self.partId = pid

    def is_same(self):
        if self.partId_before == self.partId:
            self.partId_before = self.partId
            return True
        else:
            self.partId_before = self.partId
            return False

    def is_NotSame(self, partID):
        if self.partId_before == partID:
            return False
        else:
            self.partId_before = partID
            return True

    def on_exit(self):
        print('callback on exit!!!')

    def check(self):
        pass
        # print ('check')


class mindProcessor(object):
    def __init__(self):
        self.endOfLife = True
        self.processV = 0
        self.speedV = 0
        self.partID = None

        self.curObjList = ObjectList()  # 현재 진행중인 객체를 기록함. (품종/순번)
        self.rpn = 0  # record part number

        self.state_value = "W"  # W : 대기 , P : 진해중, S : 시작, F : 끝
        self.stateV = "제품 대기중"
        self.stepV = -1
        # self.steteStartFlag = True
        self.steteStartFlag = False
        # self.steteReadyFlag = True
        self.steteReadyFlag = False

        self.tmodel = TModel()
        self.pmodel = PModel()
        self.motion = Motion()  # action
        # init transitions model
        list_of_states = ['out', 'ready', 'start', 'end']
        state_of_partid = ['new', 'existing', 'unknown']  # 신품종, 기존품종, 모름

        self.tracking_machine = Machine(model=self.tmodel, states=list_of_states, initial='out',
                                        ordered_transitions=True)

        self.partId_machine = Machine(model=self.pmodel, states=state_of_partid, initial='unknown')
        self.partId_machine.add_transition('check', 'unknown', 'new', conditions='is_same')
        self.partId_machine.add_transition('check', 'new', 'existing', conditions='is_same')
        self.partId_machine.add_transition('check', 'existing', 'existing', conditions='is_same')
        self.partId_machine.add_transition('check', 'existing', 'new', conditions='is_same')
        self.partId_machine.add_transition('checkSame', 'new', 'new', conditions='is_same')
        print('mind processor init*')

    def setStepV(self, svalue, speed):
        self.stepV = svalue
        self.speedV = speed
        self.tmodel.set_zValue(svalue)  # test  조건에 따라서 다음 스테이지로 올라가는 코드
        self.motion.setStep(svalue)
        #print('MIND PROCESSOR:setStep '+str(self.stepV) + ' speed ='+str(self.speedV))
    def setSpeedV(self, speed):
        self.speedV = speed

    def setConveySpeedV(self, speed):
        self.motion.speedV = speed

    def setPardID(self, pID):
        self.pmodel.set_PartID(pID)
        # self.pmodel.check()  # process에서도 체크 함
        self.partID = pID
        nobj = partObject(pID)  # 새로운 객체를 품종으로 생성
        nobj.setRecordNo(self.rpn)
        self.rpn = self.rpn + 1
        self.curObjList.appear(self.rpn, nobj)
        self.motion.setPartID(pID)
        # print('set part id !!!!')
        return nobj

    def setPartObject(self, obj):
        self.rpn = self.rpn + 1
        self.setPardID(obj.getPartID())
        self.curObjList.appear(self.rpn, obj)

    def infoState(self):
        print('ready = ' + str(self.tmodel.conditions['ready']))
        print('start = ' + str(self.tmodel.conditions['start']))
        print('end = ' + str(self.tmodel.conditions['end']))

    # 핵심적인 상황처리를 하는 함수

    def process(self):
        # 상태를 체크함
        command = 'n'
        self.pmodel.check()  # 실제 동적으로 check 함수가 만들어 짐. is_same이 operator역활을 해서 판단함.
        self.tmodel.poll()  # 명시적으로 만든 함수
        # print("****** " + str(self.stepV ) + ' = ' + str(self.tmodel.get_s_con()))
        if self.stepV < self.tmodel.get_s_con():  # and self.steteStartFlag:  # start
            # print("###################################### ready ######################################")
            self.tmodel.sv = 0  # 초기화
            command = 'reset'
            self.steteReadyFlag = True
            self.steteStartFlag = True
            self.motion.ready()
        elif self.stepV >= self.tmodel.get_s_con() and self.stepV <= self.tmodel.get_e_con():  # lf.steteReadyFlag:  # end
            self.motion.start()
            command = 'start'
            self.steteStartFlag = False
            #print("start****** " + str(self.stepV) + ' = ' + str(self.tmodel.get_s_con()))
        elif self.stepV > self.tmodel.get_e_con() :
            command = 'out'
            self.steteStartFlag = False
            #print("out****** " + str(self.stepV) + ' = ' + str(self.tmodel.get_e_con()))
        
        start_value = self.tmodel.get_s_con()

        return command, self.motion, start_value