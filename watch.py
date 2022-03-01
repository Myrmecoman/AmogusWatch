import time
import main

def ShowTime():
    main.oled.fill(0)
    t = main.rtc.datetime()
    main.oled.text((str(t[4]), '0' + str(t[4]))[t[4] < 10] + ":" + (str(t[5]), '0' + str(t[5]))[t[5] < 10] + ":" + (str(t[6]), '0' + str(t[6]))[t[6] < 10], 30, 32)
    main.oled.show()
    time.sleep(0.1)
