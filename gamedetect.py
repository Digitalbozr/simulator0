import cv2
import numpy as np
import mss
import time

# =========================
# CONFIG
# =========================
TOLERANCE_PERCENT = 0.40
MONITOR_INDEX = 2   

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
# COLOR CHECK FUNCTION
# =========================
def color_match(actual, expected, tolerance_percent):
    for i in range(3):
        allowed_error = expected[i] * tolerance_percent
        if abs(actual[i] - expected[i]) > allowed_error:
            return False
    return True


# =========================
# MAIN LOOP
# =========================
with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]

    print("Monitoring started on screen", MONITOR_INDEX)
    print("Press Ctrl+C to stop\n")

    while True:

        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # قص المنطقة المهمة
        cropped = frame[0:230, 0:263]

        all_ok = True

        for i, (x, y) in enumerate(game_points):

            b, g, r = cropped[y, x]
            actual_rgb = (int(r), int(g), int(b))
            expected_rgb = expected_colors[i]

            match = color_match(actual_rgb, expected_rgb, TOLERANCE_PERCENT)

            if not match:
                all_ok = False

        if all_ok:
            print("✅ GAME OPENED")
        else:
            print("❌ GAME NOT DETECTED")

        time.sleep(0.2)  # كل نصف ثانية