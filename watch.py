import main
import utime as time

now = time.time()
tm = time.localtime(now)
yearMonthDay = str(tm[0]) + ':' + str(tm[1]) + ':' + str(tm[2])
hourMinuteSec = str(tm[3]) + ':' + str(tm[4]) + ':' + str(tm[5])

def UpdateTime():
    global yearMonthDay
    yearMonthDay = str(tm[0]) + ':' + str(tm[1]) + ':' + str(tm[2])
    global hourMinuteSec
    hourMinuteSec = str(tm[3]) + ':' + str(tm[4]) + ':' + str(tm[5])

def ShowTime():
    while True:
        UpdateTime()
        main.oled.fill(0)
        global hourMinuteSec
        main.oled.text(hourMinuteSec, 0, 0)
        main.oled.show()

