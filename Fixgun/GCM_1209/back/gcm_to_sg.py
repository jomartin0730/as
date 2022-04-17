#import threading
#import time
#import random
#from socket import *
#from gcm_data import GCM_Data as gd
#from gcm_flag import GCM_Flag as gf

class GCM_Client2(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        super(GCM_Client2, self).__init__()
        self._stop = threading.Event()
        self.client_thread = None
        self.recv_thread = None
        self.FLAG_CONNECTION = False
        self.Count = 0
        self.clientSock = None
        self.Stop = False
        self.Num = 0
        self.FLAG_DISCONN = False
        self.str_array = None
        self.exception_Count = 0
        self.noreceive = 0
        # self.product_Name = ""

    def stop(self):
        self._stop.set()

    def clear(self):
        self._stop.clear()

    def run(self):
        self.client_thread = threading.Thread(target=self.client2)
        self.client_thread.daemon = True
        self.client_thread.start()

    def recv2(self):
        print(" > Now listening...", "\n")
        while(gf.FLAG_CLIENT_CLOSED == False):
            try:
                if (gf.FLAG_CLIENT_CLOSED == False and gf.FLAG_SERVER_THREAD_OPEN == True):
                    received_data = self.clientSock.recv(1024).decode("utf-8")
                    if (len(received_data) != 0):
                        self.str_array = received_data
                        print("received data : ", received_data)
                        # try:
                        #     gd.gcm_server.panel_Command[received_data]()
                        # except:
                        #     print("Error is occurred during receive data : ", received_data)
                    else:
                        self.noreceive += 1
                        if (self.noreceive > 10):
                            gf.FLAG_CLIENT_CONNECTION = False
                            gf.FLAG_CLIENT_CLOSED = True
                            gf.FLAG_CLIENT_OPEN = True
                            gf.FLAG_SERVER_THREAD_OPEN = False
                            self.noreceive = 0
                time.sleep(0.5)
            except:
                self.exception_Count += 1
                if (self.exception_Count % 10 == 0):
                    print("Server of SG Server disconnected")
                    self.exception_Count = 0
                gf.FLAG_CLIENT_CONNECTION = False
                gf.FLAG_CLIENT_CLOSED = True
                gf.FLAG_CLIENT_OPEN = True
                gf.FLAG_SERVER_THREAD_OPEN = False

    def client2(self):
        while (gf.FLAG_CLIENT_CLOSED == False):
            try:
                if (gf.FLAG_CLIENT_CONNECTION == False):
                    self.clientSock = socket(AF_INET, SOCK_STREAM)
                    ### Notice # ===================================================================================== #
                    # FIXME : IP address, Port number need to set as things of SG Server.
                    self.clientSock.connect(("192.168.0.103", 9999))
                    # ================================================================================================ #

                    print("┌───────────────────────────────────────┐")
                    print("│ GCM success to connect with SG Server.                                        │")
                    print("└───────────────────────────────────────┘")
                    self.clientSock.send("GCM".encode("utf-8"))

                    gf.FLAG_CLIENT_CONNECTION = True
                    gf.FLAG_CLIENT_OPEN = True
                    gf.FLAG_CLIENT_CLOSED = False
                    gd.client_Connection_Check = 0

                    self.recv_thread = threading.Thread(target=self.recv2)
                    self.recv_thread.daemon = True
                    self.recv_thread.start()
                    gf.FLAG_SERVER_THREAD_OPEN = True

            except:
                self.exception_Count += 1
                if (self.exception_Count % 10 == 0):
                    print("Disconnected from SG Server")
                    self.exception_Count = 0
                gf.FLAG_CLIENT_CONNECTION = False
                gf.FLAG_CLIENT_CLOSED = True
                gf.FLAG_CLIENT_OPEN = True
                gf.FLAG_SERVER_THREAD_OPEN = False
                gd.client_Connection_Check += 1

    # if (received_data == '1'):
    #     gf.FLAG_ENABLE_TO_MOVE_FIXGUN = True
    #     print("Enable to move fixgun")
    # elif (received_data == '2'):
    #     gf.FLAG_ENABLE_TO_MOVE_FIXGUN = False
    #     print("Disable to move fixgun")
    # elif (received_data == 'B'):
    #     print("Emergency stop button is pressed")
    #     gd.gcm_server.EMERGENCY()
    # elif (received_data == 'H'):
    #     gf.FLAG_AUTO_MODE = False
    #     gd.gcm_server.HOME()
    #     print("Abort job and return to home position")
    # elif (received_data == 'O'):
    #     gf.FLAG_AUTO_MODE = True
    #     print("Job start")
    # elif (received_data == 'C'):
    #     gf.FLAG_PROGRAM_SHUTDOWN = True
    #     print("Program shutdowm")











# from gcm_flag import GCM_Flag as gf


# class GCM_To_Sg():
#     def __init__(self):
#         self.product_Name = ""




#     def sg_Server(self):
#         print("SG server thread opened")
#     while (True):
#         if (self.instance_Server.FLAG_SG_SERVER_OPEN == False):
#             self.instance_Server.run()
#         else:
#             self.instance_Server.FLAG_SG_SERVER_OPEN = True
#             self.self.instance_Server.product_Name = self.product_Name
#             #self.ds.partID = self.instance_Server.received_Data
#             # if self.ds.partID != "None" :
#             # self.load_pinfo(self.ds.partID)
#             # print("ds part id ", self.ds.partID)
#         time.sleep(3)
