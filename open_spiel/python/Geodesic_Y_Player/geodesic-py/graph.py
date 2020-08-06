# Graph File

def generateNSizedGraph(n):
    if n <= 2:
        graph = []
        graph[0] = [1, 2]
        graph[1] = [0, 2]
        graph[2] = [0, 1]
        return graph

    graph = [[] for i in range(getSmallestCellNumber(n + 1))]

    graph[0] = [1, 2, 3, 4, 8]
    graph[1] = [0, 2, 4, 5, 6]
    graph[2] = [0, 1, 6, 7, 8]

    # consider simplifying graph generation
    # for i in range ...

    # Start at depth level 3 because depth level 1 and 2 are trivial
    depth = 3
    while (depth <= n):
        smallest = getSmallestCellNumber(depth)
        biggest = getSmallestCellNumber(depth + 1)
        for i in range(smallest, biggest):
            # Neighbors within depth level
            if i != biggest - 1:
                graph[i].append(i + 1)
            else:
                graph[i].append(smallest)

            if i != smallest:
                graph[i].append(i - 1)
            else:
                graph[i].append(biggest - 1)

            # Neighbors between current depth level and the depth level above
            # Ignore depth level when it is equal to the max size of the board, because it has no depth level above it
            if isCorner(i, depth) and depth != n:
                # Corner pieces always have 3 neighbors above them
                cornerNum = getCornerPlace(i, depth)
                nextCornerUp = getCorner(cornerNum, depth + 1)
                graph[i].append(nextCornerUp)
                graph[i].append(nextCornerUp + 1)
                if nextCornerUp == biggest:
                    # This is the center corner
                    graph[i].append(getSmallestCellNumber(depth + 2) - 1)
                else:
                    graph[i].append(nextCornerUp - 1)
            elif depth != n:
                # Regular edge pieces
                c = getCornerPlace(lastCorner(i, depth), depth)
                multiple = (depth - 1) * 3
                graph[i].append(i + multiple + c)
                graph[i].append(i + multiple + c + 1)

        depth += 1

    # Pair up any remaining cells where only 1 of them is counted as a neighbor
    graph = pairUpGraph(graph)
    return graph


def pairUpGraph(graph):
    g = graph[:]
    for i in range(len(g)):
        for j in range(len(g[i])):
            res = g[i][j]
            if i not in g[res]:
                g[res].append(i)
        g[i].sort()
    return g


def getSmallestCellNumber(n):
    return 3 * (n - 1) * (n - 2) // 2


def isCorner(x, depth):
    smallestCell = getSmallestCellNumber(depth)
    tup = (smallestCell, smallestCell + depth - 1, smallestCell + depth * 2 - 2)
    return x in tup


def getCornerPlace(x, depth):
    smallestCell = getSmallestCellNumber(depth)
    if x == smallestCell:
        return 0
    if x == smallestCell + depth - 1:
        return 1
    if x == smallestCell + depth * 2 - 2:
        return 2


def getCorner(num, depth):
    smallestCell = getSmallestCellNumber(depth)
    return smallestCell + (depth - 1) * num


def lastCorner(x, depth):
    first = getCorner(0, depth)
    second = getCorner(1, depth)
    third = getCorner(2, depth)
    if x < second:
        return first
    if x < third:
        return second
    return third


def getEdge(x, depth):
    first = getCorner(0, depth)
    second = getCorner(1, depth)
    third = getCorner(2, depth)

    edge = 0b0
    if first <= x <= second:
        edge |= 0b01
    if second <= x <= third:
        edge |= 0b10
    if x >= third or x == first:
        edge |= 0b100
    return edge
