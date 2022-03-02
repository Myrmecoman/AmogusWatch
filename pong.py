import main
import pyb

playerPos = 32
ballx = 64
bally = 32
lastx = 1
lasty = 1

valuesQueue = []
detectedMin = 5000
detectedMax = 0

def DisplaySprites():
    global playerPos
    global ballx
    global lastx
    global bally
    global lasty
    global valuesQueue
    global detectedMin
    global detectedMax

    v = pyb.ADC('A2').read()
    if (v < detectedMin + (detectedMax - detectedMin)/3):
        pyb.LED(2).off()
        pyb.LED(3).off()
        pyb.LED(1).on()
    elif (v < detectedMin + (2 * (detectedMax - detectedMin))/3):
        pyb.LED(1).off()
        pyb.LED(3).off()
        pyb.LED(2).on()
    else:
        pyb.LED(1).off()
        pyb.LED(2).off()
        pyb.LED(3).on()

    # calibrating potentiometer
    valuesQueue.append(v)
    if len(valuesQueue) > 10:
        del valuesQueue[0]
    mostFrequent = max(set(valuesQueue), key = valuesQueue.count)
    if mostFrequent < detectedMin:
        detectedMin = mostFrequent
    if mostFrequent > detectedMax:
        detectedMax = mostFrequent

    diff = detectedMax - detectedMin
    if diff <= 0:
        diff = 4096
    normalized = (v - detectedMin) / diff
    if normalized < 0:
        normalized = 0
    elif normalized > 1:
        normalized = 1
    screenPos = int(normalized * 64)
    #print(screenPos)
    main.oled.fill(0)
    main.oled.line(0, 0, 127, 0, 1)
    main.oled.line(0, 63, 127, 63, 1)
    main.oled.line(127, 0, 127, 63, 1)
    main.oled.fill_rect(0, screenPos - 5, 4, screenPos + 5, 1)
    main.oled.show()