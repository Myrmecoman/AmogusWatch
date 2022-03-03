import mainInit as main
import pyb


valuesQueue = []
detectedMin = 5000
detectedMax = 0

bleChosen = False

def displayChoice(value):
    main.oled.fill(0)
    main.oled.text('server', 40, 10)
    main.oled.text('client', 40, 25)
    main.oled.text('skip', 40, 40)

    if (value < 0.33):
        main.oled.line(39, 11, 95, 11, 1)
        main.oled.line(39, 17, 95, 17, 1)
        main.oled.line(39, 17, 39, 11, 1)
        main.oled.line(95, 17, 95, 11, 1)
    elif (value < 0.67):
        main.oled.line(39, 26, 95, 26, 1)
        main.oled.line(39, 32, 95, 32, 1)
        main.oled.line(39, 32, 39, 26, 1)
        main.oled.line(95, 32, 95, 26, 1)
    else:
        main.oled.line(39, 41, 95, 41, 1)
        main.oled.line(39, 47, 95, 47, 1)
        main.oled.line(39, 47, 39, 41, 1)
        main.oled.line(95, 47, 95, 41, 1)

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

    if not bleChosen:
        displayChoice(normalized)
        return
