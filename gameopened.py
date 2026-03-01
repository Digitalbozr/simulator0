import cv2
import numpy as np

# =========================
# CONFIG
# =========================
TOLERANCE_PERCENT = 0.40 

game_points = [
    (191, 69),
    (204, 63),
    (211, 123),
    (230, 127),
]

expected_colors = [
    (2, 3, 3),
    (40, 42, 44),
    (252, 252, 252),
    (255, 255, 255),
]

# =========================
# LOAD IMAGE
# =========================
image = cv2.imread('images/2.png')

if image is None:
    print("❌ Image not found")
    exit()

# قص المنطقة المهمة
cropped = image[0:230, 0:263]


# =========================
# COLOR CHECK FUNCTION
# =========================
def color_match(actual, expected, tolerance_percent):

    for i in range(3):  # R,G,B
        allowed_error = expected[i] * tolerance_percent

        if abs(actual[i] - expected[i]) > allowed_error:
            return False

    return True


# =========================
# CHECK GAME
# =========================
all_ok = True

for i, (x, y) in enumerate(game_points):

    b, g, r = cropped[y, x]
    actual_rgb = (int(r), int(g), int(b))
    expected_rgb = expected_colors[i]

    match = color_match(actual_rgb, expected_rgb, TOLERANCE_PERCENT)

    print("=" * 50)
    print(f"Point {i+1} ({x},{y})")
    print("Expected:", expected_rgb)
    print("Actual  :", actual_rgb)
    print("Match   :", match)

    if not match:
        all_ok = False

print("\n" + "=" * 50)

if all_ok:
    print("✅ GAME OPENED")
else:
    print("❌ GAME NOT DETECTED")