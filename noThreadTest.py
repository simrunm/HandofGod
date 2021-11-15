import cv2
import numpy as np
import trackingFunctions
import calculateBallPath
import scipy.optimize
import matplotlib.pyplot as plt

sideview = cv2.VideoCapture()
sideview.open(1, cv2.CAP_DSHOW)
topview = cv2.VideoCapture()
topview.open(0, cv2.CAP_DSHOW)
# l_b=np.array([25, 50, 50]) # for mac
# u_b=np.array([50, 220, 220])
l_b=np.array([27, 130, 130])
u_b=np.array([50, 220, 220])
l_b_tape=np.array([150, 130, 130])
u_b_tape=np.array([180, 220, 220])
record_path = False
show_fit = False
do_fit = False
show_linear_fit = False
show_vertical_line = False
find_theta = False
find_tape = False
real_dist = 600
sideview_centroid_x=[]
sideview_centroid_y=[]
topview_centroid_x=[]
topview_centroid_y=[]
tape_x = []
tape_y = []
calibration_ratio = 0

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
    if find_tape:
        sideview_frame_dist,y_val = trackingFunctions.get_tape_blob(sideview_frame, l_b_tape, u_b_tape, 5)
        if sideview_frame_dist != 0:
            calibration_ratio = real_dist/sideview_frame_dist
            print("calibration ratio: ", calibration_ratio)
            print("sideview_frame_dist: ", sideview_frame_dist)
            find_tape = False

    # get blobs with color sideview_frame
    x, y, w, h, sideview_mask_ball = trackingFunctions.get_color_blob(sideview_frame, l_b, u_b, 5)
    if x != 0 and y != 0 and w != 0 and h != 0:
        sideview_centroid_x.append(x)
        sideview_centroid_y.append(y)
    if len(sideview_centroid_x) > 0:
        for i in range(len(sideview_centroid_x)):
            cv2.circle(sideview_frame, (sideview_centroid_x[i], sideview_centroid_y[i]),3,(0,0,255),-1) #red
            cv2.rectangle(sideview_frame,(x,y),(x+w,y+h),(0,255,0),4)  

    # get blobs with color topview_frame
    x, y, w, h, topview_mask_ball = trackingFunctions.get_color_blob(topview_frame, l_b, u_b, 5)
    if x != 0 and y != 0 and w != 0 and h != 0:
        topview_centroid_x.append(x)
        topview_centroid_y.append(y)
    if len(topview_centroid_x) > 0:
        for i in range(len(topview_centroid_x)):
            cv2.circle(topview_frame, (topview_centroid_x[i], topview_centroid_y[i]),3,(0,0,255),-1) #red
            cv2.rectangle(topview_frame,(x,y),(x+w,y+h),(0,255,0),4) 

    if (do_fit):
        # sideview   
        if len(sideview_centroid_x) >=3:
            x_list = np.array(sideview_centroid_x); y_list = np.array(sideview_centroid_y)
            fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, x_list,y_list)
            y_fit = calculateBallPath.parabola(x_list, *fit_params)
            length_centroid = len(x_list//2)
            x1, x2, x3, y1, y2, y3 = x_list[0], x_list[length_centroid//2], x_list[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
            a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)            
            [sideview_xpos,sideview_ypos] = calculateBallPath.find_parabola(a,b,c)
        
        # topview
        if len(topview_centroid_x) == 1:
            vert_x = topview_centroid_x[0]
            show_vertical_line = True
        if len(topview_centroid_x) >= 2:
            x1, x2, y1, y2 = topview_centroid_x[0], topview_centroid_x[-1], topview_centroid_y[0], topview_centroid_y[-1]
            m,b = calculateBallPath.calc_linear_line(x1, x2, y1, y2)            
            [topview_xpos,topview_ypos] = calculateBallPath.find_line(m,b)     
            show_fit = True
        
    if (show_fit):
        # sideview
        for i in range(len(sideview_xpos)):
            if y_val - 5 < sideview_ypos[i] < y_val + 5:
                cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(255,0,0),-1)
                # do math to convert sideview_frame x -> real life x
                print("x-coordinate: ", sideview_xpos[i])
                real_x = sideview_xpos[i]*calibration_ratio
                # print("real life pose: ", sideview_xpos[i]*calibration_ratio)
            else:            
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
        # print(theta)

    if key==ord('a'):
        # start recording path
        record_path = True
        do_parabola_fit = True
    if key == ord('t'):
        find_tape = True
    if key==ord('c'):
        # clear path of centroids
        sideview_centroid_x = []
        sideview_centroid_y = []
        tape_x = []
        tape_y = []
        show_parabola_fit = False
    if key==ord('p'):
        # plot parabolic path
        print("sideview_centroid_x: ", sideview_centroid_x)
        print("sideview_centroid_y: ", sideview_centroid_y)
        sideview_centroid_x = np.array(sideview_centroid_x); sideview_centroid_y = np.array(sideview_centroid_y)
        fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, sideview_centroid_x,sideview_centroid_y)
        y_fit = calculateBallPath.parabola(sideview_centroid_x, *fit_params)
        length_centroid = len(sideview_centroid_x//2)
        x1, x2, x3, y1, y2, y3 = sideview_centroid_x[0], sideview_centroid_x[length_centroid//2], sideview_centroid_x[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
        a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
        x,y = calculateBallPath.find_parabola(a,b,c)
    if key == ord('b'):
        isReady = input("Are you ready?")
        if isReady:
            isReady = True
    if key==ord('q'):
        break

    cv2.imshow('sideview_frame',sideview_frame)
    cv2.imshow('topview_frame',topview_frame)
    cv2.imshow("topview_mask_ball",topview_mask_ball)
    cv2.imshow("sideview_mask_ball",sideview_mask_ball)
cv2.waitKey(0)
cv2.destroyAllWindows()
