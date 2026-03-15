import cv2
import numpy as np
import mss
import time
import serial

PORT = "COM7"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0)

last_state = None
last_game_open = None

TOLERANCE = 0.4

# ===============================
# GAME DETECTION
# ===============================

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

# ===============================
# OBJECTS TO DETECT
# ===============================

objects = [

# engine battery belt brake
[214,20,2,2,"engine",0],
[232,46,2,2,"battery",1],
[246,62,2,2,"belt",2],
[226,176,2,2,"handbrake",3],

# lights
[184,212,2,2,"phare",9],
[206,198,1,1,"code",7],

# indicators
[170,146,5,5,"left",13],
[198,146,5,5,"right",12],

]

# ===============================
# SERIAL READ
# ===============================

def read_serial():

    while ser.in_waiting > 0:

        try:

            msg = ser.readline().decode(errors="ignore").strip()

            if msg:

                print("SERIAL:", msg)

        except:

            pass


# ===============================
# COLOR MATCH
# ===============================

def color_match(actual, expected):

    for i in range(3):

        allowed = expected[i] * TOLERANCE

        if abs(actual[i] - expected[i]) > allowed:

            return False

    return True


# ===============================
# GAME DETECTION
# ===============================

def detect_game(frame):

    for i,(x,y) in enumerate(game_points):

        b,g,r = frame[y,x]

        actual = (int(r),int(g),int(b))

        if not color_match(actual, expected_colors[i]):

            return False

    return True


# ===============================
# DETECT STATE
# ===============================

def detect_state(region, label):

    avg = cv2.mean(region)[:3]

    b = int(avg[0])
    g = int(avg[1])
    r = int(avg[2])

    # =========================
    # ENGINE
    # =========================

    if label == "engine":

        if g > r and g > b:
            return 1

        if r > g and r > b:
            return 0

        return 0


    # =========================
    # CODE LIGHT
    # =========================

    if label == "code":

        if b > 120 and g > 120:
            return 1
        else:
            return 0


    # =========================
    # NORMAL INDICATORS
    # =========================

    diff = max(abs(r-g), abs(r-b), abs(g-b))

    return 0 if diff < 30 else 1


# ===============================
# SERIAL SEND
# ===============================

def send_game(val):

    global last_game_open

    if val != last_game_open:

        ser.write(f"GAME,{val}\n".encode())

        last_game_open = val


def send_state(state):

    global last_state

    if state != last_state:

        ser.write(f"STATE,{state}\n".encode())

        last_state = state


# ===============================
# MAIN LOOP
# ===============================

with mss.mss() as sct:

    monitor = sct.monitors[1]

    while True:

        read_serial()

        screenshot = np.array(sct.grab(monitor))

        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cropped = frame[0:230,0:263]

        game_open = detect_game(cropped)

        send_game(1 if game_open else 0)

        if not game_open:

            time.sleep(0.5)
            continue

        states = ['0'] * 14

        for x,y,w,h,label,index in objects:

            region = cropped[y:y+h, x:x+w]

            s = detect_state(region, label)

            states[index] = str(s)

        state_string = "".join(states)

        print("GAME STATE:", state_string)

        send_state(state_string)

        time.sleep(0.05)
