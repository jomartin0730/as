from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit,QComboBox, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize
#from PyQt5.QtWidgets import QFileDialog
#from PyQt5.QtWidgets import QMessageBox
import socket
import time
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import img_client
import MysqlController
import QMUtil
import os
import datetime
import schedule
import threading

PORT = 9999
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class Ui_ImageDialog(QWidget):

    infomsg_count = 0
    def __init__(self):
        super().__init__()
        self.c = img_client.ClientSocket(self)
        self.d = MysqlController.MysqlController('192.168.0.103','mgt','aA!12345','maviz')
        self.iv = QMUtil.ImageViewer()
        self.initUI()

        self.partID = None
        self.old_partID = None


    def __del__(self):
        self.c.stop()

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI')
        self.setWindowTitle('Magenta Robotics Inc')
        self.image_label = QLabel() # source image
        self.image_labelB = QLabel() # source image

        # 영상처리 영역 #############################
        grid = QGridLayout()
        grid.addWidget(self.createInfoGroup(), 0, 0)
        grid.addWidget(self.createInputImage(), 1, 0)
        self.setLayout(grid)
        self.show()


    def createInputImage(self):
        groupbox = QGroupBox('Input Image from Line')
        box = QHBoxLayout()

        self.imgCur =  cv2.imread("c.jpg", cv2.IMREAD_COLOR)
        self.imgSrc =  self.imgCur.copy()
        self.image_label.setGeometry(QRect(110, 0, 640, 480))
        self.image_label.setPixmap(QtGui.QPixmap("c.jpg"))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(False)
        self.image_label.setObjectName("image_label")

        self.imgCurB =  cv2.imread("c.jpg", cv2.IMREAD_COLOR)
        self.imgSrcB =  self.imgCurB.copy()
        self.image_labelB.setGeometry(QRect(750, 0, 640, 480))
        self.image_labelB.setPixmap(QtGui.QPixmap("c.jpg"))
        self.image_labelB.setAlignment(Qt.AlignCenter)
        self.image_labelB.setWordWrap(False)
        self.image_labelB.setObjectName("image_labelB")

        hbox = QHBoxLayout()
        hbox.addLayout(box)
        hbox.addWidget(self.image_label)
        hbox.addWidget(self.image_labelB)

        groupbox.setLayout(hbox)

        return groupbox


    def createInfoGroup(self):
        gb = QGroupBox('서버 설정')
        gb.setFlat(True)

        box = QHBoxLayout()

        label = QLabel('Server IP')

        self.ip = QLineEdit('192.9.226.148')
        self.ip.setInputMask('000.000.000.000;_')
        box.addWidget(label)
        box.addWidget(self.ip)
        label = QLabel('Server Port')
        self.port = QLineEdit(str(PORT))
        box.addWidget(label)
        box.addWidget(self.port)

        self.btn = QPushButton('접속')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)

        self.ppname = QLineEdit('')

        self.cFolder = QPushButton('폴더생성')
        self.cFolder.clicked.connect(self.createFolder)
        box.addWidget(self.ppname)
        box.addWidget(self.cFolder)

        self.savebtn = QPushButton('저장')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.savebtn.clicked.connect(self.saveImg)
        box.addWidget(self.savebtn)

        self.stopbtn = QPushButton('저장중지')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.stopbtn.clicked.connect(self.stopImg)
        box.addWidget(self.stopbtn)

        label = QLabel('정보')
        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(300)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))
        self.infomsg.setFontPointSize(30)

        cbox = QVBoxLayout()
        cbox.addWidget(label)
        cbox.addWidget(self.infomsg)

        cbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(box)
        vbox.addLayout(cbox)
        gb.setLayout(vbox)
        return gb



