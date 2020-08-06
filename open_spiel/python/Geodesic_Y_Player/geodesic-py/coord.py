import math

def getCoords(N):
    parms = []

    for i in range(N):
        parms.append([i + 1, 20 + (i * 30), 15 + (i * 28)])

    angles = [210, 90, 330]
    offsets = [30, 270, 150]
    cords = []

    v = 0

    for i in range(len(parms)):

        l = parms[i][0]
        n1 = parms[i][1]
        n2 = parms[i][2]
        n3 = math.sqrt((n1 ** 2) + (n2 ** 2) - (2 * n1 * n2 * math.cos(math.radians(120))))
        θ1 = math.degrees(math.asin((n2 * (math.sin(math.radians(120)))) / n3))

        for j in range(3):

            θ2 = θ1 + offsets[j]
            x1 = n1 * math.cos(math.radians(angles[j]))
            y1 = n1 * math.sin(math.radians(angles[j]))

            for k in range(l):

                θ3 = θ2 - (k * ((θ1 * 2) / l))
                x2 = x1 + (n3 * math.cos(math.radians(θ3)))
                y2 = y1 + (n3 * math.sin(math.radians(θ3)))

                cords.append([x2, y2])
                v += 1
    return cords
