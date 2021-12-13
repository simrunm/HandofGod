import cv2
import numpy as np
import trackingFunctions
import calculateBallPath
import scipy.optimize
import matplotlib.pyplot as plt
import serial
import time
import math
from constants import *
import time
from firmware import InitializeSerial
from firmware import MoveMotors
from firmware import CenterGantry
from firmware import ZeroGantry
l_b_side=np.array([35, 50, 50])
u_b_side=np.array([80, 220, 220])
sideview_centroid_x = []
sideview_centroid_y = []
sideview = cv2.VideoCapture()
sideview.open(1, cv2.CAP_DSHOW)

arduino = InitializeSerial()

def get_color_blob(frame, lower_bound, upper_bound, blob_min_size):
    cx, cy, w, h = 0,0,0,0
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_bound,upper_bound) 
    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        # find largest blob
        max_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour)>cv2.contourArea(max_contour):
                max_contour=contour
        contour=max_contour

        if cv2.contourArea(contour) > blob_min_size:
            # get bounding box
            approx=cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True),True)
            x,y,w,h=cv2.boundingRect(approx)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)
            # get centroid
            M=cv2.moments(contour)
            cx=int(M['m10']//M['m00'])
            cy=int(M['m01']//M['m00'])
            # cv2.circle(frame, (cx,cy),3,(255,0,0),-1)
            return True, cx, cy, w, h, mask
    return False, cx, cy, w, h, mask

while True:
    value=input("Enter command: ")
    ret,sideview_frame=sideview.read()
    cv2.imshow('sideview_frame',sideview_frame)
    # if (len(sideview_centroid_x) > 0):
    #     trackingFunctions.plot_points(sideview_centroid_x, sideview_centroid_y, sideview_frame)
    if value=='z':
        ZeroGantry(arduino)
    if value=='m':
        value=input("Enter motor position: ")
        poses = value.split(",")
        MoveMotors(arduino, (poses[0], poses[1]))
    if value == "a":  # Windows Config
        key=cv2.waitKey(1)
        get_color_blob(sideview_frame,l_b_side, u_b_side, 5)
        blobFound, x, y, w, h, sideview_mask_ball = trackingFunctions.get_color_blob(sideview_frame, l_b_side, u_b_side, 5)
        # ignore x and y points if they are too close to 0
        if not blobFound or np.allclose(x, 0, atol=0.25) or np.allclose(y, 0, atol=0.25):
            pass
        else:                
            sideview_centroid_x.append(x)
            sideview_centroid_y.append(y)
    if value == "p":
        print("x: ", sideview_centroid_x[-1], "y: ", sideview_centroid_y[-1])
    if value=='q':
        break