from threading import *
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QImage
import numpy as np
import cv2
import datetime
import os

class Signal(QObject):
    recv_signal = pyqtSignal(np.ndarray)
    recv_signalb = pyqtSignal(np.ndarray)
    send_detect_data = pyqtSignal(str, str,str)
    disconn_signal = pyqtSignal()
    send_state_signal = pyqtSignal(str,str)

class ClientSocket:
    fileCounter = 0

    def __init__(self, parent):
        print('ClientSocket int')
        self.parent = parent
        self.recv = Signal()
        self.disconn = Signal()

        self.bConnect = False
        #self.bMode = False
        self.bMode = "ColorA"
        #self.create_folder(PATH)
        self.Img_Write_Flag = False
        self.path = ""
        self.product_Name = ""

    def __del__(self):
        self.stop()

    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)

        try:
            self.client.connect((ip, port))
        except Exception as e:
            print('Connect Error : ', e)
            return False
        else:
            self.bConnect = True
            self.t = Thread(target=self.receive, args=(self.client,))
            self.t.start()
            print('Connected')

        return True

    def stop(self):
        self.bConnect = False
        if hasattr(self, 'client'):
            self.client.close()
            del (self.client)
            print('Client Stop')
            self.disconn.disconn_signal.emit()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)

        return buf

    def receive(self, client):
        #time = 0
        #timeVal = 3
        while self.bConnect:
            try:
                #time +=1
                rtype = self.recvall(self.client, 2)
                rtype = rtype.decode()
                if rtype == "DT" :
                    partID = self.recvall(self.client, 16)
                    amount = self.recvall(self.client, 2)
                    percent = self.recvall(self.client, 4)
                    partID = partID.decode().rstrip()
                    #print("partID : ", partID)
                    if len(partID) < 4:
                        self.product_Name = partID
                    elif len(partID) < 12:
                        self.product_Name = partID[:3] + '-' + partID[3:5] + "-" + partID[5:]
                    else:
                        self.product_Name = partID
                    amount = amount.decode()
                    percent = percent.decode()
                    self.recv.send_detect_data.emit(self.product_Name,amount,percent)
                elif rtype == "CT":
                    states = self.recvall(self.client, 6)
                    length = self.recvall(self.client, 16)
                    StringData = self.recvall(self.client, int(length))
                    states = states.decode()
                    state_list = states.split('@')
                    action_state = state_list[0]
                    goods_state = state_list[1]
                    camera_state = state_list[2]
                    #print(" state :" + states)
                    #print("action state :" + action_state)
                    #print("camera_state  :" + camera_state)
                    #print("good state : " + goods_state)
                    data = np.fromstring(StringData, dtype='uint8')
                    decode_img = cv2.imdecode(data, 1)


                #img_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                #img_date = datetime.datetime.now().strftime("%Y%m%d")
                #PATH = '../../../img_fursys/' + img_date

                #print("action state : ",action_state)
                #print("goods state : ", goods_state)
                #if time == timeVal :
                # if action_state == 'A' and goods_state == 'Y':
                #     if camera_state == "CA" :
                #         filename = img_time + '_colorA.jpg'
                #         PATHA = PATH + "/colorA"
                #         self.create_folder(PATHA)
                #         '''
                #         roi_x = 640
                #         roi_y = 0
                #         roi_w = 1280
                #         roi_h = 640
                #         '''
                #
                #         #cv2.imwrite(os.path.join(PATHA, filename), decode_img)
                #         #print("camera_state : " + camera_state)
                #     elif camera_state == "CB":
                #         filename = img_time + '_colorB.jpg'
                #         PATHB = PATH + "/colorB"
                #         self.create_folder(PATHB)
                #         roi_y = 0
                #         roi_x = 315
                #         roi_w = 640
                #         roi_h = 640
                #         decode_imgROI = decode_img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                #         decode_imgROI = cv2.resize(decode_imgROI, dsize=(640, 640))
                #         cv2.imwrite(os.path.join(PATHB, filename), decode_imgROI)
                #         #cv2.imwrite(os.path.join(PATHB, filename), decode_img)
                #     else :
                #         pass
                #     #time = 0
                # self.recv.send_state_signal.emit(action_state,goods_state)

                    if camera_state == "CA" :
                        #if not self.bMode:
                        #if self.bMode =="ColorA":
                        self.recv.recv_signal.emit(decode_img)
                        if self.Img_Write_Flag :
                            img_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                            img_date = datetime.datetime.now().strftime("%Y%m%d")
                            PATH = self.path
                            filename = img_time + '_color.jpg'
                            #self.create_folder(PATH)
                            cv2.imwrite(os.path.join(PATH, filename), decode_img)
                        if self.product_Name == "END" or self.product_Name == "WW" or self.product_Name == "TS" :
                            PATH = self.path
                            img_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                            filename = img_time + '_color.jpg'
                            #cv2.imwrite(os.path.join(PATH, filename), decode_img)

                    elif camera_state == 'CB':
                        self.recv.recv_signalb.emit(decode_img)
                #     #pass
                # elif camera_state == 'DA':
                #     #if self.bMode:
                #     if self.bMode == "Depth":
                #         self.recv.recv_signal.emit(decode_img)
                '''
                self.fileCounter += 1
                if self.fileCounter % 2 == 0:
                    if self.bMode:
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_time + '_depth.jpg'  # depth 파일생성
                        if action_state == 'A' and goods_state == 'Y':
                            cv2.imwrite(os.path.join(PATH, filename), decode_img)
                else:
                    if not self.bMode:
                        self.recv.recv_signal.emit(decode_img)
                        filename = img_time + '_color.jpg'  # color 파일생성
                        if action_state == 'A' and goods_state == 'Y':
                            cv2.imwrite(os.path.join(PATH, filename), decode_img)
                '''

            except Exception as e:
                print('Recv() Error :', e)
                break

        self.stop()

    #def changeMode(self):
    def changeMode(self, mode):
        if not self.bConnect:
            print('Has no connect!')
            return
        if mode == "ColorA" :
            self.bMode = "ColorA"
            print('change mode == ColorA')
        elif mode == "ColorB" :
            self.bMode = "ColorB"
            print('change mode == ColorB')
        elif mode == "Depth" :
            self.bMode = "Depth"
            print('change mode == Depth')
        '''
        self.bMode = not self.bMode
        if self.bMode:
            print('change mode == True')
        else:
            print('False')
        '''

    def send(self, msg):
        if not self.bConnect:
            return
        try:
            self.client.send(msg.encode())
        except Exception as e:
            print('send() Error :', e)

    def create_folder(self,directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory )
