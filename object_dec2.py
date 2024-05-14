import cv2
import numpy as np
import subprocess
import os
import importlib.util
from threading import Thread
import queue
from test import start_camera_stream, read_frame_from_camera

# Define paths and constants
MODEL_DIR = 'test_modle'
GRAPH_NAME = '1.tflite'
LABELMAP_NAME = 'labelmap.txt'
MIN_CONF_THRESHOLD = 0.5
RESOLUTION = '1280x720'


# Main function
def main():
    process = start_camera_stream()

    # Load TensorFlow Lite model
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        interpreter = Interpreter(model_path=os.path.join(os.getcwd(), MODEL_DIR, GRAPH_NAME))
    else:
        print("TensorFlow Lite Runtime is not available.")
        return

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    floating_model = (input_details[0]['dtype'] == np.float32)

    while True:
        frame = read_frame_from_camera(process)
        if frame is None:
            break

        frame_resized = cv2.resize(frame, (width, height))
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
                cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)

        cv2.imshow('Object Detector', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    process.terminate()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
