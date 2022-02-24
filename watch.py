import machine
import ssd1306
import utime as time

now = time.time()
tm = time.localtime(now)
yearMonthDay = str(tm[0]) + ':' + str(tm[1]) + ':' + str(tm[2])
hourMinuteSec = str(tm[3]) + ':' + str(tm[4]) + ':' + str(tm[5])

i2c = machine.SoftI2C(scl=machine.Pin('B8'), sda=machine.Pin('B9'))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def UpdateTime():
    yearMonthDay = str(tm[0]) + ':' + str(tm[1]) + ':' + str(tm[2])
    hourMinuteSec = str(tm[3]) + ':' + str(tm[4]) + ':' + str(tm[5])

def ShowTime():
    while True:
        UpdateTime()
        oled.fill(0)
        oled.text(hourMinuteSec, 0, 0)
        oled.show()

