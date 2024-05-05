import cv2
import numpy as np
import threading
import queue
import subprocess
from test import read_frame_from_camera

def start_camera_stream():
    cmd = 'libcamera-vid -t 0 --inline --codec yuv420 --width 640 --height 480 --nopreview -o -'
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=640*480*3)  # Adjust buffer size according to expected frame size
    return process

def capture_frames(process, frame_queue):
    while True:
        frame = read_frame_from_camera(process)
        if frame is not None:
            frame_queue.put(frame)
        else:
            break

def display_frames(frame_queue):
    while True:
        frame = frame_queue.get()
        if frame is None:  # Use a sentinel value to indicate shutdown
            break
        # Assuming frame processing and drawing happens here
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    process = start_camera_stream()
    frame_queue = queue.Queue(2)  # Small buffer to hold frames
    capture_thread = threading.Thread(target=capture_frames, args=(process, frame_queue))
    display_thread = threading.Thread(target=display_frames, args=(frame_queue,))

    capture_thread.start()
    display_thread.start()

    capture_thread.join()
    display_thread.join()

    process.terminate()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
