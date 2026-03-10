import cv2
import numpy as np
import mss
import time
import serial
import keyboard

SERIAL_PORT = "COM7"
BAUDRATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUDRATE)

FPS_DELAY = 0.05

game_battery = 0
game_engine = 0

objects = [
[214,20,2,2,"engine"],
[232,46,2,2,"battery"]
]

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


def press_e():
    keyboard.press_and_release("e")
    print("SEND E")


with mss.mss() as sct:

    monitor=sct.monitors[1]

    print("SYSTEM STARTED")

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

        game_engine=engine
        game_battery=battery

        # read arduino buttons
        if ser.in_waiting:

            line=ser.readline().decode().strip()

            if line.startswith("BTN"):

                _,pin,value=line.split(",")

                pin=int(pin)
                value=int(value)

                if value==0:  # button pressed

                    print("BUTTON",pin)

                    if pin==16:

                        if game_battery==1:
                            press_e()

                    if pin==14:

                        if game_engine==1:
                            press_e()
                        else:
                            keyboard.press("e")
                            time.sleep(0.7)
                            keyboard.release("e")

        time.sleep(FPS_DELAY)