# 기능관련 #############################

    def createFolder(self):
        self.cur_path = '/home/mgt-pc3/works/img/'
        self.new_dir = self.cur_path + self.ppname.text() + '/'
        if not os.path.exists(self.new_dir):
            os.mkdir(self.new_dir)
        self.infomsg.append('create Folder ' + self.new_dir)
        # self.ds.f_path = new_dir

    def connectClicked(self):
          if self.c.bConnect == False:
               ip = self.ip.text()
               port = self.port.text()
               if self.c.connectServer(ip, int(port)):
                    self.btn.setText('접속 종료')
               else:
                    self.c.stop()
                    #self.sendmsg.clear()
                    self.btn.setText('접속')
          else:
                self.c.stop()
                #self.sendmsg.clear()
                self.infomsg.clear()
                self.btn.setText('접속')
          print("접속 시도")

    def saveImg(self):
        self.c.path = self.new_dir
        self.c.Img_Write_Flag = True

    def stopImg(self):
        self.c.Img_Write_Flag = False

    def connectSignal(self):
        self.c.recv.recv_signal.connect(self.update_aimage)
        self.c.recv.recv_signalb.connect(self.update_bimage)
        self.c.recv.send_detect_data.connect(self.update_imfomsg)
        self.iv.crop.cut_signal.connect(self.cut_image)
        self.c.disconn.disconn_signal.connect(self.updateDisconnect)
        self.infomsg_append('이미지 서버에 접속 했습니다')

    def updateImageLable(self, q_img):
        self.image_label.setPixmap(q_img)
        # if self.checkBox1.isChecked() == True:
        #     self.fm()
    def updateImageLableB(self, q_img):
        self.image_labelB.setPixmap(q_img)

    # def updateFeatureLable(self, q_img):
    #     self.f_label.setPixmap(q_img)

    def sendImage2rst(self):
        self.iv.setImage(self.convert_cv_qt(self.imgCur))
        #self.rst_label.setPixmap(self.convert_cv_qt(self.imgCur))
        self.imgSrc =  self.imgCur.copy()
        self.infomsg_append('결과 영상을 업데이트 했습니다')

    def updateDisconnect(self):
        self.btn.setText('접속')
        self.infomsg_append('이미지 서버에 접속이 종료되었습니다')

    # def onActivatedCombo(self, text):
    #     self.infomsg_append(text)
    #     #self.c.changeMode()
    #     self.c.changeMode(text)
    #     self.infomsg_append('이미지 채널이 변경 되었습니다')

    def sendMsg(self):
        sendmsg = self.sendmsg.text()
        self.infomsg_append(sendmsg)
        self.sendmsg.clear()

    def clearMsg(self):
        self.infomsg.clear()

    def imgProcess(self):
        self.infomsg_append('영상처리를 시작 합니다. ')
        yCrCb = cv2.cvtColor(self.imgCur, cv2.COLOR_BGR2YCrCb)
        # y, Cr, Cb로 컬러 영상을 분리 합니다.
        y, Cr, Cb = cv2.split(yCrCb)
        # y값을 히스토그램 평활화를 합니다.
        #equalizedY = cv2.equalizeHist(y)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalizedY = clahe.apply(y)

        # equalizedY, Cr, Cb를 합쳐서 새로운 yCrCb 이미지를 만듭니다.
        yCrCb2 = cv2.merge([equalizedY, Cr, Cb])
        # 마지막으로 yCrCb2를 다시 BGR 형태로 변경합니다.
        yCrCbDst = cv2.cvtColor(yCrCb2, cv2.COLOR_YCrCb2BGR)
        #self.f_label.setPixmap(self.convert_cv_qt(yCrCbDst))


        '''
        gray_img = cv2.cvtColor(self.imgCur, cv2.COLOR_BGR2GRAY)
        equalized_img = cv2.equalizeHist(gray_img)
        img = cv2.cvtColor(equalized_img,cv2.COLOR_GRAY2BGR)
        self.f_label.setPixmap(self.convert_cv_qt(img))
        '''
        #self.f_label.setPixmap(self.convert_cv_qt(self.imgCur))

    # def saveRecode(self):
    #     pn = self.pname.text()
    #     cc = self.ccode.text()
    #     pc = self.pcode.text()
    #     if len(pn) > 0 and len(cc) > 0 and len(pc) > 0 :
    #         check_result = self.d.check_data(pc)
    #         if check_result :
    #             self.d.insert_partname(pn,cc,pc)
    #             self.d.insert_partimage(pc,self.imgSrc)
    #             self.infomsg_append('데이터를 MAVIZ DB에 저장 합니다. ')
    #             self.pname.clear()
    #         else :
    #             self.infomsg_append('데이터가 이미 DB에 존재합니다')
    #         #self.ccode.clear()
    #         #self.pcode.clear()
    #     else :
    #         self.alarm_box("DB 등록 오류", "빈칸을 입력해주세요")

    # def selectRecode(self):
    #     pn = self.pname.text()
    #     pc = self.pcode.text()
    #     if len(pc) > 0 :
    #         self.imgSrc,name,color = self.d.select_partimage(pc)
    #         self.infomsg_append('데이터를 MAVIZ DB에서 조회 합니다. ')
    #         self.pname.clear()
    #         self.ccode.clear()
    #         #self.pcode.clear()
    #         self.pname.setText(name)
    #         self.ccode.setText(color)
    #         #self.f_label.setPixmap(self.convert_cv_qt(img))
    #         self.iv.setImage(self.convert_cv_qt(self.imgSrc))
    #     else :
    #         self.alarm_box("조회 오류", "부품코드를 입력해주세요")

    # def updateRecode(self):
    #     pc = self.pcode.text()
    #     if len(pc) > 0 :
    #         self.d.change_image()




    def fm(self): #feature matching
        pass
        #result = find_almost_similar_image_locations(self.imgSrc,self.imgCur)
        # try :
        #     if result is not None:
        #         y0 = int(result['rectangle'][0][0])
        #         y1 = int(result['rectangle'][2][0])
        #         x0 = int(result['rectangle'][0][1])
        #         x1 = int(result['rectangle'][2][1])
        #         cood = f' y0={y0} y1={y1} x0={x0} x1={x1}'
        #         cv2.rectangle(self.imgCur, (y0,x0), (y1, x1), (255, 0, 255), 1)
        # finally:
        #     pass
        # #rst = self.f.get_corrected_img( self.imgSrc, self.imgCur)
        # self.iv.setImage(self.convert_cv_qt(self.imgCur))

    def test2(self):
        self.infomsg_append('test 2 ')
    def test3(self):
        self.infomsg_append('test 3 ')
    def test4(self):
        self.infomsg_append('test 4 ')

    def closeEvent(self, e):
        self.c.stop()

    # def checkBoxState(self):
    #     if self.checkBox1.isChecked() == True:
    #         self.infomsg_append('Feature matcing!! checked')
    #     else:
    #         self.infomsg_append('Feature matcing!! end')

    def convert_cv_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        frame = cv2.resize(frame,(0,0),fx=0.7,fy=0.7)
        #frame = cv2.resize(frame,dsize=(800,600))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def extract_ROI(self, frame):
        x_roi = 200
        y_roi = 40
        w_roi = 250
        h_roi = 300
        roi = frame[y_roi:y_roi+h_roi,x_roi:x_roi+w_roi]
        rgb_image = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        roi_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = roi_to_Qt_format.scaled(250, 300, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    '''
    def create_folder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory )
    '''

    def pushButtonClicked(self) :
        fname = QFileDialog.getOpenFileName(self)
        if fname[0]:
            img_path = fname[0]
            fname_list = img_path.split('/')
            length = len(fname_list)
            #print(fname_list)
            img_name = fname_list[length-2] + "/" + fname_list[length-1]
            self.infomsg_append(img_name)
            self.imgSrc = cv2.imread(img_path)
            self.infomsg_append("이미지 사이즈 : " +  str(self.imgSrc.shape))
            self.iv.setImage(self.convert_cv_qt(self.imgSrc))
        else :
            QMessageBox.about(self, 'Warning', '파일을 선택하지 않았습니다.')
        #return fname

    def alarm_box(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.about(self, title, message)

    def infomsg_append(self, str):
        self.infomsg.append(str)
        self.infomsg_count += 1
        print(self.infomsg_count)
        if self.infomsg_count == 10000 :
            self.infomsg_count = 0
            self.clearMsg()
            self.iv.clear()

    def Loading_db(self,partID,percent):
        percent = float(percent)
        if percent >= 0.80 :
            if self.old_partID is not None :
                if self.partID != self.old_partID : #새로운 제품 들어올 경우
                    self.d.loading_Insert(self.partID,percent) #새로운 제품 삽입
                    if partID == "END" :
                        self.d.loading_Update(self.partID,percent) #이전 제품 마감
                    self.old_partID = self.partID
                else : #제품 동일일 경우 그대로 진행

                    pass
            else :
                self.old_partID = partID
                self.d.loading_Insert(self.partID,percent)  # 새로운 제품 삽입
        else :
            print("percent 80% 이하")



# 슬랏  #####################################
    @pyqtSlot(np.ndarray)
    def update_aimage(self,cv_img):
        self.imgCur = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateImageLable(qt_img)

    def update_bimage(self,cv_img):
        self.imgCurB = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.updateImageLableB(qt_img)

    @pyqtSlot(np.ndarray, int, int)
    def cut_image(self,cv_img, h, w):
        self.imgSrc = cv_img
        qt_img = self.convert_cv_qt(cv_img)
        self.infomsg_append("이미지 사이즈 : width = " + str(w) + ", height = " + str(h))
        self.updateFeatureLable(qt_img)

    @pyqtSlot(str)
    def update_msg(self,str):
         self.infomsg_append(str)

    @pyqtSlot(str,str,str)
    def update_imfomsg(self,partID, amount,percent):
        self.partID = partID
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        _str = "제품 명 : " + partID + ", 수량 : " + amount + ", 확률 : " + percent + ", " + nowDatetime
        #self.Loading_db(partID,percent)
        self.infomsg_append(_str)

def job() :
    print("schedule thread start")
    while True :
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_ImageDialog()
    ui.connectSignal()

    schedule.every().day.at("08:00").do(ui.connectClicked)

    schedule_job = threading.Thread(target=job)
    schedule_job.start()
    sys.exit(app.exec_())

