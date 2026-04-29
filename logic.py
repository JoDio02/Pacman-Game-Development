import heapq
import random
from config import *
from utils import manhattan, neighbors

class PacmanGame:
    def __init__(self, map_lines, ghost_mode="astar", use_randomness=True):
        self.grid = []
        self.pellets = set()
        self.pacman = None
        self.ghost = None
        self.score = 0
        self.turn = 0
        self.ghost_mode = ghost_mode
        self.use_randomness = use_randomness
        
        self.width = 0
        self.height = 0
        self.game_over = False
        self.win = False
        self.status_message = ""

        self._load_map(map_lines)

    def _load_map(self, lines):
        self.height = len(lines)
        self.width = max(len(l) for l in lines)
        self.grid = [[EMPTY for _ in range(self.width)] for __ in range(self.height)]
        
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch == '#':
                    self.grid[y][x] = WALL
                elif ch == '.':
                    self.grid[y][x] = PELLET
                    self.pellets.add((x, y))
                elif ch == 'P':
                    self.pacman = (x, y)
                elif ch == 'G':
                    self.ghost = (x, y)
                elif ch == ' ':
                    self.grid[y][x] = EMPTY

        # Fallback placement if missing
        if self.pacman is None and self.pellets:
            empty = sorted(list(self.pellets), key=lambda p: (p[1], p[0]))
            self.pacman = random.choice(empty) if self.use_randomness else empty[0]
            self.pellets.remove(self.pacman)
        
        if self.ghost is None:
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] != WALL and (x, y) != self.pacman:
                        self.ghost = (x, y)
                        break

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_legal_moves(self, pos):
        moves = []
        for nb in neighbors(pos):
            x, y = nb
            if self.in_bounds(nb) and self.grid[y][x] != WALL:
                moves.append(nb)
        return moves

    # --- BFS ---
    def bfs_distances(self, start):
        q = [start]
        dist = {start: 0}
        head = 0
        while head < len(q):
            cur = q[head]; head += 1
            for n in neighbors(cur):
                if self.in_bounds(n) and self.grid[n[1]][n[0]] != WALL and n not in dist:
                    dist[n] = dist[cur] + 1
                    q.append(n)
        return dist

    # --- A* ---
    def astar(self, start, goal, blocked_positions=None):
        if blocked_positions is None: blocked_positions = set()
        
        if not self.in_bounds(goal): return [] # Should not happen

        danger_cells = set()
        for gx, gy in blocked_positions:
            danger_cells.add((gx, gy))
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                danger_cells.add((gx+dx, gy+dy))

        open_heap = []
        heapq.heappush(open_heap, (manhattan(start, goal), 0, start, None))
        came_from = {}
        gscore = {start: 0}
        closed = set()

        while open_heap:
            f, g, cur, parent = heapq.heappop(open_heap)
            if cur in closed: continue
            
            came_from[cur] = parent
            if cur == goal:
                path = []
                node = cur
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                path.reverse()
                return path

            closed.add(cur)
            for nb in neighbors(cur):
                dx, dy = nb
                if not self.in_bounds(nb) or self.grid[dy][dx] == WALL or nb in closed:
                    continue
                if nb in blocked_positions and nb not in danger_cells: 
                    # Strict block check if needed, but danger_cells handles ghost proximity logic
                    pass

                tentative_g = g + 1
                if nb in danger_cells:
                    tentative_g += 20
                
                if tentative_g < gscore.get(nb, 1e9):
                    gscore[nb] = tentative_g
                    heapq.heappush(open_heap, (tentative_g + manhattan(nb, goal), tentative_g, nb, cur))
        return []

    # --- Minimax ---
    def evaluate_state(self, pac, ghost, pellets):
        score = 0
        score += (100 - len(pellets)) * 10
        if pellets:
            dmin = min(manhattan(pac, p) for p in pellets)
            score -= dmin * 3
        
        dg = manhattan(pac, ghost)
        if dg == 0: return -10000
        score -= max(0, (6 - dg)) * 50
        return score

    def minimax(self, pac, ghost, pellets, depth, maximizing_player):
        if pac == ghost: return -10000, None
        if len(pellets) == 0: return 10000, None
        if depth == 0: return self.evaluate_state(pac, ghost, pellets), None

        if maximizing_player: # Pacman
            best_val = -1e9
            best_moves = []
            
            moves = self.get_legal_moves(pac)
            if self.use_randomness:
                random.shuffle(moves)
            else:
                moves.sort(key=lambda m: (m[1], m[0])) # Deterministic tie-break by coord
            
            for nb in moves:
                new_pellets = set(pellets)
                if nb in new_pellets: new_pellets.remove(nb)
                val, _ = self.minimax(nb, ghost, new_pellets, depth - 1, False)
                
                if val > best_val:
                    best_val = val
                    best_moves = [nb]
                elif val == best_val:
                    best_moves.append(nb)
            
            if not best_moves: return best_val, None
            
            if self.use_randomness:
                return best_val, random.choice(best_moves)
            else:
                return best_val, best_moves[0] # Pick first one

        else: # Ghost
            best_val = 1e9
            best_moves = []
            
            moves = self.get_legal_moves(ghost)
            if self.use_randomness:
                random.shuffle(moves)
            else:
                moves.sort(key=lambda m: (m[1], m[0]))

            for nb in moves:
                val, _ = self.minimax(pac, nb, pellets, depth - 1, True)
                
                if val < best_val:
                    best_val = val
                    best_moves = [nb]
                elif val == best_val:
                    best_moves.append(nb)
            
            if not best_moves: return best_val, None

            if self.use_randomness:
                return best_val, random.choice(best_moves)
            else:
                return best_val, best_moves[0]

    # --- Pacman Logic ---
    def choose_pacman_next_pos(self):
        # 1. Adversarial Minimax with Reversal Penalty at Root
        best_val = -1e9
        best_moves = []
        
        legal = self.get_legal_moves(self.pacman)
        if self.use_randomness:
            random.shuffle(legal)
        else:
            legal.sort(key=lambda m: (m[1], m[0]))
        
        for nb in legal:
            # PENALTY: Moving back to where we just were
            move_penalty = 0
            if hasattr(self, 'prev_pacman') and nb == self.prev_pacman:
                move_penalty = 500 # Significant penalty for reversing

            # Simulate one step
            new_pellets = set(self.pellets)
            if nb in new_pellets: new_pellets.remove(nb)
            
            # Pacman moved to nb, now Ghost minimizes
            val, _ = self.minimax(nb, self.ghost, new_pellets, PACMAN_MINIMAX_DEPTH - 1, False)
            
            # Apply penalty to the calculated value
            val -= move_penalty

            if val > best_val:
                best_val = val
                best_moves = [nb]
            elif val == best_val:
                best_moves.append(nb)

        if best_moves:
            if self.use_randomness:
                return random.choice(best_moves)
            else:
                return best_moves[0]

        # 2. Fallback
        
        # Find nearest pellet
        dists = self.bfs_distances(self.pacman)
        best_p = None
        best_d = 1e9
        
        target_pellets = list(self.pellets)
        if not self.use_randomness:
            target_pellets.sort(key=lambda p: (p[1], p[0])) # Sorting needed for determinism
            
        for p in target_pellets:
            if p in dists and dists[p] < best_d:
                best_d = dists[p]
                best_p = p
        
        if best_p:
            path = self.astar(self.pacman, best_p, blocked_positions={self.ghost})
            if len(path) >= 2:
                return path[1]
        
        # Last resort
        moves = self.get_legal_moves(self.pacman)
        safe_moves = [m for m in moves if m != self.ghost]
        
        if safe_moves:
             if self.use_randomness: return random.choice(safe_moves)
             else: safe_moves.sort(key=lambda m: (m[1], m[0])); return safe_moves[0]
        
        return self.pacman

    # --- Step ---
    def step(self):
        if self.game_over: return

        # Need to init prev positions if not exists
        if not hasattr(self, 'prev_pacman'): self.prev_pacman = self.pacman
        if not hasattr(self, 'prev_ghost'): self.prev_ghost = self.ghost

        # Pacman Move
        next_pac = self.choose_pacman_next_pos()
        self.prev_pacman = self.pacman # Store before updating
        self.pacman = next_pac

        if self.pacman == self.prev_pacman and not self.pellets:
             self.game_over = True
             self.win = True
             self.status_message = "Stuck but done!"
             return

        if self.pacman in self.pellets:
            self.pellets.remove(self.pacman)
            self.score += 10

        if self.pacman == self.ghost:
            self.game_over = True
            self.win = False
            self.status_message = "Captured by Ghost!"
            return

        if not self.pellets:
            self.game_over = True
            self.win = True
            self.status_message = "Victory! All pellets eaten."
            return

        # Ghost Move
        next_ghost = self.ghost
        if self.ghost_mode == "minimax":
            # Manual root level for Ghost to apply reversal penalty
            best_val = 1e9
            best_moves = []
            legal = self.get_legal_moves(self.ghost)
            
            if self.use_randomness:
                random.shuffle(legal)
            else:
                legal.sort(key=lambda m: (m[1], m[0]))
            
            for nb in legal:
                penalty = 0
                if nb == self.prev_ghost:
                    penalty = 500 # Ghost hates reversing too
                
                # Ghost moves to nb, Pacman maximizes
                val, _ = self.minimax(self.pacman, nb, self.pellets, MINIMAX_DEPTH - 1, True)
                
                # Ghost wants to MINIMIZE score
                val += penalty 

                if val < best_val:
                    best_val = val
                    best_moves = [nb]
                elif val == best_val:
                    best_moves.append(nb)
            
            if best_moves:
                if self.use_randomness:
                    next_ghost = random.choice(best_moves)
                else:
                    next_ghost = best_moves[0]
            else:
                next_ghost = self._ghost_fallback_greedy()

        elif self.ghost_mode == "random":
            moves = self.get_legal_moves(self.ghost)
            if moves:
                if self.use_randomness:
                    next_ghost = random.choice(moves)
                else:
                    moves.sort(key=lambda m: (m[1], m[0]))
                    next_ghost = moves[0]
        else: # astar
            path = self.astar(self.ghost, self.pacman)
            if len(path) >= 2: next_ghost = path[1]
            else: next_ghost = self._ghost_fallback_greedy()

        self.prev_ghost = self.ghost
        self.ghost = next_ghost

        if self.pacman == self.ghost:
            self.game_over = True
            self.win = False
            self.status_message = "Captured by Ghost!"
            return

        self.turn += 1
        if self.turn >= MAX_TURNS:
            self.game_over = True
            self.status_message = "Draw (Turn limit)"

    def _ghost_fallback_greedy(self):
        bestd = 1e9
        bestnb = self.ghost
        for nb in self.get_legal_moves(self.ghost):
            d = manhattan(nb, self.pacman)
            if d < bestd:
                bestd = d
                bestnb = nb
        return bestnb
