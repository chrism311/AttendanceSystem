import numpy as np
import cv2

usb_camera ="v4l2src device=/dev/video1 ! video/x-raw, width=(int)320, height=(int)240, format=(string)RGB ! videoconvert ! appsink"
cap = cv2.VideoCapture(usb_camera, cv2.CAP_GSTREAMER)
i = 0

while True:
	ret, frame = cap.read()
	cv2.imshow('Camera Image:{}'.format(i), frame)
	key = cv2.waitKey(1)

	if key == ord('c'):
		cv2.imwrite('pic{}.png'.format(i), frame)
		i += 1

	elif key == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
