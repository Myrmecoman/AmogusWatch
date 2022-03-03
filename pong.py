import mainInit as main
import pyb


score = 0

playerPos = 32
ballx = 64
bally = 32
speedx = 2
speedy = 2

valuesQueue = []
detectedMin = 5000
detectedMax = 0


def DrawRect(x0, y0, x1, y1):
    for i in range(x0, x1 + 1):
        main.oled.line(i, y0, i, y1, 1)

def DisplaySprites():
    global playerPos
    global score
    global ballx
    global speedx
    global bally
    global speedy
    global valuesQueue
    global detectedMin
    global detectedMax

    # ball collision on walls
    if ballx < 125 and speedx == 2:
        ballx += 2
    elif ballx > 2 and speedx == -2:
        ballx -= 2
    else:
        if speedx < 0: # missed the ball
            score = 0
            ballx = 64
            bally = 32
            speedx = 2
            speedy = 2
        else:
            speedx = -speedx

    if bally < 61 and speedy == 2:
        bally += 2
    elif bally > 2 and speedy == -2:
        bally -= 2
    else:
        speedy = -speedy

    # ball collision on player
    yDist = abs(playerPos - bally)
    if ballx < 5 and speedx == -2 and yDist < 6:
        speedx = -speedx
        score += 1

    v = pyb.ADC('A2').read()

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
    playerPos = int(normalized * 64)
    main.oled.fill(0)
    main.oled.line(0, 0, 127, 0, 1)                      # top line
    main.oled.line(0, 63, 127, 63, 1)                    # bottom line
    main.oled.line(127, 0, 127, 63, 1)                   # right line
    DrawRect(0, playerPos - 6, 2, playerPos + 6)         # player
    DrawRect(ballx - 1, bally - 1, ballx + 1, bally + 1) # ball
    main.oled.text(str(score), 62, 5)
    main.oled.show()
