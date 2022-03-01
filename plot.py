import main

values = []

def AddValue(val):
    values.append(val)
    if len(values) > 120:
        del values[0]

def DisplayValues():
    main.oled.fill(0)
    min = 1000000
    max = 0

    for i in range(len(values)):
        if values[i] > max:
            max = values[i]
        if values[i] < min:
            min = values[i]

    maxSpread = max - min
    if maxSpread == 0:
        return

    x = 60 - len(values)/2
    for i in range(len(values) - 1):
        y0 = ((values[i] - min)/maxSpread) * 60
        y1 = ((values[i + 1] - min)/maxSpread) * 60
        x = x + 1
        main.oled.line(int(x), int(y0), int(x) + 1, int(y1), 1)
    
    main.oled.show()
