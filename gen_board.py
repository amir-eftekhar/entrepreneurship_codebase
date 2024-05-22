import cv2
import numpy as np

# Define the size of the image and the checkerboard
image_size = (800, 800)
checkerboard_size = (7, 7)
square_size = 50

# Create a blank image with a red border
image = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)
image[:] = (0, 0, 255)  # Red border

# Draw the black border
border_thickness = 10
cv2.rectangle(image, (border_thickness, border_thickness),
              (image_size[1] - border_thickness, image_size[0] - border_thickness),
              (0, 0, 0), -1)

# Draw the checkerboard inside the black border
for i in range(checkerboard_size[0]):
    for j in range(checkerboard_size[1]):
        color = (255, 255, 255) if (i + j) % 2 == 0 else (0, 0, 0)
        top_left = (border_thickness + j * square_size, border_thickness + i * square_size)
        bottom_right = (top_left[0] + square_size, top_left[1] + square_size)
        cv2.rectangle(image, top_left, bottom_right, color, -1)

# Define positions for ArUco markers
aruco_positions = [
    (border_thickness * 3, border_thickness * 3),
    (image_size[1] - border_thickness * 3, border_thickness * 3),
    (border_thickness * 3, image_size[0] - border_thickness * 3),
    (image_size[1] - border_thickness * 3, image_size[0] - border_thickness * 3),
]

# Generate and place ArUco markers
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

for i, pos in enumerate(aruco_positions):
    marker = np.zeros((square_size, square_size), dtype=np.uint8)
    marker = cv2.aruco.generateImageMarker(aruco_dict, i, square_size)
    marker_color = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
    x, y = pos
    x = x - square_size // 2
    y = y - square_size // 2
    image[y:y + square_size, x:x + square_size] = marker_color

# Save the image
output_image_path = "checkerboard_with_markers.png"
cv2.imwrite(output_image_path, image)

print(f"Image with ArUco markers saved to {output_image_path}")
