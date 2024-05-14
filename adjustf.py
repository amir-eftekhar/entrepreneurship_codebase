import cv2
import subprocess

def capture_image_with_fswebcam():
    # Command to capture an image using fswebcam
    command = ['fswebcam', '-r', '1280x720', '--no-banner', 'photo.jpg']
    try:
        # Using subprocess to execute the command
        subprocess.run(command, check=True)
        print("Image captured successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to capture image:", e)

def process_image():
    # Load the image captured by fswebcam
    image = cv2.imread('photo.jpg')
    if image is not None:
        # Flip the image vertically
        flipped_image = cv2.flip(image, 0)  # 0 means flipping around the x-axis

        
        height, width, channels = flipped_image.shape
        width_cutoff = width // 2
        left_frame = flipped_image[:, :width_cutoff]
        right_frame = flipped_image[:, width_cutoff:]

        # Display the images
        cv2.imshow('Left Frame', left_frame)
        cv2.imshow('Right Frame', right_frame)

        # Wait for a key press and then terminate
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to load image. Check the file path.")

def main():
    capture_image_with_fswebcam()
    process_image()

if __name__ == '__main__':
    main()
