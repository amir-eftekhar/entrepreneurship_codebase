import cv2
import numpy as np
import subprocess
from gtts import gTTS
from playsound import playsound
import tempfile
import threading
import speech_recognition as sr

# Global flag to indicate when the object is found
found = threading.Event()

def start_camera_stream():
    cmd = 'libcamera-vid -t 0 --inline --codec yuv420 --width 640 --height 480 --nopreview -o -'
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=640*480*3)

def read_frame_from_camera(process):
    frame_data = process.stdout.read(640*480*3)
    if not frame_data:
        return None
    frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))
    return frame

def load_yolo():
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes

def detect_objects_on_frame(frame, target_class, net, classes):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    objects_detected = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and classes[class_id] == target_class:
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                objects_detected.append((class_id, confidence, (x, y, w, h)))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame, objects_detected

def provide_feedback(objects_detected, frame, target_class):
    height, width, _ = frame.shape
    if objects_detected:
        for obj in objects_detected:
            _, _, (x, y, w, h) = obj
            center_x = x + w // 2
            center_y = y + h // 2
            direction = ""
            if center_y < height // 3:
                direction += "up "
            elif center_y > 2 * height // 3:
                direction += "down "
            if center_x < width // 3:
                direction += "left"
            elif center_x > 2 * width // 3:
                direction += "right"
            if not direction:
                direction = "center"
            message = f"{target_class.capitalize()} detected {direction}."
    else:
        message = f"{target_class.capitalize()} not found. Please turn left or right."
    
    tts = gTTS(text=message, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + '.mp3')
        playsound(fp.name + '.mp3')

def listen_for_found():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    while not found.is_set():
        with microphone as source:
            print("Listening for 'found' command...")
            audio = recognizer.listen(source, timeout=5)
        try:
            command = recognizer.recognize_google(audio).lower()
            if "found" in command:
                found.set()
                print("Found command recognized. Stopping detection.")
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            continue

def main(target_class):
    net, classes = load_yolo()
    process = start_camera_stream()
    found_listener_thread = threading.Thread(target=listen_for_found)
    found_listener_thread.start()

    try:
        while not found.is_set():
            frame = read_frame_from_camera(process)
            if frame is not None:
                detected_frame, objects_detected = detect_objects_on_frame(frame, target_class, net, classes)
                provide_feedback(objects_detected, detected_frame, target_class)
                cv2.imshow('Object Detector', detected_frame)
                if cv2.waitKey(1) == ord('q'):
                    break
    finally:
        found.set()
        process.stdout.close()
        process.terminate()
        process.wait()
        cv2.destroyAllWindows()
        found_listener_thread.join()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_class = sys.argv[1].lower()
        main(target_class)
    else:
        print("Usage: python3 object_detection.py <target_class>")
