import cv2
import numpy as np
import math

def get_color_blob(frame, lower_bound, upper_bound, blob_min_size):
    x, y, w, h = 0,0,0,0
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
            # cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)
            # get centroid
            M=cv2.moments(contour)
            cx=int(M['m10']//M['m00'])
            cy=int(M['m01']//M['m00'])
            # cv2.circle(frame, (cx,cy),3,(255,0,0),-1)
        return x, y, w, h, mask
    return x, y, w, h, mask

def get_tape_blob(frame, lower_bound, upper_bound, blob_min_size):
    x_vals = []
    y_vals = []
    frame_dist = 0
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,lower_bound,upper_bound) 
    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        # find largest blob
        tape_blobs = []
        for contour in contours:
            if cv2.contourArea(contour)>blob_min_size:
                tape_blobs.append(contour)

        if len(tape_blobs) == 2:
            for i in range(len(tape_blobs)):
                # get bounding box
                approx=cv2.approxPolyDP(tape_blobs[i], 0.01*cv2.arcLength(tape_blobs[i],True),True)
                x,y,w,h=cv2.boundingRect(approx)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)
                # get centroid
                M=cv2.moments(tape_blobs[i])
                cx=int(M['m10']//M['m00'])
                cy=int(M['m01']//M['m00'])
                cv2.circle(frame, (cx,cy),3,(255,0,0),-1)
                x_vals.append(cx)
                y_vals.append(cy)
            y_val = (y_vals[0] + y_vals[1])/2
            frame_dist = x_vals[1] - x_vals[0]
        cv2.imshow("mask_tape",mask)
    return abs(frame_dist), y_val

def finding_theta(x_vert, y_vert,m,b,int_line):
    y_dist = abs(y_vert - int_line)
    x = (y_vert - b)/m
    x_dist = abs(x_vert - x)
    theta = np.arctan(x_dist/y_dist)
    return math.degrees(theta)

