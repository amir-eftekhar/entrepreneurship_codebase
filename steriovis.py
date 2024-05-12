import cv2
import numpy as np

# Setup the disparity stereo matcher
stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

# Initialize video capture with both cameras
cap_left = cv2.VideoCapture(0) 
cap_right = cv2.VideoCapture(1)

while True:
    ret_left, frame_left = cap_left.read()
    ret_right, frame_right = cap_right.read()

    if not ret_left or not ret_right:
        print("Error capturing video")
        break

    # Convert images to grayscale
    gray_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2GRAY)

    # Calculate the disparity map
    disparity = stereo.compute(gray_left, gray_right)

    # Normalize the disparity for display
    disp_display = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    # Display the result
    cv2.imshow('Disparity', disp_display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video captures
cap_left.release()
cap_right.release()
cv2.destroyAllWindows()
