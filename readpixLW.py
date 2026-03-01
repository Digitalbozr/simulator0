import cv2

image = cv2.imread('images/2.png')
if image is not None:
    height, width, channels = image.shape
    print(f"Width: {width} pixels")
    print(f"Height: {height} pixels")
    print(f"Channels: {channels}")
else:
    print("Failed to load image - please check the path")