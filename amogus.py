import main


lastx = 1
susx = 0
lasty = 1
susy = 0


def LCDamogus():
    global lastx
    global susx
    global lasty
    global susy
    
    if susx < 100 and lastx == 1:
        susx += 2
    elif susx > 0 and lastx == -1:
        susx -= 2
    else:
        lastx = -lastx

    if susy < 25 and lasty == 1:
        susy += 1
    elif susy > 0 and lasty == -1:
        susy -= 1
    else:
        lasty = -lasty
    
    amosus = [(25, 15), (25, 14), (24, 13), (24, 12), (23, 11), (22, 10), (21, 9), (20, 9), (19, 8), (18, 8), (17, 8), (16, 8), (15, 8), (14, 8), (13, 8), (12, 8), (11, 9), (10, 10), (10, 11), (10, 12), (10, 13), (9, 14), (9, 15), (9, 16), (9, 17), (8, 18), (8, 19), (8, 20), (8, 21), (8, 22), (8, 23), (8, 24), (7, 25), (7, 26), (7, 27), (7, 28), (7, 29), (7, 30), (7, 31), (7, 32), (6, 32), (5, 31), (4, 31), (3, 32), (2, 32), (2, 33), (2, 34), (2, 35), (3, 36), (4, 36), (5, 37), (6, 37), (7, 37), (8, 37), (9, 36), (10, 36), (11, 36), (12, 35), (13, 34), (13, 33), (13, 32), (12, 31), (12, 30), (12, 29), (13, 28), (14, 28), (15, 28), (16, 28), (17, 28), (18, 28), (19, 28), (19, 29), (19, 30), (19, 31), (19, 32), (19, 33), (19, 34), (18, 34), (17, 34), (15, 35), (15, 36), (15, 37), (16, 38), (17, 38), (18, 38), (19, 38), (20, 38), (21, 38), (22, 38), (23, 38), (24, 37), (25, 37), (26, 36), (27, 35), (27, 34), (27, 33), (27, 32), (27, 31), (27, 30), (27, 29), (26, 28), (26, 27), (26, 26), (26, 25), (26, 24), (26, 23), (26, 22), (26, 21), (25, 20), (25, 19), (25, 18), (25, 17), (25, 16), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13), (13, 14), (13, 15), (13, 16), (14, 16), (15, 16), (16, 16), (17, 16), (18, 16), (19, 16), (20, 16), (21, 15), (21, 14)]
    amogus = [[0 for i in range(64)] for i in range(32)]
    for i in amosus:
        amogus[i[0]][i[1]] = 1
    
    main.oled.fill(0)
    offset_x = 50
    offset_y = 10
    
    for i in range(len(amogus)):
        for j in range(len(amogus[0])):
            main.oled.pixel(i + susx, j + susy, amogus[i][j])
    
    main.oled.show()
