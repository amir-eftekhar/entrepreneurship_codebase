import cv2
import subprocess
import numpy as np

def read_frames():
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-video_size', '640x480',
        '-framerate', '30',
        '-input_format', 'mjpeg',
        '-i', '/dev/video2',
        '-pix_fmt', 'bgr24',
        '-f', 'image2pipe',
        '-vcodec', 'rawvideo',
        '-'
    ]

    try:
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    except Exception as e:
        print(f"Failed to start subprocess: {e}")
        return

    while True:
        raw_image = pipe.stdout.read(640 * 480 * 3)
        
        if len(raw_image) != 640 * 480 * 3:
            print("Frame read failed, received bytes:", len(raw_image))
            break

        image = np.frombuffer(raw_image, dtype='uint8').reshape((480, 640, 3))

        # Cut off the bottom half of the image
        height_cutoff = image.shape[0] // 2
        image = image[:height_cutoff, :]  

        yield image

        pipe.stdout.flush()

def modify_dark_blue_pixels(disparity, prev_disparity):
    modified_disparity = disparity.copy()
    blue_mask = disparity == 0  # Assuming dark blue is represented by zero disparity value
    
    for y in range(1, disparity.shape[0] - 1):
        for x in range(1, disparity.shape[1] - 1):
            if blue_mask[y, x]:
                neighborhood = disparity[y-1:y+2, x-1:x+2]
                non_blue_neighborhood = neighborhood[neighborhood != 0]
                if len(non_blue_neighborhood) > 0:
                    rate_of_change = np.mean(np.abs(np.diff(non_blue_neighborhood)))
                    if not np.isnan(rate_of_change):
                        modified_disparity[y, x] = min(255, int(rate_of_change * 10))

    return modified_disparity

def main():
    stereo = cv2.StereoBM_create(numDisparities=16*2, blockSize=21)
    prev_disparity = None

    cv2.namedWindow("Left Frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Right Frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)

    for frame in read_frames():
        width_cutoff = frame.shape[1] // 2
        left_frame = frame[:, :width_cutoff]
        right_frame = frame[:, width_cutoff:]

        # Convert to grayscale
        left_gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)

        # Compute disparity
        disparity = stereo.compute(left_gray, right_gray)
        disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        
        # Modify dark blue pixels
        if prev_disparity is not None:
            disparity_normalized = modify_dark_blue_pixels(disparity_normalized, prev_disparity)
        
        disparity_color = cv2.applyColorMap(disparity_normalized.astype(np.uint8), cv2.COLORMAP_JET)
        prev_disparity = disparity_normalized

        # Display frames
        cv2.imshow("Left Frame", left_frame)
        cv2.imshow("Right Frame", right_frame)
        cv2.imshow("Depth Map", disparity_color)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
