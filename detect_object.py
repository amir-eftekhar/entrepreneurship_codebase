'''import cv2
import numpy as np
import threading
import queue
import subprocess
import tensorflow as tf

# Load TFLite model and allocate tensors
interpreter = tf.lite.Interpreter(model_path="path_to_tflite_model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def detect_objects(frame):
    # Preprocess the image to required size and convert to tensor
    frame_resized = cv2.resize(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
    input_data = np.expand_dims(frame_resized, axis=0)
    input_data = (np.float32(input_data) - 127.5) / 127.5

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

        # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence of detected objects

    # Process detection results
    for i in range(len(scores)):
        if scores[i] > 0.5:  # Filter out detections with a confidence less than 50%
            ymin, xmin, ymax, xmax = boxes[i]
            class_id = int(classes[i])
            confidence = scores[i]

            # Calculate the center of the detected object
            center_x = (xmin + xmax) / 2
            center_y = (ymin + ymax) / 2

            # Example to determine the direction relative to the center of the frame
            frame_center_x = frame.shape[1] / 2
            direction = "left" if center_x < frame_center_x else "right"

            # Generate voice feedback based on object location
            object_name = "object"  # Placeholder: replace with actual class name lookup if available
            voice_feedback = f"{object_name} detected {direction}, {int(confidence * 100)}% confidence"

            # Here, integrate with your voice assistant or output system
            print(voice_feedback)  # Placeholder for actual voice feedback implementation

    # Continue to the next part of the application
    return frame
'''

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tensorflow_hub as hub
import numpy as np
import tensorflow as tf
import cv2


detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")

def load_prep_image(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.resize(img, [640, 480])
    img = tf.image.convert_image_dtype(img, tf.uint8)  # Move conversion here
    img = img[tf.newaxis, :]
    return img

def detect_objects(image_path):
    img = load_prep_image(image_path)
    detector_output = detector(img)
    result = {key:value.numpy() for key,value in detector_output.items()}
    return result
def draw_boxes_cv2(image_path, detection_results):
    # Load the image using cv2
    img = cv2.imread(image_path)

    # Get the detection boxes, classes, and scores
    boxes = detection_results['detection_boxes'][0]
    classes = detection_results['detection_classes'][0]
    scores = detection_results['detection_scores'][0]

    # For each box
    for i in range(len(boxes)):
        # If the detection score is above a threshold
        if scores[i] > 0.5:
            # Get the box coordinates and scale them to the image size
            ymin, xmin, ymax, xmax = boxes[i]
            xmin, ymin, xmax, ymax = int(xmin * 480), int(ymin * 640), int(xmax * 480), int(ymax * 640)

            # Draw the bounding box
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

            # Draw the label
            label = f'Class: {classes[i]}, Score: {scores[i]}'
            cv2.putText(img, label, (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    # Display the image
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

# Example usage
image_path = 'photo.jpg'
detection_results = detect_objects(image_path)
print(detection_results)
draw_boxes_cv2(image_path, detection_results)

