import mainInit as main
import time
import pongServer
import pongClient
import pyb

uart = None

valuesQueue = []
detectedMin = 5000
detectedMax = 0

bleChosen = -1
serverInc = 0
clientInc = 0

scoreServer = 0
scoreClient = 0
serverPos = 32
clientPos = 32
ballx = 64
bally = 32
speedx = 2
speedy = 2

def DrawRect(x0, y0, x1, y1):
    for i in range(x0, x1 + 1):
        main.oled.line(i, y0, i, y1, 1)

def displayChoice(value):
    global bleChosen
    global serverInc
    global clientInc
    global uart

    main.oled.fill(0)
    main.oled.text('server', 40, 10)
    main.oled.text('client', 40, 25)
    time.sleep(0.1)

    if (value < 0.5):
        main.oled.line(39, 11, 95, 11, 1)
        main.oled.line(39, 17, 95, 17, 1)
        main.oled.line(39, 17, 39, 11, 1)
        main.oled.line(95, 17, 95, 11, 1)
        serverInc += 1
        clientInc = 0
    else:
        main.oled.line(39, 26, 95, 26, 1)
        main.oled.line(39, 32, 95, 32, 1)
        main.oled.line(39, 32, 39, 26, 1)
        main.oled.line(95, 32, 95, 26, 1)
        clientInc += 1
        serverInc = 0

    if serverInc >= 50:
        uart = pongServer.setup()
        bleChosen = 0
        serverInc = 0
        clientInc = 0
    if clientInc >= 50:
        pongClient.setup()
        bleChosen = 1
        serverInc = 0
        clientInc = 0

    main.oled.show()


def playServer(normalized):
    global uart
    global serverPos
    global clientPos
    global ballx
    global bally
    global speedx
    global speedy

    serverPos = int(normalized * 64)
    main.oled.text('server', 0, 5)

    if uart is not None and uart.is_connected():
        ballx += speedx
        bally += speedy

    # ball collision on walls
    if bally < 2 and speedy == -2:
        speedy = -speedy
    if bally > 125 and speedy == 2:
        speedy = -speedy

    # ball collision on server
    yDist = abs(serverPos - bally)
    if ballx < 5 and speedx == -2 and yDist < 6:
        speedx = -speedx
    # ball collision on client
    yDist = abs(clientPos - bally)
    if ballx > 122 and speedx == 2 and yDist < 6:
        speedx = -speedx
    
    # ball not catched
    if ballx < 2:
        scoreClient += 1
        ballx = 64
        bally = 32
        speedx = 2
        speedy = 2
    if ballx > 125:
        scoreServer += 1
        ballx = 64
        bally = 32
        speedx = -2
        speedy = 2
    
    pongServer.peripheralBLE(uart)


def playClient(normalized):
    global clientPos
    clientPos = int(normalized * 64)
    main.oled.text('client', 0, 5)
    pongClient.centralBLE()


def Play():
    global bleChosen
    global valuesQueue
    global detectedMin
    global detectedMax
    global scoreServer
    global scoreClient
    global serverPos
    global clientPos
    global ballx
    global bally

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

    if bleChosen == -1:
        displayChoice(normalized)
    else:
        main.oled.fill(0)
        main.oled.line(0, 0, 127, 0, 1)    # wall
        main.oled.line(0, 63, 127, 63, 1)  # wall
        main.oled.text(str(scoreServer), 53, 5) # server score
        main.oled.text(str(scoreClient), 65, 5) # client score

        if bleChosen == 0:
            playServer(normalized)
        else:
            playClient(normalized)

        DrawRect(0, serverPos - 6, 2, serverPos + 6)         # server sprite
        DrawRect(125, clientPos - 6, 127, clientPos + 6)     # client sprite
        DrawRect(ballx - 1, bally - 1, ballx + 1, bally + 1) # ball
        main.oled.show()
