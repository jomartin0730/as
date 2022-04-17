from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit,QComboBox
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize
import socket
import time
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import os
import threading
from time import sleep

HOST = '192.168.0.5'

PORT = 49153
LINE_MAX = 10000
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class Ui_TestDialog(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serverStartB = False
        self.connection = None
        self.client_address = None
        self.sendmsg = ""

    def __del__(self):
        pass
 
    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI') 
        self.setWindowTitle('Data Test')    #윈도우 창 제목
              # 영상처리 영역 #############################
        vb = QVBoxLayout()
        vb.addLayout(self.createInfoGroup())
        self.setLayout(vb)
        self.show()                     #윈도우창띄우기
       

    def createInfoGroup(self):
        #######1번째행#######
        box = QHBoxLayout()         #box = Hbox
        label = QLabel('Server IP')     #박스 옆에 ServerIP라벨
        
        self.ip = QLineEdit(HOST)
        self.ip.setInputMask('000.000.000.000;_')
        box.addWidget(label)            
        box.addWidget(self.ip)          #Server IP 제목과 입력 위젯 생성

        label = QLabel('Server Port')
        self.port = QLineEdit(str(PORT))
        box.addWidget(label)
        box.addWidget(self.port)        #Server Port 제목과 입력 위젯 생성

        self.btn = QPushButton('접속')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn.clicked.connect(self.connectClicked)
        box.addWidget(self.btn)
  
        self.clearbtn = QPushButton('초기화')
        self.clearbtn.clicked.connect(self.clearMsg)
        ####################

        #######3번째행#######
        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(300)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;") 
        self.infomsg.setTextColor(QColor(255,255,0))
        ####################

        #######2번째행#######
        self.data = QTextEdit()
        # self.data = QTextEdit()
        self.data.setFixedHeight(200)
        self.cSendData = QPushButton('send')
        self.cSendData.clicked.connect(self.sendMsg)
        self.ssbtn = QPushButton('서버시작')
        self.ssbtn.clicked.connect(self.serverStart)
        self.sstopbtn = QPushButton('중단')
        self.sstopbtn.clicked.connect(self.saveStop)    
        ####################
        
        cbox = QHBoxLayout()
        cbox.addWidget(self.ssbtn)
        cbox.addWidget(self.cSendData)
        cbox.addWidget(self.clearbtn)
        cbox.addWidget(self.sstopbtn)
        # cbox.addWidget(self.clearbtn)
        cbox.addStretch(1)
        
        vbox = QVBoxLayout()        
        vbox.addLayout(box)                 #1번째
        vbox.addWidget(self.data)
        vbox.addLayout(cbox)                #2번째
        vbox.addWidget(self.infomsg)      #3번째
        return vbox    

    
# Signal Slot connect #############################
    def connectSignal(self):
        #self.ds.dssg.msg_signal.connect(self.update_msg)
        self.infomsg.append('출력')  

# 기능관련 #############################

    def connectClicked(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
            self.client_socket.sendall('MMD'.encode("utf-8"))
            self.bConnB = True
            self.ds.bConnect = True
            self.infomsg.append('MAVIZ에 연결을 시작합니다.')
        except Exception as e:
            print("mmd connect error : ", e)


    def serverStart(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.server_socket:
            print("Fail to create socket!")
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       # hostaddr = self.ip.text
        self.server_socket.bind((HOST,PORT))
        self.server_socket.listen(3)
        #self.infomsg.append(hostaddr+" now socket listen!")

        self.thread_server = threading.Thread(target=self.server) #server 쓰레드
        self.thread_server.daemon = True
        self.thread_server.start()
        self.infomsg.append('서버가 시작 되었습니다.')
        self.serverStartB = True       

    def server(self):
        try:
            while True:
                self.connection, self.client_address = self.server_socket.accept()
                print('client_address = ', self.client_address)
            
                data = self.connection.recv(1024).decode("utf-8")
                if data:
                    print("data = ",data)
                else:
                    print("there is no data!")
                    
        except Exception as e:
            print("accept_Client : ", e)
        finally:
            print("connection close!")
            self.connection.close()
        

    def sendMsg(self):
        if self.serverStartB :
            splited_msg = self.data.toPlainText().split("\n")
            print('splited_msg = ',splited_msg)
            for send_msg in splited_msg :
                print(send_msg)
                self.connection.sendall(bytes(send_msg, encoding='utf8'))
                self.infomsg.append(send_msg)
                sleep(0.1)
        else :
            self.infomsg.append('서버가 시작되지 않았습니다. ')      

    def clearMsg(self):
        self.data.clear()
        self.infomsg.append('Data 초기화 ')  

    def saveStart(self):
        self.infomsg.append('save start ply file..')

    def saveStop(self):
        self.infomsg.append('stop save ply file to folder')            

    def updateDisconnect(self):
        self.btn.setText('접속')
        self.infomsg.append('이미지 서버에 접속이 종료되었습니다')  
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_TestDialog()
    ui.connectSignal()
    sys.exit(app.exec_())
