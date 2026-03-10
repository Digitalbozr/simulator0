import cv2
import numpy as np
import mss
import time
import serial

# =========================
# SERIAL CONFIG
# =========================
SERIAL_PORT = "COM7"
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

# =========================
# SCREEN CAPTURE CONFIG
# =========================
MONITOR_INDEX = 1
FPS_DELAY = 0.05

# =========================
# LAST STATE (anti spam)
# =========================
last_state = None

# =========================
# ICON POSITIONS
# =========================
objects = [
    [214,20,2,2,"engine"],
    [232,46,2,2,"battery"],
]

# =========================
# COLOR DETECTION
# =========================
def detect_indicator(region,label):

    avg = cv2.mean(region)[:3]

    b = int(avg[0])
    g = int(avg[1])
    r = int(avg[2])

    if label == "engine":

        print("ENGINE RGB:", r,g,b)

        # green = engine ON
        if g > r and g > b:
            return 1

        # red = engine OFF
        return 0


    if label == "battery":

        print("BATTERY RGB:", r,g,b)

        diff = max(abs(r-g),abs(r-b),abs(g-b))

        if diff < 30:
            return 0
        else:
            return 1


# =========================
# SEND STATE TO ARDUINO
# =========================
def send_state(battery,engine):

    global last_state

    state = (battery,engine)

    if state == last_state:
        return

    cmd = f"CAR_STATE,{battery},{engine}\n"

    print("SEND ->",cmd.strip())

    ser.write(cmd.encode())

    last_state = state


# =========================
# MAIN LOOP
# =========================
with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]

    print("VISION SYSTEM STARTED")

    while True:

        screenshot = np.array(sct.grab(monitor))

        frame = cv2.cvtColor(
            screenshot,
            cv2.COLOR_BGRA2BGR
        )

        cropped = frame[0:230,0:263]

        engine_state = 0
        battery_state = 0

        for x,y,w,h,label in objects:

            region = cropped[y:y+h,x:x+w]

            state = detect_indicator(region,label)

            if label == "engine":
                engine_state = state

            if label == "battery":
                battery_state = state

        print("GAME STATE -> BAT:",battery_state,"ENG:",engine_state)

        send_state(battery_state,engine_state)

        time.sleep(FPS_DELAY)
