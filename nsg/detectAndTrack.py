import sys
import cv2
import numpy as np
import base64
import os
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
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, strip_optimizer, set_logging)
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized
from utils_ds.parser import get_config
from deep_sort import build_tracker
#import datasets
import datetime
import threading
import socket
import JsonLoader
#import FeatureMatching
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

class Detector:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='best_2.pt', help='model.pt path(s)')
        #parser.add_argument('--weights', nargs='+', type=str, default='best.pt', help='model.pt path(s)')
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
        parser.add_argument("--config_deepsort", type=str, default="./configs/deep_sort.yaml")

        self.opt = parser.parse_args()
        model, imgsz, out, source, weights, view_img, save_txt, device, half, modelc, dataset, save_img, classify = None, None, None, None, None, None, None, None, None, None, None, None, None

        self.FLAG_CONNECTION = False
        self.FLAG_CONNECTION2 = False
        self.FLAG_CLIENT = True
        self.FLAG_CLIENT2 = True

        self.partID = "None"
        self.old_partID = None
        self.working = False
        self.js = JsonLoader.JsonLoader()
        self.json_data = self.js.load_data("detect")
        #self.fm = FeatureMatching.FeatureMatching()
        self.j = 0
        self.xyxy = None
        self.img_size = 640
        self.stride = 32

    def __del__(self):
        print(".....detect end thread.")
        #self.wait()


    def detect_set(self, rno):
        self.out, self.source, self.weights, self.view_img, self.save_txt, self.imgsz, self.deepsort = \
            self.opt.output, self.opt.source, self.opt.weights, self.opt.view_img, self.opt.save_txt, self.opt.img_size, self.opt.config_deepsort
        # self.webcam = self.source.isnumeric() or self.source.startswith(('rtsp://', 'rtmp://', 'http://')) or self.source.endswith('.txt')

        # Initialize
        set_logging()
        self.device = select_device(self.opt.device)

        if os.path.exists(self.out):
            shutil.rmtree(self.out)  # delete output folder
        # ***************************** initialize DeepSORT **********************************
        cfg = get_config()
        cfg.merge_from_file(self.deepsort )

        os.makedirs(self.out)  # make new output folder
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA
        self.deepsort = build_tracker(cfg, self.half)
        # Load model
        if rno == 1 :
            self.weights = 'best.pt'
        else :
            self.weights = 'best_2.pt'
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 model
        self.imgsz = check_img_size(self.imgsz, s=self.model.stride.max())  # check img_size
        if self.half:
            self.model.half()  # to FP16

        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(
                torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()
        # Set Dataloader
        self.working = True
        print('detect set ok')

    # def detect(self, iv,f_label,d,save_img=False):
    def detect(self,imgSrc):
          # Get names and colors

        im0 = None  #return image
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

        #print("pred",pred)
        # Process detections

        for i, det in enumerate(pred):  # detections per image
            s = ''
            im0 = imgSrc
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            # detect 했을 경우
            if det is not None and len(det):
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

                bbox_xywh = xyxy2xywh(det[:, :4]).cpu()
                confs = det[:, 4:5].cpu()

            # ****************************** deepsort ****************************
                outputs = self.deepsort.update(bbox_xywh, confs, im0)                    

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    goods_type = names[int(cls)]
                    #pname = goods_type
                    if conf < 0.5:  # 80%이하는 버림 (수정해야함)
                        continue
                    percent = '%.2f' % (conf)
                    # print(type(percent))
                    percent = float(percent)
                    # print("percent",type(percent))
                    #label = '%s %.2f' % (names[int(cls)], conf)
                    #print("품종 : "+ goods_type + ' ('+str(percent)+')')

                    if old_good is None :
                        old_good = goods_type
                    if old_percent == 0 :
                        old_percent = percent
                    #현재 퍼센트가 더 높은 경우 높은 제품으로 인식

                    if old_percent < percent :
                        old_good = goods_type
                        old_percent = percent
                    else :
                        pass

                    pname = old_good
                    returnData = xyxy
                    self.partID = pname
                    self.xyxy = xyxy

            else:
                outputs = torch.zeros((0, 5))
                detect_check = False
                pass

            #print(f'{s}Done. ({t2 - t1:.3f}s)')
        return returnData, im0, pname, detect_check, outputs


    def create_folder(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("폴더 생성 성공")
        except OSError:
            print('Error: Creating directory. ' + directory)