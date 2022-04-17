#!/usr/bin/python
import numpy as np
import socket
import time
import copy
import cv2
import sys
import os
import datetime
from pypylon import pylon
os.environ["PYLON_CAMEMU"] = "3"
from pypylon import genicam

import threading
import datetime

#Yolo detect
import argparse
#import platform
import shutil
import time
from pathlib import Path
import torch
import torch.backends.cudnn as cudnn
from numpy import random
from models.experimental import attempt_load
from yolo_utils.datasets import LoadStreams, LoadImages
from yolo_utils.general import check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, strip_optimizer, set_logging
from yolo_utils.torch_utils import select_device, load_classifier, time_synchronized

#old_pname = None

# Number of images to be grabbed.
countOfImagesToGrab = 10

maxCamerasToUse = 2

HOST = '192.9.226.149'
PORT = 9999

# ROI 전체 사진 짜르기 camera A 1280 x 620
roi_x = 400
roi_y = 45
roi_w = 1150
roi_h = 1150

# ROI 기계 작동 유무
move_value = 0
# move_value = 250

# ROI 물체 유무
x_roi_goods = 640
y_roi_goods = 0
w_roi_goods = 640
h_roi_goods = 570
goods_value = 5000

# mog2 setting
mog_history = 400
mog_varTh = 16

# Text setting
FONT_LOCATION = (25, 420)
FONT_SIZE = 3
FONT_SCALE = cv2.FONT_HERSHEY_SIMPLEX
FONT_COLOR = (0, 0, 255)

# FONT_LOCATION_TIME = (255, 20)
FONT_LOCATION_TIME = (25, 440)
FONT_COLOR_TIME = (255, 255, 255)
FONT_SCALE_TIME = cv2.FONT_HERSHEY_PLAIN

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)




