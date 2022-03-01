import time
import machine 

now = (2020, 1, 21, 2, 10, 32, 36, 0)

rtc = machine.RTC()
rtc.datetime(now)

import main

def ShowTime():
    global rtc
    while True:
        main.oled.fill(0)
        t = rtc.datetime()
        main.oled.text(str(t[4]) + ":" + str(t[5]) + ":" + str(t[6]), 0, 0)
        main.oled.show()
        time.sleep(0.1)

