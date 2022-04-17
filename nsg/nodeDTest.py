# 테스트용 센서
# 정해진 폴더에서 하나씩 영상을 읽어서 보낸다.
import os
import numpy as np
# from threading import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import cv2
import os
import time
import datetime
import math

class SensorSignal(QObject):
    color_signal = pyqtSignal(np.ndarray)
    depth_signal = pyqtSignal(np.ndarray)
    report_signal = pyqtSignal(str)

class dSensor(QThread):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.dssg = SensorSignal()
        self.frame_idx = 0
        self.f_no = 0
        self.working = True
        self.bFileWrite = False
        self.src_cfolder = None
        self.src_dfolder = None        
        self.cimg_filenames = []
        self.dimg_filenames = []        
        self.img_index = 0
        self.img_cexist = False
        self.img_dexist = False        
        self.interval = 0.1
        print('dsensor init*')

    def __del__(self):
        print(".....end thread.")
        #self.wait()

    def cam_setting(self):    
        self.img_dindex =1
        self.img_cindex =1         
        #color_folder = './img/1f4'
        #depth_folder = './img/1g4'
        #color_folder = './img/1s_5F'
        #depth_folder = './img/1s_5F'           
        #color_folder = './img/0084_2s5f'
        #depth_folder = './img/0084_2s5g' 
        color_folder = './img/0242_2f'
        depth_folder = './img/0242_2g'                             
        if os.path.isdir(color_folder) :
            print("cam_setting."+ color_folder)
            for filename in os.listdir(color_folder):
                self.cimg_filenames.append(filename)
            self.src_cfolder = color_folder
            self.img_cexist = True
        else :
            self.src_cfolder = None
            self.img_cexist = False

        if os.path.isdir(depth_folder) :
            print("cam_setting."+ depth_folder)
            for filename in os.listdir(depth_folder):
                self.cimg_filenames.append(filename)
            self.src_dfolder = depth_folder
            self.img_dexist = True
        else :
            self.src_dfolder = None
            self.img_dexist = False

    def setInterval(self, iv):
        self.interval = iv

    # main Thread 
    def run(self):
        self.cam_setting()
        while self.working :
            if self.img_cexist :
                filename = str(self.img_cindex )+'.png'
                cimg = cv2.imread(os.path.join(self.src_cfolder,filename))
                if cimg is not None:
                    self.img_cindex = self.img_cindex +1
                    color_image = np.asanyarray(cimg)
                    c_img = cv2.resize(color_image, dsize=(480, 270), interpolation=cv2.INTER_AREA)
                    self.dssg.color_signal.emit(c_img)

                else :
                    self.img_cexist = False
            if self.img_dexist :
                filename = str(self.img_dindex )+'.png'
                dimg = cv2.imread(os.path.join(self.src_dfolder,filename))
                if dimg is not None:
                    self.img_dindex = self.img_dindex +1
                    m_img = cv2.resize(dimg, dsize=(480, 270), interpolation=cv2.INTER_AREA)                                        
                    self.dssg.depth_signal.emit(m_img)
                    self.dssg.report_signal.emit(filename)
                    #print(filename + " : depth_frame signal emit")
                else :
                    self.img_dexist = False
                    continue
            time.sleep(self.interval)

    def setThickness(self, t):
        self.thickness = t

    def stop(self):
        self.working = False
        self.frame_idx = 0

    def resume(self) :
        self.working = True
        

