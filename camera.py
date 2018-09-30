import numpy as np
import cv2
import sys

if len(sys.argv) < 4:
	print("ERROR: python3 camera.py path/ Width Height")
	quit()
path = sys.argv[1]
width = sys.argv[2]
height = sys.argv[3]

gtx_camera ="nvcamerasrc !video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)I420, framerate=(fraction)120/1 ! nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! videoconvert ! appsink".format(width, height)
usb_camera ="v4l2src device=/dev/video1 ! video/x-raw, width=(int){}, height=(int){}, format=(string)RGB, framerate=(fraction)30/1 ! videoconvert ! appsink".format(width, height)
cap = cv2.VideoCapture(usb_camera, cv2.CAP_GSTREAMER)
i = 0

while True:
	ret, frame = cap.read()
	cv2.imshow('Camera Image:{}'.format(i), frame)
	key = cv2.waitKey(1)

	if key == ord('c'):
		cv2.imwrite(path + 'pic{}.png'.format(i), frame)
		i += 1
		
	elif key == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
