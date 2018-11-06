import cv2
import numpy as np

width = 640 
height = 360

usb_camera ="v4l2src device=/dev/video1 ! video/x-raw, width=(int){}, height=(int){}, format=(string)RGB, framerate=(fraction)30/1 ! videoconvert ! appsink".format(width, height)

cap = cv2.VideoCapture(usb_camera, cv2.CAP_GSTREAMER)

out = cv2.VideoWriter('output1.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10,(width, height))

while True:
	ret, frame = cap.read()
	
	if ret == True:
		out.write(frame)
		cv2.imshow('frame',frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else:
		break
cap.release()
out.release()

cv2.destroyAllWindows()

