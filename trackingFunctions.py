import cv2

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
    return 0,0,0,0, mask