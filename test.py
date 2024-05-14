import cv2
import numpy as np
import subprocess

def start_camera_stream():
    cmd = 'libcamera-vid -t 0 --inline --codec yuv420 --width 640 --height 480 --nopreview -o -'
    bufsize = int(640 * 480 * 1.5)  # Buffer size for YUV420
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=bufsize)
    return process

def read_frame_from_camera(process):
    w, h = 640, 480
    # Frame size calculation for YUV420 format
    frame_size = int(w * h * 1.5)
    frame_data = process.stdout.read(frame_size)
    if len(frame_data) != frame_size:
        return None  # This might happen if the stream ends or there is an error

    # Convert the raw frame data to a numpy array that represents the YUV420 image
    frame_yuv = np.frombuffer(frame_data, dtype=np.uint8).reshape((int(h * 1.5), w))
    
    # Convert YUV420 to BGR for image processing
    frame_bgr = cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR_I420)
    
    # Finally convert BGR to RGB for correct color display
    #frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    return frame_bgr

def main():
    process = start_camera_stream()
    while True:
        frame = read_frame_from_camera(process)
        if frame is None:
            break
        cv2.imshow('Object Detector', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    process.stdout.close()
    process.terminate()  # Ensure the subprocess is terminated
    process.wait()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
