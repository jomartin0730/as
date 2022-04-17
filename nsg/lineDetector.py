# This file is code for find out line from roi image
import cv2
import numpy as np


class lineDetector():
    def __init__(self):
        self.countLines = 0
        self.lineDetectModelSet = {"A011B0084","A011B3834"}

    def isLineDetectModel(self, pname):
        if pname in self.lineDetectModelSet:
            return True
        else:
            return False

    def checkLine(self, cv_img, roi):
        src = cv_img[roi[1]: roi[1] + roi[3], roi[0]: roi[0] + roi[2]]
        rho = 0.0
        theta = 0.0
        count = 0
        canny = cv2.Canny(src, 5000, 1500, apertureSize=5, L2gradient=True)
        # lines = cv2.HoughLines(canny, 0.8, np.pi / 180, 30, srn = 100, stn = 10, min_theta = 0, max_theta = np.pi)
        lines = cv2.HoughLines(canny, 1, np.pi / 180, 50)
        # lines = cv2.HoughLinesP(canny,1,np.pi/180,40,minLineLength=20,maxLineGap=30)
        if lines is not None:
            for i in lines:
                rho, theta = i[0][0], i[0][1]
                #print('rho = '+ str(rho) + ' theta = '+str(theta))
                count = count +1
                #break
        return rho, theta,  count

    def checkLineC(self, cv_img, roi, dimg):
        src = cv_img[roi[1]: roi[1] + roi[3], roi[0]: roi[0] + roi[2]]
        mx = int(roi[0])
        my = int(roi[1])
        
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, 5000, 1500, apertureSize=5, L2gradient=True)
        # lines = cv2.HoughLines(canny, 0.8, np.pi / 180, 30, srn = 100, stn = 10, min_theta = 0, max_theta = np.pi)
        lines = cv2.HoughLines(canny, 1, np.pi / 180, 50)
        angle = 0
        # lines = cv2.HoughLinesP(canny,1,np.pi/180,40,minLineLength=20,maxLineGap=30)
        if lines is not None:
            for i in lines:
                rho, theta = i[0][0], i[0][1]
                a, b = np.cos(theta), np.sin(theta)
                x0, y0 = a * rho, b * rho
                scale = src.shape[0] + src.shape[1] - 30
                x1 = int(x0 + scale * -b)
                y1 = int(y0 + scale * a)
                x2 = int(x0 - scale * -b)
                y2 = int(y0 - scale * a)
                dy = y2 - y1
                dx = x2 - x1
                if dx != 0 and dy != 0:
                    slope = (y2 - y1) / (x2 - x1)
                    angle = np.rad2deg(np.arctan(slope))
                else:
                    angle = 0

                # print('x1 = '+ str(x1) + '  y1='+str(y1) + ' x2='+str(x2)+ ' y2='+str(y2))
                cv2.line(dimg, (mx + int(x0), my + int(y0)), (mx - x2, my - y2), (0, 0, 255), 1)
                cv2.circle(dimg, (mx + int(x0), my + int(y0)), 6, (255, 0, 255), 2, cv2.FILLED)
                cv2.putText(dimg, '{0:0.2f}'.format(angle), (mx + x1+10, my + src.shape[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 1, cv2.LINE_AA)

                # print('rho = '+ str(rho) + '  theta='+str(theta) + ' x='+str(x0)+ ' y0='+str(y0))
                #edge = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
                #cv2.line(edge, (x1, y1), (x2, y2), (0, 255, 255), 2)
                #dimg[roi[1]:roi[3], roi[0]:roi[2]] = edge
                break

        # cv2.imshow('edges', canny)
        return angle
