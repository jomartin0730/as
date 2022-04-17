from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QGridLayout, QCheckBox, QMenu, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import QDir, Qt, QRect, QSize, QCoreApplication
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect, QObject
#from RCM.rcm_client import *
from RCM.rcm_server import *
from RCM.rcm_sql import *
from RCM.rcm_flag import RCM_Flag as rf
from RCM.rcm_data import RCM_Data as rd


# from video_writer import *

class Ui_SensorDialog(QWidget):
    # rcm_server = None
    # rcm_client = None
    thread_event = None
    thread_rcm = None
    robot_Motions = {}
    client_Connection_Check = 2

    def __init__(self):
        super().__init__()
        # self.vw = videowriter()
        self.vb = self.initUI()
        self.Motion = None
        self.rcm_server = RCM_Server()
        #self.rcm_client = RCM_Client()
        self.rcm_sql = RCM_Sql()

    def initUI(self):
        # 서버 접속관련 설정 부분 #############################
        print('initUI')
        self.setWindowTitle('Robot Control Manager')
        hbox = QHBoxLayout()
        vb = QVBoxLayout()
        vb.addLayout(self.createInfoGroup())
        vb.addLayout(hbox)

        return vb
        # self.setLayout(vb)
        # self.show()

    def createInfoGroup(self):
        box = QHBoxLayout()
        self.btn = QPushButton('안전위치')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn.clicked.connect(self.set_Robot_Home_Position)
        box.addWidget(self.btn)
        self.btn2 = QPushButton('로봇정지', self)
        self.btn2.clicked.connect(self.set_Robot_Emergency)
        box.addWidget(self.btn2)
        self.btn3 = QPushButton('로봇실행', self)
        self.btn3.clicked.connect(self.control_Recv_From_Nsg)
        box.addWidget(self.btn3)
        # self.btn4 = QPushButton('녹화')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        # self.btn4.clicked.connect(self.camOn)
        # box.addWidget(self.btn4)
        # self.btn5 = QPushButton('정지')
        # self.btn5.clicked.connect(self.camOff)
        # box.addWidget(self.btn5)

        box2 = QHBoxLayout()
        self.btn2_1 = QPushButton('로봇모션')
        self.btn2_1.clicked.connect(self.data_Get_Robot_Motion_Datas_From_Db)
        box2.addWidget(self.btn2_1)
        self.btn2_2 = QPushButton('모션테스트', self)
        self.btn2_2.clicked.connect(self.execute_Robot_Motion_Test)
        box2.addWidget(self.btn2_2)
        self.btn2_3 = QPushButton('고정건모션')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn2_3.clicked.connect(self.data_Get_Fixed_Gun_Motion_Datas_From_Db)   
        box2.addWidget(self.btn2_3)
        self.btn2_4 = QPushButton('모션테스트', self)
        self.btn2_4.clicked.connect(self.execute_Fixed_Gun_Motion_Test)
        box2.addWidget(self.btn2_4)
        self.btn2_5 = QPushButton('고정건')  # 나중에 연결상태표시를 아이콘으로 했으면 함.
        self.btn2_5.clicked.connect(self.set_Fixed_Gun_Status)
        box.addWidget(self.btn2_5)

        self.infomsg = QTextEdit()
        self.infomsg.setFixedHeight(400)
        self.infomsg.setStyleSheet("background-color: black; border: 1px solid gray;")
        self.infomsg.setTextColor(QColor(255, 255, 0))
        self.infomsg.append('Robot Control Manager 실행')

        cbox = QHBoxLayout()
        vbox = QVBoxLayout()
        vbox.addLayout(box)
        vbox.addLayout(box2)
        vbox.addLayout(cbox)
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
            # self.rcm_server.data_Reset()
        else:
            pass

    def set_Robot_Emergency(self):
        if (rf.FLAG_SERVER_OPEN == True and rf.FLAG_SERVER_CLOSED == False):
            self.rcm_server.EMERGENCY()
            self.infomsg.clear()
            self.infomsg.append('명령송신 : 로봇 비상정지')
            rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
            rf.FLAG_AUTO_MODE = False
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
            else:
                rf.FLAG_GUN_SPRAYING_ON = False
                self.infomsg.append('명령송신 : 도장건 꺼짐')
            self.rcm_server.PAINTING_GUN()
        else:
            pass

    def camOn(self):
        # self.vw.working = True
        self.vw.start()

    def camOff(self):
        self.vw.working = False
        self.vw.stop()

    def data_Get_Robot_Motion_Datas_From_Db(self):
        self.infomsg.clear()
        # self.rcm_sql = RCM_Sql()
        sql_List = self.rcm_sql.load_Robot_Motion_Names()
        cnt = 0
        for motion in sql_List:
            cnt += 1
            self.robot_Motions[str(cnt)] = motion
            self.infomsg.append(str(cnt) + '. ' + motion)

    def execute_Robot_Motion_Test(self):
        motion_number, ok = QInputDialog.getText(self, '실행할 모션', '모션 번호:')
        motion_count, ok = QInputDialog.getInt(self, '실행할 모션', '실행 횟수:')
        if ok:
            table_Name = self.robot_Motions[motion_number]
            print("실행할 모션 : ", motion_number, ', ', table_Name)
            print("────────────────────────────────────────────────")
            # rd.rcm_server.EMERGENCY()
            # rd.rcm_server.CLEAR()
            # rcm_sql = RCM_Sql()
            rf.FLAG_SIMULATION = True
            self.rcm_server.product_Name = table_Name
            self.rcm_server.old_Product_Name = table_Name
            self.rcm_server.run_Robot_By_Scheduler_Combined_Data('50')  # rcm 속도변경
            self.rcm_server.repetition = motion_count  # rcm 반복횟수
            rf.FLAG_THREAD_SENDING_STATE = True
            rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = True
            self.infomsg.clear()
            sql_Name = self.rcm_sql.load_Pose_Data_With_Product_Name_From_DB(table_Name)
            self.infomsg.append("실행 중인 모션 : ")
            self.infomsg.append(sql_Name)
        # print("motion", rd.combined_Joint_Angle_Data)

    def control_Recv_From_Nsg(self):
        if (rf.FLAG_RECV_FROM_NSG_STOP == False):
            rf.FLAG_RECV_FROM_NSG_STOP = True
            print("RCM 동작 가능", rf.FLAG_RECV_FROM_NSG_STOP)
            # self.rcm_server.data_Reset()
            # rd.data_Reset_Pose()
            # self.rcm_server.product_Name = ""
            # self.rcm_server.old_Product_Name = ""
        else:
            rf.FLAG_RECV_FROM_NSG_STOP = False
            print("NSG 동작 가능", rf.FLAG_RECV_FROM_NSG_STOP)
            rf.FLAG_SIMULATION = False

    def set_Fixed_Gun_Status(self):
        if (rf.FLAG_SERVER_OPEN == True and rf.FLAG_SERVER_CLOSED == False):
            self.infomsg.clear()
            if (rf.FLAG_GUN_SPRAYING_ON == False):
                rf.FLAG_GUN_SPRAYING_ON = True
                self.infomsg.append('명령송신 : 도장건 켜짐')
            else:
                rf.FLAG_GUN_SPRAYING_ON = False
                self.infomsg.append('명령송신 : 도장건 꺼짐')
            rd.rcm_server.PAINTING_GUN()
        else:
            pass

    def data_Get_Fixed_Gun_Motion_Datas_From_Db(self):
        self.infomsg.clear()
        sql_List = self.rcm_sql.load_Fixgun_Motion_Names()
        cnt = 0
        for motion in sql_List:
            cnt += 1
            rd.fixgun_Motions[str(cnt)] = motion
            self.infomsg.append(str(cnt) + '. ' + motion)

    def execute_Fixed_Gun_Motion_Test(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
        if ok:
            table_Name = rd.fixgun_Motions[text]
            print("실행할 모션 : ", text, ', ', table_Name)
            print("────────────────────────────────────────────────")
            sql_List = eval(self.rcm_sql.load_Fixgun_Motion(table_Name))
            converted_Data = rd.data_Set_Fixgun_Motion_Integer_To_String(sql_List)
            print(converted_Data)
            self.rcm_server.send_To_FIXGUN(converted_Data)

    ### Thread # ====================================================================================================== #
    def run_Rcm_Thread(self):
        self.thread_rcm = threading.Thread(target=self.run_RCM)
        self.thread_rcm.daemon = True
        self.thread_rcm.start()

    def run_RCM(self):
        while (rf.FLAG_PROGRAM_SHUTDOWN == False):
            if (rf.FLAG_DATABASE_IS_ON == False):
                try:
                    # rcm_sql = RCM_Sql()
                    self.rcm_sql.check_Db_On_Sg()
                    self.rcm_sql.check_Db_On_FixGun()
                except:
                    rf.FLAG_DATABASE_IS_ON = False
                    print("Can't connect to database")
            else:
                if (rf.FLAG_CLIENT_CONNECTION == False and rf.FLAG_CLIENT_OPEN == False):  # FIXME : need to open (closed 210209)
                    # self.rcm_client = RCM_Client()
                    #self.rcm_client.run()
                # elif (rf.FLAG_CLIENT_CLOSED == True):
                #     if (self.client_Connection_Check == 1):
                #         print("┌────────────────────────────────────┐")
                #         print("│ RCM is disconnected from panel pc. │")
                #         print("└────────────────────────────────────┘")
                #         print(" > Waiting for connection...", "\n")
                #     rf.FLAG_CLIENT_CLOSED = False
                #     self.rcm_client.stop()
                #     self.rcm_client.clear()
                #     self.rcm_client.run()
                #     rf.FLAG_CLIENT_CONNECTION = False
                #     rf.FLAG_CLIENT_OPEN = True
                # else:
                    if (rf.FLAG_SERVER_OPEN == False and rf.FLAG_SERVER_CLOSED == False):
                        self.rcm_server.server_init()
                        # self.rcm_server = RCM_Server()
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
            #self.rcm_client.stop()
            #self.rcm_client.clear()
            self.rcm_server.stop()
            self.rcm_server.clear()
            rf.FLAG_SERVER_CLOSED = True
            # QCoreApplication.instance().quit()
            # os.system("shutdown -h now")

    def stop_RCM_Thread(self):
        rf.FLAG_PROGRAM_SHUTDOWN = True
        rf.FLAG_THREAD_STOP = True
        # rf.FLAG_SERVER_CLOSED == True
        # rf.FLAG_SERVER_OPEN == False
        rf.FLAG_RECV_FROM_NSG_STOP = True

    def start_RCM_Thread(self):
        rf.FLAG_PROGRAM_SHUTDOWN = False
        rf.FLAG_THREAD_STOP = False
        # rf.FLAG_SERVER_CLOSED == False
        # rf.FLAG_SERVER_OPEN == True
        rf.FLAG_RECV_FROM_NSG_STOP = False

    # @pyqtSlot(str)
    # def rcm_status(self, str):
    #     # self.inform_cnt += 1
    #     # if self.inform_cnt > LINE_MAX:
    #     #     self.infomsg.clear()
    #     #     self.inform_cnt = 0
    #     print("debug : ", str)
    #     self.infomsg.append(str)
# ==================================================================================================================== #

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ui = Ui_SensorDialog()
#     ui.run_Rcm_Thread()
#     sys.exit(app.exec_())