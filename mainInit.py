# CTRL-D to reboot

import watch
import plot
import amogus
import pong
import pyb
import machine
import ssd1306
import time
from pyb import ADC
from pyb import Pin
#import _thread # can't import for some reason


now = (2020, 1, 21, 2, 10, 32, 36, 0)
rtc = machine.RTC()
rtc.datetime(now)
lastCall = rtc.datetime()

menuSelected = 0
i2c = machine.SoftI2C(scl=machine.Pin('B8'), sda=machine.Pin('B9'))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


def ClearLCD():
    global oled
    oled.fill(0)

def PrepareSPO2():
    pa7 = Pin('A7', Pin.OUT)
    pa7.value(1)
    pa1 = Pin('A1', Pin.IN, Pin.PULL_UP)
    #pa6 = Pin('A6', Pin.IN, Pin.PULL_DOWN) # put output on ground
    return pa7

def PreparePmetre():
    pa0 = Pin('A0', Pin.OUT)
    pa0.value(1)
    pa2 = Pin('A2', Pin.IN, Pin.PULL_UP)
    return pa0

def rtcToMs(rtcTime):
    return rtcTime[3] * 86400000 + rtcTime[4] * 3600000 + rtcTime[5] * 60000 + rtcTime[6] * 1000 + rtcTime[7] // 1000

def callback(p):
    global menuSelected
    global lastCall
    currentTime = rtcToMs(rtc.datetime())
    if (currentTime - rtcToMs(lastCall) > 180):
        menuSelected += 1
        menuSelected %= 4
        lastCall = rtc.datetime()

def initButtonCallback():
    pa8 = Pin('A8', Pin.IN, Pin.PULL_UP)
    pa8.irq(trigger=Pin.IRQ_FALLING, handler=callback)


initButtonCallback()
# graph values
volt = PrepareSPO2()
isPair = 0
loopBeforeDisplay = 10
loopNb = 0
backGroundNoise = 0
# end of graph values
# potentiometer
pmetr = PreparePmetre()

# end of potentiometer
def menus():
    global isPair
    global volt
    global loopBeforeDisplay
    global loopNb
    global backGroundNoise
    global pmetr
    global valuesQueue
    global detectedMin
    global detectedMax
    while True:
        if menuSelected == 0:
            amogus.LCDamogus()
        elif menuSelected == 1:
            if isPair == 0:
                volt.value(0)
                time.sleep(0.005)
                backGroundNoise = ADC('A1').read()
            else:
                volt.value(1)
                time.sleep(0.005)
                plot.AddValue(ADC('A1').read() - backGroundNoise)
                if loopNb <= 1:
                    plot.DisplayValues()
            loopNb += 1
            loopNb = loopNb % loopBeforeDisplay
            isPair += 1
            isPair = isPair % 2
        elif menuSelected == 2:
            watch.ShowTime()
        else:
            pmetr.value(1)
            time.sleep(0.01)
            pong.DisplaySprites()
            pmetr.value(0)

