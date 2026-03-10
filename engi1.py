import cv2
import numpy as np
import mss
import time
import serial

# ============================================================
# SERIAL CONFIG
# ============================================================

SERIAL_PORT = "COM7"
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

# ============================================================
# CONFIG
# ============================================================

FPS_DELAY = 0.05
TOLERANCE_PERCENT = 0.40
THRESHOLD = 30
ANTI_SPAM_DELAY = 0.3

BLINK_WINDOW = 0.8
BLINK_THRESHOLD = 0.5

# ============================================================
# INDICES
# ============================================================

HAZARD_INDEX = 5
LEFT_INDEX = 13
RIGHT_INDEX = 12
CODE_INDEX = 7

# ============================================================
# KEY MAP (keyboard actions)
# ============================================================

key_map = {

    2: 'c',   # ceinture
    3: '1',   # frein a main
    9: 'g',   # phare
    7: 'p',   # code
    10: 'k',
    12: 'l',  # signal droite
    13: 'r',  # signal gauche
    5: 'h',   # hazard

}

hold_indices = [0,4,11]

# ============================================================
# SERIAL STATE
# ============================================================

real_state = {}
last_send_time = {}

serial_buffer = ""
last_code_state_sent = None

# ============================================================
# BLINK MEMORY
# ============================================================

blink_history = {

    LEFT_INDEX: [],
    RIGHT_INDEX: []

}

# ============================================================
# GAME DETECTION POINTS
# ============================================================

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

# ============================================================
# OBJECTS (ALL GAME INDICATORS)
# ============================================================

objects = [

    [214, 20, 2, 2, "dimarage", 0],
    [232, 46, 2, 2, "batterie", 1],
    [246, 62, 2, 2, "ceinture", 2],
    [184, 212, 2, 2, "phare", 9],
    [206, 198, 1, 1, "code", 7],
    [226, 176, 2, 2, "frein_a_main", 3],
    [170, 146, 5, 5, "signalGauche", 13],
    [198, 146, 5, 5, "signalDroite", 12],

]

# ============================================================
# SEND KEY TO MICRO
# ============================================================

def send_to_micro(key):

    command = f"PRESS,{key}\n"

    ser.write(command.encode())

# ============================================================
# SEND CODE STATE
# ============================================================

def send_code_state(state):

    global last_code_state_sent

    if state != last_code_state_sent:

        ser.write(f"CODE_STATE,{state}\n".encode())

        last_code_state_sent = state

# ============================================================
# COLOR MATCH
# ============================================================

def color_match(actual, expected):

    for i in range(3):

        allowed_error = expected[i] * TOLERANCE_PERCENT

        if abs(actual[i] - expected[i]) > allowed_error:

            return False

    return True

# ============================================================
# CHECK GAME OPEN
# ============================================================

def is_game_open(cropped):

    for i,(x,y) in enumerate(game_points):

        b,g,r = cropped[y,x]

        actual = (int(r),int(g),int(b))

        if not color_match(actual, expected_colors[i]):

            return False

    return True

# ============================================================
# DETECT INDICATOR
# ============================================================

def detect_indicator(region,label):

    avg = cv2.mean(region)[:3]

    b,g,r = int(avg[0]),int(avg[1]),int(avg[2])

    if label == "dimarage":

        if r > 100 and r > g + 20 and r > b + 20:
            return 0

        elif g > 100 and g > r + 20 and g > b + 20:
            return 1

        else:
            return 0

    else:

        max_diff = max(abs(r-g),abs(r-b),abs(g-b))

        return 0 if max_diff < THRESHOLD else 1

# ============================================================
# BLINK DETECTION
# ============================================================

def process_blink(index,current_state):

    now = time.time()

    blink_history[index] = [

        (t,s) for (t,s) in blink_history[index]
        if now - t <= BLINK_WINDOW

    ]

    blink_history[index].append((now,current_state))

    if len(blink_history[index]) < 3:
        return current_state

    on_count = sum(1 for (_,s) in blink_history[index] if s==1)

    ratio = on_count / len(blink_history[index])

    return 1 if ratio >= BLINK_THRESHOLD else 0

# ============================================================
# SERIAL READER
# ============================================================

def read_serial():

    global serial_buffer

    if ser.in_waiting > 0:

        data = ser.read(ser.in_waiting).decode(errors="ignore")

        serial_buffer += data

        while "\n" in serial_buffer:

            line,serial_buffer = serial_buffer.split("\n",1)

            line = line.strip()

            if line.startswith("STATE"):

                parts = line.replace("STATE,","").replace(",END","").split(",")

                for i,val in enumerate(parts):

                    real_state[i] = int(val)

# ============================================================
# MAIN LOOP
# ============================================================

with mss.mss() as sct:

    monitor = sct.monitors[1]

    while True:

        read_serial()

        screenshot = np.array(sct.grab(monitor))

        frame = cv2.cvtColor(
            screenshot,
            cv2.COLOR_BGRA2BGR
        )

        cropped = frame[0:230,0:263]

        if not is_game_open(cropped):

            time.sleep(0.5)
            continue

        left_state = None
        right_state = None
        code_state = None

        for x,y,w,h,label,index in objects:

            region = cropped[y:y+h,x:x+w]

            game_state = detect_indicator(region,label)

            if index == LEFT_INDEX:

                left_state = process_blink(index,game_state)

            elif index == RIGHT_INDEX:

                right_state = process_blink(index,game_state)

            elif index == CODE_INDEX:

                code_state = game_state

        hazard_game_state = 1 if (left_state == 1 and right_state == 1) else 0

        send_code_state(code_state)

        if HAZARD_INDEX in real_state:

            if real_state[HAZARD_INDEX] != hazard_game_state:

                now = time.time()

                if HAZARD_INDEX not in last_send_time or \
                   (now - last_send_time[HAZARD_INDEX]) > ANTI_SPAM_DELAY:

                    send_to_micro(key_map[HAZARD_INDEX])

                    last_send_time[HAZARD_INDEX] = now

        if hazard_game_state == 1:

            time.sleep(FPS_DELAY)

            continue

        for x,y,w,h,label,index in objects:

            if index in hold_indices:
                continue

            if index == LEFT_INDEX:

                game_state = left_state

            elif index == RIGHT_INDEX:

                game_state = right_state

            else:

                region = cropped[y:y+h,x:x+w]

                game_state = detect_indicator(region,label)

            if index in real_state:

                if real_state[index] != game_state:

                    now = time.time()

                    if index not in last_send_time or \
                       (now - last_send_time[index]) > ANTI_SPAM_DELAY:

                        if index in key_map:

                            send_to_micro(key_map[index])

                            last_send_time[index] = now

        time.sleep(FPS_DELAY)
