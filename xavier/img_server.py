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
import pymysql
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
from yolo_utils.general import check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, plot_one_box, strip_optimizer, set_logging
from yolo_utils.torch_utils import select_device, load_classifier, time_synchronized

#old_pname = None

# Number of images to be grabbed.
countOfImagesToGrab = 10

maxCamerasToUse = 2

HOST = '192.168.0.2'
#HOST = '172.17.0.103'
PORT = 9999

# ROI 전체 사진 짜르기 camera A 1280 x 620
roi_x = 405
roi_y = 0
roi_w = 640
roi_h = 640

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

class xavier_init() :
    def __init__(self):
        self.strike_flag = False
        self.detect_flag = False

        self.db_connect()
        self.camera_set()
        self.detect_set()

    def db_connect(self):
        #host = "172.17.1.70"
        host = "192.9.226.32"
        passwd = 'aA!12345'
        user = 'mgt'
        db = 'maviz'
        try:
            self.conn = pymysql.connect(host=host, user=user, password=passwd, db=db, charset='utf8')
            self.curs = self.conn.cursor()
            print("db connect success")
        except Exception as e:
            print('Connect Error : ', e)


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

        out, source, weights, view_img, save_txt, imgsz = \
            self.opt.output, self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size
        self.webcam = source.isnumeric() or source.startswith(('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')

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
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()

        # Set Dataloader
        # vid_path, vid_writer = None, None
        if self.webcam:
            view_img = True
            cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(source, img_size=imgsz)
        else:
            save_img = True
            self.dataset = LoadImages(source, img_size=imgsz)

    def detect_act(self,imgSrc,goods_state):

        filename = "detect.png"
        path = "./detect"
        cv2.imwrite(os.path.join(path, filename), imgSrc)
        #resultimg = None
        #pname = None

        if goods_state == "Y":
            im0, pname = self.detect(imgSrc)

        return im0,pname


    def detect(self,save_img=False):
        # Get names and colors
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        #colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
        im0 = None
        pname = None
        # Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, self.imgsz, self.imgsz), device=self.device)  # init img
        _ = self.model(img.half() if self.half else img) if self.device.type != 'cpu' else None  # run once
        for path, img, im0s, vid_cap in self.dataset:
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
                pred = apply_classifier(pred, self.modelc, img, im0s)

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                if self.webcam:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                save_path = str(Path(self.out) / Path(p).name)
                txt_path = str(Path(self.out) / Path(p).stem) + ('_%g' % self.dataset.frame if self.dataset.mode == 'video' else '')
                # s += '%gx%g ' % img.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    # print("type : " , type(det))
                    # print("det : " , det)
                    goods_type = None
                    percent = None
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += '%g %s, ' % (n, names[int(c)])  # add to string

                    old_percent = 0
                    old_good = "None"
                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if self.save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format
                        percent = '%.2f' % (conf)

                        #print(cls)
                        if self.save_img or self.view_img:  # Add bbox to image
                            goods_type = names[int(cls)]
                            #percent = '%.2f' % (conf)
                            label = '%s %.2f' % (names[int(cls)], conf)

                            if percent > 0.70 :
                                if old_percent == 0:
                                    old_percent = percent
                                if old_percent < percent:
                                    old_good = goods_type
                                    old_percent = percent
                                else :
                                    pass
                            #pname = old_good


                                #print(percent)
                            # plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                            plot_one_box(xyxy, im0, label=label, color=(0, 0, 255), line_thickness=3)

                    self.strike_check(xyxy)

                    #print("names : ", names[int(cls)])
                    #pname = names[int(cls)]
                    pname = old_good
                    percent = float(percent)
                    print("확률 : ", percent)
                    print()



                    if old_pname is None :
                        old_pname = pname

                    print("old pname : ",old_pname)
                    print("pname : ",pname)

                    if self.strike_check :
                        print("strike")
                        if pname != old_pname:
                            print("pname != old_pname")
                            try:
                                sql = """SELECT count(*) FROM product_log WHERE pcode = %s"""
                                args = (pname)
                                self.curs.execute(sql, args)
                                rows = self.curs.fetchall()
                                result = rows[0][0]
                                if result > 0:
                                    check_flag = False
                                else:
                                    check_flag = True
                                    print("data 없음")

                                if check_flag :
                                    sql = """INSERT INTO product_log (laneNumber,pcode,startTime) VALUES (%s,%s,%s)"""
                                    laneNumber = "1"
                                    now = datetime.datetime.now()
                                    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                                    args = (laneNumber, pname, nowDatetime)
                                    self.curs.execute(sql, args)
                                    self.conn.commit()
                                    print("insert complete")
                                else :
                                    pass


                                sql = """SELECT count(*) FROM product_log WHERE pcode = %s"""
                                args = (old_pname)
                                self.curs.execute(sql, args)
                                rows = self.curs.fetchall()
                                result = rows[0][0]
                                if result > 0:
                                    check_result = True
                                    print("data 중복")
                                else:
                                    check_result = False

                                if check_result :
                                    sql = """UPDATE product_log SET endTime = %s WHERE pcode = %s"""
                                    now = datetime.datetime.now()
                                    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
                                    args = (nowDatetime,old_pname)
                                    self.curs.execute(sql, args)
                                    self.conn.commit()

                            finally:
                                pass
                            #insert_log(pname)
                            print("db insert check")
                    old_pname = pname

                    detect_flag = True
                else:
                    print("detect 없음")
                    detect_flag = False

                print(s)
                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))

                # Stream results
                if self.view_img:
                    cv2.imshow(p, im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if self.save_img:
                    if self.dataset.mode == 'images':
                        cv2.imwrite(save_path, im0)
                    else:
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer

                            fourcc = 'mp4v'  # output video codec
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                        vid_writer.write(im0)
        return im0,pname

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
            except KeyboardInterrupt:
                serv_sock.close()
                print("Keyboard interrupt")
            t = threading.Thread(target=self.handle_client, args=(clnt_sock, addr))
            t.daemon = True
            t.start()


    def handle_client(self,clnt_sock, addr) :
        color_a = None
        color_b = None
        no_bg = None

        active_flag = True

        goods_state = 'Y'  # default Y / 없을 경우 N
        active_state = 'A'  # default A / 멈춘 경우 S

        #time = 0
        #time_val = 4

        first_frame = None

        prevFrame = None
        oldTime = None

        while clnt_sock is not None:
            # Wait for a coherent pair of frames: depth and color
            grabResult = self.cameras.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            # When the cameras in the array are created the camera context value
            # is set to the index of the camera in the array.
            # The camera context is a user settable value.
            # This value is attached to each grab result and can be used
            # to determine the camera that produced the grab result.
            cameraContextValue = grabResult.GetCameraContext()

            # Print the index and the model name of the camera.
            # print("Camera ", cameraContextValue, ": ", cameras[cameraContextValue].GetDeviceInfo().GetModelName())

            # Now, the image data can be processed.
            # print("GrabSucceeded: ", grabResult.GrabSucceeded())
            # print("SizeX: ", grabResult.GetWidth())
            # print("SizeY: ", grabResult.GetHeight())
            # img = grabResult.GetArray()
            # print("Gray value of first pixel: ", img[0, 0])

            if grabResult.GrabSucceeded():
                #time += 1
                image = self.converter.Convert(grabResult)
                img = image.GetArray()
                # color_a = img
                # print(time)
                # print("cameraContextValue : " + str(cameraContextValue))
                if cameraContextValue < 1:
                    # img0 = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
                    img0 = cv2.resize(img, dsize=(1280, 640))
                    color_a = img0
                    a_raw = color_a
                    color_a = color_a[roi_y:roi_h, roi_x:roi_x + roi_w]
                    # color_a = img
                    # print( cameraContextValue, img0.shape )
                    # cv2.imshow('title-0', img0)
                elif cameraContextValue < 2:
                    img1 = cv2.resize(img, dsize=(1280, 640))
                    color_b = img1
                    # color_b = color_b[b_y: b_h, b_x: b_w]
                    # img1 = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
                    # print( cameraContextValue, img1.shape )
                    # cv2.imshow('title-1', img1)
                    # no_bg = img

                else:
                    pass
                # color_a = img
                # print(color_a)
                if color_a is not None and color_b is not None:
                    # 기계 이동 체크
                    #if time % 2 == 0:
                    dst, move_check, goods_check = active_check(first_frame, color_a)
                    first_frame = color_a
                    if goods_check > goods_value:
                        goods_bool = True
                        goods_state = 'Y'
                        active_flag = True
                        active_state = 'A'
                    else:
                        goods_bool = False
                        goods_state = 'N'
                        if goods_check != 0:
                            print("goods_check : " + str(goods_check))
                        active_flag = False
                        active_state = 'S'

                    a_raw = color_histo(a_raw)
                    a_histo = color_histo(color_a)
                    b_histo = color_histo(color_b)
                    hsv = cv2.cvtColor(a_histo, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, (50, 150, 0), (70, 255, 255))
                    # no_bg = cv2.copyTo(a_histo, mask)
                    cv2.bitwise_not(mask, mask)
                    no_bg = cv2.bitwise_and(a_histo, a_histo, mask=mask)

                    low_green = np.array([50, 150, 0])
                    high_green = np.array([70, 255, 255])
                    imgHSV = cv2.cvtColor(b_histo, cv2.COLOR_BGR2HSV)
                    bmask = cv2.inRange(imgHSV, low_green, high_green)
                    bmask = ~bmask
                    blur_img = cv2.GaussianBlur(bmask, (3, 3), 0)
                    ret, thresh_img = cv2.threshold(blur_img, 16, 255, cv2.THRESH_BINARY)
                    # 'THRESH_BINARY', 'THRESH_BINARY_INV', 'THRESH_MASK', 'THRESH_OTSU', 'THRESH_TOZERO', 'THRESH_TOZERO_INV', 'THRESH_TRIANGLE', 'THRESH_TRUNC'
                    thresh1_img = cv2.dilate(thresh_img, (5, 5), iterations=2)
                    thresh2_img = cv2.erode(thresh1_img, (5, 5), iterations=3)
                    mask_roi = thresh2_img[70:200, 600:1050]
                    check = cv2.countNonZero(mask_roi)

                    if check < 10000:
                        print("check : ", check)
                        print("새로운 바 진입중\n")

                    filename = "detect.png"
                    path = "./detect"
                    cv2.imwrite(os.path.join(path, filename), a_raw)
                    if goods_state == "Y":
                        ret,pname = detect_act(color_a, goods_state)

                    #print("detect_flag : ",detect_flag)
                    if detect_flag == True:
                        print( pname+ "품종이 검출되었습니다")
                        det_img = ret
                    #else :
                        #print("검출된 품종이 없습니다")

                    prevtime = time.time()
                    #opticalFlow(a_raw,prevtime,prevFrame,oldTime)
                    oldTime = prevtime
                    prevFrame = a_raw

                    active_flag_old = active_flag 

                    # print(cameraContextValue, img.shape)
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]  # jpg의 별도 파라미터, 0~100 품질 높을수록 좋음 90설정

                    color_result, color_img_encode = cv2.imencode('.jpg', a_histo, encode_param)  # encode결과 result에 별도로 저장
                    if color_result == False:
                        print('could not encode image!')
                        quit()

                    colorb_result, colorb_img_encode = cv2.imencode('.jpg', b_histo,
                                                                    encode_param)  # encode결과 result에 별도로 저장
                    if colorb_result == False:
                        print('could not encode image!')
                        quit()


                    try:
                        #if time == time_val:
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
                        clnt_sock.sendall(
                            color_state + (str(len(color_stringData))).encode().ljust(16) + color_stringData)

                        # color_b
                        colorb_array_data = np.array(colorb_img_encode)
                        if colorb_array_data is None:
                            print('There is no color img data!')
                            serv_sock.close()
                            break
                        colorb_state = state + "@CB"
                        colorb_state = colorb_state.encode()
                        colorb_stringData = colorb_array_data.tostring()
                        clnt_sock.sendall(
                            colorb_state + (str(len(colorb_stringData))).encode().ljust(16) + colorb_stringData)

                        # depth
                        if detect_flag == True:
                            depth_result, depth_img_encode = cv2.imencode('.jpg', det_img,
                                                                          encode_param)  # encode결과 result에 별도로 저장
                            # depth_result, depth_img_encode = cv2.imencode('.jpg', color_b, encode_param)  # encode결과 result에 별도로 저장
                            if depth_result == False:
                                print('could not encode image!')
                                quit()
                            depth_array_data = np.array(depth_img_encode)
                            if depth_array_data is None:
                                print('There is no depth img data!')
                                serv_sock.close()
                                break
                            depth_state = state + "@DA"
                            depth_state = depth_state.encode()
                            depth_stringData = depth_array_data.tostring()
                            clnt_sock.sendall(
                                depth_state + (str(len(depth_stringData))).encode().ljust(16) + depth_stringData)
                        #time = 0
                    except ConnectionResetError as e:
                        print('Disconnected by ' + str(addr))
                        break
                        serv_sock.close()



    #기계 작동유무 확인 함수
    def active_check (self,src1, src2) :
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
        dst_roi = dst_th[0: 40 , 0: 360]
        goods_roi = dst_th
        move_check = cv2.countNonZero(dst_roi)
        if move_check < move_value and move_check > 10:
            print("ROI_move_value :", move_check)
        goods_check = cv2.countNonZero(goods_roi)
        #print("ROI goods_check :", goods_check)
        #print("ROI_move_value :", move_check)
        return dst, move_check,goods_check

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






