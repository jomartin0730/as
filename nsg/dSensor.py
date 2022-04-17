import os
import pyrealsense2 as rs
import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import time
import sys
import cv2
import datetime
import detect
import MysqlController
import threading
import math

import DeviceManager
import irp

import MovingFilter
import JsonLoader

json_data = JsonLoader.JsonLoader().load_data("dsensor")
min_area = json_data['contour']['min_area']  # 2**9=512
arcRate = json_data['contour']['arcRate']
xs = json_data['state']['start_x']
st = json_data['state']['step_width']
rc = json_data['state']['recycle_count']
cThHold = json_data['state']['cThHold']

fps = json_data['speed']['fps']
px2m = json_data['speed']['px2m']
ms2kmh = json_data['speed']['ms2kmh']

def writePly(filename, pointslist, colorVal):
    print('write file ')
    listcount = len(pointslist)
    # Write header of .ply file
    fid = open(filename, 'wb')
    fid.write(bytes('ply\n', 'utf-8'))
    fid.write(bytes('format binary_little_endian 1.0\n', 'utf-8'))
    fid.write(bytes('element vertex %d\n' % listcount, 'utf-8'))
    fid.write(bytes('property float x\n', 'utf-8'))
    fid.write(bytes('property float y\n', 'utf-8'))
    fid.write(bytes('property float z\n', 'utf-8'))
    fid.write(bytes('property float u\n', 'utf-8'))
    fid.write(bytes('property float v\n', 'utf-8'))
    fid.write(bytes('property float u\n', 'utf-8'))
    fid.write(bytes('property float v\n', 'utf-8'))
    fid.write(bytes('property float u\n', 'utf-8'))
    fid.write(bytes('property float v\n', 'utf-8'))
    fid.write(bytes('end_header\n', 'utf-8'))

    # Write 3D points to .ply file
    for i in range(listcount):
        # fid.write(bytearray(struct.pack("fffff",pointslist[i,0],pointslist[i,1],pointslist[i,2],
        #                                coordlist[i,0],coordlist[i,1])))
        fid.write(
            bytes("{:.2f},{:.2f},{:.2f},0,0,1,{},{},{}\n".format(pointslist[i, 0], pointslist[i, 1], pointslist[i, 2],
                                                                 colorVal[i, 0], colorVal[i, 1], colorVal[i, 2]),
                  'utf-8'))
    print('file close')
    fid.close()


