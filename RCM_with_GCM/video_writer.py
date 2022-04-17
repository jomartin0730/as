import numpy as np
import cv2
import pyrealsense2 as rs
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread

class videowriter(QThread):
    def __init__(self,parent=None):
        super(self.__class__, self).__init__(parent)
        print("video Writer init")
        self.working = True
        self.camSet()
        self.setVideoWrite()

    def camSet(self):
        context = rs.context()
        connect_device = []
        for d in context.devices:
            if d.get_info(rs.camera_info.name).lower() != 'platform camera':
                connect_device.append(d.get_info(rs.camera_info.serial_number))
        self.pipeline1 = rs.pipeline()
        self.pipeline2 = rs.pipeline()

        self.cfg1 = rs.config()
        self.cfg2 = rs.config()

        self.cfg1.enable_device(connect_device[0])
        self.cfg1.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.cfg1.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)

        # self.cfg2.enable_device(connect_device[1])
        # self.cfg2.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # self.cfg2.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)


    def run(self):
        print("녹화 시작")
        self.pipeline1.start(self.cfg1)
        #self.pipeline2.start(self.cfg2)
        while self.working:
            frames1 = self.pipeline1.wait_for_frames()
            #frames2 = self.pipeline2.wait_for_frames()

            color_frame1 = frames1.get_color_frame()
            #color_frame2 = frames2.get_color_frame()

            source_frame1 = np.asanyarray(color_frame1.get_data())
            #source_frame2 = np.asanyarray(color_frame2.get_data())

            self.out1.write(source_frame1)
            #self.out2.write(source_frame2)

    def stop(self):
        print("녹화 종료")
        self.working = False
        self.quit()
        self.pipeline1.stop()
        self.pipeline2.stop()
        self.wait(5000)


    def setVideoWrite(self):
        self.w = 640
        self.h = 480
        self.fps = 30
        self.fcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
        self.out1 = cv2.VideoWriter('../video/Test1.avi', self.fcc, self.fps, (self.w, self.h))
        self.out2 = cv2.VideoWriter('../video/Test2.avi', self.fcc, self.fps, (self.w, self.h))


    def setWidth(self,w):
        self.w = w

    def setHeight(self,h):
        self.h = h

    def __del__(self):
        print("video Writer del")
        pass
