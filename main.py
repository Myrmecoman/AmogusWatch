# main.py -- put your code here!
# CTRL-D to reboot

import watch
import plot
import amogus
#import _thread # can't import for some reason
import pyb
import machine
import ssd1306
import time
from pyb import ADC
from pyb import Pin


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

def PrepareSPO2():
    pa7 = machine.Pin('A7', machine.Pin.OUT)
    pa7.value(1)
    pa1 = Pin('A1', Pin.IN, Pin.PULL_UP)
    #pa6 = Pin('A6', Pin.IN, Pin.PULL_DOWN) # put output on ground
    return pa7


amogus.LCDamogus()
volt = PrepareSPO2()

isPair = 0
backGroundNoise = 0
while True:
    if isPair == 0:
        volt.value(0)
        time.sleep(0.005)
        backGroundNoise = ADC('A1').read()
    else:
        volt.value(1)
        time.sleep(0.005)
        plot.AddValue(ADC('A1').read() - backGroundNoise)
        plot.DisplayValues()
    isPair += 1
    isPair = isPair % 2
