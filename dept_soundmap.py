import cv2
import numpy as np
import threading
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
import subprocess

def read_frames():
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-video_size', '640x480',
        '-i', '/dev/video0',
        '-pix_fmt', 'bgr24',
        '-vcodec', 'rawvideo',
        '-an',
        '-sn',
        '-r', '40',
        '-f', 'image2pipe',
        '-'
    ]
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    while True:
        raw_image = pipe.stdout.read(640 * 480 * 3)
        if len(raw_image) != 640 * 480 * 3:
            print("Frame read failed, received bytes:", len(raw_image))
            continue
        image = np.frombuffer(raw_image, dtype='uint8').reshape((480, 640, 3))
        yield image
    pipe.kill()

def generate_audio_signals(depth_map):
    segments = {
        'left': depth_map[:, :depth_map.shape[1]//3],
        'center': depth_map[:, depth_map.shape[1]//3:2*depth_map.shape[1]//3],
        'right': depth_map[:, 2*depth_map.shape[1]//3:]
    }
    
    for segment_name, segment_data in segments.items():
        focus_depth = np.mean(segment_data)
        volume = np.clip((1 - (focus_depth / 255)) * 0.5, 0, 1)
        sound = AudioSegment.from_file("test_tone.wav")
        sound = sound - (1 - volume) * 20
        pan = {'left': -1, 'center': 0, 'right': 1}[segment_name]
        sound = sound.pan(pan)
        play(sound)

def depth_processing_thread(frame_queue, depth_queue):
    stereo = cv2.StereoBM_create(numDisparities=16*2, blockSize=21)
    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        width_cutoff = gray_frame.shape[1] // 2
        left_gray = gray_frame[:, :width_cutoff]
        right_gray = gray_frame[:, width_cutoff:]
        disparity = stereo.compute(left_gray, right_gray)
        disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        depth_queue.put(disparity_normalized)

def display_and_audio_thread(depth_queue):
    while True:
        disparity_normalized = depth_queue.get()
        if disparity_normalized is None:
            break
        disparity_color = cv2.applyColorMap(disparity_normalized.astype(np.uint8), cv2.COLORMAP_JET)
        cv2.imshow("Depth Map", disparity_color)
        generate_audio_signals(disparity_normalized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    frame_queue = Queue()
    depth_queue = Queue()

    depth_thread = threading.Thread(target=depth_processing_thread, args=(frame_queue, depth_queue), daemon=True)
    display_thread = threading.Thread(target=display_and_audio_thread, args=(depth_queue,), daemon=True)

    depth_thread.start()
    display_thread.start()

    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
    try:
        for frame in read_frames():
            if frame is not None:
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
                frame_queue.put(frame)
    finally:
        frame_queue.put(None)
        depth_queue.put(None)
        depth_thread.join()
        display_thread.join()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
