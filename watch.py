import time
import main

def ShowTime():
    main.oled.fill(0)
    t = main.rtc.datetime()
    main.oled.text(str(t[4]) + ":" + str(t[5]) + ":" + str(t[6]), 0, 0)
    main.oled.show()
    time.sleep(0.1)
