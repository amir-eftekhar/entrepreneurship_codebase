import cv2

def process_frame(frame):
    # Flip the frame vertically
    flipped_frame = cv2.flip(frame, 1)
    # Split the frame into two images
    height, width = flipped_frame.shape[:2]
    mid_point = width // 2
    left_image = flipped_frame[:, :mid_point]
    right_image = flipped_frame[:, mid_point:]
    return left_image, right_image

# Set up the video capture device
cap = cv2.VideoCapture(0)  # Adjust the device index as needed

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process the captured frame
    left_image, right_image = process_frame(frame)
    
    # Display the results
    cv2.imshow('Left Image', left_image)
    cv2.imshow('Right Image', right_image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
