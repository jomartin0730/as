import threading
import time
from socket import *
from gcm_data import GCM_Data as gd
from gcm_flag import GCM_Flag as gf

class GCM_Client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        super(GCM_Client, self).__init__()
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
        while(gf.FLAG_CLIENT_CLOSED == False):
            try:
                if (gf.FLAG_CLIENT_CLOSED == False and gf.FLAG_SERVER_THREAD_OPEN == True):
                    received_data = self.clientSock.recv(1024).decode("utf-8")
                    if (len(received_data) != 0):
                        self.str_array = received_data
                        print("received data : ", received_data)
                        try:
                            gd.gcm_server.panel_Command[received_data]()
                        except:
                            print("Error is occurred during receive data : ", received_data)
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
                    print("Server of panel pc disconnected")
                    self.exception_Count = 0
                gf.FLAG_CLIENT_CONNECTION = False
                gf.FLAG_CLIENT_CLOSED = True
                gf.FLAG_CLIENT_OPEN = True
                gf.FLAG_SERVER_THREAD_OPEN = False

    def client(self):
        while (gf.FLAG_CLIENT_CLOSED == False):
            try:
                if (gf.FLAG_CLIENT_CONNECTION == False):
                    self.clientSock = socket(AF_INET, SOCK_STREAM)
                    ### Notice # ===================================================================================== #
                    # FIXME : IP address, Port number need to set as things of panel pc.
                    self.clientSock.connect(("192.168.0.104", 9999))
                    # ================================================================================================ #

                    print("┌───────────────────────────────────────┐")
                    print("│ GCM success to connect with panel pc. │")
                    print("└───────────────────────────────────────┘")
                    self.clientSock.send("FIXGUN".encode("utf-8"))

                    gf.FLAG_CLIENT_CONNECTION = True
                    gf.FLAG_CLIENT_OPEN = True
                    gf.FLAG_CLIENT_CLOSED = False
                    gd.client_Connection_Check = 0

                    self.recv_thread = threading.Thread(target=self.recv)
                    self.recv_thread.daemon = True
                    self.recv_thread.start()
                    gf.FLAG_SERVER_THREAD_OPEN = True

            except:
                self.exception_Count += 1
                if (self.exception_Count % 10 == 0):
                    print("Disconnected from panel pc")
                    self.exception_Count = 0
                gf.FLAG_CLIENT_CONNECTION = False
                gf.FLAG_CLIENT_CLOSED = True
                gf.FLAG_CLIENT_OPEN = True
                gf.FLAG_SERVER_THREAD_OPEN = False
                gd.client_Connection_Check += 1