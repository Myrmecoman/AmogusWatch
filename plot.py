import main

values = []

def AddValue(val):
    values.append(val)
    if len(values) > 64:
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

    x = 64 - len(values)/2
    for i in range(len(values)):
        y = ((values[i] - min)/maxSpread) * 32
        x = x + 1
        main.oled.pixel(int(x), int(y), 1)
    
    main.oled.show()
