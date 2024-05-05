import os
import cv2
import numpy as np
import subprocess
from threading import Thread
import importlib.util
from test import start_camera_stream, read_frame_from_camera

# Hardcoded settings
MODEL_DIR = 'test_modle'
GRAPH_NAME = '1.tflite'
LABELMAP_NAME = 'labelmap.txt'
MIN_CONF_THRESHOLD = 0.5
RESOLUTION = '1280x720'
USE_EDGE_TPU = False  # Set to True if using Coral Edge TPU

# Load TensorFlow interpreter
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if USE_EDGE_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    print("TensorFlow Lite Runtime is not available.")
    exit(1)

# Load the model and labels
CWD_PATH = os.getcwd()
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_DIR, GRAPH_NAME)
PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_DIR, LABELMAP_NAME)

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
if labels[0] == '???':
    del labels[0]

interpreter = Interpreter(model_path=PATH_TO_CKPT)
if USE_EDGE_TPU:
    interpreter.load_delegate('libedgetpu.so.1.0')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
floating_model = (input_details[0]['dtype'] == np.float32)

# Main detection function
def main():
    process = start_camera_stream()
    try:
        while True:
            frame = read_frame_from_camera(process)
            if frame is None:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            if floating_model:
                input_data = (input_data - 127.5) / 127.5

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            boxes = interpreter.get_tensor(output_details[0]['index'])[0]
            classes = interpreter.get_tensor(output_details[1]['index'])[0]
            scores = interpreter.get_tensor(output_details[2]['index'])[0]

            for i in range(len(scores)):
                if scores[i] > MIN_CONF_THRESHOLD:
                    ymin, xmin, ymax, xmax = boxes[i]
                    (left, right, top, bottom) = (xmin * width, xmax * width, ymin * height, ymax * height)
                    cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 4)
                    label = f"{labels[int(classes[i])]}: {int(scores[i]*100)}%"
                    cv2.putText(frame, label, (int(left), int(top)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow('Object detector', frame)
            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        process.stdout.close()
        process.terminate()
        process.wait()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
