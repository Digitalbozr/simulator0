import cv2
import easyocr
import numpy as np
import torch

# Check GPU availability
gpu_available = torch.cuda.is_available()
print(f"GPU available: {gpu_available}")
if gpu_available:
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")

# Step 1: Load original image
image = cv2.imread('images/1.png')
if image is None:
    print("❌ Failed to load image - please check the path 'images/1.png'")
    exit()

# Step 2: Crop the region of interest
x, y, crop_width, crop_height = 0, 0, 263, 230
height, width = image.shape[:2]

if x + crop_width > width or y + crop_height > height:
    print(f"❌ Crop region exceeds image boundaries! Image size: {width}x{height}")
    exit()

cropped = image[y:y + crop_height, x:x + crop_width].copy()
print(f"✓ Successfully cropped region: {crop_width}x{crop_height} pixels")

# Step 3: Initialize EasyOCR reader with GPU (if available)
try:
    reader = easyocr.Reader(['en'], gpu=gpu_available, verbose=False)
    print(f"✓ EasyOCR reader initialized with {'GPU' if gpu_available else 'CPU'}")
except Exception as e:
    print(f"⚠️ GPU initialization failed, falling back to CPU: {e}")
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print("✓ EasyOCR reader initialized with CPU")

# Step 4: Extract text from cropped image (with performance timing)
import time
start_time = time.time()
results = reader.readtext(
    cropped,
    decoder='greedy',        # Faster than beam search
    batch_size=10,           # Process multiple text regions in parallel
    contrast_ths=0.1,        # Better for low-contrast text
    adjust_contrast=0.5,
    width_ths=0.7,
    height_ths=0.7
)
processing_time = time.time() - start_time
print(f"✓ OCR completed in {processing_time:.2f} seconds")

# Step 5: Display results
print("\n" + "="*60)
print("EXTRACTED TEXT & NUMBERS FROM CROPPED REGION:")
print("="*60)

if not results:
    print("⚠️  No text detected in the cropped region")
else:
    for i, (bbox, text, confidence) in enumerate(results, 1):
        clean_text = ' '.join(text.split())
        status = "✓" if confidence > 0.7 else "⚠️"
        print(f"{status} {i}. '{clean_text}' | Confidence: {confidence:.1%} | GPU: {gpu_available}")

print("="*60)

# Step 6: Visualize detected text with bounding boxes
visualized = cropped.copy()
for bbox, text, confidence in results:
    pts = np.array(bbox, dtype=np.int32).reshape((-1, 1, 2))
    color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)  # Green for high confidence, orange for low
    cv2.polylines(visualized, [pts], True, color, 2)

# Display images
cv2.imshow('Original Cropped Region', cropped)
cv2.imshow('Detected Text (GPU Accelerated)' if gpu_available else 'Detected Text (CPU)', visualized)
print("\n💡 Press any key in the image window to close...")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Step 7: Save results
cv2.imwrite('images/cropped_region.png', cropped)
cv2.imwrite('images/ocr_result_gpu.png' if gpu_available else 'images/ocr_result_cpu.png', visualized)
print("\n✓ Saved images:")
print("  - cropped_region.png : Original cropped area")
print(f"  - {'ocr_result_gpu.png' if gpu_available else 'ocr_result_cpu.png'} : With detection boxes")

# Save extracted text
if results:
    output_file = 'images/extracted_text_gpu.txt' if gpu_available else 'images/extracted_text_cpu.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for bbox, text, confidence in results:
            f.write(f"{text.strip()}|{confidence:.4f}\n")
    print(f"  - {output_file} : Text with confidence scores")