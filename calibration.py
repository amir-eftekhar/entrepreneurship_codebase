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

def find_and_draw_corners(image, chessboard_size=(10, 10)):
    gray = preprocess_image(image)

    # Find the chessboard corners with adjusted parameters
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, 
                                             cv2.CALIB_CB_ADAPTIVE_THRESH + 
                                             cv2.CALIB_CB_NORMALIZE_IMAGE + 
                                             cv2.CALIB_CB_FAST_CHECK)
    # If found, refine corners and draw them
    if ret:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        cv2.drawChessboardCorners(image, chessboard_size, corners, ret)
    return image, ret, corners

def main():
    chessboard_size = (10, 10)  # Define the number of inner corners per a chessboard row and column
    left_img, right_img = load_and_split_image("better_image3.jpg")  

    # Show the original images
    cv2.imshow('Original Left Image', left_img)
    cv2.imshow('Original Right Image', right_img)

    left_img_with_corners, retL, cornersL = find_and_draw_corners(left_img, chessboard_size)
    right_img_with_corners, retR, cornersR = find_and_draw_corners(right_img, chessboard_size)

    # Show the images with corners drawn
    if retL and retR:
        cv2.imshow('Left Image with Corners', left_img_with_corners)
        cv2.imshow('Right Image with Corners', right_img_with_corners)
    else:
        print("Chessboard corners not found in one or both images.")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
