from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel,QGridLayout,QCheckBox,QMenu, QVBoxLayout, QHBoxLayout, \
     QGroupBox, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider, QInputDialog
from PyQt5.QtGui import QPixmap,QImage,QColor
from PyQt5.QtCore import QDir, Qt,QRect,QSize, QCoreApplication
import socket
import time
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
import numpy as np
import os
import threading
from gcm_flag import GCM_Flag as gf
from gcm_client import *
from gcm_server import *
from gcm_sql import *
from gcm_data import GCM_Data as gd

class Ui_SensorDialog(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        gd.gcm_server = None

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI') 
        self.setWindowTitle('Robot Control Manager')
        hbox = QHBoxLayout()
        vb = QVBoxLayout()
        vb.addLayout(self.createInfoGroup())
        vb.addLayout(hbox)
        self.setLayout(vb)
        self.show()
       
    def createInfoGroup(self):
        box = QHBoxLayout()
        self.btn = QPushButton('고정건모션')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn.clicked.connect(self.data_Get_Fixed_Gun_Motion_Datas_From_Db)
        box.addWidget(self.btn)
        self.btn2 = QPushButton('모션테스트', self)
        self.btn2.clicked.connect(self.execute_Fixed_Gun_Motion_Test)
        box.addWidget(self.btn2)
        self.btn3 = QPushButton('고정건')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn3.clicked.connect(self.set_Fixed_Gun_Status)
        box.addWidget(self.btn3)

        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(400)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))
        self.infomsg.append('Robot Control Manager 실행')

        cbox = QHBoxLayout()
        vbox = QVBoxLayout()        
        vbox.addLayout(box)
        vbox.addLayout(cbox)
        vbox.addWidget(self.infomsg)
        return vbox

### Functions # ====================================================================================================== #
    def set_Robot_Emergency(self):
        if (gf.FLAG_SERVER_OPEN == True and gf.FLAG_SERVER_CLOSED == False):
            gd.gcm_server.EMERGENCY()
            self.infomsg.clear()
            self.infomsg.append('명령송신 : 로봇 비상정지')
            gf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
            gf.FLAG_AUTO_MODE = False
        else:
            pass

    def set_Fixed_Gun_Status(self):
        if (gf.FLAG_SERVER_OPEN == True and gf.FLAG_SERVER_CLOSED == False):
            self.infomsg.clear()
            if (gf.FLAG_GUN_SPRAYING_ON == False):
                gf.FLAG_GUN_SPRAYING_ON = True
                self.infomsg.append('명령송신 : 도장건 켜짐')
            else:
                gf.FLAG_GUN_SPRAYING_ON = False
                self.infomsg.append('명령송신 : 도장건 꺼짐')
            gd.gcm_server.PAINTING_GUN()
        else:
            pass

    def data_Get_Fixed_Gun_Motion_Datas_From_Db(self):
        self.infomsg.clear()
        gcm_sql = GCM_Sql()
        sql_List = gcm_sql.load_Fixgun_Motion_Names()
        cnt = 0
        for motion in sql_List:
            cnt += 1
            gd.fixgun_Motions[str(cnt)] = motion
            self.infomsg.append(str(cnt) + '. ' + motion)

    def execute_Fixed_Gun_Motion_Test(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
        if ok:
            table_Name = gd.fixgun_Motions[text]
            print("실행할 모션 : ", text, ', ', table_Name)
            print("────────────────────────────────────────────────")
            gcm_sql = GCM_Sql()
            sql_List = eval(gcm_sql.load_Fixgun_Motion(table_Name))
            converted_Data = gd.data_Set_Fixgun_Motion_Integer_To_String(sql_List)
            print(converted_Data)
            gd.gcm_server.send_To_FIXGUN(converted_Data)

### Thread # ====================================================================================================== #
    def run_Gcm_Thread(self):
        gd.thread_gcm = threading.Thread(target=self.run_GCM)
        gd.thread_gcm.daemon = True
        gd.thread_gcm.start()

    def run_GCM(self):
        while(gf.FLAG_PROGRAM_SHUTDOWN == False):
            if (gf.FLAG_DATABASE_IS_ON == False):
                try:
                    gcm_sql = GCM_Sql()
                    gcm_sql.check_Db_On()
                except:
                    gf.FLAG_DATABASE_IS_ON = False
                    print("Can't connect to database")
            else:
                if (gf.FLAG_SERVER_OPEN == False and gf.FLAG_SERVER_CLOSED == False):
                    gd.gcm_server = GCM_Server()
                    gd.gcm_server.run_Thread()
                elif (gf.FLAG_SERVER_CLOSED == True):
                    gf.FLAG_SERVER_CLOSED = False
                    gd.gcm_server.stop()
                    gd.gcm_server.clear()
                    gd.gcm_server.run_Thread()
                    gf.FLAG_SERVER_OPEN = True
                else:
                    gf.FLAG_SERVER_CLOSED = False
            time.sleep(1)

        if (gf.FLAG_PROGRAM_SHUTDOWN == True):
            gd.gcm_client.stop()
            gd.gcm_client.clear()
            gd.gcm_server.stop()
            gd.gcm_server.clear()
            QCoreApplication.instance().quit()
            # os.system("shutdown -h now")                                        # FIXME : need to open (closed 210209)

# ==================================================================================================================== #

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_SensorDialog()
    ui.run_Gcm_Thread()
    sys.exit(app.exec_())
