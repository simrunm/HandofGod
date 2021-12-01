
import cv2
import numpy as np
import trackingFunctions
import calculateBallPath
import scipy.optimize
import matplotlib.pyplot as plt
import serial
import math

sideview = cv2.VideoCapture()
sideview.open(1, cv2.CAP_DSHOW)
topview = cv2.VideoCapture()
topview.open(2, cv2.CAP_DSHOW)
l_b_side=np.array([35, 110, 110])
u_b_side=np.array([80, 220, 220])
l_b_top=np.array([35, 70, 70])
u_b_top=np.array([80, 220, 220])
l_b_tape=np.array([150, 130, 130])
u_b_tape=np.array([180, 220, 220])
record_path = False
found_distance = False
show_top_fit = False
show_side_fit = False
do_fit = False
show_linear_fit = False
show_vertical_line = False
show_horizantal_line = False
find_theta = False
real_dist = 610
real_dist_cam_tape = 300
sideview_centroid_x=[]
sideview_centroid_y=[]
topview_centroid_x=[]
topview_centroid_y=[]
tape_x = []
tape_y = []
real_val = []

# calibration_ratio = 0
calibration_ratio = 0.807
cam_dist = 10 # measure adn change this
megaBoard = serial.Serial('COM7', 9600)

if sideview.isOpened():
    width  = sideview.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = sideview.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    # print("width: ", width, ", height: ", height)
    # width 640 cooresponds to 62 cms at a distance of 62 cms. at a distance of 30.5 cm, a widt of 
    # 640 corresponds to 31.5 cm 

while True:
    key=cv2.waitKey(1)
    ret,sideview_frame=sideview.read()
    ret,topview_frame=topview.read()

    # get blobs with color sideview_frame
    x, y, w, h, sideview_mask_ball = trackingFunctions.get_color_blob(sideview_frame, l_b_side, u_b_side, 5)
    if np.allclose(x, 0, atol=0.25) or np.allclose(y, 0, atol=0.25):
        pass
    else:
        sideview_centroid_x.append(x)
        sideview_centroid_y.append(y)
    if len(sideview_centroid_x) > 0:
        for i in range(len(sideview_centroid_x)):
            cv2.circle(sideview_frame, (sideview_centroid_x[i], sideview_centroid_y[i]),3,(0,0,255),-1) #red
            # cv2.rectangle(sideview_frame,(x,y),(x+w,y+h),(0,255,0),4)  

    # get blobs with color topview_frame
    x, y, w, h, topview_mask_ball = trackingFunctions.get_color_blob(topview_frame, l_b_top, u_b_top, 5)
    if x != 0 and y != 0 and w != 0 and h != 0:
        topview_centroid_x.append(x)
        topview_centroid_y.append(y)
    if len(topview_centroid_x) > 0:
        for i in range(len(topview_centroid_x)):
            cv2.circle(topview_frame, (topview_centroid_x[i], topview_centroid_y[i]),3,(0,0,255),-1) #red
            # cv2.rectangle(topview_frame,(x,y),(x+w,y+h),(0,255,0),4) 

    if (do_fit):
        # sideview   
        if len(sideview_centroid_x) >=3:
            x_list = np.array(sideview_centroid_x); y_list = np.array(sideview_centroid_y)
            fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, x_list,y_list)
            y_fit = calculateBallPath.parabola(x_list, *fit_params)
            length_centroid = len(x_list//2)
            x1, x2, x3, y1, y2, y3 = x_list[0], x_list[length_centroid//2], x_list[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]            
            denom = (x1-x2) * (x1-x3) * (x2-x3);
            if np.allclose(denom, 0, atol=0.25):
                pass
            else:
                a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)        
                [sideview_xpos,sideview_ypos] = calculateBallPath.find_parabola(a,b,c)
                show_side_fit = True
    
        # topview
        if len(topview_centroid_x) == 1:
            vert_x = topview_centroid_x[0]
            show_vertical_line = True
            show_horizantal_line = True
        if len(topview_centroid_x) >= 2:
            x1, x2, y1, y2 = topview_centroid_x[0], topview_centroid_x[-1], topview_centroid_y[0], topview_centroid_y[-1]
            m,b = calculateBallPath.calc_linear_line(x1, x2, y1, y2)            
            [topview_xpos,topview_ypos] = calculateBallPath.find_line(m,b)     
            show_top_fit = True
        
    # if (show_top_fit & show_side_fit):
    if (show_side_fit):
        # sideview
        for i in range(len(sideview_xpos)):
            if y_val - 5 < sideview_ypos[i] < y_val + 5:
                cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(255,0,0),-1)
                # do math to convert sideview_frame x -> real life x
                # print("x-coordinate: ", sideview_xpos[i])
                side_x = sideview_xpos[i]
                real_side_x = sideview_xpos[i]*calibration_ratio # the side coordinate converted into real distances
                print("side x real distance: ", real_side_x)
                real_val.append(real_side_x)
                if len(real_val) >= 30:
                    quit
                    found_distance = True
            else:   
                if not math.isnan(sideview_xpos[i]):        
                    cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(0,255,0),-1)
        # topview
        for i in range(len(topview_xpos)):          
            cv2.circle(topview_frame, (int(topview_xpos[i]), int(topview_ypos[i])),2,(0,255,0),-1)
            find_theta = True
    if (show_vertical_line):        
        for i in range(int(height)):
            cv2.circle(topview_frame, (int(vert_x), i),2,(0,255,255),-1)
    if(find_theta):
        theta = trackingFunctions.finding_theta(vert_x,3*height/4,m,b,topview_centroid_y[0]) # centroid_y[0] is the intersection of the two lines  
        if(found_distance): # if program has determined target x and y
            top_x = trackingFunctions.find_x(theta, real_side_x, cam_dist) # top x is x and side x is y from drawing      
            megaBoard.write(b'top_x')
            megaBoard.write(b',')
            megaBoard.write(b'real_side_x')
            megaBoard.write(b'\n')
            print("x: ", top_x, "y: ", real_side_x)
    if key==ord('a'):
        # start recording path
        record_path = True
        do_fit = True
    if key == ord('t'):
        sideview_frame_dist,y_val = trackingFunctions.get_tape_blob(sideview_frame, l_b_tape, u_b_tape, 5)
        if sideview_frame_dist != 0:
            calibration_ratio = real_dist/sideview_frame_dist
            
            print("calibration ratio: ", calibration_ratio)
            # print("sideview_frame_dist: ", sideview_frame_dist)
            find_tape = False
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
    cv2.imshow('sideview_frame',sideview_frame)
    cv2.imshow('topview_frame',topview_frame)
    cv2.imshow("topview_mask_ball",topview_mask_ball)
    cv2.imshow("sideview_mask_ball",sideview_mask_ball)
cv2.waitKey(0)
cv2.destroyAllWindows()
