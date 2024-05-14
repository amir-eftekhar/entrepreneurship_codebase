import cv2
import numpy as np

# Assume 'objpoints' and 'imgpoints' are filled from the detected chessboard corners
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray_frame.shape[::-1], None, None)

# Stereo calibration
stereo_ret, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints1, imgpoints2, mtx, dist, mtx, dist, gray_frame.shape[::-1])

# Stereo rectification
R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
    cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, gray_frame.shape[::-1], R, T)

# Compute the maps for remapping the camera views
map1x, map1y = cv2.initUndistortRectifyMap(cameraMatrix1, distCoeffs1, R1, P1, gray_frame.shape[::-1], cv2.CV_16SC2)
map2x, map2y = cv2.initUndistortRectifyMap(cameraMatrix2, distCoeffs2, R2, P2, gray_frame.shape[::-1], cv2.CV_16SC2)

# Remap the images
rectified_img1 = cv2.remap(img1, map1x, map1y, cv2.INTER_LINEAR)
rectified_img2 = cv2.remap(img2, map2x, map2y, cv2.INTER_LINEAR)
