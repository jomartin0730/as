import threading
import time
from socket import *
from RCM.rcm_data import RCM_Data as rd
from RCM.rcm_flag import RCM_Flag as rf

class RCM_Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        super(RCM_Client, self).__init__()
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

    def stop(self):
        self._stop.set()

    def clear(self):
        self._stop.clear()

    def run(self):
        self.client_thread = threading.Thread(target=self.client)
        self.client_thread.daemon = True
        self.client_thread.start()

    def recv(self):
        print(" > Now listening...", "\n")
        while(rf.FLAG_CLIENT_CLOSED == False):
            try:
                if (rf.FLAG_CLIENT_CLOSED == False and rf.FLAG_SERVER_THREAD_OPEN == True):
                    received_data = self.clientSock.recv(1024).decode("utf-8")
                    if (len(received_data) != 0):
                        self.str_array = received_data
                        print("received data : ", received_data)
                        try:
                            rd.rcm_server.panel_Command[received_data]()
                        except:
                            print("Error is occurred during receive data : ", received_data)
                    else:
                        self.noreceive += 1
                        if (self.noreceive > 10):
                            rf.FLAG_CLIENT_CONNECTION = False
                            rf.FLAG_CLIENT_CLOSED = True
                            rf.FLAG_CLIENT_OPEN = True
                            rf.FLAG_SERVER_THREAD_OPEN = False
                            self.noreceive = 0
                time.sleep(0.5)
            except:
                self.exception_Count += 1
                if (self.exception_Count % 10 == 0):
                    print("Server of panel pc disconnected")
                    self.exception_Count = 0
                rf.FLAG_CLIENT_CONNECTION = False
                rf.FLAG_CLIENT_CLOSED = True
                rf.FLAG_CLIENT_OPEN = True
                rf.FLAG_SERVER_THREAD_OPEN = False

    def client(self):
        while (rf.FLAG_CLIENT_CLOSED == False):
            try:
                if (rf.FLAG_CLIENT_CONNECTION == False):
                    self.clientSock = socket(AF_INET, SOCK_STREAM)
                    ### Notice # ===================================================================================== #
                    # FIXME : IP address, Port number need to set as things of panel pc.
                    self.clientSock.connect(("192.168.0.104", 9999))
                    # ================================================================================================ #

                    print("┌───────────────────────────────────────┐")
                    print("│ GCM success to connect with panel pc. │")
                    print("└───────────────────────────────────────┘")
                    self.clientSock.send("FIXGUN".encode("utf-8"))

                    rf.FLAG_CLIENT_CONNECTION = True
                    rf.FLAG_CLIENT_OPEN = True
                    rf.FLAG_CLIENT_CLOSED = False
                    rd.client_Connection_Check = 0

                    self.recv_thread = threading.Thread(target=self.recv)
                    self.recv_thread.daemon = True
                    self.recv_thread.start()
                    rf.FLAG_SERVER_THREAD_OPEN = True
                time.sleep(0.3)
            except:
                self.exception_Count += 1
                if (self.exception_Count % 10 == 0):
                    print("Disconnected from panel pc")
                    self.exception_Count = 0
                rf.FLAG_CLIENT_CONNECTION = False
                rf.FLAG_CLIENT_CLOSED = True
                rf.FLAG_CLIENT_OPEN = True
                rf.FLAG_SERVER_THREAD_OPEN = False
                rd.client_Connection_Check += 1