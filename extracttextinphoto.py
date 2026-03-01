import cv2
import easyocr
import numpy as np

# Step 1: Load original image
image = cv2.imread('images/1.png')
if image is None:
    print("❌ Failed to load image - please check the path 'images/1.png'")
    exit()

# Step 2: Crop the region of interest (your coordinates: x=0, y=0, width=263, height=230)
x, y, crop_width, crop_height = 0, 0, 263, 230
height, width = image.shape[:2]

if x + crop_width > width or y + crop_height > height:
    print(f"❌ Crop region exceeds image boundaries! Image size: {width}x{height}")
    exit()

cropped = image[y:y + crop_height, x:x + crop_width].copy()
print(f"✓ Successfully cropped region: {crop_width}x{crop_height} pixels")

# Step 3: Initialize EasyOCR reader (English + numbers only)
# gpu=False for compatibility; set to True if you have CUDA-compatible GPU
reader = easyocr.Reader(['en'], gpu=False)
print("✓ EasyOCR reader initialized (English language)")

# Step 4: Extract text from cropped image
results = reader.readtext(cropped)

# Step 5: Display results
print("\n" + "="*60)
print("EXTRACTED TEXT & NUMBERS FROM CROPPED REGION:")
print("="*60)

if not results:
    print("⚠️  No text detected in the cropped region")
else:
    for i, (bbox, text, confidence) in enumerate(results, 1):
        # Clean text: remove extra spaces/newlines
        clean_text = ' '.join(text.split())
        print(f"{i}. Text: '{clean_text}' | Confidence: {confidence:.2%}")

print("="*60)

# Step 6: Optional - Visualize detected text with bounding boxes
visualized = cropped.copy()
for bbox, text, confidence in results:
    # Get bounding box coordinates
    pts = np.array(bbox, dtype=np.int32).reshape((-1, 1, 2))
    
    # Draw polygon around text (green)
    cv2.polylines(visualized, [pts], True, (0, 255, 0), 2)
    
    # Draw cleaned text above box (optional - remove if you don't want text on image)
    # cv2.putText(visualized, text, tuple(pts[0][0]), 
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# Display images
cv2.imshow('Original Cropped Region', cropped)
cv2.imshow('Detected Text Regions', visualized)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Step 7: Save results
cv2.imwrite('images/cropped_region.png', cropped)
cv2.imwrite('images/ocr_result.png', visualized)
print("\n✓ Saved images:")
print("  - cropped_region.png : Original cropped area")
print("  - ocr_result.png     : With detection boxes")

# Optional: Save extracted text to file
if results:
    with open('images/extracted_text.txt', 'w', encoding='utf-8') as f:
        for bbox, text, confidence in results:
            f.write(f"{text.strip()} (confidence: {confidence:.2%})\n")
    print("  - extracted_text.txt : Plain text results")