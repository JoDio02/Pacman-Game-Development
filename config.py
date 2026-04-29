# ------------ Config ------------
SLEEP = 0.1
# Depth for ghost minimax
MINIMAX_DEPTH = 3
# Depth for Pacman minimax
PACMAN_MINIMAX_DEPTH = 3
MAX_TURNS = 2000

WALL = '#'
EMPTY = ' '
PELLET = '.'
PAC = 'P'
GHOST = 'G'

# Colors
COLOR_BG = (0, 0, 0)
COLOR_WALL = (30, 30, 150)
COLOR_PELLET = (255, 184, 174)
COLOR_PACMAN = (255, 255, 0)
COLOR_GHOST = (255, 0, 0) # Red ghost usually
COLOR_TEXT = (255, 255, 255)

# Default Map
DEFAULT_MAP = [
    "#####################",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#.#.....#.#.#.....#.#",
    "#.#.###.#.#.#.###.#.#",
    "#P#.#....... .....#G#",
    "#.#.#.#####.#####.#.#",
    "#...#...........#...#",
    "###.###.#####.###.###",
    "#.........#.........#",
    "#####################",
]
