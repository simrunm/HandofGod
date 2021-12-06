import cv2
from imutils.video import WebcamVideoStream

top = WebcamVideoStream(src=0).start()
side = WebcamVideoStream(src=1).start()
while True:
	key = cv2.waitKey(1) & 0xFF
	# grab the frame from the threaded video stream
	top_frame = top.read()
	side_frame = side.read()

	# display frame to our screen
	cv2.imshow("Top Frame", top_frame)
	cv2.imshow("Side Frame", side_frame)

	if key==ord('q'):
		break