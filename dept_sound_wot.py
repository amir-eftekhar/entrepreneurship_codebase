import cv2
import numpy as np
import subprocess
import time

def read_frame():
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-video_size', '640x240',
        '-i', '/dev/video2',
        '-pix_fmt', 'bgr24',
        '-vcodec', 'rawvideo',
        '-an',
        '-sn',
        '-r', '1',  # Capture one frame at a time
        '-frames:v', '1',
        '-f', 'image2pipe',
        '-'
    ]
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    try:
        raw_image = pipe.stdout.read(640 * 240 * 3)
        if len(raw_image) != 640 * 240 * 3:
            print("Frame read failed, received bytes:", len(raw_image))
            return None
        image = np.frombuffer(raw_image, dtype='uint8').reshape((240, 640, 3))
        return image
    finally:
        pipe.kill()

def main():
    stereo = cv2.StereoBM_create(numDisparities=16*2, blockSize=21)
    
    #cv2.namedWindow("Left Frame", cv2.WINDOW_NORMAL)
    #cv2.namedWindow("Right Frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
    
    try:
        while True:
            frame = read_frame()
            if frame is not None:
                # Split the frame into left and right images
                width_cutoff = frame.shape[1] // 2
                left_frame = frame[:, :width_cutoff]
                right_frame = frame[:, width_cutoff:]
                
                left_gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
                right_gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)
                
                disparity = stereo.compute(left_gray, right_gray)
                disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
                disparity_color = cv2.applyColorMap(disparity_normalized.astype(np.uint8), cv2.COLORMAP_JET)
                
                # Display the frames and depth map
                #cv2.imshow("Left Frame", left_frame)
                #cv2.imshow("Right Frame", right_frame)
                cv2.imshow("Depth Map", disparity_color)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time.sleep(0.5)  # Delay before capturing the next frame
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
