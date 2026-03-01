import cv2
import numpy as np
import mss
import time

# =========================
# CONFIG
# =========================
MONITOR_INDEX = 2   # غيّرها (2 أو 3 حسب شاشتك)
THRESHOLD = 30
FPS_DELAY = 0.1     # كل 100ms

# =========================
# DASHBOARD REGIONS
# =========================
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

# =========================
# MAIN LOOP
# =========================
with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]

    print("Live Dashboard Reader Started...")
    print("Press Ctrl+C to stop\n")

    while True:

        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cropped = frame[0:230, 0:263]

        print("\n" + "="*60)
        print("DASHBOARD INDICATOR STATES")
        print("="*60)

        for i, (x1, y1, w, h, label) in enumerate(objects, 1):

            x2, y2 = min(x1 + w, 263), min(y1 + h, 230)

            region = cropped[y1:y2, x1:x2]
            avg_bgr = cv2.mean(region)[:3]

            b, g, r = int(avg_bgr[0]), int(avg_bgr[1]), int(avg_bgr[2])
            rgb = (r, g, b)

            # =========================
            # SPECIAL RULE FOR DIMARAGE
            # =========================
            if label == "dimarage":

                if r > 100 and r > g + 20 and r > b + 20:
                    state = 0   # RED
                elif g > 100 and g > r + 20 and g > b + 20:
                    state = 1   # GREEN
                else:
                    state = 0

                max_diff = max(abs(r-g), abs(r-b), abs(g-b))

            else:
                max_diff = max(abs(r-g), abs(r-b), abs(g-b))
                state = 0 if max_diff < THRESHOLD else 1

            status = "OFF" if state == 0 else "ON"

            print(f"{i}. {label:<20} {state} [{status:<3}] RGB{rgb} (diff={max_diff})")

        print("="*60)
        print(f"Threshold: {THRESHOLD}")
        print("="*60)

        time.sleep(FPS_DELAY)