from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QGridLayout, QCheckBox, QInputDialog, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider
from PyQt5.QtGui import QPixmap, QImage, QColor
# from PyQt5.QtCore import QDir, Qt, QRect, QSize
import socket
import time
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
from numpy import ndarray
import nodeL515 as dSensor
#import nodeDTest as dSensor
import nodePartDetector  # 품종인식
import nodeStepChecker
import nodeSpeedChecker
import mindProcessor
# import MysqlController
import QMUtil
import os
import threading
import JsonLoader
from partObject import partObject, ObjectList

import RCM.rcm
from RCM.rcm_flag import RCM_Flag as rf
from RCM.rcm_data import RCM_Data as rd

PORT = 49153
LINE_MAX = 100
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class Ui_SensorDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.js = JsonLoader.JsonLoader()
        self.nsg_info = self.js.load_data("sg")
        self.nsource = dSensor.dSensor()
        self.lineNo = int(self.nsg_info["robot"]["number"])
        self.npd = nodePartDetector.nodePartDetector(self.lineNo )
        self.nsc = nodeSpeedChecker.nodeSpeedChecker(self.lineNo )
        self.nstep = nodeStepChecker.nodeStepChecker(self.lineNo )
        self.cur_path = self.nsg_info["path"]["cur_path"]
        self.ip_address = self.nsg_info["connect"]["ip"]
        self.mind = mindProcessor.mindProcessor()
        self.rcm = RCM.rcm.RobotControlManager()
        self.initUI()
        self.channel = 0  # color:0  depth =1
        self.camMode = False
        self.inform_cnt = 0
        self.ptext_cnt = 0
        self.stext_cnt = 0
        self.sptext_cnt = 0
        self.rcm_inform_cnt = 0
        self.bConnB = False
        self.testV = 0
        self.oldStateV = None
        self.curObjList = ObjectList()  # 현재 진행중인 객체를 기록함. (품종/순번)
        self.rpn = 0  # record part number
        self.srcImgChenel = 0
        self.bConnect = False  # rcm 접속 flag
        self.sgConnect = False  # detect sg 접속 flag
        # self.partID = None
        self.partID = "debug"
        self.start_flag = False

    def __del__(self):
        self.deleteLater()
        pass
        # self.ds.stop()

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI')
        self.setWindowTitle('* New Sense Generator *')
        self.image_label = QLabel()  # source image

        self.imgCur = cv2.imread("c.jpg", cv2.IMREAD_COLOR)
        self.imgSrc = self.imgCur.copy()
        self.image_label.setGeometry(QRect(0, 0, 640, 480))
        self.image_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(False)
        self.image_label.setObjectName("image_label")

        self.depth_image_label = QLabel()  # source image
        self.depth_imgCur = cv2.imread("c.jpg", cv2.IMREAD_COLOR)
        self.depth_imgSrc = self.depth_imgCur.copy()
        self.depth_image_label.setGeometry(QRect(0, 0, 640, 480))
        self.depth_image_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.depth_image_label.setAlignment(Qt.AlignCenter)
        self.depth_image_label.setWordWrap(False)
        self.depth_image_label.setObjectName("image_label")

        self.partID_text = QTextEdit()
        self.partID_text.setFixedHeight(80)
        self.partID_text.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.partID_text.setTextColor(QColor(255, 255, 0))

        self.step_text = QTextEdit()
        self.step_text.setFixedHeight(180)
        self.step_text.setStyleSheet("background-color: blue; border: 1px solid gray;")
        self.step_text.setTextColor(QColor(255, 255, 255))

        self.speed_text = QTextEdit()
        self.speed_text.setFixedHeight(250)
        self.speed_text.setStyleSheet("background-color:black; border: 1px solid gray;")
        self.speed_text.setTextColor(QColor(255, 255, 255))
        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(250)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255, 255, 0))

        textBox = QVBoxLayout()
        textBox.addWidget(self.infomsg)
        plabel = QLabel('품종인식 결과 : part id list')
        textBox.addWidget(plabel)
        textBox.addWidget(self.partID_text)
        stlabel = QLabel('Step Processing    ...')
        textBox.addWidget(stlabel)
        textBox.addWidget(self.step_text)
        splabel = QLabel('Speed check')
        textBox.addWidget(splabel)
        textBox.addWidget(self.speed_text)

        img_vb = QVBoxLayout()
        img_vb.addWidget(self.image_label)
        img_vb.addWidget(self.depth_image_label)

        hb = QHBoxLayout()
        hb.addLayout(img_vb)
        hb.addLayout(textBox)

        whole_hb = QHBoxLayout()
        whole_hb.addLayout(hb)
        whole_hb.addLayout(self.testInfoBox())

        whole_vb = QVBoxLayout()
        whole_vb.addLayout(whole_hb)

        self.setLayout(whole_vb)
        self.show()
        self.bConnect = False

    def testInfoBox(self):
        testbox = QVBoxLayout()

        hbox = QHBoxLayout()

        self.camBtn = QPushButton('ON')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.camBtn.clicked.connect(self.start)
        hbox.addWidget(self.camBtn)
        self.clearbtn = QPushButton('STOP')
        self.clearbtn.clicked.connect(self.clearMsg)
        hbox.addWidget(self.clearbtn)

        self.motionMode = QPushButton('모션모드')
        self.motionMode.clicked.connect(self.manual_motion_mode)
        hbox.addWidget(self.motionMode)
        
        self.ssbtn = QPushButton('저장시작')
        self.ssbtn.clicked.connect(self.saveStart)
        self.sstopbtn = QPushButton('저장중단')
        self.sstopbtn.clicked.connect(self.saveStop)
        
        testbox.addLayout(hbox)
        testbox.addLayout(self.rcm.vb)

        return testbox

    # Signal Slot connect #############################
    def connectSignal(self):
        # camera node slot
        self.nsource.dssg.color_signal.connect(self.update_image)
        #self.nsource.dssg.depth_signal.connect(self.depth_image)
        self.nsource.dssg.report_signal.connect(self.update_msg)
        #self.nsc.sig.report_signal.connect(self.update_msg)
        #self.nsc.sig.rstImg_signal.connect(self.update_result_depth)
        #self.nsc.sig.speed_signal.connect(self.setSpeed)
        # step checker node slot
        self.nstep.nsig.report_signal.connect(self.update_step_text)
        self.nstep.nsig.step_signal.connect(self.setStep)
        self.nstep.nsig.rst_signal.connect(self.ret_image)
        self.nstep.nsig.colorImg_signal.connect(self.update_result_color)
        self.nstep.nsig.depthImg_signal.connect(self.update_result_depth)
        self.nstep.nsig.tObjSig.connect(self.sendTarget)
        # self.rcm.rcm_server.signal.connect(self.rcm_status)
        self.nstep.nsig.tact_time_signal.connect(self.update_rcm_infomsg)
        self.npd.dsig.partObjSig.connect(self.detectPart)
        self.npd.dsig.dt_signal.connect(self.update_dt)
        self.npd.dsig.clsStep_signal.connect(self.setPartClassStep)   
        self.infomsg.append('OPENCV VERSION = ' +cv2.__version__)
        
    # 기능관련 #############################
    def start(self):
        # self.nds.start()  # camera node start
        # self.nds.working = True
        self.nsource.cam_setting()
        # self.nsource.cam_setting("../A011B0084/")
        self.nsource.start()
        self.npd.start()
        #self.nsc.start()
        self.nstep.start()
        self.camMode = True
        self.infomsg.append('Thread 시작 했습니다')
        self.rcm.start_RCM_Thread()
        self.rcm.btn3.setStyleSheet("background-color: rgb(0, 255, 0)")
        self.manual_motion_mode()
        # self.rcm.run_Rcm_Thread()

        # self.infomsg.append('RealSensor에서 영상을 촬영을 시작 했습니다')

    def stop(self):
        # self.nds.stop()
        self.npd.stop()
        #self.nsc.stop()
        self.nstep.stop()
        self.camMode = False
        self.nsource.stop()
        self.rcm.stop_RCM_Thread()
        # if self.bConnect == True:

        # self.bConnect = False
        self.infomsg.append('Thread 를 중단합니다. ')

    
    def manual_motion_mode(self):
        if(rf.FLAG_RECV_FROM_NSG_PRODUCT == False):
            rf.FLAG_RECV_FROM_NSG_PRODUCT = True
            self.motionMode.setStyleSheet("background-color: rgb(0, 255, 0)")         
            print("Auto Mode")  
        else:
            rf.FLAG_RECV_FROM_NSG_PRODUCT = False
            self.motionMode.setStyleSheet("background-color: rgb(255, 0, 0)")
            print("Manual Mode")
            motion_number = "1"
            self.rcm.data_Get_Robot_Motion_Datas_From_Db()  
            motion_number, ok = QInputDialog.getText(self, '실행할 모션', '모션 번호:')
            if ok:
                rd.rcm_product_Name = rd.robot_Motions[motion_number]
                print("실행할 모션 : ", rd.rcm_product_Name)
            elif (len(rd.rcm_product_Name) == 0):
                rd.rcm_product_Name = "None"


    #  TEST UI ########################################################

    def updateImageLable(self, q_img):
        self.image_label.setPixmap(q_img)

    def updateDepthLable(self, q_img):
        self.depth_image_label.setPixmap(q_img)

    def clearMsg(self):
        self.ppname.clear()
        # self.ds.working = False
        self.stop()
        self.infomsg.append('thread 를 종료합니다. ')

    def createFolder(self):
        product_name, ok = QInputDialog.getText(self, '제품 이름 생성', '제품명:')
        if ok:
            self.cur_path = self.cur_path
            self.new_dir = self.cur_path + product_name + '/'
            if not os.path.exists(self.new_dir):
                os.mkdir(self.new_dir)
            self.infomsg.append('create Folder ' + self.new_dir)
            # self.ds.f_path = new_dir

    def createFolderPly(self):
        self.cur_path = self.cur_path
        self.new_dir_ply = self.cur_path + self.plypname.text() + '/'
        if not os.path.exists(self.new_dir_ply):
            os.mkdir(self.new_dir_ply)
        self.infomsg.append('create Folder ' + self.new_dir_ply)

    def saveStart(self):
        self.infomsg.append('save start ply file..')
        self.nsource.bFileWrite = True
        self.nsource.save_dir = self.new_dir

    def saveStop(self):
        self.nsource.bFileWrite = False
        self.nsource.f_no = 0
        self.infomsg.append('stop save ply file to folder')

    def closeEvent(self, e):
        pass  # self.ds.working = False

    def convert_cv_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def extract_ROI(self, frame):
        x_roi = 200
        y_roi = 40
        w_roi = 250
        h_roi = 300
        roi = frame[y_roi:y_roi + h_roi, x_roi:x_roi + w_roi]
        rgb_image = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        roi_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = roi_to_Qt_format.scaled(250, 300, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def inactive_msg(self, str):
        self.append_stateV(str)

    def append_stateV(self, state_value):
        stateV = None
        if state_value != self.oldStateV:
            if state_value == "W":
                stateV = "제품 대기중"
            elif state_value == "S":
                stateV = "도장 시작"
            elif state_value == "P":
                stateV = "로봇 도장 중"
            elif state_value == "F":
                stateV = "도장 완료"
            else:
                pass
            self.infomsg.append(stateV)
        self.oldStateV = state_value

    def keyPressEvent(self, e):       
        if e.key() == Qt.Key_0: 
            self.start()

        elif e.key() == Qt.Key_Period: 
            sys.exit()

        elif e.key() == Qt.Key_1: 
            self.createFolder()

        elif e.key() == Qt.Key_2: 
            self.saveStart()

        elif e.key() == Qt.Key_3: 
            self.saveStop()

        elif e.key() == Qt.Key_4: 
            self.rcm.data_Get_Robot_Motion_Datas_From_Db()

        elif e.key() == Qt.Key_5: 
            self.rcm.execute_Robot_Motion_Test()

        elif e.key() == Qt.Key_6: 
            self.rcm.set_Fixed_Gun_Status()

        elif e.key() == Qt.Key_7: 
            self.rcm.set_Robot_Home_Position()

        elif e.key() == Qt.Key_8: 
            self.rcm.set_Robot_Emergency()

        elif e.key() == Qt.Key_9: 
            self.rcm.control_Recv_From_Nsg()

        elif e.key() == Qt.Key_Asterisk:
            self.manual_motion_mode()



    #################################################################
    # 기능 슬롯
    # partObject
    @pyqtSlot(partObject)
    def detectPart(self, dpart):
        self.nstep.setObject(dpart)
        
    def sendTarget(self, dpart):
        #print('nsg send target object : ', dpart.getInfoStr())
        #self.nsc.setObject(dpart)
        pass


    # image slot for get image
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):

        self.npd.setImage(cv_img)
        #self.nsc.setImage(cv_img)
        self.nstep.setColorImage(cv_img.copy())  #

    def depth_image(self, cv_img):
        pass
        #self.nsc.setImage(cv_img)


    def update_result_color(self, cv_img):
        self.imgCur = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateImageLable(qt_img)

    def update_result_depth(self, cv_img):
        self.depth_imgSrc = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateDepthLable(qt_img)
    # image slot for get image

    def ret_image(self, cv_img):
        if self.srcImgChenel == 1:
            qt_img = self.convert_cv_qt(cv_img)
            # self.updateImageLable(qt_img)
            self.updateDepthLable(qt_img)

    @pyqtSlot(list)
    def update_dt(self, outs):
         self.nstep.setDT(outs)

    @pyqtSlot(str)
    def update_msg(self, str):
        self.inform_cnt += 1
        if self.inform_cnt > LINE_MAX:
            self.infomsg.clear()
            self.inform_cnt = 0
        self.infomsg.append(str)

    def update_partID(self, str):
        self.ptext_cnt += 1
        if self.ptext_cnt > LINE_MAX:
            self.partID_text.clear()
            self.ptext_cnt = 0
        self.partID_text.append(str)

    def update_step_text(self, str):
        self.stext_cnt += 1
        if self.stext_cnt > LINE_MAX:
            self.step_text.clear()
            self.stext_cnt = 0
        self.step_text.append(str)

    def update_speed_text(self, str):
        self.sptext_cnt += 1
        if self.sptext_cnt > LINE_MAX:
            self.speed_text.clear()
            self.sptext_cnt = 0
        self.speed_text.append(str)
    
    def update_rcm_infomsg(self, str):
        self.rcm_inform_cnt += 1
        if self.rcm_inform_cnt > 12:
            self.rcm.infomsg.clear()
            self.rcm_inform_cnt = 0
        self.rcm.infomsg.append(str)

    @pyqtSlot(int, int, int)
    def setPartClassStep(self, rs, ss, es):
        self.start_state = ss
        self.mind.tmodel.set_s_con(self.start_state)
        self.mind.motion.setstartState(self.start_state)
        self.nstep.setStateStart(self.start_state)
        #self.pStart.setText(str(self.start_state))
        self.end_state = es
        self.mind.tmodel.set_e_con(self.end_state)
        self.mind.motion.setEndState(self.end_state)
        self.nstep.setStateEnd(self.end_state)
        #self.pState.setText(str(es))
        self.reset_state = rs
        self.mind.tmodel.set_r_con(self.reset_state)
        self.nstep.setStateReady(self.reset_state)
        #self.pFinish.setText(str(rs))
        self.mind.infoState()

    @pyqtSlot(int, float, str)
    def setStep(self, stepV, speedV, partid):
        # input sensor data............................
        start_flag = False
        self.mind.setStepV(stepV, speedV)
        self.mind.setPardID(partid)
        self.update_speed_text('step = ' + str(stepV) + ' : ' + str(speedV))

        # processing....................................
        tstete, motion,start_value = self.mind.process()

        if tstete == 'start':
            no,spx,self.start_flag = self.nstep.startRun(start_value)
            self.nstep.setReady()
            #if speedV == 0 :  # 추적 실패 코드
            #    self.nsc.stopTracking()
            self.partID_text.append('No ' + str(no) + ' run ;' + str(spx))
        elif tstete == 'out' :
            self.nstep.out()
            self.partID_text.append('Out ')



        str_array = motion.getWord()

        if str_array is not None and self.start_flag == True:
            #print("전송 정보 : ", str_array)
            if (rf.FLAG_ROBOT_START == True):
                self.rcm.rcm_server.recv_From_Nsg(str_array,self.start_flag)


    @pyqtSlot(float, int)
    def setSpeed(self, speedV, rstate):
        self.nstep.setSpeed(speedV,rstate)
        # self.mind.setSpeedV(speedV)
        # stete = self.mind.process()
        #self.infomsg.append(f"spped = "+str(speedV))
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_SensorDialog()
    ui.connectSignal()
    ui.rcm.run_Rcm_Thread()
    ui.rcm.connectSignal()
    # ui.start()
    sys.exit(app.exec_())