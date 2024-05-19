import cv2
import numpy as np

def load_and_split_image(image_path):
    # Load the full stereo image
    full_image = cv2.imread(image_path)
    # Assuming the image is split vertically down the middle
    height, width, _ = full_image.shape
    left_img = full_image[:, :width//2]
    right_img = full_image[:, width//2:]
    return left_img, right_img

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply histogram equalization to improve contrast
    gray = cv2.equalizeHist(gray)
    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray

def find_and_draw_markers(image, aruco_dict_type=cv2.aruco.DICT_4X4_50):
    gray = preprocess_image(image)
    aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    aruco_params = cv2.aruco.DetectorParameters_create()

    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
    return image, ids, corners

def main():
    left_img, right_img = load_and_split_image("asemboard9.jpg")  

    # Show the original images
    cv2.imshow('Original Left Image', left_img)
    cv2.imshow('Original Right Image', right_img)

    left_img_with_markers, idsL, cornersL = find_and_draw_markers(left_img)
    right_img_with_markers, idsR, cornersR = find_and_draw_markers(right_img)

    # Show the images with markers drawn
    if idsL is not None and idsR is not None:
        cv2.imshow('Left Image with Markers', left_img_with_markers)
        cv2.imshow('Right Image with Markers', right_img_with_markers)
    else:
        print("ArUco markers not found in one or both images.")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
