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

objects = [
[214,20,2,2,"engine",0],
[232,46,2,2,"battery",1],
[246,62,2,2,"belt",2],
[184,212,2,2,"lights",9],
[226,176,2,2,"handbrake",3]
]

def color_match(actual, expected):

    for i in range(3):

        allowed = expected[i] * TOLERANCE

        if abs(actual[i] - expected[i]) > allowed:

            return False

    return True


def detect_game(frame):

    for i,(x,y) in enumerate(game_points):

        b,g,r = frame[y,x]

        actual = (int(r),int(g),int(b))

        if not color_match(actual, expected_colors[i]):

            return False

    return True


def detect_state(region):

    avg = cv2.mean(region)[:3]

    b,g,r = int(avg[0]),int(avg[1]),int(avg[2])

    diff = max(abs(r-g),abs(r-b),abs(g-b))

    if diff < 30:

        return 0

    else:

        return 1


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


with mss.mss() as sct:

    monitor = sct.monitors[1]

    while True:

        screenshot = np.array(sct.grab(monitor))

        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cropped = frame[0:230,0:263]

        game_open = detect_game(cropped)

        send_game(1 if game_open else 0)

        if not game_open:

            time.sleep(0.5)
            continue

        states = ['0']*14

        for x,y,w,h,label,index in objects:

            region = cropped[y:y+h, x:x+w]

            s = detect_state(region)

            states[index] = str(s)

        state_string = "".join(states)

        send_state(state_string)

        time.sleep(0.05)
