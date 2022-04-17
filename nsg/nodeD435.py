# intel d453에서 이미지 데이터를 시그널로 nsg에 전달한다.
# QThread로부터 상속받아 Signal로 동작한다.
import os
#import pyrealsense2 as rs
import numpy as np
# from threading import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import cv2
import os
import time

# load image from folder  = './your/folder/'
def load_images_from_folder(folder):
    if os.path.isdir(folder) :
        images = []
        for filename in os.listdir(folder):
            img = cv2.imread(os.path.join(folder,filename))
            if img is not None:
                images.append(img)
        return images
    else :
        return None

class SensorSignal(QObject):
    color_signal = pyqtSignal(np.ndarray)
    depth_signal = pyqtSignal(np.ndarray)
    report_signal = pyqtSignal(str)


class dSensor(QThread):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.dssg = SensorSignal()
        print('dsensor init*')

    def __del__(self):
        print(".....end thread.")
        self.wait()

    # main Thread 
    def run(self):
        print('run')
        folder = './img/color/'
        dfolder = './img/depth/'
        color_imgs = load_images_from_folder(folder)
        depth_imgs = load_images_from_folder(dfolder)
        if color_imgs is None :
            print("Image is None")
            return

        index = 0
        for cimg in color_imgs:
            self.dssg.report_signal.emit('d435 : '+str(index)+ ':'+str(time.time() ))
            self.dssg.color_signal.emit(cimg)
            dimg = depth_imgs[index]
            self.dssg.depth_signal.emit(dimg)
            time.sleep(0.4)
            index += 1
