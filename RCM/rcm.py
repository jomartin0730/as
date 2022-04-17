from PyQt5.QtWidgets import QWidget,QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QInputDialog, QSizePolicy, QLabel, QGroupBox
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtCore import pyqtSlot 
from RCM.rcm_server import *
from RCM.rcm_sql import *
from RCM.rcm_flag import RCM_Flag as rf
from RCM.rcm_data import RCM_Data as rd

LINE_MAX = 10

class QPushButtonOperation(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = QFont("Helvetia", 13)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet("""
        QPushButton {
            background-color:rgb(245, 245, 245);
            color:black;
        }
        QPushButton:hover {
            background-color:rgb(255, 255, 255);
            color:black;
        }
        """)

class RobotControlManager(QWidget):
    thread_rcm = None

    def __init__(self):
        super().__init__()
        self.vb = self.initUI()      
        self.rcm_server = RCM_Server()
        self.rcm_sql = RCM_Sql()
        
    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI1') 
        self.setWindowTitle('Robot Control Manager')
        hbox = QHBoxLayout()
        vb = QVBoxLayout()
        vb.addLayout(self.createInfoGroup())
        vb.addLayout(hbox)
        return vb

    def connectSignal(self):
        self.rcm_server.rcm_server_signal.server_signal.connect(self.rcm_update_msg)
        self.rcm_server.rcm_server_signal.red_alarm_signal.connect(self.rcm_update_box_color)
        self.rcm_server.rcm_server_signal.yellow_alarm_signal.connect(self.rcm_update_box_color)
        self.rcm_server.rcm_server_signal.green_alarm_signal.connect(self.rcm_update_box_color)

    def createInfoGroup(self):
        box = QHBoxLayout()
        self.btn = QPushButtonOperation('안전위치')
        self.btn.clicked.connect(self.set_Robot_Home_Position)
        box.addWidget(self.btn)
        self.btn2 = QPushButtonOperation('로봇정지')
        self.btn2.clicked.connect(self.set_Robot_Emergency)
        box.addWidget(self.btn2)
        self.btn3 = QPushButtonOperation('로봇실행')
        self.btn3.clicked.connect(self.control_Recv_From_Nsg)
        self.btn3.setStyleSheet("background-color: rgb(0, 255, 0)")
        box.addWidget(self.btn3)

        box2 = QHBoxLayout()
        self.btn2_1 = QPushButtonOperation('로봇모션')
        self.btn2_1.clicked.connect(self.data_Get_Robot_Motion_Datas_From_Db)
        box2.addWidget(self.btn2_1)
        self.btn2_2 = QPushButtonOperation('모션테스트')
        self.btn2_2.clicked.connect(self.execute_Robot_Motion_Test)
        box2.addWidget(self.btn2_2)
        self.btn2_3 = QPushButtonOperation('고정건')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn2_3.clicked.connect(self.set_Fixed_Gun_Status)
        box2.addWidget(self.btn2_3)

        self.box3 = QHBoxLayout()
        self.red_box = QLabel()
        self.image_red = QPixmap("RCM/button_img/button_D3.png") # 꺼진 사진
        self.image_red = self.image_red.scaledToWidth(80)
        self.red_box.setPixmap(QPixmap(self.image_red))
        self.box3.addWidget(self.red_box)
        self.yellow_box = QLabel()    
        self.image_yellow = QPixmap("RCM/button_img/button_D2.png") # 꺼진 사진
        self.image_yellow = self.image_yellow.scaledToWidth(80)
        self.yellow_box.setPixmap(QPixmap(self.image_yellow))
        self.box3.addWidget(self.yellow_box)
        self.green_box = QLabel()
        self.image_green = QPixmap("RCM/button_img/button_D1.png") # 꺼진 사진
        self.image_green = self.image_green.scaledToWidth(80)
        self.green_box.setPixmap(QPixmap(self.image_green)) 
        self.box3.addWidget(self.green_box)

        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(400)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255,255,0))
        self.infomsg.append('Robot Control Manager 실행')

        vbox = QVBoxLayout()
        vbox.addLayout(self.box3)        
        vbox.addLayout(box)
        vbox.addLayout(box2)
        vbox.addWidget(self.infomsg)
        return vbox

