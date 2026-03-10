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

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

# =========================
# VISION CONFIG
# =========================
FPS_DELAY = 0.05
TOLERANCE_PERCENT = 0.40
THRESHOLD = 30

last_car_state = None

# =========================
# OBJECT POSITIONS
# =========================
objects = [
    [214,20,2,2,"engine"],
    [232,46,2,2,"battery"],
]

# =========================
# GAME DETECTION POINTS
# =========================
game_points = [
(191,69),
(204,63),
(211,123),
(230,127)
]

expected_colors = [
(2,3,3),
(40,42,44),
(252,252,252),
(255,255,255)
]

# =========================
# SEND STATE TO ARDUINO
# =========================
def send_car_state(battery,engine):

    global last_car_state

    state = (battery,engine)

    if state != last_car_state:

        cmd = f"CAR_STATE,{battery},{engine}\n"

        print("SEND ->", cmd.strip())

        ser.write(cmd.encode())

        last_car_state = state


# =========================
# COLOR MATCH FUNCTION
# =========================
def color_match(actual,expected):

    for i in range(3):

        allowed = expected[i] * TOLERANCE_PERCENT

        if abs(actual[i] - expected[i]) > allowed:

            return False

    return True


# =========================
# CHECK IF GAME IS OPEN
# =========================
def is_game_open(img):

    for i,(x,y) in enumerate(game_points):

        b,g,r = img[y,x]

        actual = (int(r),int(g),int(b))

        if not color_match(actual,expected_colors[i]):

            return False

    return True


# =========================
# DETECT ICON STATE
# =========================
def detect_indicator(region,label):

    avg = cv2.mean(region)[:3]

    b = int(avg[0])
    g = int(avg[1])
    r = int(avg[2])

    # =====================
    # ENGINE ICON
    # =====================
    if label == "engine":

        print("ENGINE RGB:", r, g, b)

        # GREEN = ENGINE ON
        if g > r and g > b:
            return 1

        # RED = ENGINE OFF
        else:
            return 0

    # =====================
    # BATTERY ICON
    # =====================
    if label == "battery":

        print("BATTERY RGB:", r, g, b)

        max_diff = max(abs(r-g),abs(r-b),abs(g-b))

        if max_diff < THRESHOLD:
            return 0
        else:
            return 1


# =========================
# MAIN VISION LOOP
# =========================
with mss.mss() as sct:

    monitor = sct.monitors[1]

    print("VISION SYSTEM STARTED")

    while True:

        screenshot = np.array(sct.grab(monitor))

        frame = cv2.cvtColor(
            screenshot,
            cv2.COLOR_BGRA2BGR
        )

        cropped = frame[0:230,0:263]

        # =====================
        # CHECK GAME
        # =====================
        if not is_game_open(cropped):

            print("GAME NOT DETECTED")

            time.sleep(0.5)
            continue

        engine_state = 0
        battery_state = 0

        # =====================
        # DETECT OBJECTS
        # =====================
        for x,y,w,h,label in objects:

            region = cropped[y:y+h,x:x+w]

            state = detect_indicator(region,label)

            if label == "engine":
                engine_state = state

            if label == "battery":
                battery_state = state


        # =====================
        # PRINT STATE
        # =====================
        print(
            "GAME STATE ->",
            "Battery:", battery_state,
            "Engine:", engine_state
        )


        # =====================
        # SEND TO ARDUINO
        # =====================
        send_car_state(
            battery_state,
            engine_state
        )


        time.sleep(FPS_DELAY)
