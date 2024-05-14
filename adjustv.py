import cv2
import subprocess
import numpy as np

def read_frames():
    command = ['ffmpeg', '-f', 'v4l2', '-video_size', '640x480', '-i', '/dev/video0', '-pix_fmt', 'bgr24', '-vcodec', 'rawvideo', '-an', '-sn', '-r', '40', '-f', 'image2pipe', '-']
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    
    while True:
        
        raw_image = pipe.stdout.read(640*480*3)
        
        if len(raw_image) != 640*480*3:
            print("Frame read failed, received bytes:", len(raw_image))
            break

        image = np.frombuffer(raw_image, dtype='uint8').reshape((480, 640, 3))

        height_cutoff = image.shape[0] // 2
        image = image[:height_cutoff, :]  

        yield image

        pipe.stdout.flush()

def main():
    cv2.namedWindow("Left Frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Right Frame", cv2.WINDOW_NORMAL)

    for frame in read_frames():
        width_cutoff = frame.shape[1] // 2
        left_frame = frame[:, :width_cutoff]
        right_frame = frame[:, width_cutoff:]

        cv2.imshow("Left Frame", left_frame)
        cv2.imshow("Right Frame", right_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
