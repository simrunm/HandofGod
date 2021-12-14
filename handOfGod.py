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
    find_theta = False
    sideview_centroid_x = []
    sideview_centroid_y = []
    topview_centroid_x = []
    topview_centroid_y = []
    predicted_landing_poses = []
    # importing other neccessary constants from constants.
    # for some reason, constants aren't importing
    l_b_side=np.array([35, 50, 50])
    u_b_side=np.array([80, 220, 220])
    l_b_top=np.array([35, 70, 70])
    u_b_top=np.array([80, 220, 220])
    l_b_tape=np.array([150, 130, 130])
    u_b_tape=np.array([180, 220, 220])
    calibration_ratio = 1.789 #1.713
    y_val = 272 
    cam_dist = 1516-(610+270)
    height_over_cam = 0
    start_predicting = False 
 

    if sideview.isOpened():
        width  = sideview.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = sideview.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        print("width: ", width)

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
            sideview_centroid_x.append(x)
            sideview_centroid_y.append(y)
        trackingFunctions.plot_points(sideview_centroid_x, sideview_centroid_y, sideview_frame)

         
        # TOPVIEW --------------------------------------------------------------------
        throwaway, x, y, w, h, topview_mask_ball = trackingFunctions.get_color_blob(topview_frame, l_b_top, u_b_top, 5)
        if x != 0 and y != 0 and w != 0 and h != 0:
            topview_centroid_x.append(x)
            topview_centroid_y.append(y)
        trackingFunctions.plot_points(topview_centroid_x, topview_centroid_y, topview_frame)

        # Finding height
        if len(topview_centroid_x) > 0 and height_over_cam == 0:
            height_over_cam = sideview_centroid_y[-1]
            print("height", height_over_cam)

        # Finding all the points in the parabola for sideview and a straight line for topview. 
        if (do_fit):
            # SIDEVIEW -------------------------------------------------------------------
            if len(sideview_centroid_x) > 3:
                show_side_fit = True
                len_centroid_x = len(sideview_centroid_x)
                x1, x2, x3, y1, y2, y3 = sideview_centroid_x[0], sideview_centroid_x[len_centroid_x//2], sideview_centroid_x[-1], sideview_centroid_y[0], sideview_centroid_y[len_centroid_x//2], sideview_centroid_y[-1] 
                denom = (x1-x2) * (x1-x3) * (x2-x3)
                if not np.allclose(denom, 0, atol=0.25):
                    a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)        
                    [sideview_xpos,sideview_ypos] = calculateBallPath.find_parabola(a,b,c)
                    if len(sideview_centroid_x) >= 12:
                        start_predicting = True
        
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

        # Plotting all the calculated points and finding the x and y coordinates
        # SIDEVIEW -----------------------------------------------------------------
        if (show_side_fit):            
            for i in range(500):
                if not math.isnan(sideview_xpos[i]):        
                    cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(0,255,0),-1)
        if (start_predicting):            
            for i in range(300):
                if y_val - 5 < sideview_ypos[i] < y_val + 5:
                    cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(255,0,0),-1)
                    # print("frame x: ", sideview_xpos[i])
                    real_side_x = convert(196, 89, sideview_xpos[i])# the side coordinate converted into real distances
                    # print("gantry: ", real_side_x)
                    predicted_landing_poses.append(real_side_x)
                # Plotting all the points parabola points that are not the end coordinate
                else:
                    if not math.isnan(sideview_xpos[i]):        
                        cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(0,255,0),-1)
                if len(predicted_landing_poses) != 0:
                    found_distance = True
                    print("finished side prediction")

        # TOPVIEW --------------------------------------------------------------------------------------
        if (show_top_fit):
            for i in range(len(topview_xpos)):          
                cv2.circle(topview_frame, (int(topview_xpos[i]), int(topview_ypos[i])),2,(0,255,0),-1)
                find_theta = True
        if (show_vertical_line):
            for i in range(int(height)):
                cv2.circle(topview_frame, (int(vert_x), i),2,(0,255,255),-1)
        if(find_theta):
            print("find theta now")
            if(found_distance): # if program has determined target x and y
                predicted_y = predicted_landing_poses[-1] -50
                if (predicted_y < 0):
                    predicted_y = 0
                theta = trackingFunctions.finding_theta(vert_x,3*height/4,m,b,topview_centroid_y[0]) # centroid_y[0] is the intersection of the two lines  
                print("theta: ", theta)
                gradient = trackingFunctions.find_gradient(height_over_cam)
                print("Relationship between frame and gantry points: ", gradient)
                x_int = trackingFunctions.finding_x_int(height_over_cam, theta)
                print("The x intercept: ", x_int)
                x_change = trackingFunctions.get_x_change(predicted_y, theta)
                print("X Change: ", x_change)
                x_start = trackingFunctions.finding_x_start(x_int, topview_centroid_y[0], gradient)
                print("Frame X: ", topview_centroid_y[0], "X Start: ", x_start)
                # top_x = trackingFunctions.find_x(theta, predicted_y, cam_dist) # top x is x and side x is y from drawing      
                predicted_x = x_start + x_change  
                print("finished top prediction")              
                print("Predicted x: ", predicted_x, "y: ", predicted_y)
                MoveMotors(arduino, (int(predicted_x), int(predicted_y)))
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
            show_side_fit= False
            find_theta = False
            show_vertical_line = False
            start_predicting = False
        if key==ord('p'):
            print("x: ", sideview_centroid_x[-1], "y: ", sideview_centroid_y[-1])

        if key==ord('q'):
            break

        # displaying everything
        cv2.imshow('sideview_frame',sideview_frame)
        cv2.imshow('topview_frame',topview_frame)
        # cv2.imshow("topview_mask_ball",topview_mask_ball)
        # cv2.imshow("sideview_mask_ball",sideview_mask_ball)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def convert(start_frame, end_frame, prediction):
    """
    Convert from real life x and y distance to x, y coordinate on the gantry.

    gantry dimensions:
    370, 410 origin in bottom right corner
    460mm, 500mm
    412, 468, 520 most recent 12/10

    distance from sideframe edge to gantry 1516
    """
    gantry_pred = (abs(prediction - start_frame) * 410) / (start_frame - end_frame)
    return gantry_pred

def find_gantry_x():
    """at 410 gantry y- 9 degrees is the furthest point
        at middle 205 gantry - 11 degrees is the furthest
        at the start 0 gantry - 13 degrees is teh furthest
    """
    pass

arduino = InitializeSerial()
ZeroGantry(arduino)
CenterGantry(arduino)
HandOfGod()
