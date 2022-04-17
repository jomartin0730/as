import os
import cv2
import bpy
import math
import time
import socket
import threading
import random
import numpy as np

from bl_op_sql import *
from bl_op_kawasaki import *
from bl_op_data import Bl_Op_Data as bod
from bl_op_flag import Bl_Op_Flag as bof
from bl_ui_draw_pose import Bl_Ui_Draw_Pose as budp
from bl_op_pcm import *

def URxMoveToPoseOperator(code, cmd1 = 0, cmd2 = 0, cmd3 = 0):
    if(code == 0):
        print("debug : URxMoveToPoseOperator code : 0 , ")

    elif(code == 1):
        print("debug : URxMoveToPoseOperator code : 1 , ")

    elif (code == 2):
        print("debug : URxMoveToPoseOperator code : 2 , ")

    return {'FINISHED'}

class Bl_Maviz_Server():

    def __init__(self):
        self.lock = threading.Lock()  # 스레드락
        self.clients = {}  # 접속된 클라이언트 리스트
        self.client_Count = 0  # client의 수
        self.check_Count = 100
        self.host = self.get_Ip()
        # bod.data_Info_Pc_One_Ip = self.host
        self.port = 9999
        self.server_socket = None
        self.max_bytes = 2048  # 최대 수신 데이터
        self.sended_Data_Number = 0
        self.product_Name = ""
        bod.bl_op_sql = Bl_Op_Sql()
        bod.bl_op_sql.load_Pose_Data_Names()

    def get_Ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.0.1', 0))
        ip = s.getsockname()[0]
        bod.data_Info_Curr_Pc_Ip_Adress = ip
        try:
            if (ip == bod.data_Info_Pc_One_Ip):
                bod.data_Pc_Point_Cloud_Edge_Restrict_Value[ip] = bod.data_Draw_Restrict_Value[0]
                if (bof.FLAG_SQL_CONNECTION_ERROR == False):
                    bod.bl_op_sql.table = "motion_data"
            else:
                bod.data_Pc_Point_Cloud_Edge_Restrict_Value[ip] = bod.data_Draw_Restrict_Value[1]
                if (bof.FLAG_SQL_CONNECTION_ERROR == False):
                    bod.bl_op_sql.table = "motion_data2"
        except:
            pass

        return ip

    def init_Server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        self.server_socket.settimeout(2)
        self.max_bytes = 2048  # 최대 수신 데이터

    def deinit_Server(self):
        self.server_socket = None
        bod.bl_op_robot = None

    def close_Server(self):
        self.deinit_Server()

    def run_Server(self):
        self.init_Server()
        bod.bl_op_robot = robot_Controller()

        # 서버 스레드 스타트
        thread_server = threading.Thread(target=self.server)
        thread_server.daemon = True
        thread_server.start()
        # 클라이언트 접속 여부 확인 스레드
        thread_client_Conn_Check = threading.Thread(target=self.client_Conn_Check)
        thread_client_Conn_Check.daemon = True
        thread_client_Conn_Check.start()

    def server(self):
        print("Server Started (IP :", str(self.host) +", PORT :", str(self.port) + ")\n")
        try:
            self.accept_Client()
        except Exception as e:
            print("Server has an error : ", e)

    def accept_Client(self):
        try:
            while (bof.FLAG_SERVER_OPENED):
                try:
                    client_socket, addr = self.server_socket.accept()
                    print('accept', addr)
                except socket.timeout :
                    continue
                # 최초 접속시 XAVIER OR ROBOT 이라는 디바이스 명을 받아 저장하여 클라이언트 관리
                deviceName = client_socket.recv(1024).decode("utf-8")

                # 클라이언트 정보 저장
                self.add_Client(deviceName, client_socket, addr)

                # 각 클라이언트의 디바이스 명으로 각각의 recv 스레드 생성
                recv_thread = threading.Thread(target=self.recv, args=(client_socket, addr, deviceName))
                recv_thread.daemon = True
                recv_thread.start()
                bof.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
        except Exception as e:
            print("accept_Client : ", e)

        time.sleep(1)
        print("  > Server closed")

    # 클라이언트 생존 여부 확인
    def client_Conn_Check(self):
        check_Count = 0
        while (bof.FLAG_SERVER_OPENED):
            devices = self.clients.keys()
            try:
                if devices:
                    for device in devices:
                        if device == "ROBOT" and "ROBOT" not in bod.data_Tcp_Clinet_List:
                            bod.data_Tcp_Clinet_List[device] = self.client_Count
                            self.client_Count += 1
                            # self.START_SENDING()
                        if device == "MMD" and "MMD" not in bod.data_Tcp_Clinet_List:
                            bod.data_Tcp_Clinet_List[device] = self.client_Count
                            self.client_Count += 1

                if check_Count == self.check_Count:
                    if len(bod.data_Tcp_Clinet_List) != 0:
                        print("Connected Client : ", bod.data_Tcp_Clinet_List)
                    else:
                        print("Not Connected")
                    check_Count = 0
                check_Count += 1
            except Exception as e:
                print("client_Conn_Check : ", e)
            time.sleep(0.1)

    def recv(self, client, addr, deviceName):
        while (bof.FLAG_SERVER_OPENED):
            try:
                try:
                    recv_data = client.recv(self.max_bytes)
                except socket.timeout :
                    continue
                length = len(recv_data)

                # 데이터 길이 및 유무 확인 후 없다면 연결 종료
                if not recv_data and deviceName == 'MMD':
                    print("Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    bod.old_Product_Name = ""
                    bod.old_Process_Value = 0
                    break

                if bof.FLAG_ROBOT_DISCONNECTED == True and deviceName == 'ROBOT':
                    bof.FLAG_ROBOT_DISCONNECTED = False
                    bof.FLAG_SEND_ANGLE_DATA_TO_ROBOT = True
                    print("  > Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    break

                elif deviceName == 'MMD': # MMD = Magenta Motion Detector
                    if (bof.FLAG_OP_MODE_AUTO == True):
                        buffer = recv_data.decode()

                    if (len(buffer) == 0):
                        pass
                    else:
                        splited_Received_Data = buffer.split(':')
                        bod.data_Pc_Point_Cloud_Name = splited_Received_Data[0]
                        process_Value = splited_Received_Data[1]
                        process_State = splited_Received_Data[2]
                        product_Name_ = splited_Received_Data[3]

                        if (bof.FLAG_EMERGENCY == True):
                            pass

                        elif (process_State == 'S'):
                            print("Conveyor belt stopped.")

                        else:
                            if (bof.FLAG_START_SENDING_JOINT_ANGLE_DATA == False):
                                if len(product_Name_) < 12:
                                    product_Name = product_Name_[:3] + '-' + product_Name_[3:5] + "-" + product_Name_[5:]
                                else:
                                    product_Name = product_Name_

                                if bod.old_Product_Name != product_Name:
                                    self.product_Name = product_Name
                                    bod.scheduler.append(self.product_Name)
                                    print("New product : ", self.product_Name)
                                    print("schedule N : ", bod.scheduler)

                                if process_State == 'P':
                                    pass
                                elif process_State == 'R':
                                    print("Repeat motion")

                                if bod.old_Process_Value != process_Value:
                                    if process_Value == '2' and bof.FLAG_RECV_OK == True:
                                        bod.bl_op_server.EXECUTE()
                                        if len(bod.scheduler) != 0:
                                            bod.scheduler.pop(0)
                                        bof.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False

                                bod.old_Product_Name = product_Name
                                bod.old_Process_Value = process_Value

                # 디바이스 명이 ROBOT 일 경우 받은 데이터 처리
                elif deviceName == 'ROBOT':
                    buffer = recv_data.decode()
                    if (len(buffer) == 0):
                        pass
                    else:
                        print("Received data from ROBOT")
                        print(" >", buffer)
                        if (buffer == '1'):
                            bof.FLAG_FIRST_MOTION = False
                            print("first pass !!\n")
                        else:
                            bof.FLAG_ROBOT_MOTION_DONE = True
                            # if (self.new_Product_Count > 0):
                            #     bof.FLAG_MOTION_EXECUTED = False

                # 디바이스 명 없이 접속
                else:
                    buffer = recv_data.decode()
                    print("Unkown Device Name Read : {}".format(buffer))
                    print("Unkown Device Name Disconnected by - ", addr[0], ':', addr[1])
                    client.close()
                    break

            except Exception as e:
                print("Error occurred during reception : {}".format(e))
                client.close()
                self.del_Client(deviceName)
                break

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
            del bod.data_Tcp_Clinet_List[deviceName]
            self.client_Count -= 1
            self.lock.release()
        except Exception as e:
            print("del_Client error", e)
# ==================================================================================================================== #

bod.bl_op_server = Bl_Maviz_Server()
bod.bl_data_robot = robot_Data()