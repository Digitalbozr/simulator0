import cv2

# Load and crop the image (natural colors)
image = cv2.imread('images/1.png')
if image is None:
    print("Failed to load image - please check the path")
    exit()

height, width = image.shape[:2]
x, y, crop_width, crop_height = 0, 0, 263, 230

if x + crop_width > width or y + crop_height > height:
    print("Error: Crop region exceeds image boundaries!")
    exit()

cropped = image[y:y + crop_height, x:x + crop_width].copy()

# Define objects with labels stored in variables (not displayed on image)
objects = [
    [40, 8, 24, 24, "lampes"],
    [206, 11, 24, 24, "libre volant "],
    [223, 34, 24, 24, "battrie"],
    [236, 57, 24, 24, "ceinture"],

    [172, 202, 24, 24, "frein a main"],
    [172+24, 202-15, 24, 24, ""],
    [172+24+20, 202-15-20, 24, 24, "fare "],

    [164 , 139 , 20, 20, "signalGauche "],
    [192 , 139 , 20, 20, "signalDroite "],


]

# Draw only bounding boxes (no text labels)
for obj in objects:
    x1, y1, w, h, label = obj  # Label is kept in variable but not used for display
    x2, y2 = x1 + w, y1 + h
    
    # Draw rectangle with distinct color per object (optional)
    cv2.rectangle(cropped, (x1, y1), (x2, y2), (255, 0, 0), 1)  # Blue boxes

# Display result
cv2.imshow('Cropped Image (Natural Colors)', cropped) # what is problem with this line ? : 
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save result
cv2.imwrite('images/cropped_with_boxes.png', cropped)
print(f"Saved labeled image: cropped_with_boxes.png ({crop_width}x{crop_height} pixels)")

# Optional: Access labels later in code if needed
print("\nObject labels (stored in variables):")
for obj in objects:
    print(f"  - {obj[4]} at position ({obj[0]}, {obj[1]})")