import main
import time
import machine 

now = (2020, 1, 21, 2, 10, 32, 36, 0)

def ShowTime():
    rtc = machine.RTC()
    rtc.datetime(now)
    while True:
        main.oled.fill(0)
        t = rtc.datetime()
        main.oled.text(str(t[4]) + ":" + str(t[5]) + ":" + str(t[6]), 0, 0)
        main.oled.show()
        time.sleep(0.1)

