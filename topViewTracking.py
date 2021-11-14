import cv2
import numpy as np
import trackingFunctions
import calculateBallPath
import scipy.optimize
import matplotlib.pyplot as plt

vid = cv2.VideoCapture()
vid.open(1, cv2.CAP_DSHOW)
# l_b=np.array([25, 50, 50]) # for mac
# u_b=np.array([50, 220, 220])
l_b=np.array([27, 130, 130])
u_b=np.array([50, 220, 220])
l_b_tape=np.array([150, 130, 130])
u_b_tape=np.array([180, 220, 220])
record_path = False
show_linear_fit = False
show_vertical_line = False
do_linear_fit = False
find_tape = False
find_theta = False
real_dist = 600
centroid_x=[]
centroid_y=[]
tape_x = []
tape_y = []
calibration_ratio = 0


if vid.isOpened(): 
    # get vcap property 
    width  = vid.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    # print("width: ", width, ", height: ", height)
    # width 640 cooresponds to 62 cms at a distance of 62 cms. at a distance of 30.5 cm, a widt of 
    # 640 corresponds to 31.5 cm 

while True:
    key=cv2.waitKey(1)
    ret,frame=vid.read()
    if find_tape:
        frame_dist,y_val = trackingFunctions.get_tape_blob(frame, l_b_tape, u_b_tape, 5)
        if frame_dist != 0:
            calibration_ratio = real_dist/frame_dist
            print("calibration ratio: ", calibration_ratio)
            print("frame_dist: ", frame_dist)
            find_tape = False
 
    # cv2.imshow('frame',frame)

    # get blobs with color frame
    x, y, w, h, mask_ball = trackingFunctions.get_color_blob(frame, l_b, u_b, 5)
    if x != 0 and y != 0 and w != 0 and h != 0:
        centroid_x.append(x)
        centroid_y.append(y)
    if len(centroid_x) > 0:
        for i in range(len(centroid_x)):
            cv2.circle(frame, (centroid_x[i], centroid_y[i]),3,(0,0,255),-1) #red
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)  

    if (do_linear_fit):
        if len(centroid_x) == 1:
            vert_x = centroid_x[0]
            show_vertical_line = True

        if len(centroid_x) >= 2:
            # x_list = np.array(centroid_x); y_list = np.array(centroid_y)
            # fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.linear, x_list,y_list)
            # y_fit = calculateBallPath.linear(x_list, *fit_params)
            # length_centroid = len(x_list//2)
            x1, x2, y1, y2 = centroid_x[0], centroid_x[-1], centroid_y[0], centroid_y[-1]
            m,b = calculateBallPath.calc_linear_line(x1, x2, y1, y2)            
            [x_pos,y_pos] = calculateBallPath.find_line(m,b)     
            show_linear_fit = True
        
    if (show_linear_fit):
        for i in range(len(x_pos)):          
            cv2.circle(frame, (int(x_pos[i]), int(y_pos[i])),2,(0,255,0),-1)
            find_theta = True
    if (show_vertical_line):        
        for i in range(int(height)):
            cv2.circle(frame, (int(vert_x), i),2,(0,255,255),-1)
    if(find_theta):
        theta = trackingFunctions.finding_theta(vert_x,3*height/4,m,b,centroid_y[0]) # centroid_y[0] is the intersection of the two lines       
        # print(theta)
        

    if key==ord('a'):
        # start recording path
        record_path = True
        do_linear_fit = True

    if key == ord('t'):
        find_tape = True

    if key==ord('c'):
        # clear path of centroids
        centroid_x = []
        centroid_y = []
        tape_x = []
        tape_y = []
        show_linear_fit = False
        show_vertical_line = False
    # if key==ord('p'):
    #     # plot parabolic path
    #     print("centroid_x: ", centroid_x)
    #     print("centroid_y: ", centroid_y)
    #     centroid_x = np.array(centroid_x); centroid_y = np.array(centroid_y)
    #     fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, centroid_x,centroid_y)
    #     y_fit = calculateBallPath.parabola(centroid_x, *fit_params)
    #     length_centroid = len(centroid_x//2)
    #     x1, x2, x3, y1, y2, y3 = centroid_x[0], centroid_x[length_centroid//2], centroid_x[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
    #     a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
    #     x,y = calculateBallPath.find_parabola(a,b,c)
    if key == ord('b'):
        isReady = input("Are you ready?")
        if isReady:
            isReady = True

    if key==ord('q'):
        break

    cv2.imshow('frame',frame)
    cv2.imshow("mask_ball",mask_ball)
cv2.waitKey(0)
cv2.destroyAllWindows()