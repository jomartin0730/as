import time
import threading
import socket
import datetime

from pymysql import NULL
from gcm_sql import *

class GCM_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        super(GCM_Server, self).__init__()
        self._stop = threading.Event()
        self.lock = threading.Lock()  # 스레드락
        self.clients = {}  # 접속된 클라이언트 리스트
        self.client_Count = 0  # client의 수
        self.check_Count = 100
        self.thread_server = None
        self.thread_client_Conn_Check = None
        self.recv_thread = None
        self.gcm_sql = GCM_Sql()

        self.productCode = ""
        self.oldProductCode = ""

        self.host = "192.168.0.102"
        #self.host = "192.168.0.16"
        self.port = 9999
        # self.port = 49153
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(3)
        self.max_bytes = 2048  # 최대 수신 데이터

    def stop(self):
        print("stop")
        self._stop.set()

    def clear(self):
        print("clear")
        self._stop.clear()

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

    def server(self):
        print("┌───────────────────────┐")
        print("│ GCM server is opened. │")
        print("└───────────────────────┘")
        try:
            gf.FLAG_SERVER_OPEN = True
            self.accept_Client()
        except Exception as e:
            print("Server has an error : ", e)
            gf.FLAG_SERVER_EMS_MSG = True
            self.send_To_All('D')
            gf.FLAG_SERVER_CLOSED = True
            gf.FLAG_SERVER_OPEN = False
            gf.FLAG_SERVER_THREAD_OPEN = False

    def accept_Client(self):
        try:
            while (gf.FLAG_SERVER_CLOSED == False):
                client_socket, addr = self.server_socket.accept()
                print('accept', addr)
                # 최초 접속시 XAVIER OR ROBOT 이라는 디바이스 명을 받아 저장하여 클라이언트 관리
                if addr[0] == '192.168.0.104':
                    deviceName = "FIXGUN"
                elif addr[0] == '192.168.0.101':
                    deviceName = "SG2"
                else:
                    deviceName = client_socket.recv(1024).decode("utf-8")
                # 클라이언트 정보 저장
                self.add_Client(deviceName, client_socket, addr)

                # 각 클라이언트의 디바이스 명으로 각각의 recv 스레드 생성
                self.recv_thread = threading.Thread(target=self.recv, args=(client_socket, addr, deviceName))
                self.recv_thread.daemon = True
                self.recv_thread.start()
                gf.FLAG_SEND_ANGLE_DATA_TO_ROBOT = False
        except Exception as e:
            print("accept_Client : ", e)

    # 클라이언트 생존 여부 확인
    def client_Conn_Check(self):
        check_Count = 0
        while (gf.FLAG_SERVER_CLOSED == False):
            devices = self.clients.keys()
            #try:
            if devices:
                for device in devices:
                    if device == 'FIXGUN' and 'FIXGUN' not in gd.data_Tcp_Clinet_List:
                        gd.data_Tcp_Clinet_List[device] = self.client_Count
                        self.client_Count += 1
                        #sql_List = self.gcm_sql.send_Product_Name() #sg_log 데이터 보냄
                        # if sql_List != gd.old_sql_List:
                        #     if len(sql_List) < 12:
                        #         sql_List_ = sql_List[:3] + '-' + sql_List[3:5] + "-" + sql_List[5:]
                        #         print("send product name : ", sql_List_)
                        #         gd.gcm_server.send_To_FIXGUN(sql_List_)
                        #     else:
                        #         print("send product name : ", sql_List)
                        #         gd.gcm_server.send_To_FIXGUN(sql_List)
                        # gd.old_sql_List = sql_List
                    if device == 'SG2' and 'SG2' not in gd.data_Tcp_Clinet_List:
                        gd.data_Tcp_Clinet_List[device] = self.client_Count
                        self.client_Count += 1

            if check_Count == self.check_Count:
                if len(gd.data_Tcp_Clinet_List) != 0:
                    print("Connect Client : ", gd.data_Tcp_Clinet_List)
                else:
                    print("Not Connected")
                check_Count = 0
            check_Count += 1


            # except Exception as e:
            #     print("client_Conn_Check : ", e)
            time.sleep(0.1)

    def recv(self, client, addr, deviceName):
        while (gf.FLAG_SERVER_CLOSED == False):
            try:
                recv_data = client.recv(self.max_bytes)

        ### DISCONNECTION # ========================================================================================== #
                # 데이터 길이 및 유무 확인 후 없다면 연결 종료
                if not recv_data and deviceName == 'FIXGUN':
                    self.data_Reset()
                    print("Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    break

                if not recv_data and deviceName == 'SG2':
                    self.data_Reset()
                    print("Disconnected by - ", deviceName, ':', addr[0], ':', addr[1])
                    self.del_Client(deviceName)
                    client.close()
                    break

        ### CONNECTION # ================================================================================================= #
                if deviceName == 'FIXGUN':
                    buffer = recv_data.decode()
                    print("recv buffer : ", buffer)
                    fixGunMotion = buffer #모션 저장 코드
                    converted_Data = gd.convert_Fixgun_Motion_From_Panel_PC(fixGunMotion)
                    print("recv data : ", converted_Data)
                    #self.gcm_sql.save_Pose_Data_To_DB(self.gcm_sql.send_Product_Name(), converted_Data)#DB 모션 저장 코드
                    self.gcm_sql.save_Pose_Data_To_DB('Change', converted_Data)#DB 모션 저장 코드

                elif deviceName == 'SG2':
                    self.productCode = recv_data.decode()
                    print("recv from nsg : ", self.productCode)
                    if (self.oldProdcutCode != self.productCode):
                        sql_List = eval(self.gcm_sql.load_Fixgun_Motion(self.productCode))
                        converted_Data = gd.data_Set_Fixgun_Motion_Integer_To_String(sql_List)
                        print(converted_Data)
                        #time.sleep(20)
                        gd.gcm_server.send_To_FIXGUN(converted_Data)
                    else:
                        pass
                    self.oldProdcutCode = self.productCode
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

    def send_To_FIXGUN(self, datas):
        if 'FIXGUN' in self.clients:
            client = self.clients.get('FIXGUN')
            client.sendall(bytes(datas, encoding='utf8'))
        else:
            print("Not Connect FIXGUN")

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
            del gd.data_Tcp_Clinet_List[deviceName]
            self.client_Count -= 1
            self.lock.release()
        except Exception as e:
            print("del_Client error", e)
