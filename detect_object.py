import cv2
import numpy as np
import subprocess
from threading import Thread, Lock
from queue import Queue
import signal
import time
def start_camera_stream():
    # This function should set up your camera stream as before
    cmd = 'libcamera-vid -t 0 --inline --codec yuv420 --width 640 --height 480 --nopreview -o -'
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=640*480*3)

def read_frame_from_camera(process):
    # Function to read frames from the camera process
    frame_data = process.stdout.read(640*480*3)
    if not frame_data:
        return None
    frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))
    return frame

class FrameReader(Thread):
    def __init__(self, process):
        super().__init__()
        self.process = process
        self.queue = Queue(maxsize=1)
        self.active = True

    def run(self):
        while self.active:
            frame = read_frame_from_camera(self.process)
            if frame is None:
                self.active = False
                break
            if self.queue.full():
                self.queue.get()
            self.queue.put(frame)

    def get_frame(self):
        return self.queue.get() if not self.queue.empty() else None

    def stop(self):
        self.active = False

class DetectionThread(Thread):
    def __init__(self, input_queue, output_queue):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
        self.layer_names = self.net.getLayerNames()
        
        out_layer_indices = self.net.getUnconnectedOutLayers()
        # Check if the indices are wrapped in another array
        if out_layer_indices.ndim == 1:
            self.output_layers = [self.layer_names[i - 1] for i in out_layer_indices.flatten()]
        else:
            self.output_layers = [self.layer_names[i[0] - 1] for i in out_layer_indices]

    def run(self):
        while True:
            img = self.input_queue.get()
            if img is None:
                break
            blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)
            self.output_queue.put((img, outs))

    def stop(self):
        self.active = False

def main():
    process = start_camera_stream()
    frame_reader = FrameReader(process)
    frame_reader.start()

    frame_queue = Queue(maxsize=1)  # Keep queue size to 1
    detections_queue = Queue(maxsize=1)  # Keep queue size to 1

    detector = DetectionThread(frame_queue, detections_queue)
    detector.start()

    last_display_time = 0
    display_interval = 0.5  # Set a display interval (in seconds)

    try:
        while True:
            frame = frame_reader.get_frame()
            if frame is not None:
                # Clear the queue if not empty to only keep the most recent frame
                while not frame_queue.empty():
                    frame_queue.get_nowait()

                frame_queue.put(frame)

                # Process detections
                if not detections_queue.empty():
                    display_frame, detections = detections_queue.get_nowait()

                    # Display the frame at defined intervals to manage display rate
                    if time.time() - last_display_time > display_interval:
                        last_display_time = time.time()
                        if display_frame is not None:
                            for out in detections:
                                for detection in out:
                                    scores = detection[5:]
                                    class_id = np.argmax(scores)
                                    confidence = scores[class_id]
                                    if confidence > 0.5:
                                        center_x = int(detection[0] * display_frame.shape[1])
                                        center_y = int(detection[1] * display_frame.shape[0])
                                        w = int(detection[2] * display_frame.shape[1])
                                        h = int(detection[3] * display_frame.shape[0])
                                        x = int(center_x - w / 2)
                                        y = int(center_y - h / 2)
                                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.imshow('Object Detector', display_frame)
                            if cv2.waitKey(1) == ord('q'):
                                break
    finally:
        frame_reader.stop()
        detector.stop()
        process.stdout.close()
        process.terminate()
        process.wait()
        cv2.destroyAllWindows()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    frame_reader.stop()
    detector.stop()
    process.terminate()
    cv2.destroyAllWindows()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
