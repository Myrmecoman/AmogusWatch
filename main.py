# main.py -- put your code here!
# CTRL-D to reboot

import watch
import amogus
import pyb
import machine
import ssd1306
from pyb import ADC


i2c = machine.SoftI2C(scl=machine.Pin('B8'), sda=machine.Pin('B9'))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


def LEDsOn():
    pyb.LED(1).on()
    pyb.LED(2).on()
    pyb.LED(3).on()

def LEDsOff():
    pyb.LED(1).off()
    pyb.LED(2).off()
    pyb.LED(3).off()

def LCDtext(text):
    global oled
    oled.fill(0)
    oled.text(text, 0, 0)
    oled.show()

def ClearLCD():
    global oled
    oled.fill(0)

def SPO2on():
    p = pyb.Pin('A7')
    tim = pyb.Timer(1, freq=1)
    ch = tim.channel(1, pyb.Timer.PWM, pin=p)
    ch.pulse_width_percent(50)


#LCDamogus()
SPO2on()