def detectContour(src_img, depth_img):
    # print(src_img.shape)
    arr_data = []
    blur_img = cv2.GaussianBlur(src_img, (3, 3), 0)
    ret, thresh_img = cv2.threshold(blur_img, 16, 255, cv2.THRESH_BINARY)
    # 'THRESH_BINARY', 'THRESH_BINARY_INV', 'THRESH_MASK', 'THRESH_OTSU', 'THRESH_TOZERO', 'THRESH_TOZERO_INV', 'THRESH_TRIANGLE', 'THRESH_TRUNC'
    thresh1_img = cv2.dilate(thresh_img, (5, 5), iterations=2)
    thresh2_img = cv2.erode(thresh1_img, (5, 5), iterations=3)

    # check roi countNonZero
    zoneV = np.arange(rc)
    for i in range(rc):
        zone = thresh2_img[50:450, xs - (i + 1) * st:xs - i * st]
        zzV = cv2.countNonZero(zone)
        zoneV[i] = zzV
        #print(f'zone {i} = {zzV}')

    contours, hierachy = cv2.findContours(thresh2_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnt_contours = len(contours)

    if cnt_contours > 0:
        for i in range(cnt_contours):
            contour_area = cv2.contourArea(contours[i])
            if contour_area > min_area:
                epsilon = arcRate * cv2.arcLength(contours[i], True)
                approx = cv2.approxPolyDP(contours[i], epsilon, True)
                center, radius = cv2.minEnclosingCircle(approx)

                arr_data.append([int(center[0]), int(center[1]), 0, 0])
                cnt_approx = approx.shape[0]
                for j in range(cnt_approx):
                    apX = approx[j, 0, 0]
                    apY = approx[j, 0, 1]
                    apZ = depth_img[apY, apX]
                    apA = 0
                    arr_data.append([apX, apY, apZ, apA])
                # for end
            else:
                pass
        # for end
    else:
        pass
    return contours, arr_data, zoneV


class Signal(QObject):
    color_signal = pyqtSignal(np.ndarray) # capture image
    depth_signal = pyqtSignal(np.ndarray)
    result_signal = pyqtSignal(np.ndarray)
    msg_signal = pyqtSignal(str)
    detect_signal = pyqtSignal(str,str)
    #detectInfo_signal = pyqtSignal(str, str, int)
    detectInfo_signal = pyqtSignal(str)
    inactive_signal = pyqtSignal(str)
    state_signal = pyqtSignal(int)

class dSensor(QThread):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.d = MysqlController.MysqlController()
        self.d.db_connect()
        self.f_path = json_data['path']['f_path']
        self.f_no = 0
        self.c_path = "/home/mgt-pc1/works/MAVIZ/test"
        self.bConnect = False
        self.bFileWrite = False
        self.bFirstCh = True
        self.dssg = Signal()
        self.processName = "SG"

        rs_config = rs.config()
        self.pc = rs.pointcloud()
        self.working = False
        print('@start sensing')
        self.targetD = 1400
        self.thickness = 600

        self.processV = 0
        self.state = 0
        self.oldState = 0
        self.step = 0
        self.startTime = time.time()
        self.partID = "None"
        self.speed = 50

        self.prevFrame = None
        self.newTime = None
        self.oldTime = None

        # self.pname = None
        self.pstate = 18
        self.speedCnt = 0
        self.speedAvg = 0
        self.state_value = "W" # W : 대기 , P : 진해중, S : 시작, F : 끝
        self.stateV = "제품 대기중"

        self.state_flag = False
        self.stop_flag = False
        self.detect_flag = False

        # detect 객체
        #self.det = detect.Detector()
        #self.det.detect_set()

        self.start_val = 10
        self.finish_val = 8

        self.track_len = 2
        self.detect_interval = 6
        self.frame_idx = 0
        self.tracks = []
        self.speedList = []
        self.ptn1 = 0
        self.prn1 = 0
        self.prv1 = 0
        self.alpha = 0.2
        self.oldv1 = 0

        self.mf = MovingFilter.MovAvgFilter()

        self.prevStateTime = 0
        self.StateTime = 0

        self.device_count = len(device_manager._available_devices)
        if self.device_count > 1 :

            self.pipeline1 = rs.pipeline()
            self.pipeline2 = rs.pipeline()

            self.cfg1 = rs.config()
            self.cfg2 = rs.config()

            self.cfg1.enable_device(device_manager._available_devices[0])
            self.cfg1.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 6)
            self.cfg1.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 6)

            self.cfg2.enable_device(device_manager._available_devices[1])
            self.cfg2.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 6)
            self.cfg2.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 6)

            self.irp = irp.IRP()
            self.irp.set_irp(self.pipeline2,self.cfg2)
        else :

            self.pipeline1 = rs.pipeline()

            self.cfg1 = rs.config()

            self.cfg1.enable_device(device_manager._available_devices[0])
            self.cfg1.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 6)
            self.cfg1.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 6)

        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        print('dsensor init*')

    def __del__(self):
        print(".....end thread.")
        #self.wait()

    def checkOldStep(self, nst):
        if self.oldState != nst:
            prevStateTime = time.time()
            self.StateTime = prevStateTime - self.prevStateTime
            self.prevStateTime = prevStateTime
            print(f'state {self.state} - prev_state[{self.state-1}] = {[self.StateTime]}')

            self.stop_flag = False
            self.oldState = nst
            self.step = 0
        else:
            self.stop_flag = True
            self.step += 1

        if self.step > 10 and self.step < 50:
            #print(f'{self.step} delay process')
            self.stop_flag = True
        elif self.step > 50:
            #self.state = 0
            self.step = 0

    def checkState(self, zoneV):

        if self.state == 0:
            self.state_value ="W"
            if zoneV[0] > cThHold:
                self.state = 1
        elif self.state == 1:
            if zoneV[1] > cThHold:
                self.state = 2
        elif self.state == 2:
            if zoneV[2] > cThHold:
                self.state = 3
        elif self.state == 3:
            if zoneV[3] > cThHold:
                self.state = 4
        elif self.state == 4:
            if zoneV[4] > cThHold:
                self.state = 5
        elif self.state == 5:
            if zoneV[5] > cThHold:
                self.state = 6
        elif self.state == 6:
            if zoneV[6] > cThHold:
                self.state = 7
        elif self.state == 7:
            if zoneV[7] > cThHold:
                self.state = 8
        elif self.state == 8:
            if zoneV[8] > cThHold:
                self.state = 9
        elif self.state == 9:
            if zoneV[9] > cThHold:
                self.state = 10
        elif self.state == 10:
            if zoneV[10] > cThHold:
                self.state = 11
        elif self.state == 11:
            self.detect_flag = False
            if zoneV[11] > cThHold:
                self.state = 12
        elif self.state == 12:
            self.state_value = "W"
            if zoneV[12] > cThHold:
                self.state_value = "S"
                self.state = 13
        elif self.state == 13:
            if zoneV[13] > cThHold:
                self.state = 14
        elif self.state == 14:
            if zoneV[14] > cThHold:
                self.state = 15
        elif self.state == 15:
            if zoneV[15] > cThHold:
                self.state = 16
        elif self.state == 16:
            if zoneV[16] > cThHold:
                self.state = 17
        elif self.state == 17:
            if zoneV[17] > cThHold:
                self.state = 18
        elif self.state == 18:
            if zoneV[18] > cThHold:
                self.state = 19
        elif self.state == 19:
            if zoneV[19] > cThHold:
                self.state = 20
        elif self.state == 20:
            if zoneV[20] > cThHold:
                self.state = 21
        elif self.state == 21:
            if zoneV[21] > cThHold:
                self.state = 22
        elif self.state == 22:
            if zoneV[22] > cThHold:
                self.state = 23
        elif self.state == 23:
            if zoneV[23] > cThHold:
                self.state = 24
        elif self.state == 24:
            if zoneV[24] > cThHold:
                self.state = self.finish_val

        if self.state > 0:
            self.checkOldStep(self.state)
            #print(f'state {self.state} zone[{self.state-1}] = {zoneV[self.state-1]}')
            self.state_flag = True

            if self.state > self.pstate:
                #print("도장완료")
                self.state_value ="F"
                #self.state = 4
                self.state = self.finish_val
                self.detect_flag = True
            elif self.state <= self.start_val:
                self.state_value ="W"
            #elif self.state == 1:
            #    pass
            else:
                self.state_value ="P"
                pass
        else:
            self.state_flag = False
            pass

    def imageProcessing(self, adFrame, crFrame):
        depth_align = np.asanyarray(adFrame.get_data())
        color_image = np.asanyarray(crFrame.get_data())
        zoneV_cimage = color_image.copy()
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_align, alpha=0.05), cv2.COLORMAP_JET)
        depthZ_img = depth_align.copy()
        lower_z = np.array([self.targetD])
        upper_z = np.array([self.targetD + self.thickness])
        maskZ_img = cv2.inRange(depthZ_img, lower_z, upper_z)

        contours, arr_send, zV = detectContour(maskZ_img, depth_align)
        self.checkState(zV)

        #color_image = cv2.drawContours(color_image, contours, -1, (125, 125, 120), 3)
        color_image = cv2.drawContours(color_image, contours, -1, (204, 255, 255), 3)
        self.append_stateV(self.state_value)

        for i in range(rc):
            if i > self.state:
                #cv2.rectangle(color_image, (xs - (i + 1) * st, 50), (xs - i * st, 450), (0, 120, 0), 1)
                cv2.rectangle(color_image, (xs - (i + 1) * st, 50), (xs - i * st, 450), (255, 255, 204), 1)
            else:
                #cv2.rectangle(color_image, (xs - (i + 1) * st, 50), (xs - i * st, 450), (0, 255, 0), 3)
                cv2.rectangle(color_image, (xs - (i + 1) * st, 420), (xs - i * st, 450), (102, 255, 102), -1)

        # cv2.line(color_image,(600,0),(600,480),(255,0,255),1,1)
        cv2.line(color_image, (440, 0), (440, 480), (0, 255, 0), 1, 1)
        cv2.line(color_image, (315, 0), (315, 480), (255, 0, 255), 1, 1)
        # cv2.putText(color_image, "start", (505, 475), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255),2)
        cv2.putText(color_image, "start", (505, 475), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        # cv2.line(color_image,(50,0),(50,480),(255,0,255),1,1)
        # cv2.line(color_image, (40, 0), (0, 480), (255, 0, 255), 1, 1)
        # cv2.putText(color_image, "end", (65, 475), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255),2)
        # cv2.putText(color_image,f'state = {self.state}', (280,30), 3, 1, (10, 55, 20))
        cv2.putText(color_image, f'state = {self.state}', (60, 30), 3, 1, (0, 0, 255), 2)

        cv2.putText(color_image, self.stateV, (280, 30), 3, 1, (0, 0, 255), 2)

        cv2.putText(zoneV_cimage, f'zoneV = {zV[self.state]}', (400, 475), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.putText(zoneV_cimage, f'state = {self.state}', (60, 475), 3, 1, (0, 0, 255), 2)
        cv2.line(zoneV_cimage, (315, 0), (315, 480), (255, 0, 255), 1, 1)
        # print(self.stateV)
        self.dssg.color_signal.emit(color_image)
        return zoneV_cimage

    def run(self):
        print('run')

        if self.device_count > 1:
            self.pipeline1.start(self.cfg1)
            #self.pipeline2.start(self.cfg2)
            #self.IRP_thread()
            self.irp.pipeline_start()
        else :
            self.pipeline1.start(self.cfg1)

        #roi_frame_default = None
        #old_partID = "None"
        old_partID = None
        old_state = 0
        cnt = 0
        state_value = "None"
        frame_idx = 0

        while self.working:

            img_t = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img_d = datetime.datetime.now().strftime("%Y%m%d")
            # ???????
            PATH = '../img_fursys/' + img_d
            self.create_folder(PATH)

            img_filename = img_t + '_color.jpg'

            frames = self.pipeline1.wait_for_frames()

            self.newTime = time.time()

            depth_frame = frames.get_depth_frame()
            aligned_frames = self.align.process(frames)
            aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()
            if not aligned_depth_frame or not color_frame:
                continue

            depth_align = np.asanyarray(aligned_depth_frame.get_data())
            # dimension = depth_align.shape
            source_frame = np.asanyarray(color_frame.get_data())
            color_image = source_frame.copy()
            pc_image = source_frame.copy()

            self.speed = self.opticalFlow(color_image, self.newTime)

            img_time = datetime.datetime.now().strftime("%H%M%S%f")
            img_date = datetime.datetime.now().strftime("%Y%m%d_")

            fileName = img_date + img_time + '.ply'
            imgFileName = img_date + img_time + '.png'
            str_array = None

            #self.irp.run()
            if old_partID is None :
                old_partID = self.partID


            if self.partID != "None" :
                pname, state, speed = self.d.load_image(self.partID)
                info_data = self.load_pinfo(self.partID)
                self.dssg.detectInfo_signal.emit(info_data)

                if state is not None:
                    self.pstate = state
                    # print("pstate >>>>>>>>> ", self.pstate)
                    # print("state >>>>>>>>> ", state)
                else:
                    # self.pstate = 20
                    pass
                #print("ds part ID ", self.partID)
                #print("[detect 품종코드]:", self.partID)
                if speed is None:
                    pass
                    #speed = self.speed



            if old_partID != self.partID:
                state_value = "P"
            else:
                if self.state == self.start_val:
                    state_value = "R"
                elif self.state_flag == False:
                    state_value = "S"
                else:
                    state_value = "P"



            str_array = fileName + ":" + str(self.state) + ":" + str(state_value) + ":" + str(self.partID) + ":"+ str(self.pstate) + ":" + str(self.speed)
            #str_array = fileName + ":" + str(self.state) + ":" + str(state_value) + ":" + str(self.partID) +":"
            #print("str array //" + str_array + "\n")

            if frame_idx % 2 == 0 :
                zoneV_cimage = self.imageProcessing(aligned_depth_frame, color_frame)
                #print("str array //" + str_array + "\n")

            self.pc.map_to(color_frame)
            points = self.pc.calculate(depth_frame)

            PName = str(frame_idx) + '.png'
            #cv2.imwrite(os.path.join(self.c_path, PName), pc_image)

            if self.bFileWrite:  # and not self.bConnect
                if old_state != self.state :
                    ftPName = str(self.f_no) + '.ply'
                    ftIName = str(self.f_no) + '.png'
                    print(self.f_path + fileName)
                    #points.export_to_ply(self.f_path + ftPName, color_frame)
                    points.export_to_ply(self.f_path + ftPName, color_frame)
                    #cv2.imwrite(os.path.join(self.f_path, ftIName), color_image)
                    cv2.imwrite(os.path.join(self.f_path, ftIName), zoneV_cimage)
                    self.f_no += 1

            #if self.bConnect and self.state > 0:
            if self.bConnect :
                if self.state != old_state :
                    path = "/home/mgt-pc1/works/MAVIZ/ply/Demo_product/"
                    points.export_to_ply(path + fileName, color_frame)
                    #("stateV",self.state_value)
                    #print("state", self.state)
                    if self.stop_flag == False :
                        self.dssg.detect_signal.emit(str_array,self.state_value)

            #elif self.bConnect and self.state == 0 :
            #    self.dssg.inactive_signal.emit(self.state_value)

            # if self.speedCnt == self.pstate:
            #     s_avg = round((self.speedAvg / self.pstate), 2)
            #     self.reset_speed_set()
            #     print("평균속도 : ", s_avg)

            old_partID = self.partID
            old_state = self.state

            self.dssg.state_signal.emit(self.pstate)

            frame_idx += 1
            #time.sleep(0.2)
            #time.sleep(0.01)


        self.pipeline1.stop()
        self.irp.pipeline_stop()
        #self.pipeline2.stop()

    def setStartSave(self):
        self.bFileWrite = True
        self.f_no = 0
        self.startTime = time.time()

    def infosave(self):
        self.bFileWrite = False
        curTime = time.time()
        takTime = curTime - self.startTime
        print(self.f_path + 'info.txt')
        file = open(self.f_path + 'info.txt', "w")
        file.write(f'tak ={takTime} \n')
        file.write(f'end ={curTime} \n')
        file.write(f'start ={self.startTime} \n')
        file.write(f'depth = {self.self.targetD}')
        file.close()

    def conn(self, conn_state):
        self.bConnect = conn_state
        print('ds connected ')

    def setDepth(self, dValue):
        if dValue > 1000 and dValue < 3000:
            self.targetD = dValue

    def setState(self, StateValue):
        if StateValue >= 0 and StateValue <= 24:
            self.pstate = StateValue

    def setSpeed(self, SpeedValue):
        if SpeedValue >= 0 and SpeedValue <= 100:
            self.speed = SpeedValue

    def detectBlobs(self, mask):
        # Set up the SimpleBlobdetector with default parameters.
        params = cv2.SimpleBlobDetector_Params()
        # Change thresholds
        params.minThreshold = 1
        params.maxThreshold = 255
        # Filter by Area.
        params.filterByArea = True
        params.maxArea = 4000
        params.minArea = 300

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.1

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.5

        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.1

        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs.
        reversemask = mask
        keypoints = detector.detect(reversemask)
        im_with_keypoints = cv2.drawKeypoints(mask, keypoints, np.array([]),
                                              (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return im_with_keypoints

    def thresholdDepth(self, depth):
        depth[depth == 0] = 255  # set all invalid depth pixels to 255
        # threshold_value = cv2.getTrackbarPos('Threshold','Truncated Depth')
        threshold_value = 1.0
        ret, truncated_depth = cv2.threshold(depth, threshold_value, 255, 1)
        return truncated_depth

    def create_folder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory)

    def active_check(self, src1, src2):

        if src1 is None:
            src1 = src2

        move_value = 15000
        move_flag = True
        # prev_image
        gray_src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
        gray_src1 = cv2.GaussianBlur(gray_src1, (0, 0), 1.0)

        # current_image
        gray_src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        gray_src2 = cv2.GaussianBlur(gray_src2, (0, 0), 1.0)

        dst = cv2.absdiff(gray_src1, gray_src2)
        _, dst_th = cv2.threshold(dst, 5, 255, cv2.THRESH_BINARY)
        goods_roi = dst_th
        move_check = cv2.countNonZero(dst_th)
        #print("move_check", move_check)
        if move_check < move_value and move_check > 0:
            #print("ROI_move_value :", move_check)
            move_flag = False
        else:
            move_flag = True
        # print("ROI goods_check :", goods_check)
        # print("ROI_move_value :", move_check)
        return dst_th, move_check, move_flag

    def opticalFlow(self, frame, time):
        # params for ShiTomasi corner detection

        v = 0
        # feature_params = dict(maxCorners=100,
        #                       qualityLevel=0.01,
        #                       minDistance=30,
        #                       blockSize=14)

        feature_params = dict(maxCorners=100,
                              qualityLevel=0.01,
                              minDistance=30,
                              blockSize=14)

        # Parameters for lucas kanade optical flow
        lk_params = dict(winSize=(15, 15),
                         maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # lk_params = dict(winSize=(15, 15),
        #                  maxLevel=0,
        #                  criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # Create some random colors
        # color = np.random.randint(0,255,(100,3))
        # Take first frame and find corners in it

        #frame = f.copy()
        frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        vis = frame.copy()
        cmask = frame.copy()

        v1 = 0
        mm1 = 0
        z = 0
        v_sum = 0
        v_avg = 0

        self.draw_str(vis, (30, 40), 'ptn1: %d' % self.prn1)
        #self.draw_str(vis, (30, 80), 'lane speed: %d km/h' % self.prv1)
        self.draw_str(vis, (200, 40), 'speed: %0.2f m/m' % self.prv1)

        #pg1 = np.array([[0, 0],[640, 0], [640, 240],[0, 240]])
        #pg1 = np.array([[0, 100],[640, 100], [640, 400],[0, 400]])
        #pg1 = np.array([[0, 0],[640, 0], [640, 430],[0, 430]])
        pg1 = np.array([[0, 0],[640, 0], [640, 480],[0, 480]])
        #pg1 = np.array([[0, 0],[320, 0], [320, 430],[0, 430]])

        cv2.fillPoly(cmask, [pg1], (120, 0, 120), cv2.LINE_AA)

        if len(self.tracks) > 0 :
            img0, img1 = self.prev_gray, frame_gray
            p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
            p1, _st, _err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
            p0r, _st, _err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
            d = abs(p0 - p0r).reshape(-1, 2).max(-1)
            good = d < 1
            new_tracks = []
            for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                if not good_flag:
                    continue

                tr.append((x, y))
                if len(tr) > self.track_len:
                    del tr[0]
                new_tracks.append(tr)
                cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)

            self.tracks = new_tracks

            self.ptn1 = 0
            for idx, tr in enumerate(self.tracks) :
                result_pg1 = cv2.pointPolygonTest(pg1, tr[0], True)
                if result_pg1 > 0:
                    #self.ptn1 += 1
                    dif1 = tuple(map(lambda i, j: i - j, tr[0], tr[1]))
                    if dif1[0] > 0 :
                        z = math.sqrt(dif1[0] * dif1[0] + dif1[1] * dif1[1])
                        if z > 3 and z < 9:
                            #print("z value : " ,z)
                            asin_value = dif1[1] / z
                            if asin_value <=1 and asin_value >= -1 :
                                angle = math.degrees(math.asin(dif1[1]/z))
                                #print("angle : ",angle)
                                if angle <= 45 and angle >= -45 :
                                #mm1 += math.sqrt(dif1[0] * dif1[0] + dif1[1] * dif1[1])
                                    self.ptn1 += 1
                                    mm1 += z
                                    mmm1 = mm1 / self.ptn1
                                    #v1 = mmm1 * px2m * fps * ms2kmh
                                    v1 = mmm1 * px2m * fps * (100 / 6)


            cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 0, 255))

        self.prn1 = self.ptn1
        if len(self.speedList) == 5 :
            # v_sum = sum(self.speedList)
            # v_avg = v_sum/len(self.speedList)
            # print("5초 평균 속도 : ",v_avg)
            v_avg,_ = self.mf.mov_avg_filter(self.speedList,v1)
            print("5초 평균 속도 : ", round(v_avg,2))

            if self.ptn1 > 10 :
                self.draw_str(vis, (30, 40), 'ptn1: %d' % self.ptn1)
                #self.draw_str(vis, (80, 40), 'lane speed: %0.2f m/m' % v1)
                self.draw_str(vis, (200, 40), 'speed: %0.2f m/m' % v_avg)
            self.prv1 = v_avg

            img_t = datetime.datetime.now().strftime("%H:%M:%S")
            img_d = datetime.datetime.now().strftime("%Y%m%d")

            if self.prv1 > 5 :
                log_data = img_t + "," + str(self.ptn1) + "," + str(self.prv1)

                try:
                    if not os.path.exists("log"):
                        os.makedirs("log")
                except OSError:
                    print('Error: Creating directory. log')

                f = open("./log/" + img_d + '_log.csv', mode='at', encoding='utf-8')
                f.writelines(log_data + '\n')
                f.close()

            self.speedList.clear()

        if self.frame_idx % self.detect_interval == 0 :
            # if self.ptn1 > 10 :
            #     self.draw_str(vis, (30, 40), 'ptn1: %d' % self.ptn1)
            #     #self.draw_str(vis, (80, 40), 'lane speed: %0.2f m/m' % v1)
            #     self.draw_str(vis, (80, 40), 'lane speed: %0.2f m/m' % v_avg)

            # self.prv1 = v_avg

            mask = np.zeros_like(frame_gray)
            mask[:] = 255
            for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                cv2.circle(mask, (x, y), 5, 0, -1)
            p = cv2.goodFeaturesToTrack(frame_gray, mask=mask, **feature_params)
            if p is not None:
                for x, y in np.float32(p).reshape(-1, 2):
                    self.tracks.append([(x, y)])  #
            self.speedList.append(v1)

        self.frame_idx += 1
        self.prev_gray = frame_gray

        cv2.addWeighted(cmask, self.alpha, vis, 1 - self.alpha, 0, vis)
        #self.dssg.color_signal.emit(vis)

        #round_v = round(self.prv1)
        round_v = round(self.prv1,2)
        speed_result = self.speed_check(round_v)

        if speed_result > 5 :
            self.oldv1 = speed_result
            v = speed_result
            self.stop_flag = False
        else :
            v = self.oldv1
            self.stop_flag = True

        return v


    def speed_check(self, v):
        returnData = 50
        if v >= 6.0 :
            returnData = 50
        else :
            returnData = 50
        # if v >= 6.8 :
        #     returnData = 70
        # elif v >= 6.3 and v < 6.8 :
        #     returnData = 65
        # elif v >= 5.8 and v < 6.3 :
        #     returnData = 60
        # elif v >= 5.3 and v < 5.8 :
        #     returnData = 55
        # elif v < 5.3 :
        #     returnData = 50

        return returnData




    def reset_speed_set(self):
        self.speedAvg = 0
        self.speedCnt = 0

    def append_stateV(self,state_value):
        if state_value == "W" :
            self.stateV = "Waiting"
        elif state_value == "S" :
            self.stateV = "Start"
        elif state_value == "P" :
            self.stateV = "Process"
        elif state_value == "F" :
            self.stateV = "Finish"
        else :
            pass

    def draw_str(self, dst, target, s):
        x, y = target
        cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (104, 204, 255), 3, cv2.LINE_AA)

    def load_pinfo(self,pcode):
        _,name,color = self.d.select_partimage(pcode)
        if len(pcode) < 12:
            code = pcode[:3] + '-' + pcode[3:5] + "-" + pcode[5:]
        else:
            code = pcode
        str_array = "품종명 : " + name + " , 품종코드 : " + code

        return str_array
