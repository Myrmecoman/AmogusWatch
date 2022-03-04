import mainInit as main
import time
import pyb


valuesQueue = []
detectedMin = 5000
detectedMax = 0

bleChosen = -1
serverInc = 0
clientInc = 0

def displayChoice(value):
    global bleChosen
    global serverInc
    global clientInc

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
        bleChosen = 0
        serverInc = 0
        clientInc = 0
    if clientInc >= 50:
        bleChosen = 1
        serverInc = 0
        clientInc = 0

    main.oled.show()

def LoadServer():
    main.oled.fill(0)
    main.oled.text('server', 0, 5)
    main.oled.show()

def LoadClient():
    main.oled.fill(0)
    main.oled.text('client', 0, 5)
    main.oled.show()

def Play():
    global bleChosen
    global valuesQueue
    global detectedMin
    global detectedMax

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
        return
    elif bleChosen == 0:
        LoadServer()
    elif bleChosen == 1:
        LoadClient()
    else:
        print('ERROR while choosing multiplayer pong')
