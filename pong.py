import main
import pyb


playerPos = 32
ballx = 64
bally = 32
speedx = 1
speedy = 1

valuesQueue = []
detectedMin = 5000
detectedMax = 0


def DrawRect(x0, y0, x1, y1):
    for i in range(x0, x1 + 1):
        main.oled.line(i, y0, i, y1, 1)

def DisplaySprites(minP, maxP):
    global playerPos
    global ballx
    global speedx
    global bally
    global speedy
    global valuesQueue
    global detectedMin
    global detectedMax

    v = pyb.ADC('A2').read()

    print("min:" + str(minP) + '  ' + "max:" + str(maxP) + '  ' + "current : " + str(v))

    diff = maxP - minP
    if diff <= 0:
        diff = 4096
    normalized = (v - minP) / diff
    if normalized < 0:
        normalized = 0
    elif normalized > 1:
        normalized = 1
    screenPos = int(normalized * 64)
    main.oled.fill(0)
    main.oled.line(0, 0, 127, 0, 1)                      # top line
    main.oled.line(0, 63, 127, 63, 1)                    # bottom line
    main.oled.line(127, 0, 127, 63, 1)                   # right line
    DrawRect(0, screenPos - 6, 3, screenPos + 6)         # player
    DrawRect(ballx - 1, bally - 1, ballx + 1, bally + 1) # ball
    main.oled.show()
