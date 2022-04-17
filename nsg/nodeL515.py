# intel d453에서 이미지 데이터를 시그널로 nsg에 전달한다.
# QThread로부터 상속받아 Signal로 동작한다.
import os
import pyrealsense2 as rs
import numpy as np
# from threading import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import cv2
import os
import time
import datetime
import math

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
        self.frame_idx = 0
        self.f_no = 0
        self.ply_f_no = 0
        self.working = True
        self.bFileWrite = False
        self.plyFileWrite = False
        self.save_dir = ""
        self.save_dir_ply = ""
        self.targetD = 4800
        self.thickness = 1800
        print('dsensor init*')

    def __del__(self):
        print(".....end thread.")
        self.wait()

    def cam_setting(self):
        self.pipeline = rs.pipeline()
        self.cfg = rs.config()
        self.pc = rs.pointcloud()

        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.cfg.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        print("device_product_line : ", device_product_line)

        self.cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.cfg.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)

        self.pipeline.start(self.cfg)
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        print('run')

    # main Thread
    def run(self):
        self.cam_setting()
        self.working = True
        while self.working :
            frames = self.pipeline.wait_for_frames()

            depth_frame = frames.get_depth_frame()
            aligned_frames = self.align.process(frames)
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            #aligned_frames = self.align.process(frames)

            if not aligned_depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            mask_img = self.imageProcessing(aligned_depth_frame, color_frame)

            #ply png 파일 저장
            img_time = datetime.datetime.now().strftime("%H%M%S%f")
            img_date = datetime.datetime.now().strftime("%Y%m%d_")
            plyfileName = img_date + img_time + '.ply'
            pngFileName = img_date + img_time + '.png'

            #self.pc.map_to(color_frame)
            #points = self.pc.calculate(depth_frame)



            if self.bFileWrite:  # and not self.bConnec
                if self.frame_idx % 6 == 0 :

                    ftIName = str(self.f_no) + '.png'
                    depth_dir = self.save_dir + "depth/"
                    if not os.path.exists(depth_dir):
                        os.mkdir(depth_dir)
                    cv2.imwrite(os.path.join(self.save_dir, ftIName), color_image)
                    cv2.imwrite(os.path.join(depth_dir, ftIName), mask_img)
                    self.f_no += 1

                    # self.pc.map_to(color_frame)
                    # points = self.pc.calculate(depth_frame)
                    # ftPName = str(self.f_no) + '.ply'
                    # points.export_to_ply(self.save_dir + ftPName, color_frame)

            # if self.plyFileWrite :
            #     if self.frame_idx % 6 == 0:
            #         self.pc.map_to(color_frame)
            #         points = self.pc.calculate(depth_frame)
            #         ftPName = str(self.ply_f_no) + '.ply'
            #         points.export_to_ply(self.save_dir_ply + ftPName, color_frame)
            #         self.ply_f_no += 1

            c_img = cv2.resize(color_image, dsize=(480, 270), interpolation=cv2.INTER_AREA)
            #m_img = cv2.resize(mask_img, dsize=(480, 270), interpolation=cv2.INTER_AREA)
            m_img = np.zeros((480,270),np.uint8)
            m_img = cv2.cvtColor(m_img, cv2.COLOR_GRAY2BGR)

            #if self.frame_idx % 3 == 0 :
            self.dssg.color_signal.emit(c_img)
            self.dssg.depth_signal.emit(m_img)
            #self.dssg.color_signal.emit(mask_img)
            #self.dssg.color_signal.emit(depth_image)

            self.frame_idx += 1

        # folder = './img/color/'
        # dfolder = './img/depth/'
        # color_imgs = load_images_from_folder(folder)
        # depth_imgs = load_images_from_folder(dfolder)
        # if color_imgs is None :
        #     print("Image is None")
        #     return
        #
        # index = 0
        # for cimg in color_imgs:
        #     self.dssg.report_signal.emit('d515 : '+str(index)+ ':'+str(time.time() ))
        #     self.dssg.color_signal.emit(cimg)
        #     dimg = depth_imgs[index]
        #     self.dssg.depth_signal.emit(dimg)
        #     time.sleep(0.4)
        #     index += 1

    def setTargetD(self, d):
        self.targetD = d

    def setThickness(self, t):
        self.thickness = t

    def imageProcessing(self, adFrame, crFrame):

        depth_align = np.asanyarray(adFrame.get_data())
        color_image = np.asanyarray(crFrame.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_align, alpha=0.05), cv2.COLORMAP_JET)
        depthZ_img = depth_align.copy()
        lower_z = np.array([self.targetD])
        upper_z = np.array([self.targetD + self.thickness])
        maskZ_img = cv2.inRange(depthZ_img, lower_z, upper_z)

        return maskZ_img

    def opticalFlow(self, frame, time):
        # params for ShiTomasi corner detection

        v = 0
        feature_params = dict(maxCorners=100,
                              qualityLevel=0.01,
                              minDistance=30,
                              blockSize=14)

        # feature_params = dict(maxCorners=100,
        #                       qualityLevel=0.01,
        #                       minDistance=7,
        #                       blockSize=7)

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

            px2m = 0.0099
            fps = 30

            self.ptn1 = 0
            for idx, tr in enumerate(self.tracks) :
                result_pg1 = cv2.pointPolygonTest(pg1, tr[0], True)
                if result_pg1 > 0:
                    #self.ptn1 += 1
                    dif1 = tuple(map(lambda i, j: i - j, tr[0], tr[1]))
                    if dif1[0] < 0 :
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
            v_avg,_ = self.mov_avg_filter(self.speedList,v1)
            print("5초 평균 속도 : ", round(v_avg,2))

            if v_avg < 5 :
                self.stop_flag = True
            else :
                self.stop_flag = False

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
            self.speedList.append(round(v1,2))

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
        else :
            v = self.oldv1

        return v

    def draw_str(self, dst, target, s):
        x, y = target
        cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (104, 204, 255), 3, cv2.LINE_AA)

    def mov_avg_filter(self,x_n,x_means):
        n = len(x_n)
        for i in range(n-1):
            x_n[i] = x_n[i+1]
        x_n[n-1] = x_means
        x_avg = np.mean(x_n)

        return x_avg, x_n

    def stop(self):
        self.working = False
        self.frame_idx = 0
        self.pipeline.stop()
