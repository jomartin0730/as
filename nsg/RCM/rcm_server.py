from PyQt5.QtCore import Qt, pyqtSignal, QObject
import time
import threading
import socket
import datetime
from RCM.rcm_kawasaki_script import *
from RCM.rcm_sql import *

class RcmServerSignal(QObject):
    server_signal = pyqtSignal(str)

class RCM_Server(threading.Thread):
    def __init__(self):
        super(RCM_Server, self).__init__()
        self.rcm_server_signal = RcmServerSignal()
        self._stop = threading.Event()
        self.lock = threading.Lock()  # 스레드락
        self.clients = {}  # 접속된 클라이언트 리스트
        self.client_Count = 0  # client의 수       
        self.sended_Data_Number = 0
        self.motionRowNumber = 0
        self.check_Count = 100
        self.send_Waiting_Order = None
        self.thread_server = None
        self.thread_client_Conn_Check = None
        self.recv_thread = None
        self.product_Name = ""
        self.end_State = ""
        self.product_Static_Speed = "6.5"
        self.robot_Log_Count = 3 # count = 3 정상, count = 2 비정상, count = 1
        self.nsgData = ""    
        self.old_Process_Value = 0
        self.old_Product_Name = ""
        self.old_Product_Velocity = 0
        self.old_Moving_State = 0
        self.startTime = 0
        self.endTime = 0
        self.rcmStartTime = 0

        # self.partID = ""
        # self.p_value = ""
        # self.stepV = 0
        # self.start_state = 0
        # self.end_state = 0
        # self.speedV = 0
        # self.motion_repeat = 0
        #self.motion = Motion()

        self.paint_Count = 0
        self.repeat_Count = 0
        self.repetition = 1
        self.new_Product_Count = 0
        self.first_Product = 0
        self.rcm_sql = RCM_Sql()

    def server_init(self):
        # Server Init###########################################################
        self.host = self.get_Ip()
        self.port = 9999
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        self.max_bytes = 2048  # 최대 수신 데이터
        if(rf.FLAG_RECV_FROM_NSG_STOP == True):
            self.server_socket.close()
            print("RCM Server Closed")
        #######################################################################

    def stop(self):
        print("stop")
        self._stop.set()

    def get_Ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.0.1', 0))
        ip = s.getsockname()[0]
        rd.curr_Pc_Ip_Adress = ip
        if (rd.curr_Pc_Ip_Adress == rd.pc_One_Ip):
            self.rcm_sql.table = 'motion_data'
            self.rcm_sql.log_Table = 'Robot_log'
        else:
            self.rcm_sql.table = 'motion_data2'
            self.rcm_sql.log_Table = 'Robot_log2'
        return ip

    def run_Thread(self):
        # 서버 스레드 스타트
        self.thread_server = threading.Thread(target=self.server)
        self.thread_server.daemon = True
        self.thread_server.start()
        # 클라이언트 접속 여부 확인 스레드
        self.thread_client_Conn_Check = threading.Thread(target=self.client_Conn_Check)
        self.thread_client_Conn_Check.daemon = True
        self.thread_client_Conn_Check.start()
        time.sleep(0.1)
        # robot에 대기명령 내리는 스레드
        self.send_Waiting_Order = threading.Thread(target=self.send_Waiting_Order_To_Robot)
        self.send_Waiting_Order.daemon = True
        self.send_Waiting_Order.start()

    def server(self):
            print("┌───────────────────────┐")
            print("│ RCM server is opened. │")
            print("└───────────────────────┘")
            if(rf.FLAG_SERVER_CLOSED == False):
                try:
                    rf.FLAG_SERVER_OPEN = True
                    self.accept_Client()
                except Exception as e:
                    print("Server has an error : ", e)
                    rf.FLAG_SERVER_CLOSED = True
                    rf.FLAG_SERVER_OPEN = False
            else:
                print("Server Close")

    def accept_Client(self):
        try:
            while (rf.FLAG_SERVER_CLOSED == False):
                client_socket, addr = self.server_socket.accept()
                print('accept', addr)
                deviceName = client_socket.recv(1024).decode("utf-8")
                self.add_Client(deviceName, client_socket, addr)

                # 각 클라이언트의 디바이스 명으로 각각의 recv 스레드 생성
                self.recv_thread = threading.Thread(target=self.recv, args=(client_socket, addr, deviceName))
                self.recv_thread.daemon = True
                self.recv_thread.start()
                rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
        except Exception as e:
            print("accept_Client : ", e)

    # 클라이언트 생존 여부 확인
    def client_Conn_Check(self):
        check_Count = 0
        while (rf.FLAG_SERVER_CLOSED == False):
            devices = self.clients.keys()
            try:
                if devices:
                    for device in devices:
                        if device == "ROBOT" and "ROBOT" not in rd.clientList:
                            rd.clientList[device] = self.client_Count
                            self.client_Count += 1

                if check_Count == self.check_Count:
                    if len(rd.clientList) != 0:
                        print("Connect Client : ", rd.clientList)
                        rf.FLAG_ROBOT_START = True
                    else:
                        print("Not Connected")
                    check_Count = 0
                check_Count += 1

            except Exception as e:
                print("client_Conn_Check : ", e)
            time.sleep(0.1)

    def send_Waiting_Order_To_Robot(self):
        print(" > Sending standby command to Kawasaki is started.\n")
        while (rf.FLAG_SERVER_CLOSED == False):
            try:
                if (rf.FLAG_THREAD_SENDING_STATE == False):
                    if (rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT == False):
                        if 'ROBOT' in rd.clientList:
                            self.STANDBY()
                    time.sleep(0.2)
                else:
                    if (rf.FLAG_START_SENDING_JOINT_ANGLE_DATA == True):
                        while (self.repeat_Count <= self.repetition):
                            if (rf.FLAG_HOME == True):
                                rf.FLAG_HOME = False
                                break
                            elif (self.repeat_Count == self.repetition):
                                rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
                                rf.FLAG_THREAD_SENDING_STATE = False
                                rf.FLAG_MOTION_EXECUTED = False
                                rf.FLAG_SIMULATION = False
                                self.repeat_Count = 0
                                break
                            elif (self.sended_Data_Number > (self.motionRowNumber - 1) and rf.FLAG_ROBOT_MOTION_DONE == True):
                                rf.FLAG_ROBOT_MOTION_DONE = False
                                self.robot_Log_Count = 3
                                self.save_Log_Data_Of_Robot(self.product_Name, self.product_Static_Speed, 'O')
                                self.sended_Data_Number = 0
                                self.repeat_Count += 1
                                rf.FLAG_SIMULATION = False
                            elif (self.sended_Data_Number > (self.motionRowNumber - 1) and rf.FLAG_ROBOT_MOTION_DONE == False):
                                pass
                            else:
                                self.JMOVE(rd.combined_Joint_Angle_Data[self.sended_Data_Number])
                                self.sended_Data_Number += 1
                            time.sleep(0.03) # Speed that send data to robot.
            except Exception as e:
                rf.FLAG_THREAD_SENDING_STATE = False
                rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = True
                rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
                rf.FLAG_ROBOT_DISCONNECTED = True
                print("Disconnected", e)

    def recv_From_Nsg(self, str_data, start_flag):
        if(rf.FLAG_RECV_FROM_NSG_STOP == False):
            print("recv str_data : ", str_data)
            self.nsgData = str_data
            splitedNsgData = self.nsgData.split(':')
            product_Name_ = splitedNsgData[0]
            if (len(product_Name_) == 0):
                product_Name_ = "None"
            process_Status = splitedNsgData[1]
            moving_State = splitedNsgData[2]
            start_State = splitedNsgData[3]
            self.end_State = splitedNsgData[4]
            product_Static_Speed = splitedNsgData[5]
            repeat_State = splitedNsgData[6]
            # product_Name_        = self.partID
            # process_Status       = self.p_value
            # moving_State         = self.stepV
            # start_State          = self.start_state
            # self.end_State       = self.end_state
            # product_Static_Speed = self.speedV
            # repeat_State         = self.motion_repeat
            #if (rf.FLAG_AUTO_MODE == True):
            if (process_Status == 'S'):
                rf.FLAG_CUT_RECEIVE = True
                print("Conveyor belt stopped.")
                self.old_Product_Name = "STOP"
                rf.FLAG_MOTION_EXECUTED = False
                rf.FLAG_HOME = True
                rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
                rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = False
                rf.FLAG_THREAD_SENDING_STATE = False
                # self.new_Product_Count = 0
                self.sended_Data_Number = 0
                self.repeat_Count = 0
                self.HOME()

            if (repeat_State == '0'):
                self.repetition = 1
            else:
                self.repetition = int(repeat_State)

            if (rf.FLAG_CUT_RECEIVE == False):
                if (rf.FLAG_START_SENDING_JOINT_ANGLE_DATA == False):
                    if (product_Name_ == "None"):
                        product_Name = product_Name_
                    elif len(product_Name_) < 12:
                        product_Name = product_Name_[:3] + '-' + product_Name_[3:5] + "-" + product_Name_[5:]
                    else:
                        product_Name = product_Name_
                    
                    if self.old_Product_Name != product_Name:
                        ### Leave log when robot didn't complete one's motion # ========================== #
                        if (self.robot_Log_Count == 2):
                            self.save_Log_Data_Of_Robot(self.old_Product_Name, self.old_Product_Velocity, 'X')
                        # ================================================================================ #
                        self.robot_Log_Count = 1
                        self.new_Product_Count = 0
                        self.product_Name = product_Name
                        print("\n===================================")
                        print("New product : ", self.product_Name)
                        print("===================================\n")
                        rf.FLAG_FIRST_MOTION = True
                        self.run_Robot_By_Scheduler_Combined_Data(product_Static_Speed)

                    if process_Status == 'P':
                        if (self.first_Product == 0):
                            pass
                        else:
                            self.robot_Log_Count = 1
                            print("\n===================================")
                            print("Recognized product : ", self.product_Name)
                            print("===================================\n")
                            rf.FLAG_FIRST_MOTION = False
                            self.run_Robot_By_Scheduler_Combined_Data(product_Static_Speed)

                    elif process_Status == 'R':
                        
                        if (product_Static_Speed != self.product_Static_Speed):
                            ### Leave log when robot didn't complete one's motion # ====================== #
                            if (self.robot_Log_Count == 2):
                                self.save_Log_Data_Of_Robot(self.old_Product_Name, self.old_Product_Velocity, 'X')
                            # ============================================================================ #

                            self.robot_Log_Count = 1
                            self.product_Name = product_Name
                            self.data_Reset()
                            # self.new_Product_Count = 0
                            # rf.FLAG_FIRST_MOTION = True
                            self.run_Robot_By_Scheduler_Combined_Data(product_Static_Speed)
                        else:
                            self.robot_Log_Count = 1
                            if (rf.FLAG_FIRST_MOTION == False):
                                pass
                        self.product_Static_Speed = product_Static_Speed

                    if self.old_Moving_State != moving_State:
                        if moving_State == start_State:
                            #print("start_flag1 :", start_flag)
                            self.rcmStartTime = time.time()
                            if start_flag == True:
                                #print("start_flag2 :", start_flag)
                                if (rf.FLAG_FIRST_MOTION == False):
                                    print("===================================")
                                    print("Robot executed")
                                    print("===================================\n")
                                self.robot_Log_Count = 2

                                if (self.new_Product_Count == 0):
                                    if (rf.FLAG_FIRST_MOTION == True):
                                        self.new_Product_Count = 0
                                    else:
                                        rf.FLAG_MOTION_EXECUTED = True
                                        rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
                                        rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = True
                                        rf.FLAG_THREAD_SENDING_STATE = True
                                        self.new_Product_Count += 1
                                else:
                                    rf.FLAG_MOTION_EXECUTED = True
                                    rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
                                    rf.FLAG_START_SENDING_JOINT_ANGLE_DATA = True
                                    rf.FLAG_THREAD_SENDING_STATE = True
                                    self.new_Product_Count += 1
                    self.old_Product_Name = product_Name
                    self.old_Moving_State = moving_State
                    self.old_Product_Velocity = product_Static_Speed

    def recv(self, client, addr, deviceName):
        while (rf.FLAG_SERVER_CLOSED == False):
            try:
                recv_data = client.recv(self.max_bytes)

        ### DISCONNECTION # ========================================================================================== #
                if rf.FLAG_ROBOT_DISCONNECTED == True and deviceName == 'ROBOT':
                    rf.FLAG_ROBOT_DISCONNECTED = False
                    rf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = True
                    self.old_Product_Name = ""
                    self.old_Process_Value = 0
                    self.product_Static_Speed = "6.5"
                    self.data_Reset()
                    print("Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    break

        ### ROBOT # ================================================================================================== #
                if deviceName == 'ROBOT':
                    buffer = recv_data.decode()
                    if (len(buffer) == 0):
                        pass
                    else:
                        print("Received data from ROBOT")
                        print(" >", buffer)
                        if (buffer == '1'):
                            rf.FLAG_FIRST_MOTION = False
                            self.new_Product_Count += 1
                            print("first pass !!\n")
                        else:
                            self.endTime = time.time()
                            if (rf.FLAG_RECV_FROM_NSG_STOP == False): # 로봇 자동 동작
                                #print("a",f"{self.endTime - self.startTime:.5f} sec")
                                if (rf.FLAG_SIMULATION == True):
                                    self.rcm_server_signal.server_signal.emit("Manual Cycle Time : " + f"{self.endTime - rd.rcmStartTime:.5f} Sec")
                                else:
                                    self.rcm_server_signal.server_signal.emit("Auto Cycle Time : " + f"{self.endTime - self.rcmStartTime:.5f} Sec")
                            else :                                   #로봇 수동 동작
                                #print("b", f"{self.endTime - rd.rcmStartTime:.5f} sec")
                                self.rcm_server_signal.server_signal.emit("Manual Cycle Time : " + f"{self.endTime - rd.rcmStartTime:.5f} Sec")
                            rf.FLAG_ROBOT_MOTION_DONE = True
                            self.first_Product += 1
                            if (self.new_Product_Count > 0):
                                rf.FLAG_MOTION_EXECUTED = False

        ### NONAME # ================================================================================================== #
                else:
                    buffer = recv_data.decode()
                    print("Unknown Device Name Read : {}".format(buffer))
                    print("Unknown Device Name Disconnected by - ", addr[0], ':', addr[1])
                    client.close()
                    break

            except Exception as e:
                print("Error occurred during reception : {}".format(e))
                client.close()
                self.del_Client(deviceName)
                break

    def save_Log_Data_Of_Robot(self, product_Name, product_Static_Speed, painting):
        datetime_ = str(datetime.datetime.now())
        splited_datetime = datetime_.split(' ')
        _date = splited_datetime[0]
        _time = splited_datetime[1]
        self.rcm_sql.save_Log_Data_To_DB(_date, _time, product_Name, product_Static_Speed, painting)

    def run_Robot_By_Scheduler_Combined_Data(self, speed):
        self.data_Reset()
        rd.sql_Datas = self.rcm_sql.load_Robot_Motion_Names()
        if (self.product_Name in rd.sql_Datas):
            loaded_Motion_Data = eval(self.rcm_sql.load_Pose_Data_With_Appearance_Rate_From_DB(self.product_Name))[1]
            self.data_Load_Joint_Angle_List(loaded_Motion_Data, speed)
        else:
            print("There is no motion in database\nExecute default motion.\n")
            loaded_Motion_Data = eval(self.rcm_sql.load_Pose_Data_With_Appearance_Rate_From_DB("DEFAULT"))[1]
            self.data_Load_Joint_Angle_List(loaded_Motion_Data, speed)

    def data_Load_Joint_Angle_List(self, loaded_Motion_Data, received_Speed):
        # ===================================================================================== #
        # NOTE : 퍼시스 안성공장 1호기 로봇 엔드 체결이 4˚가량 돌아가 있어 이를 보정해주기 위한 코드
        # joint6_Revising = False
        # if (rd.curr_Pc_Ip_Adress == rd.pc_One_Ip):
        #     joint6_Revising = True

        for joint_Angle in loaded_Motion_Data:
            # if (joint6_Revising):
            #     joint_Angle[8] = round(joint_Angle[8] - 4.0, 3)
        # ===================================================================================== #

            rd.drawRobotPoseList.append(joint_Angle[2:8])
            ### mm/s # =============================================================================================== #
            speed_ = joint_Angle[8] - float(joint_Angle[8] * (float(received_Speed) / 7.0)) # 7 > 9
            speed = round((joint_Angle[8] + speed_), 1)
            #print("received_Speed : ", received_Speed)
            #print("speed : ", speed)
            # ======================================================================================================== #

            rd.drawRobotSpeedList.append(speed)
            try:
                rd.drawGripperList.append(joint_Angle[12])
            except:
                length = len(loaded_Motion_Data)
                if self.paint_Count < length - 1:
                    rd.drawGripperList.append('1')
                elif self.paint_Count == length - 1:
                    rd.drawGripperList.append('0')
                    self.paint_Count = 0
                self.paint_Count += 1
        way_To_Robot_Move = loaded_Motion_Data[0][1]
        rd.ghost_Robot_Angle_List = rd.data_Calculate_Angle_To_Kawasaki_Protocol(rd.drawRobotPoseList)
        speed = rd.drawRobotSpeedList
        gripper = rd.drawGripperList
        self.motionRowNumber = len(rd.ghost_Robot_Angle_List)
        try:
            rd.data_Set_Combine_Angle_Data(self.motionRowNumber, way_To_Robot_Move, rd.ghost_Robot_Angle_List, gripper, speed)
            if (rf.FLAG_SIMULATION == False):
                if (self.new_Product_Count == 0 and rf.FLAG_FIRST_MOTION == True):
                    length = len(rd.combined_Joint_Angle_Data)
                    self.JMOVE(rd.combined_Joint_Angle_Data[length - 1])
        except:
            self.Exception()

    def Exception(self):
        print("Receiving error is occurred\nExecute default motion.\n")
        self.data_Reset()
        rd.sql_Datas = self.rcm_sql.load_Pose_Data_Names()
        loaded_Motion_Data = eval(self.rcm_sql.load_Pose_Data_With_Appearance_Rate_From_DB("DEFAULT"))[1]
        self.data_Load_Joint_Angle_List(loaded_Motion_Data, '7.0')

    def data_Reset(self):
        rd.drawRobotPoseList = []
        rd.drawRobotSpeedList = []
        rd.drawGripperList = []
        rd.ghost_Robot_Angle_List = []
        rd.combined_Joint_Angle_Data = []

    # 전 클라이언트에게 데이터 순차 전송
    def send_To_All(self, data):
        if len(self.clients) != 0 :
            for client in self.clients.values():
                client.sendall(bytes(data, encoding='utf8'))

    # 로봇에게만 데이터 전송
    def send_To_Robot(self, datas):
        if "ROBOT" in self.clients:
            client = self.clients.get("ROBOT")
            client.sendall(bytes(datas, encoding='utf8'))
        else:
            print("Not Connect ROBOT")

    # 클라이언트 추가
    def add_Client(self, deviceName, client, addr):
        self.lock.acquire()
        self.clients[deviceName] = (client)
        self.lock.release()
        print("Join Client : ", deviceName)

    # 클라이언트 삭제
    def del_Client(self, deviceName):
        try:
            self.lock.acquire()
            del self.clients[deviceName]
            del rd.clientList[deviceName]
            self.client_Count -= 1
            self.lock.release()
        except Exception as e:
            print("del_Client error", e)

### Kawasaki command # =============================================================================================== #
    def STANDBY(self):
        script = kawasaki_Script()
        script.STANDBY()
        # print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
        self.send_To_Robot(script.command_Line_Kawasaki)
    def JMOVE(self, angle_Data):
        script = kawasaki_Script()
        script.JMOVE(angle_Data)
        print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
        self.send_To_Robot(script.command_Line_Kawasaki)

    def EMERGENCY(self):
        script = kawasaki_Script()
        script.EMERGENCY()
        print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
        self.send_To_Robot(script.command_Line_Kawasaki)

    def HOME(self):
        script = kawasaki_Script()
        script.HOME()
        print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
        self.send_To_Robot(script.command_Line_Kawasaki)

    def PAINTING_GUN(self):
        script = kawasaki_Script()
        script.PAINTING_GUN()
        print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
        self.send_To_Robot(script.command_Line_Kawasaki)



    # def START_SENDING(self):
    #     script = kawasaki_Script()
    #     script.START_SENDING()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def CLEAR(self):
    #     script = kawasaki_Script()
    #     script.CLEAR()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def EXECUTE(self):
    #     script = kawasaki_Script()
    #     script.EXECUTE()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def SENDING_FINISHED(self):
    #     script = kawasaki_Script()
    #     script.SENDING_FINISHED()
    #     print("Data that MAVIZ sended : ", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def SPEEDUP(self):
    #     script = kawasaki_Script()
    #     script.SPEEDUP()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def NORMALSPEED(self):
    #     script = kawasaki_Script()
    #     script.NORMALSPEED()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # def SPEEDDOWN(self):
    #     script = kawasaki_Script()
    #     script.SPEEDDOWN()
    #     print("Data that MAVIZ sended :", script.command_Line_Kawasaki)
    #     self.send_To_Robot(script.command_Line_Kawasaki)

    # ================================================================================================================ #