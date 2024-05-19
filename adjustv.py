print("start")
import cv2
import subprocess
import numpy as np
print(("starting"))

def read_frames():
    print(("reading frame"))
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-video_size', '640x480',
        '-framerate', '30',
        '-input_format', 'mjpeg',
        '-i', '/dev/video2',  # Ensure this is /dev/video2
        '-pix_fmt', 'bgr24',
        '-f', 'image2pipe',
        '-vcodec', 'rawvideo',
        '-'
    ]
    
    print("Executing command:", " ".join(command))  # Debug statement to check the command

    try:
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    except Exception as e:
        print(f"Failed to start subprocess: {e}")
        return
    
    while True:
        print("reading")
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

def main():
    print("Starting the script...")
    
    cv2.namedWindow("Left Frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Right Frame", cv2.WINDOW_NORMAL)

    for frame in read_frames():
        width_cutoff = frame.shape[1] // 2
        left_frame = frame[:, :width_cutoff]
        right_frame = frame[:, width_cutoff:]

        # Flip vertically
        left_frame = cv2.flip(left_frame, 0)
        right_frame = cv2.flip(right_frame, 0)

        cv2.imshow("Left Frame", left_frame)
        cv2.imshow("Right Frame", right_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print("Script ended.")

if __name__ == '__main__':
    main()
