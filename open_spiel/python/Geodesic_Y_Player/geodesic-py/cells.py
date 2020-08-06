import coord
import graph

def getCoordinates(baseSize, offsetX, offsetY):
    g = graph.generateNSizedGraph(baseSize + 1)
    centers = coord.getCoords(baseSize)

    for p in centers:
        p[0] += offsetX
        p[1] = -p[1] + offsetY

    vertices = []
    edges = []
    polygons = [[] for i in range(graph.getSmallestCellNumber(baseSize + 1))]

    for i in range(len(g)):
        for j in range(len(g[i])):
            if i > g[i][j]:
                continue
            nb = g[i][j]
            junctions = filter(lambda x: x > nb and x in g[i], g[nb])
            for junc in junctions:
                vertex = { "junction": [i, nb, junc], "position": [] }
                xpos = (centers[i][0] + centers[nb][0] + centers[junc][0])/3
                ypos = (centers[i][1] + centers[nb][1] + centers[junc][1])/3
                vertex["position"] = [xpos, ypos]

                for v in vertices:
                    count = 0
                    if i in v["junction"]:
                        count += 1
                    if nb in v["junction"]:
                        count += 1
                    if junc in v["junction"]:
                        count += 1

                    if count >= 2:
                        edge = { "start": [], "end": [] }
                        edge["start"] = v["position"]
                        edge["end"] = vertex["position"]
                        edges.append(edge)
                vertices.append(vertex)

    for i in range(graph.getSmallestCellNumber(baseSize + 1)):
        firstNb = g[i][0]
        twoJunctions = list(filter(lambda x: i in x["junction"] and firstNb in x["junction"], vertices))
        cp = twoJunctions[1]["junction"][:]
        cp.remove(i)
        cr = cp[:]
        polygons[i].append((twoJunctions[1]["position"][0], twoJunctions[1]["position"][1]))
        while True:
            nx = list(filter(lambda nb: cr[0] in g[nb] and cr[1] not in g[nb] and cr[1] != nb, g[i]))[0]
            cr[0], cr[1] = nx, cr[0]

            if cr[0] == cp[0]: break

            v = list(filter(lambda x: i in x["junction"] and cr[0] in x["junction"] and cr[1] in x["junction"], vertices))[0]
            polygons[i].append((v["position"][0], v["position"][1]))

    centers = centers[:graph.getSmallestCellNumber(baseSize + 1)]

    return { "vertices": vertices, "edges": edges, "centers": centers, "polygons": polygons }

