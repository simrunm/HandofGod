import cv2
import numpy as np
import calculateBallPath # import plot_parabola

import scipy.optimize
import matplotlib.pyplot as plt


vid = cv2.VideoCapture()
vid.open(1, cv2.CAP_DSHOW)
# l_b=np.array([25, 50, 50]) # for mac
# u_b=np.array([50, 220, 220])
l_b=np.array([27, 130, 130])
u_b=np.array([50, 220, 220])
record_path = False
show_parabola_fit = False
do_parabola_fit = False
centroid_x=[]
centroid_y=[]


if vid.isOpened(): 
    # get vcap property 
    width  = vid.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
    # print("width: ", width, ", height: ", height)


while True:
    key=cv2.waitKey(1)
    ret,frame=vid.read()

    # get blobs with color frame
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)
    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # find largest blob
        max_contour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour)>cv2.contourArea(max_contour):
                max_contour=contour
        contour=max_contour

        if cv2.contourArea(contour) > 5:
            # get bounding box
            approx=cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True),True)
            x,y,w,h=cv2.boundingRect(approx)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)

            # get centroid
            M=cv2.moments(contour)
            cx=int(M['m10']//M['m00'])
            cy=int(M['m01']//M['m00'])
            cv2.circle(frame, (cx,cy),3,(255,0,0),-1)
        
        # get path of centroids
        if record_path and cv2.contourArea(contour)>15:
            centroid_x.append(cx)
            centroid_y.append(cy)
    for i in range(len(centroid_x)):
        cv2.circle(frame, (centroid_x[i], centroid_y[i]),3,(0,0,255),-1)
    
    if (do_parabola_fit):
        if len(centroid_x) >=3:
            x_list = np.array(centroid_x); y_list = np.array(centroid_y)
            fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, x_list,y_list)
            y_fit = calculateBallPath.parabola(x_list, *fit_params)
            length_centroid = len(x_list//2)
            x1, x2, x3, y1, y2, y3 = x_list[0], x_list[length_centroid//2], x_list[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
            a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
            [x_pos,y_pos] = calculateBallPath.find_parabola(a,b,c)       
            show_parabola_fit = True
        
    if (show_parabola_fit):
        for i in range(len(x_pos)):
            if 450 < y_pos[i] < 460:
                cv2.circle(frame, (int(x_pos[i]), int(y_pos[i])),2,(255,0,0),-1)
            else:
                cv2.circle(frame, (int(x_pos[i]), int(y_pos[i])),2,(0,255,0),-1)

    if key==ord('a'):
        # start recording path
        record_path = True
        do_parabola_fit = True

    if key==ord('c'):
        # clear path of centroids
        centroid_x = []
        centroid_y = []
        show_parabola_fit = False
    if key==ord('p'):
        # plot parabolic path
        print("centroid_x: ", centroid_x)
        print("centroid_y: ", centroid_y)
        centroid_x = np.array(centroid_x); centroid_y = np.array(centroid_y)
        fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, centroid_x,centroid_y)
        y_fit = calculateBallPath.parabola(centroid_x, *fit_params)
        length_centroid = len(centroid_x//2)
        x1, x2, x3, y1, y2, y3 = centroid_x[0], centroid_x[length_centroid//2], centroid_x[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
        a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
        x,y = calculateBallPath.find_parabola(a,b,c)
    # if key == ord('o'):
    #     centroid_x = [609, 588, 562, 536, 509, 482, 454, 428, 396, 373, 240]
    #     centroid_y = [129, 110, 95, 87, 85, 90, 102, 122, 154, 185, 441]
    #     centroid_x = np.array(centroid_x); centroid_y = np.array(centroid_y)
    #     fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, centroid_x,centroid_y)
    #     y_fit = calculateBallPath.parabola(centroid_x, *fit_params)
    #     length_centroid = len(centroid_x//2)
    #     x1, x2, x3, y1, y2, y3 = centroid_x[0], centroid_x[length_centroid//2], centroid_x[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]
    #     a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)
    #     [x_pos,y_pos] = calculateBallPath.find_parabola(a,b,c)       
    #     show_parabola_fit = True

    if key==ord('q'):
        break

    cv2.imshow('frame',frame)
    cv2.imshow("mask",mask)
cv2.waitKey(0)
cv2.destroyAllWindows()


