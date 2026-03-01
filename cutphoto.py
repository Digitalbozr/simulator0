import cv2

# Load the image
image = cv2.imread('images/1.png')
if image is None:
    print("Failed to load image - please check the path")
    exit()

# Get original dimensions
height, width = image.shape[:2]
print(f"Original image size: {width}x{height} pixels")

# Define crop region (x, y, width, height)
# Example: crop a 200x150 region starting at (x=100, y=50)
x = 0      # X coordinate of top-left corner
y = 0       # Y coordinate of top-left corner
crop_width = 263
crop_height = 230

# Validate crop boundaries
if x + crop_width > width or y + crop_height > height:
    print("Error: Crop region exceeds image boundaries!")
    exit()

# Crop the image (OpenCV uses [y:y+h, x:x+w] slicing)
cropped = image[y:y + crop_height, x:x + crop_width]

# Display results (optional)
cv2.imshow('Original Image', image)
cv2.imshow('Cropped Image', cropped)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the cropped image
cv2.imwrite('images/cropped_output.png', cropped)
print(f"Cropped image saved: {crop_width}x{crop_height} pixels")