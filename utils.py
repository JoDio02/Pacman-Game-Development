def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(pos):
    x, y = pos
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        yield (x + dx, y + dy)
