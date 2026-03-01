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
x = 0           # X coordinate of top-left corner
y = 0           # Y coordinate of top-left corner
crop_width = 263
crop_height = 230

# Validate crop boundaries
if x + crop_width > width or y + crop_height > height:
    print("Error: Crop region exceeds image boundaries!")
    exit()

# Crop the image
cropped = image[y:y + crop_height, x:x + crop_width]
print(f"Cropped region: {crop_width}x{crop_height} pixels")

# Convert cropped image to grayscale (black and white)
cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

# Display results
cv2.imshow('Original Image', image)
cv2.imshow('Cropped (Color)', cropped)
cv2.imshow('Cropped (Grayscale)', cropped_gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the grayscale cropped image
cv2.imwrite('images/cropped_grayscale.png', cropped_gray)
print("Grayscale cropped image saved as 'cropped_grayscale.png'")