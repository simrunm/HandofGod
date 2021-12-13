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
import cmath
import types

def HandOfGod():
    # Windows Config
    sideview = cv2.VideoCapture()
    sideview.open(1, cv2.CAP_DSHOW)
    topview = cv2.VideoCapture()
    topview.open(2, cv2.CAP_DSHOW)

    # Ubuntu Config
    #sideview = cv2.VideoCapture('/dev/video2')
    #topview = cv2.VideoCapture('/dev/video2')

    found_distance = False
    show_top_fit = False
    show_side_fit = False
    do_fit = False
    show_linear_fit = False
    show_vertical_line = False
    show_horizantal_line = False
    isPrint = True
    find_theta = False
    sideview_centroid_x = []
    sideview_centroid_y = []
    topview_centroid_x = []
    topview_centroid_y = []
    predicted_landing_poses = []
    previous_prediction = 0
    current_time = 0
    current_roc = 0
    # importing other neccessary constants from constants.
    # for some reason, constants aren't importing
    l_b_side=np.array([35, 50, 50])
    u_b_side=np.array([80, 220, 220])
    l_b_top=np.array([35, 70, 70])
    u_b_top=np.array([80, 220, 220])
    l_b_tape=np.array([150, 130, 130])
    u_b_tape=np.array([180, 220, 220])
    real_dist = 610 # real life length between pink tape
    calibration_ratio = 1.789 #1.713
    y_val = 364.5 #397.5
    cam_dist = 1516-(610+270)
    timestamp_sideview_centroid = []    

    previous_pred = (185,205)
    # start_time = []
    roc = 0
    roroc_threshold = 10

    if sideview.isOpened():
        width  = sideview.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = sideview.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`

    while True:
        key=cv2.waitKey(1)
        ret,sideview_frame=sideview.read()
        ret,topview_frame=topview.read()

        # Getting red color blobs for sideview and topview               
        
        # SIDEWIEW--------------------------------------------------------------
        blobFound, x, y, w, h, sideview_mask_ball = trackingFunctions.get_color_blob(sideview_frame, l_b_side, u_b_side, 5)
        # ignore x and y points if they are too close to 0
        if not blobFound or np.allclose(x, 0, atol=0.25) or np.allclose(y, 0, atol=0.25):
            pass
        else:
            timestamp_sideview_centroid.append(time.time())    
            sideview_centroid_x.append(x)
            sideview_centroid_y.append(y)
        trackingFunctions.plot_points(sideview_centroid_x, sideview_centroid_y, sideview_frame)

         
        # TOPVIEW --------------------------------------------------------------------
        throwaway, x, y, w, h, topview_mask_ball = trackingFunctions.get_color_blob(topview_frame, l_b_top, u_b_top, 5)
        if x != 0 and y != 0 and w != 0 and h != 0:
            topview_centroid_x.append(x)
            topview_centroid_y.append(y)
        trackingFunctions.plot_points(topview_centroid_x, topview_centroid_y, topview_frame)

        # Finding all the points in the parabola for sideview and a straight line for topview. 
        if (do_fit):
            # SIDEVIEW -------------------------------------------------------------------

            if len(sideview_centroid_x) >=2:
                print("change in time: ", timestamp_sideview_centroid[1] - timestamp_sideview_centroid[0] )
                print(sideview_centroid_x[1])
                v_x = (sideview_centroid_x[1] - sideview_centroid_x[0]) / (timestamp_sideview_centroid[1] - timestamp_sideview_centroid[0])      
                v_y = ((height-sideview_centroid_y[1]) - (height-sideview_centroid_y[0])) / (timestamp_sideview_centroid[1] - timestamp_sideview_centroid[0])
                print("v_x: ", v_x)
                print("v_y: ", v_y)
                print("initial y : ", sideview_centroid_y[0])
                sol1,sol2 = quadratic(-0.5*9.8, v_y, height-sideview_centroid_y[0] - (height - y_val))
                print("sol1: ", sol1, "sol2: ", sol2)
                if sol1 > 0:
                    x_t = v_x * sol1
                elif sol2 > 0:
                    x_t = v_x * sol2
                print(x_t)
                frame_x = x_t + sideview_centroid_x[0]
                
            # SIDEVIEW -------------------------------------------------------------------
          
              
        
            # # TOPVIEW -------------------------------------------------------------------------------------------------       
            if len(topview_centroid_x) == 1:
                vert_x = topview_centroid_x[0]
                show_vertical_line = True
            if len(topview_centroid_x) >= 3:
                x1, x2, y1, y2 = topview_centroid_x[0], topview_centroid_x[-1], topview_centroid_y[0], topview_centroid_y[-1]
                denom = x2-x1
                if not np.allclose(denom, 0, atol=0.01):
                    m,b = calculateBallPath.calc_linear_line(x1, x2, y1, y2)            
                    [topview_xpos,topview_ypos] = calculateBallPath.find_line(m,b)     
                    show_top_fit = True

 
        # TOPVIEW --------------------------------------------------------------------------------------
        if (show_top_fit):
            for i in range(len(topview_xpos)):          
                cv2.circle(topview_frame, (int(topview_xpos[i]), int(topview_ypos[i])),2,(0,255,0),-1)
                find_theta = True
        if (show_vertical_line):
            for i in range(int(height)):
                cv2.circle(topview_frame, (int(vert_x), i),2,(0,255,255),-1)
        if(find_theta):
            theta = trackingFunctions.finding_theta(vert_x,3*height/4,m,b,topview_centroid_y[0]) # centroid_y[0] is the intersection of the two lines  
            if(found_distance): # if program has determined target x and y
                top_x = trackingFunctions.find_x(theta, predicted_landing_poses[-1], cam_dist) # top x is x and side x is y from drawing      
                print("xy: ", convert(top_x, frame_x))
                MoveMotors(arduino, convert(top_x, frame_x))
                return True
           
        # KEYBOARD COMMANDS
        if key==ord('a'):
            do_fit = True
        if key == ord('t'):
            sideview_frame_dist,y_val = trackingFunctions.get_tape_blob(sideview_frame, l_b_tape, u_b_tape, 2)
            if sideview_frame_dist != 0:
                calibration_ratio = real_dist/sideview_frame_dist                
                print("calibration ratio: ", calibration_ratio)
                print("y_val: ", y_val)
        if key==ord('c'):
            # clear path of centroids
            sideview_centroid_x = []
            sideview_centroid_y = []
            sideview_xpos = []
            sideview_ypos = []
            topview_centroid_x = []
            topview_centroid_y = []
            show_top_fit = False
            find_theta = False
            show_vertical_line = False

        if key==ord('q'):
            break

        # displaying everything
        cv2.imshow('sideview_frame',sideview_frame)
        cv2.imshow('topview_frame',topview_frame)
        # cv2.imshow("topview_mask_ball",topview_mask_ball)
        # cv2.imshow("sideview_mask_ball",sideview_mask_ball)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def convert(x,y):
    """
    Convert from real life x and y distance to x, y coordinate on the gantry.

    gantry dimensions:
    370, 410 origin in bottom right corner
    460mm, 500mm

    distance from sideframe edge to gantry 1516
    """
    y = y - 1516
    y = y * (410/460)
    x = x + (460/2)
    x = x * (370/460)
    print("converted x: ", x, "converted y: ", y)
    if (x < 0) or (y < 0):
        return 185,205
    else:
        return int(x),int(y)

def distance_between(prev, current):
    return math.sqrt((current[1]-prev[1])**2 + (current[0]-prev[0])**2)

def quadratic(a, b, c):
    # calculate the discriminant
    d = (b**2) - (4*a*c)

    # find two solutions
    sol1 = (-b-cmath.sqrt(d))/(2*a)
    sol2 = (-b+cmath.sqrt(d))/(2*a)
    return sol1, sol2

def find_real(sol1,sol2):
    if isinstance(sol1, types.ComplexType):
        return sol2
    if isinstance(sol2, types.ComplexType):
        return sol1
    return "both complex"

arduino = InitializeSerial()
ZeroGantry(arduino)
CenterGantry(arduino)
HandOfGod()
