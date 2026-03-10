import cv2
import numpy as np
import mss
import time
import serial

SERIAL_PORT="COM7"
BAUDRATE=115200

ser=serial.Serial(SERIAL_PORT,BAUDRATE)

FPS_DELAY=0.05

last_state=None

objects=[
[214,20,2,2,"engine"],
[232,46,2,2,"battery"]
]

def send_state(battery,engine):

    global last_state

    state=(battery,engine)

    if state==last_state:
        return

    cmd=f"CAR_STATE,{battery},{engine}\n"

    print("SEND ->",cmd.strip())

    ser.write(cmd.encode())

    last_state=state


def detect(region,label):

    avg=cv2.mean(region)[:3]

    b=int(avg[0])
    g=int(avg[1])
    r=int(avg[2])

    if label=="engine":

        if g>r and g>b:
            return 1
        else:
            return 0

    if label=="battery":

        diff=max(abs(r-g),abs(r-b),abs(g-b))

        if diff<30:
            return 0
        else:
            return 1


with mss.mss() as sct:

    monitor=sct.monitors[1]

    print("VISION STARTED")

    while True:

        img=np.array(sct.grab(monitor))
        frame=cv2.cvtColor(img,cv2.COLOR_BGRA2BGR)

        cropped=frame[0:230,0:263]

        engine=0
        battery=0

        for x,y,w,h,label in objects:

            region=cropped[y:y+h,x:x+w]

            state=detect(region,label)

            if label=="engine":
                engine=state

            if label=="battery":
                battery=state

        print("STATE -> BAT:",battery,"ENG:",engine)

        send_state(battery,engine)

        time.sleep(FPS_DELAY)
