import cv2
import numpy as np
import mss
import time
import serial

# ============================================================
# CONFIGURATION
# ============================================================

MONITOR_INDEX = 1
SERIAL_PORT = "COM7"
BAUDRATE = 115200

FPS_DELAY = 0.05
TOLERANCE_PERCENT = 0.40
THRESHOLD = 30
ANTI_SPAM_DELAY = 0.3

LEFT_INDEX = 12
RIGHT_INDEX = 13
CODE_INDEX = 7

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

real_state = {}
serial_buffer = ""
last_code_state_sent = None

# ============================================================
# DASHBOARD REGIONS
# ============================================================

objects = [
    [184, 212, 2, 2, "phare", 9],
    [206, 198, 1, 1, "code", 7],
]

# ============================================================
# FUNCTIONS
# ============================================================

def send_code_state(state):
    global last_code_state_sent

    if state != last_code_state_sent:
        ser.write(f"CODE_STATE,{state}\n".encode())
        print("SEND → CODE_STATE,", state)
        last_code_state_sent = state


def detect_indicator(region):
    avg_bgr = cv2.mean(region)[:3]
    b, g, r = int(avg_bgr[0]), int(avg_bgr[1]), int(avg_bgr[2])
    max_diff = max(abs(r-g), abs(r-b), abs(g-b))
    return 0 if max_diff < THRESHOLD else 1


def read_serial():
    global serial_buffer

    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting).decode(errors="ignore")
        serial_buffer += data

        while "\n" in serial_buffer:
            line, serial_buffer = serial_buffer.split("\n", 1)
            line = line.strip()

            if line.startswith("STATE"):
                parts = line.replace("STATE,", "").replace(",END", "").split(",")
                for i, val in enumerate(parts):
                    real_state[i] = int(val)

# ============================================================
# MAIN LOOP
# ============================================================

with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]
    print("PYTHON MASTER ENGINE RUNNING...\n")

    while True:

        read_serial()

        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        cropped = frame[0:230, 0:263]

        code_state = None

        for x1, y1, w, h, label, index in objects:

            if index == CODE_INDEX:
                region = cropped[y1:y1+h, x1:x1+w]
                code_state = detect_indicator(region)

        if code_state is not None:
            send_code_state(code_state)

        time.sleep(FPS_DELAY)
