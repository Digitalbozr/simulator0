import cv2
import numpy as np

# Load and crop image (NO MODIFICATIONS)
image = cv2.imread('images/3.png')
if image is None:
    print("❌ Failed to load image - check path 'images/6.png'")
    exit()

cropped = image[0:230, 0:263]

# Define precise sampling regions
objects = [
    [50, 16, 2, 2, "lampes"],
    [214, 20, 2, 2, "dimarage"],
    [230, 44, 2, 2, "batterie"],
    [246, 62, 2, 2, "ceinture"],
    [184, 212, 2, 2, "phare"],
    [206, 198, 1, 1, "code"],
    [226, 176, 2, 2, "frein_a_main"],
    [170, 146, 5, 5, "signalGauche"],
    [198, 146, 5, 5, "signalDroite"],
]

THRESHOLD = 30
results = []

print("\n" + "="*60)
print("DASHBOARD INDICATOR STATES")
print("0 = OFF  |  1 = ON")
print("="*60)

for i, (x1, y1, w, h, label) in enumerate(objects, 1):

    # Validate boundaries
    x2, y2 = min(x1 + w, 263), min(y1 + h, 230)
    x1, y1 = max(0, x1), max(0, y1)

    if x2 <= x1 or y2 <= y1:
        state = -1
        rgb = (0, 0, 0)
        max_diff = 0
    else:
        # Extract region
        region = cropped[y1:y2, x1:x2]
        avg_bgr = cv2.mean(region)[:3]

        b = int(avg_bgr[0])
        g = int(avg_bgr[1])
        r = int(avg_bgr[2])
        rgb = (r, g, b)

        # =========================
        # SPECIAL RULE FOR DIMARAGE
        # =========================
        if label == "dimarage":

            # Detect RED
            if r > 100 and r > g + 20 and r > b + 20:
                state = 0   # RED → 0

            # Detect GREEN
            elif g > 100 and g > r + 20 and g > b + 20:
                state = 1   # GREEN → 1

            # Fallback
            else:
                state = 0

            max_diff = max(abs(r - g), abs(r - b), abs(g - b))

        else:
            # =========================
            # NORMAL LOGIC FOR OTHERS
            # =========================
            max_diff = max(abs(r - g), abs(r - b), abs(g - b))
            state = 0 if max_diff < THRESHOLD else 1

    results.append((label, state, rgb, max_diff))

    # Print result
    if state == -1:
        print(f"{i}. {label:<20} ❌ INVALID")
    else:
        status = "OFF" if state == 0 else "ON"
        print(f"{i}. {label:<20} {state} [{status:<3}] RGB{rgb} (diff={max_diff})")

print("="*60)
print(f"💡 Threshold: {THRESHOLD}")
print("="*60)

# Save states to file
with open('images/states.txt', 'w') as f:
    for label, state, _, _ in results:
        if state != -1:
            f.write(f"{label.replace(' ', '_')}:{state}\n")

print("\n✓ States saved to: images/states.txt")
print("  Format: indicator_name:state (0=OFF, 1=ON)")