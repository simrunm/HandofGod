import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt

vid = cv2.VideoCapture(0)
ret,frame=vid.read()
l_b=np.array([30, 50, 50])
u_b=np.array([45, 255, 255])
while ret==True:
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
    
    cv2.imshow('frame',frame)
    cv2.imshow("mask",mask)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break
cv2.waitKey(0)
cv2.destroyAllWindows()
