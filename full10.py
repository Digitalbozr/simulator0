import cv2
import numpy as np
import mss
import time
import serial

MONITOR_INDEX = 1
SERIAL_PORT = "COM7"
BAUDRATE = 115200

FPS_DELAY = 0.05
TOLERANCE_PERCENT = 0.40
THRESHOLD = 30

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

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

objects = [
    [214,20,2,2,"engine",0],
    [232,46,2,2,"battery",1],
    [246,62,2,2,"seatbelt",2],
    [226,176,2,2,"handbrake",3],
    [184,212,2,2,"far",4],
    [206,198,1,1,"code",5],
    [170,146,5,5,"left",6],
    [198,146,5,5,"right",7],
]

def send_game_state(states):

    msg = "GAME,"
    for s in states:
        msg += str(s) + ","
    msg += "END\n"

    ser.write(msg.encode())


def color_match(actual, expected):

    for i in range(3):
        allowed_error = expected[i] * TOLERANCE_PERCENT
        if abs(actual[i] - expected[i]) > allowed_error:
            return False

    return True


def is_game_open(cropped):

    for i,(x,y) in enumerate(game_points):

        b,g,r = cropped[y,x]
        actual = (int(r),int(g),int(b))

        if not color_match(actual,expected_colors[i]):
            return False

    return True


def detect_indicator(region,label):

    avg_bgr = cv2.mean(region)[:3]
    b,g,r = int(avg_bgr[0]),int(avg_bgr[1]),int(avg_bgr[2])

    if label == "engine":

        if r > 100 and r > g+20 and r > b+20:
            return 0

        elif g > 100 and g > r+20 and g > b+20:
            return 1

        else:
            return 0

    else:

        max_diff = max(abs(r-g),abs(r-b),abs(g-b))

        if max_diff < THRESHOLD:
            return 0
        else:
            return 1


with mss.mss() as sct:

    monitor = sct.monitors[MONITOR_INDEX]

    while True:

        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        cropped = frame[0:230,0:263]

        if not is_game_open(cropped):
            time.sleep(0.5)
            continue

        states = [0]*8

        for x,y,w,h,label,index in objects:

            region = cropped[y:y+h, x:x+w]

            state = detect_indicator(region,label)

            states[index] = state

        send_game_state(states)

        time.sleep(FPS_DELAY)
