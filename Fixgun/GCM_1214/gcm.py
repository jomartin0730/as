from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication
import socket
import time
import sys
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
        self.setWindowTitle('Gun Control Manager')
        columnName = ['고정건 모션 리스트']

        self.motionList = QTableWidget(self)
        self.motionList.setFixedHeight(400)
        self.motionList.setFixedWidth(500)
        self.motionList.setColumnCount(1)
        self.motionList.setColumnWidth(0, 480)
        self.motionList.setHorizontalHeaderLabels(columnName)
        self.motionList.itemDoubleClicked.connect(self.execute_Fixed_Gun_Motion_Test)
        self.motionList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.bold = QFont()
        self.bold.setBold(True)
        self.bold.setWeight(75)

        vb = QVBoxLayout()
        vb.addLayout(self.createInfoGroup())
        self.setLayout(vb)
       
    def createInfoGroup(self):
        box = QHBoxLayout()
        self.btn = QPushButton('모션 리스트 최신화') 
        self.btn.setStyleSheet("background-color: red")
        self.btn.setFont(self.bold)
        self.btn.clicked.connect(self.data_Get_Fixed_Gun_Motion_Datas_From_Db)
        box.addWidget(self.btn)

        vbox = QVBoxLayout()        
        vbox.addLayout(box)
        vbox.addWidget(self.motionList)
        return vbox

### Functions # ====================================================================================================== #
    def data_Get_Fixed_Gun_Motion_Datas_From_Db(self):
        gcm_sql = GCM_Sql()
        sql_List1 = gcm_sql.load_Fixgun_Motion_Names()
        cnt = 0
        for name in sql_List1:
            item = QTableWidgetItem(name)
            self.motionList.setRowCount(cnt + 1)
            self.motionList.setItem(0, cnt, item)
            item.setForeground(QtGui.QColor(255, 0, 255))
            item.setFont(self.bold)
            cnt += 1

    def execute_Fixed_Gun_Motion_Test(self, item_List):
        print("실행할 모션 : ", item_List.text() )
        print("────────────────────────────────────────────────")
        gcm_sql = GCM_Sql()
        sql_List = eval(gcm_sql.load_Fixgun_Motion(item_List.text() ))        
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

# ==================================================================================================================== #

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Ui_SensorDialog()
    ui.run_Gcm_Thread()
    ui.show()
    sys.exit(app.exec_())