class xavier_init() :
    def __init__(self):
        self.strike_flag = False
        #self.detect_flag = False

        self.camera_flag = False
        self.camera_data = None
        self.camera_state = False
        self.detect_data = None
        self.A_detect_flag = False
        self.img = None

        self.detect_set()
        self.camera_set()


    def detect_set(self):
        # detect Setting
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
        parser.add_argument('--source', type=str, default='./detect', help='source')  # file/folder, 0 for webcam
        parser.add_argument('--output', type=str, default='./output', help='output folder')  # output folder
        parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
        parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
        parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='display results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--update', action='store_true', help='update all models')
        self.opt = parser.parse_args()

        self.img_size = 640
        self.stride = 32

        self.partID = "default"
        self.percent = 0
        self.old_partID = None
        self.amount = 0
        self.time = "time"
        self.str_array = ""


        out, source, weights, view_img, save_txt, imgsz = \
            self.opt.output, self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size
        #self.webcam = source.isnumeric() or source.startswith(('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')

        # Initialize
        set_logging()
        self.device = select_device(self.opt.device)

        if os.path.exists(out):
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.imgsz = check_img_size(imgsz, s=self.model.stride.max())  # check img_size
        if self.half:
            self.model.half()  # to FP16

        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(
                torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()


    # def detect_act(self,imgSrc,goods_state):
    #     if goods_state == "Y":
    #         returnData, im0, pname, detect_check = self.detect(imgSrc)
    #         print("return Data : ", returnData)
    #         print("detect_check: ", detect_check)
    #         print("pname : ", pname)
    #
    #         return im0,pname

    def detect(self, imgSrc):
        # Get names and colors
        # Get names and colors
        print('detect start')
        im0 = None  # return image
        pname = None
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        # colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
        # Run inference
        img = torch.zeros((1, 3, self.imgsz, self.imgsz), device=self.device)  # init img
        _ = self.model(img.half() if self.half else img) if self.device.type != 'cpu' else None  # run once
        returnData = None
        old_percent = 0
        old_good = None
        detect_check = False

        # Padded resize
        img = letterbox(imgSrc, self.img_size, stride=self.stride)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = self.model(img, augment=self.opt.augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
                                   agnostic=self.opt.agnostic_nms)
        t2 = time_synchronized()


        # Apply Classifier
        if self.classify:
            pred = apply_classifier(pred, self.modelc, img, imgSrc)

        # Process detections

        for i, det in enumerate(pred):  # detections per image
            s = ''
            im0 = imgSrc
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            # detect 했을 경우
            if det is not None and len(det):
                self.amount = len(det)
                detect_check = True
                total = 0.0
                goods_type = None
                percent = None
                more_than_90 = 0
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += '%g %s, ' % (n, names[int(c)])  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    goods_type = names[int(cls)]
                    print("품종 : ", goods_type)
                    # pname = goods_type
                    percent = '%.2f' % (conf)
                    # print(type(percent))
                    percent = float(percent)
                    # print("percent",type(percent))
                    label = '%s %.2f' % (names[int(cls)], conf)
                    # print("정확도 : ", percent)

                    if old_good is None:
                        old_good = goods_type
                    if old_percent == 0:
                        old_percent = percent
                    # 현재 퍼센트가 더 높은 경우 높은 제품으로 인식

                    if old_percent < percent:
                        old_good = goods_type
                        old_percent = percent
                    else:
                        pass

                    pname = old_good
                    returnData = xyxy
                    self.partID = pname
                    self.percent = old_percent

            else:
                # print("[[detect None]]")
                detect_check = False
                self.amount = 0
                returnData = "nodata"
                pass


                # print(f'{s}Done. ({t2 - t1:.3f}s)')
        return returnData, im0, self.partID, detect_check,self.percent

    def camera_set(self):
        #try:
        # Get the transport layer factory.
        self.tlFactory = pylon.TlFactory.GetInstance()

        # Get all attached devices and exit application if no device is found.
        self.devices = self.tlFactory.EnumerateDevices()
        if len(self.devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")

        # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
        self.cameras = pylon.InstantCameraArray(min(len(self.devices), maxCamerasToUse))

        l = self.cameras.GetSize()

        # Create and attach all Pylon Devices.
        for i, cam in enumerate(self.cameras):
            cam.Attach(self.tlFactory.CreateDevice(self.devices[i]))

            # Print the model name of the camera.
            print(i ,"Using device ", cam.GetDeviceInfo().GetModelName())

        # Starts grabbing for all cameras starting with index 0. The grabbing
        # is started for one camera after the other. That's why the images of all
        # cameras are not taken at the same time.
        # However, a hardware trigger setup can be used to cause all cameras to grab images synchronously.
        # According to their default configuration, the cameras are
        # set up for free-running continuous acquisition.
        self.cameras.StartGrabbing()
        self.converter = pylon.ImageFormatConverter()
        # converting to opencv bgr format
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        if self.cameras.IsGrabbing():  # realsense 가 0이면 usb3.0 연결됨
            self.device_bool = True
            print("> usb3.0 connect BASLER")
        else:  # 아니면 python3 시스템 exit
            self.device_bool = False
            print("> NOT connect BASLER camera ! \n> python3 system exit !!!")
            sys.exit()

        device_bool = self.device_bool

        camera_thread = threading.Thread(target=self.camera_thread, args=(device_bool,))
        camera_thread.daemon = True
        camera_thread.start()

        detect_thread = threading.Thread(target=self.detect_thread, args=(device_bool,))
        detect_thread.daemon = True
        detect_thread.start()

    def accept_client(self):
        global serv_sock
        # Create socket and wait for client connection
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Socket created!')
        serv_sock.bind((HOST, PORT))  # 소켓 연결 바인드
        print('Socket bind complete!')
        serv_sock.listen(5)
        print('Socket now listening!')

        while True :
            try:
                clnt_sock, addr = serv_sock.accept()
                print(str(addr) + ' Socket client accepted!')
                t = threading.Thread(target=self.handle_client, args=(clnt_sock, addr))
                t.daemon = True
                t.start()

            except KeyboardInterrupt:
                serv_sock.close()
                print("Keyboard interrupt")

    def camera_thread(self, device_bool):
        goods_state = 'Y'  # default Y / 없을 경우 N
        active_state = 'A'  # default A / 멈춘 경우 S

        while device_bool is True:
            # Wait for a coherent pair of frames: depth and color
            grabResult = self.cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            cameraContextValue = grabResult.GetCameraContext()
            # print("cameraContextValue : ",cameraContextValue)

            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)
                img = image.GetArray()

                if cameraContextValue < 1:
                    # img0 = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
                    height, width, channel = img.shape
                    print(height, width, channel)
                    color_a = img
                    a_raw = color_a
                    color_a = color_a[roi_y:roi_h, roi_x:roi_x + roi_w]
                    color_a = cv2.resize(color_a, dsize=(640, 640))

                    self.img = color_a


                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # jpg의 별도 파라미터, 0~100 품질 높을수록 좋음 90설정

                    color_result, color_img_encode = cv2.imencode('.jpg', color_a,
                                                                  encode_param)  # encode결과 result에 별도로 저장
                    if color_result == False:
                        print('could not encode image!')
                        quit()

                    try:
                        # if time == time_val:
                        ctype = "CT"
                        ctype = ctype.encode()
                        state = active_state + "@" + goods_state
                        # state = state.encode()
                        color_array_data = np.array(color_img_encode)
                        if color_array_data is None:
                            print('There is no color img data!')
                            serv_sock.close()
                            break
                        color_state = state + "@CA"
                        color_state = color_state.encode()
                        color_stringData = color_array_data.tostring()
                        # size_c = len(color_stringData)
                        # print("size : " ,size_c)

                        self.camera_data = ctype + color_state + (str(len(color_stringData))).encode().ljust(16) + color_stringData
                        self.camera_flag = True

                    except ConnectionResetError as e:
                        print('Disconnected by ' + str(addr))
                        break
                        serv_sock.close()
            self.camera_state = False
            time.sleep(0.5)


    def detect_thread(self,device_bool):
        while device_bool is True:
            if self.camera_state == True:
                if self.img is not None :
                    returnData, ret, pname, d_flag, self.percent = self.detect(self.img)
                    if d_flag == True:
                        print(pname + " 품종이 검출되었습니다")
                        now = datetime.datetime.now()
                        d_str = "DT"
                        d_str = d_str.encode()
                        self.str_array = d_str + pname.encode().ljust(16) + str(self.amount).encode().ljust(
                            2) + str(self.percent).encode().ljust(4)
                        self.detect_data = self.str_array
                        self.A_detect_flag = True
                        self.img = None


    def handle_client(self,clnt_sock, addr) :

        goods_state = 'Y'  # default Y / 없을 경우 N
        active_state = 'A'  # default A / 멈춘 경우 S

        while clnt_sock is not None:
            if self.camera_flag == True :
                if self.camera_data is not None :
                    clnt_sock.sendall(self.camera_data)
                    self.camera_flag = False
                    self.camera_data = None

            if self.A_detect_flag == True:
                if self.detect_data is not None:
                    clnt_sock.sendall(self.detect_data)
                    self.A_detect_flag = False
                    self.detect_data = None
                    print("Detect 데이터 전송완료")

    # 기계 작동유무 확인 함수
    def active_check(self, src1, src2):
        if src1 is None:
            src1 = src2
        # prev_image
        gray_src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
        gray_src1 = cv2.GaussianBlur(gray_src1, (0, 0), 1.0)

        # current_image
        gray_src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        gray_src2 = cv2.GaussianBlur(gray_src2, (0, 0), 1.0)

        dst = cv2.absdiff(gray_src1, gray_src2)
        _, dst_th = cv2.threshold(dst, 15, 255, cv2.THRESH_BINARY)
        dst_roi = dst_th[0: 40, 0: 360]
        goods_roi = dst_th
        move_check = cv2.countNonZero(dst_roi)
        if move_check < move_value and move_check > 10:
            print("ROI_move_value :", move_check)
        goods_check = cv2.countNonZero(goods_roi)
        # print("ROI goods_check :", goods_check)
        # print("ROI_move_value :", move_check)
        return dst, move_check, goods_check


    def open_close_dilate(self,src) :
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel3 = np.ones((3, 3), np.uint8)
        kernel5 = np.ones((5, 5), np.uint8)
        kernel7 = np.ones((7, 7), np.uint8)
        kernel11 = np.ones((11, 11), np.uint8)
        dst = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel11)
        #dst = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel11)
        dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel5)
        #dst = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel5)
        #dst = cv2.dilate(dst, kernel3, iterations=3)
        dst = cv2.dilate(dst, kernel3,iterations=2)
        return dst

    # returns a frame that is the average of all the provided frames
    def bg_average(self,average, images,count):
        cv2.accumulate(images, average)
        average = average / count
        average = np.uint8(average)
        return average

    def color_histo (self,src) :
        yCrCb = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
        # y, Cr, Cb로 컬러 영상을 분리 합니다.
        y, Cr, Cb = cv2.split(yCrCb)
        # y값을 히스토그램 평활화를 합니다.
        # equalizedY = cv2.equalizeHist(y)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalizedY = clahe.apply(y)

        # equalizedY, Cr, Cb를 합쳐서 새로운 yCrCb 이미지를 만듭니다.
        yCrCb2 = cv2.merge([equalizedY, Cr, Cb])
        # 마지막으로 yCrCb2를 다시 BGR 형태로 변경합니다.
        yCrCbDst = cv2.cvtColor(yCrCb2, cv2.COLOR_YCrCb2BGR)
        return yCrCbDst


    def strike_check(self,x) :
        center_x = (int(x[2]) + int(x[0])) /2
        print("센터x 좌표값 : ",center_x)
        if center_x > 300 and center_x < 340 :
            self.strike_flag = True
        else :
            self.strike_flag = False

if __name__ == '__main__':
    xavier = xavier_init()
    try:
        #while device_bool:
        if xavier.device_bool :
            xavier.accept_client()
    finally :
        # Stop streaming
        # Releasing the resource
        xavier.cameras.StopGrabbing()