### Functions # ====================================================================================================== #
    def set_Robot_Home_Position(self):
        if (rf.FLAG_SERVER_OPEN == True and rf.FLAG_SERVER_CLOSED == False):
            self.rcm_server.HOME()
            self.infomsg.clear()
            self.infomsg.append('명령송신 : 로봇 안전위치')
            rf.FLAG_HOME = True
            self.rcm_server.repeat_Count = 0
            self.rcm_server.sended_Data_Number = 0
            rf.FLAG_MOTION_EXECUTED = False
            rf.FLAG_THREAD_SENDING_STATE = False
            rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
            rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
            self.rcm_server.data_Reset()
        else:
            pass

    def set_Robot_Emergency(self):
        if (rf.FLAG_SERVER_OPEN == True and rf.FLAG_SERVER_CLOSED == False):
            self.rcm_server.EMERGENCY()
            self.infomsg.clear()
            self.infomsg.append('명령송신 : 로봇 비상정지')
            rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
            #rf.FLAG_AUTO_MODE = False
            rf.FLAG_MOTION_EXECUTED = False
            rf.FLAG_THREAD_SENDING_STATE = False
            rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
            self.rcm_server.data_Reset()
        else:
            pass

    def set_Fixed_Gun_Status(self):
        if (rf.FLAG_SERVER_OPEN == True and rf.FLAG_SERVER_CLOSED == False):
            self.infomsg.clear()
            if (rf.FLAG_GUN_SPRAYING_ON == False):
                rf.FLAG_GUN_SPRAYING_ON = True
                self.infomsg.append('명령송신 : 도장건 켜짐')
                self.btn2_3.setStyleSheet("background-color: rgb(0, 0, 255)")
            else:
                rf.FLAG_GUN_SPRAYING_ON = False
                self.infomsg.append('명령송신 : 도장건 꺼짐')
                self.btn2_3.setStyleSheet("background-color: rgb(245, 245, 245)")
            self.rcm_server.PAINTING_GUN()
        else:
            pass

    def data_Get_Robot_Motion_Datas_From_Db(self):
        self.infomsg.clear()
        sql_List = self.rcm_sql.load_Robot_Motion_Names()
        cnt = 0
        for motion in sql_List:
            cnt += 1
            rd.robot_Motions[str(cnt)] = motion
            self.infomsg.append(str(cnt) + '. ' + motion)

    def execute_Robot_Motion_Test(self):
        motion_number, ok = QInputDialog.getText(self, '실행할 모션', '모션 번호:')
        motion_count, ok = QInputDialog.getInt(self, '실행할 모션', '실행 횟수:')
        if ok:
            table_Name = rd.robot_Motions[motion_number]
            print("실행할 모션 : ", motion_number, ', ', table_Name)
            print("────────────────────────────────────────────────")
            rf.FLAG_SIMULATION = True
            self.rcm_server.product_Name = table_Name
            self.rcm_server.old_Product_Name = table_Name
            self.rcm_server.run_Robot_By_Scheduler_Combined_Data('7.0') # rcm 속도변경
            self.rcm_server.repetition = motion_count# rcm 반복횟수
            rf.FLAG_THREAD_SENDING_STATE = True
            rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = True
            self.infomsg.clear()
            sql_Name = self.rcm_sql.load_Pose_Data_With_Product_Name_From_DB(table_Name)
            rd.rcmStartTime = time.time()
            self.infomsg.append("실행 중인 모션 : ")
            self.infomsg.append(sql_Name)

    def control_Recv_From_Nsg(self):
        if (rf.FLAG_RECV_FROM_NSG_STOP == False):
            self.btn3.setStyleSheet("background-color: rgb(255, 0, 0)")
            rf.FLAG_RECV_FROM_NSG_STOP = True
            print("RCM 동작 가능", rf.FLAG_RECV_FROM_NSG_STOP)
            self.rcm_server.data_Reset()
            self.rcm_server.product_Name = ""
            self.rcm_server.old_Product_Name = ""
        else:
            self.btn3.setStyleSheet("background-color: rgb(0, 255, 0)")
            rf.FLAG_RECV_FROM_NSG_STOP = False
            print("NSG 동작 가능", rf.FLAG_RECV_FROM_NSG_STOP)
            rf.FLAG_SIMULATION = False
# ==================================================================================================================== #

