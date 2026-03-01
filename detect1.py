import cv2
import numpy as np

# Load image
image = cv2.imread('images/5.png')
if image is None:
    print("❌ Failed to load image - check path 'images/2.png'")
    exit()

# Crop region of interest
cropped = image[0:230, 0:263].copy()
print(f"✓ Cropped region: 263x230 pixels")

# Define precise sampling points (small regions to avoid noise)
objects = [
    [50, 16, 2, 2, "lampes"],
    [214, 20, 2, 2, "libre_volant"],
    [230, 44, 2, 2, "batterie"],
    [246, 62, 2, 2, "ceinture"],
    [184, 212, 2, 2, "phare"],
    [206, 198, 1, 1, "code"],          # Fixed y-coordinate
    [226, 176, 2, 2, "frein_a_main"],  # Fixed y-coordinate
    [170, 146, 5, 5, "signalGauche"],
    [198, 146, 5, 5, "signalDroite"],
]

# STEP 1: ANALYZE COLORS FIRST (on pristine image - NO DRAWING YET)
print("\n" + "="*70)
print("PIXEL ANALYSIS: 0=GRAY (OFF) | 1=COLORED (ON)")
print("="*70)
print(f"{'#':<3} {'Indicator':<20} {'State':<10} {'RGB Value':<20}")
print("-"*70)

results = []
for i, (x1, y1, w, h, label) in enumerate(objects, 1):
    # Validate boundaries
    x2, y2 = min(x1 + w, 263), min(y1 + h, 230)
    x1, y1 = max(0, x1), max(0, y1)
    
    if x2 <= x1 or y2 <= y1:
        results.append((i, label, -1, (0,0,0)))
        print(f"{i:<3} {label:<20} {'❌ INVALID':<10} N/A")
        continue
    
    # Extract region from ORIGINAL cropped image (untouched)
    region = cropped[y1:y2, x1:x2]
    
    # Get average BGR → convert to RGB
    avg_bgr = cv2.mean(region)[:3]
    r, g, b = int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0])
    
    # Detect state: 0=gray (channels similar), 1=colored (significant difference)
    max_diff = max(abs(r - g), abs(r - b), abs(g - b))
    state = 0 if max_diff < 25 else 1  # Threshold tuned for dashboard indicators
    
    # Store result
    results.append((i, label, state, (r, g, b)))
    
    # Terminal color preview (truecolor terminals only)
    color_block = f"\033[48;2;{r};{g};{b}m    \033[0m" if r+g+b > 10 else "    "
    state_display = f"{state} (OFF)" if state == 0 else f"{state} (ON)"
    print(f"{i:<3} {label:<20} {state_display:<10} {color_block} ({r},{g},{b})")

print("="*70)

# STEP 2: DRAW VISUALIZATION ON A SEPARATE COPY (after analysis is complete)
visualized = cropped.copy()
colors_bgr = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255),
              (255, 255, 0), (128, 0, 128), (0, 128, 0), (128, 128, 0)]

for i, (x1, y1, w, h, label) in enumerate(objects):
    x2, y2 = min(x1 + w, 263), min(y1 + h, 230)
    x1, y1 = max(0, x1), max(0, y1)
    
    if x2 > x1 and y2 > y1:
        # Draw on VISUALIZATION copy only (original 'cropped' remains pristine)
        cv2.rectangle(visualized, (x1, y1), (x2, y2), colors_bgr[i % len(colors_bgr)], 1)

# Display visualization
cv2.imshow('Dashboard Analysis (Boxes drawn AFTER analysis)', visualized)
print("\n💡 Press any key in image window to close...")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save outputs
cv2.imwrite('images/analysis_result.png', visualized)
with open('images/states.txt', 'w') as f:
    for _, label, state, _ in results:
        if state != -1:
            f.write(f"{label}: {state}\n")

print("\n✓ Saved:")
print("  - analysis_result.png : Visualization with boxes")
print("  - states.txt          : Indicator states (0=OFF, 1=ON)")