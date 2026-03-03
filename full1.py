import cv2
import numpy as np
import mss
import time
import serial
from pynput.keyboard import Controller

# =========================
# CONFIG
# =========================
MONITOR_INDEX = 1
SERIAL_PORT = "COM8"
BAUDRATE = 115200
FPS_DELAY = 0.05
TOLERANCE_PERCENT = 0.40
THRESHOLD = 30
ANTI_SPAM_DELAY = 0.3

keyboard = Controller()
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.01)

# =========================
# GAME DETECTION POINTS
# =========================
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
# DASHBOARD REGIONS
# =========================
objects = [
    [50, 16, 2, 2, "lampes", 8],
    [214, 20, 2, 2, "dimarage", 0],
    [232, 46, 2, 2, "batterie", 1],
    [246, 62, 2, 2, "ceinture", 2],
    [184, 212, 2, 2, "phare", 10],
    [206, 198, 1, 1, "code", 9],
    [226, 176, 2, 2, "frein_a_main", 3],
    [170, 146, 5, 5, "signalGauche", 12],
    [198, 146, 5, 5, "signalDroite", 13],
    
    [198, 146, 5, 5, "4 signal", 5],
    [198, 146, 5, 5, "4 signal", 5],
    # fog 12
    # horn 11
]

# =========================
# KEY MAP (INDEX → KEY)
# =========================
key_map = {
    2: 'c',   # ceinture
    3: '1',   # frein
    8: 'p',   # position
    9: 'g',   # fog / code
    10: 'd',  # dipped
    12: 'l',  # left
    13: 'r',  # right
}

hold_indices = [0, 4, 11] 

last_send_time = {}
real_state = {}

# =========================
# FUNCTIONS
# =========================
def press_key(key):
    keyboard.press(key)
    keyboard.release(key)
    print("SYNC →", key)


def color_match(actual, expected):
    for i in range(3):
        allowed_error = expected[i] * TOLERANCE_PERCENT
        if abs(actual[i] - expected[i]) > allowed_error:
            return False
    return True


def is_game_open(cropped):
    for i, (x, y) in enumerate(game_points):
        b, g, r = cropped[y, x]
        actual = (int(r), int(g), int(b))
        if not color_match(actual, expected_colors[i]):
            return False
    return True


def detect_indicator(region, label):
    avg_bgr = cv2.mean(region)[:3]
    b, g, r = int(avg_bgr[0]), int(avg_bgr[1]), int(avg_bgr[2])

    if label == "dimarage":
        if r > 100 and r > g + 20 and r > b + 20:
            return 0
        elif g > 100 and g > r + 20 and g > b + 20:
            return 1
        else:
            return 0
    else:
        max_diff = max(abs(r-g), abs(r-b), abs(g-b))
        return 0 if max_diff < THRESHOLD else 1

serial_buffer = ""

def read_serial():
    global serial_buffer

    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting).decode(errors="ignore")
        serial_buffer += data

        while "\n" in serial_buffer:
            line, serial_buffer = serial_buffer.split("\n", 1)
            line = line.strip()

            if line:
                print("SERIAL →", line)

            if line.startswith("STATE"):
                parts = line.replace("STATE,", "").replace(",END", "").split(",")

                for i, val in enumerate(parts):
                    real_state[i] = int(val)

# =========================
# MAIN LOOP
# =========================
with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]

    print("PYTHON MASTER ENGINE RUNNING...\n")

    while True:

        # ---- READ MICRO ----
        read_serial()

        # ---- CAPTURE SCREEN ----
        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cropped = frame[0:230, 0:263]

        # ---- CHECK GAME ----
        if not is_game_open(cropped):
            time.sleep(0.5)
            continue

        # ---- DASHBOARD READ ----
        for x1, y1, w, h, label, index in objects:

            if index in hold_indices:
                continue

            x2, y2 = min(x1 + w, 263), min(y1 + h, 230)
            region = cropped[y1:y2, x1:x2]

            game_state = detect_indicator(region, label)

            if index in real_state:

                if real_state[index] != game_state:

                    now = time.time()

                    if index not in last_send_time or \
                       (now - last_send_time[index]) > ANTI_SPAM_DELAY:

                        if index in key_map:
                            press_key(key_map[index])
                            last_send_time[index] = now

        time.sleep(FPS_DELAY)