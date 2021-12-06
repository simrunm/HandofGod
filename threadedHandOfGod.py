import cv2
import numpy as np
import trackingFunctions
import calculateBallPath
import scipy.optimize
import matplotlib.pyplot as plt
import serial
import time
import math
import constants
import time
from imutils.video import WebcamVideoStream


def HandOfGod():
    topview = WebcamVideoStream(src=0).start()
    sideview = WebcamVideoStream(src=1).start()
    found_distance = False
    show_top_fit = False
    show_side_fit = False
    do_fit = False
    show_linear_fit = False
    show_vertical_line = False
    show_horizantal_line = False
    isPrint = True
    find_theta = False
    sideview_centroid_x = []
    sideview_centroid_y = []
    topview_centroid_x = []
    topview_centroid_y = []
    predicted_landing_poses = []
    calibration_ratio = 1.713
    y_val = 397.5

    while True:
        key=cv2.waitKey(1)
        topview_frame = topview.read()
        sideview_frame = sideview.read()

        # Getting red color blobs for sideview and topview               
        
        # SIDEWIEW--------------------------------------------------------------
        blobFound, x, y, w, h, sideview_mask_ball = trackingFunctions.get_color_blob(sideview_frame, constants.l_b_side, constants.u_b_side, 5)
        # ignore x and y points if they are too close to 0
        if not blobFound or np.allclose(x, 0, atol=0.25) or np.allclose(y, 0, atol=0.25):
            pass
        else:
            sideview_centroid_x.append(x)
            sideview_centroid_y.append(y)
        trackingFunctions.plot_points(sideview_centroid_x, sideview_centroid_y, sideview_frame)
         
        # TOPVIEW --------------------------------------------------------------------
        throwaway, x, y, w, h, topview_mask_ball = trackingFunctions.get_color_blob(topview_frame, constants.l_b_top, constants.u_b_top, 5)
        if x != 0 and y != 0 and w != 0 and h != 0:
            topview_centroid_x.append(x)
            topview_centroid_y.append(y)
        trackingFunctions.plot_points(topview_centroid_x, topview_centroid_y, topview_frame)

        # Finding all the points in the parabola for sideview and a straight line for topview. 
        if (do_fit):
            # SIDEVIEW -------------------------------------------------------------------
            if len(sideview_centroid_x) >=3:
                # start_time.append(time.time())              
                x_list = np.array(sideview_centroid_x); y_list = np.array(sideview_centroid_y)
                fit_params, pcov = scipy.optimize.curve_fit(calculateBallPath.parabola, x_list,y_list)
                y_fit = calculateBallPath.parabola(x_list, *fit_params)
                length_centroid = len(x_list//2)
                x1, x2, x3, y1, y2, y3 = x_list[0], x_list[length_centroid//2], x_list[length_centroid - 1], y_fit[0], y_fit[length_centroid//2], y_fit[length_centroid - 1]            
                denom = (x1-x2) * (x1-x3) * (x2-x3)
                if not np.allclose(denom, 0, atol=0.25):
                    a,b,c = calculateBallPath.calc_parabola_vertex(x1, x2, x3, y1, y2, y3)        
                    [sideview_xpos,sideview_ypos] = calculateBallPath.find_parabola(a,b,c)
                    show_side_fit = True
        
            # # TOPVIEW -------------------------------------------------------------------------------------------------       
            # if len(topview_centroid_x) == 1:
            #     vert_x = topview_centroid_x[0]
            #     show_vertical_line = True
            #     show_horizantal_line = True
            # if len(topview_centroid_x) >= 2:
            #     x1, x2, y1, y2 = topview_centroid_x[0], topview_centroid_x[-1], topview_centroid_y[0], topview_centroid_y[-1]
            #     m,b = calculateBallPath.calc_linear_line(x1, x2, y1, y2)            
            #     [topview_xpos,topview_ypos] = calculateBallPath.find_line(m,b)     
            #     show_top_fit = True

        # Plotting all the calculated points and finding the x and y coordinates
        # SIDEVIEW -----------------------------------------------------------------
        if (show_side_fit):            
            for i in range(len(sideview_xpos)):
                if y_val - 5 < sideview_ypos[i] < y_val + 5:
                    cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(255,0,0),-1)
                    real_side_x = sideview_xpos[i]*calibration_ratio # the side coordinate converted into real distances
                    # print("side x real distance: ", real_side_x)
                    predicted_landing_poses.append(real_side_x)

                    # if end time - start time is greater than two seconds, return last point
                if len(predicted_landing_poses) > 20:
                    return 100, predicted_landing_poses[-1]

                    # if found_distance == False:
                    # if predicted landing pose has converged
                    # convergence_threshold = 30
                    # if blobFound:
                    #     roc = trackingFunctions.convergence_check(previous_prediction, real_side_x, current_time, blobFound)
                    #     if (abs(current_roc-roc) < convergence_threshold):
                    #         print("we have converged")
                    #         return (100,real_side_x)
                    # # if hasn't converged
                    # else:
                    #     current_time = time.time()
                    #     previous_prediction = real_side_x
                    #     current_roc = roc
                    
                    # TODO Find a way to send over a good final point and return it here
                    # if len(real_val) >= 30:
                    #     return True
                    #     found_distance = True

                # Plotting all the points parabola points that are not the end coordinate
                else:   
                    if not math.isnan(sideview_xpos[i]):        
                        cv2.circle(sideview_frame, (int(sideview_xpos[i]), int(sideview_ypos[i])),2,(0,255,0),-1)
        
        # TOPVIEW --------------------------------------------------------------------------------------
        #     for i in range(len(topview_xpos)):          
        #         cv2.circle(topview_frame, (int(topview_xpos[i]), int(topview_ypos[i])),2,(0,255,0),-1)
        #         find_theta = True
        # if (show_vertical_line):        
        #     for i in range(int(height)):
        #         cv2.circle(topview_frame, (int(vert_x), i),2,(0,255,255),-1)
        # if(find_theta):
        #     theta = trackingFunctions.finding_theta(vert_x,3*height/4,m,b,topview_centroid_y[0]) # centroid_y[0] is the intersection of the two lines  
        #     if(found_distance): # if program has determined target x and y
        #         top_x = trackingFunctions.find_x(theta, real_side_x, cam_dist) # top x is x and side x is y from drawing      
        #         print("x: ", top_x, "y: ", real_side_x)
        #         return top_x, real_side_x
                
        # KEYBOARD COMMANDS
        if key==ord('a'):
            do_fit = True
        if key == ord('t'):
            sideview_frame_dist,y_val = trackingFunctions.get_tape_blob(sideview_frame, constants.l_b_tape, constants.u_b_tape, 2)
            if sideview_frame_dist != 0:
                calibration_ratio = constants.real_dist/sideview_frame_dist                
                print("calibration ratio: ", calibration_ratio)
        if key==ord('c'): # clear everything
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

        # displaying everything
        cv2.imshow('sideview_frame',sideview_frame)
        cv2.imshow('topview_frame',topview_frame)
        cv2.imshow("topview_mask_ball",topview_mask_ball)
        cv2.imshow("sideview_mask_ball",sideview_mask_ball)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def convert(x,y):
    """
    Convert from real life x and y distance to x, y coordinate on the gantry.

    gantry dimensions:
    370, 410 origin in bottom right corner
    460mm, 500mm

    distance from sideframe edge to gantry 620*2=1240
    """
    y = y - 1240
    y = y * (410/500)
    print("converted x: ", x, "converted y: ", y)
    return 100,y

x, y = HandOfGod()
convert(x, y)