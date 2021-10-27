import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt

# img = cv2.imread('testimg.png')
# cv2.imshow('image',img)
# cv2.waitKey()

vid = cv2.VideoCapture(0)
while(True):
    ret, frame = vid.read()     # Capture the video frame by frame
    cv2.imshow('frame', frame)  # Display the resulting frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()
cv2.destroyAllWindows()