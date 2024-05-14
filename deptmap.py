import cv2
import numpy as np
from adjustv import read_frames  # Ensure this module properly provides frames

def main():
    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)

    # Create StereoBM object with optimized settings
    stereo = cv2.StereoBM_create(numDisparities=16*2, blockSize=21)

    try:
        for frame in read_frames():
            # Resize frame for faster processing
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)

            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Split frame into left and right images
            width_cutoff = gray_frame.shape[1] // 2
            left_gray = gray_frame[:, :width_cutoff]
            right_gray = gray_frame[:, width_cutoff:]

            # Compute disparity map
            disparity = stereo.compute(left_gray, right_gray)

            # Normalize the disparity map
            disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Color mapping
            disparity_color = cv2.applyColorMap(disparity_normalized, cv2.COLORMAP_JET)

            # Calculate and print depth information, ignoring the left 1/4th
            three_fourths_width_start = disparity_color.shape[1] // 4
            segments = {
                'Center': disparity_color[:, three_fourths_width_start:3*disparity_color.shape[1]//4],
                'Right': disparity_color[:, 3*disparity_color.shape[1]//4:]
            }

            for name, segment in segments.items():
                average_depth = np.mean(segment)
                print(f"{name} Segment Average Depth: {average_depth:.2f}")

            # Display the depth map
            cv2.imshow("Depth Map", disparity_color)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
