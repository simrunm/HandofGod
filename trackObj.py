import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt

vid = cv2.VideoCapture(0)
ret,frame=vid.read()
l_b=np.array([30, 50, 50])# lower hsv bound for red
u_b=np.array([45, 255, 255])# upper hsv bound to red
while ret==True:
    ret,frame=vid.read()
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)
    cv2.imshow('frame',frame)
    cv2.imshow("mask",mask)
    key=cv2.waitKey(1)
    if key==ord('q'):
        break
cv2.waitKey(0)
cv2.destroyAllWindows()