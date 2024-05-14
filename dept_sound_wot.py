import cv2
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine
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
    try:
        while True:
            raw_image = pipe.stdout.read(640 * 480 * 3)
            if len(raw_image) != 640 * 480 * 3:
                print("Frame read failed, received bytes:", len(raw_image))
                continue
            image = np.frombuffer(raw_image, dtype='uint8').reshape((480, 640, 3))
            yield image
    finally:
        pipe.kill()

def generate_audio_signals(depth_map):
    segments = {
        'left': depth_map[:, :depth_map.shape[1]//3],
        'center': depth_map[:, depth_map.shape[1]//3:2*depth_map.shape[1]//3],
        'right': depth_map[:, 2*depth_map.shape[1]//3:]
    }
    frequencies = {'left': 440, 'center': 880, 'right': 1320}  # Different frequencies for different parts

    for segment_name, segment_data in segments.items():
        focus_depth = np.mean(segment_data)
        volume = np.clip((1 - (focus_depth / 255)) * 0.5, 0, 1)
        sound = Sine(frequencies[segment_name]).to_audio_segment(duration=500)  # Generate a 0.5 sec sine wave
        sound = sound - (1 - volume) * 20
        pan = {'left': -1, 'center': 0, 'right': 1}[segment_name]
        sound = sound.pan(pan)
        play(sound)

def main(runvar):
    stereo = cv2.StereoBM_create(numDisparities=16*2, blockSize=21, )

    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
    try:
        for frame in read_frames():
            if not runvar: 
                break
            if frame is not None:
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                width_cutoff = gray_frame.shape[1] // 2
                left_gray = gray_frame[:, :width_cutoff]
                right_gray = gray_frame[:, width_cutoff:]
                disparity = stereo.compute(left_gray, right_gray)
                disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
                disparity_color = cv2.applyColorMap(disparity_normalized.astype(np.uint8), cv2.COLORMAP_JET)
                cv2.imshow("Depth Map", disparity_color)
                generate_audio_signals(disparity_normalized)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()