### Thread # ====================================================================================================== #
    def run_Rcm_Thread(self):
        self.thread_rcm = threading.Thread(target=self.run_RCM)
        self.thread_rcm.daemon = True
        self.thread_rcm.start()

    def run_RCM(self):
        while(rf.FLAG_PROGRAM_SHUTDOWN == False):
            if (rf.FLAG_DATABASE_IS_ON == False):
                try:
                    self.rcm_sql.check_Db_On()
                except:
                    rf.FLAG_DATABASE_IS_ON = False
                    print("Can't connect to database")
            else:
                if (rf.FLAG_SERVER_OPEN == False and rf.FLAG_SERVER_CLOSED == False):
                    self.rcm_server.server_init()
                    #self.rcm_server = RCM_Server()
                    self.rcm_server.run_Thread()
                elif (rf.FLAG_SERVER_CLOSED == True):
                    rf.FLAG_SERVER_CLOSED = False
                    self.rcm_server.stop()
                    self.rcm_server.clear()
                    self.rcm_server.run_Thread()
                    rf.FLAG_SERVER_OPEN = True
                else:
                    rf.FLAG_SERVER_CLOSED = False
            time.sleep(1)

        if (rf.FLAG_PROGRAM_SHUTDOWN == True):
            self.rcm_server.stop()
            self.rcm_server.clear()
            rf.FLAG_SERVER_CLOSED = True    

    def stop_RCM_Thread(self):
        rf.FLAG_PROGRAM_SHUTDOWN = True
        rf.FLAG_THREAD_STOP = True
        rf.FLAG_RECV_FROM_NSG_STOP = True

    def start_RCM_Thread(self):
        rf.FLAG_PROGRAM_SHUTDOWN = False
        rf.FLAG_THREAD_STOP = False
        rf.FLAG_RECV_FROM_NSG_STOP = False

    @pyqtSlot(str)
    def rcm_update_msg(self, str):
        #self.infomsg.clear()
        self.infomsg.append(str)

    def rcm_update_box_color(self, str):
        if (str == "R"):
            self.box3.removeWidget(self.green_box)
            self.box3.removeWidget(self.yellow_box)
            self.box3.removeWidget(self.red_box)
            self.red_box.clear()
            self.yellow_box.clear()
            self.green_box.clear()

            self.red_box = QLabel()
            self.image_red = QPixmap("RCM/button_img/button_R.png") # 꺼진 사진
            self.image_red = self.image_red.scaledToWidth(80)
            self.red_box.setPixmap(QPixmap(self.image_red))
            self.box3.addWidget(self.red_box)
            self.yellow_box = QLabel()    
            self.image_yellow = QPixmap("RCM/button_img/button_D2.png") # 꺼진 사진
            self.image_yellow = self.image_yellow.scaledToWidth(80)
            self.yellow_box.setPixmap(QPixmap(self.image_yellow))
            self.box3.addWidget(self.yellow_box)
            self.green_box = QLabel()
            self.image_green = QPixmap("RCM/button_img/button_D1.png") # 꺼진 사진
            self.image_green = self.image_green.scaledToWidth(80)
            self.green_box.setPixmap(QPixmap(self.image_green)) 
            self.box3.addWidget(self.green_box)

        elif (str == "Y"):
            self.box3.removeWidget(self.green_box)
            self.box3.removeWidget(self.yellow_box)
            self.box3.removeWidget(self.red_box)
            self.red_box.clear()
            self.yellow_box.clear()
            self.green_box.clear()

            self.red_box = QLabel()
            self.image_red = QPixmap("RCM/button_img/button_D3.png") # 꺼진 사진
            self.image_red = self.image_red.scaledToWidth(80)
            self.red_box.setPixmap(QPixmap(self.image_red))
            self.box3.addWidget(self.red_box)  
            self.yellow_box = QLabel()    
            self.image_yellow = QPixmap("RCM/button_img/button_Y.png") # 꺼진 사진
            self.image_yellow = self.image_yellow.scaledToWidth(80)
            self.yellow_box.setPixmap(QPixmap(self.image_yellow))
            self.box3.addWidget(self.yellow_box)
            self.green_box = QLabel()
            self.image_green = QPixmap("RCM/button_img/button_D1.png") # 꺼진 사진
            self.image_green = self.image_green.scaledToWidth(80)
            self.green_box.setPixmap(QPixmap(self.image_green)) 
            self.box3.addWidget(self.green_box)
           
        else:
            self.box3.removeWidget(self.green_box)
            self.box3.removeWidget(self.yellow_box)
            self.box3.removeWidget(self.red_box)
            self.red_box.clear()
            self.yellow_box.clear()
            self.green_box.clear()

            self.red_box = QLabel()
            self.image_red = QPixmap("RCM/button_img/button_D3.png") # 꺼진 사진
            self.image_red = self.image_red.scaledToWidth(80)
            self.red_box.setPixmap(QPixmap(self.image_red))
            self.box3.addWidget(self.red_box)
            self.yellow_box = QLabel()    
            self.image_yellow = QPixmap("RCM/button_img/button_D2.png") # 꺼진 사진
            self.image_yellow = self.image_yellow.scaledToWidth(80)
            self.yellow_box.setPixmap(QPixmap(self.image_yellow))
            self.box3.addWidget(self.yellow_box)
            self.green_box = QLabel()
            self.image_green = QPixmap("RCM/button_img/button_G.png") # 꺼진 사진
            self.image_green = self.image_green.scaledToWidth(80)
            self.green_box.setPixmap(QPixmap(self.image_green)) 
            self.box3.addWidget(self.green_box)
# ==================================================================================================================== #

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ui = Ui_SensorDialog()
#     ui.run_Rcm_Thread()
#     sys.exit(app.exec_())
