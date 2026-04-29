import sys
import time
import pygame
from config import *
from logic import PacmanGame

class PacmanViewer:
    def __init__(self):
        pygame.init()
        self.cell_size = 40
        self.font = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        self.game = None
        self.running = True
        
        # Setup Screen
        self.screen_w = 800
        self.screen_h = 600
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Pacman AI - Pygame")

    def show_menu(self):
        # Step 1: Select Ghost Mode
        selected = 0
        options = ["astar", "minimax", "random"]
        ghost_mode = "astar"
        
        step = 1 # 1=GhostMode, 2=Randomness
        
        while step == 1:
            self.screen.fill(COLOR_BG)
            title = self.font.render("Select Ghost AI Mode", True, COLOR_TEXT)
            self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 100))
            
            for i, opt in enumerate(options):
                color = COLOR_PACMAN if i == selected else (100, 100, 100)
                txt = self.font.render(f"> {opt} <" if i==selected else opt, True, color)
                self.screen.blit(txt, (self.screen_w//2 - txt.get_width()//2, 200 + i*50))
            
            info = self.font.render("Press UP/DOWN and ENTER", True, (150, 150, 150))
            self.screen.blit(info, (self.screen_w//2 - info.get_width()//2, 450))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN: selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        ghost_mode = options[selected]
                        step = 2
            self.clock.tick(30)
            
        # Step 2: Select Randomness
        selected = 0
        bool_opts = [True, False]
        bool_labels = ["Yes (More Dynamic)", "No (Deterministic/Robot)"]
        use_rand = True
        
        while step == 2:
            self.screen.fill(COLOR_BG)
            title = self.font.render("Use Randomness?", True, COLOR_TEXT)
            self.screen.blit(title, (self.screen_w//2 - title.get_width()//2, 100))
            
            desc = self.font.render(f"Mode: {ghost_mode}", True, COLOR_GHOST)
            self.screen.blit(desc, (self.screen_w//2 - desc.get_width()//2, 140))

            for i, val in enumerate(bool_opts):
                color = COLOR_PACMAN if i == selected else (100, 100, 100)
                txt = self.font.render(f"> {bool_labels[i]} <" if i==selected else bool_labels[i], True, color)
                self.screen.blit(txt, (self.screen_w//2 - txt.get_width()//2, 250 + i*50))
                
            info = self.font.render("Press UP/DOWN and ENTER", True, (150, 150, 150))
            self.screen.blit(info, (self.screen_w//2 - info.get_width()//2, 450))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selected = (selected - 1) % len(bool_opts)
                    elif event.key == pygame.K_DOWN: selected = (selected + 1) % len(bool_opts)
                    elif event.key == pygame.K_RETURN:
                        use_rand = bool_opts[selected]
                        return ghost_mode, use_rand
            self.clock.tick(30)

    def run_game_loop(self, ghost_mode, use_randomness):
        self.game = PacmanGame(DEFAULT_MAP, ghost_mode, use_randomness)
        self.running = True
        
        # Resize screen
        gw = self.game.width * self.cell_size
        gh = self.game.height * self.cell_size + 60
        self.screen = pygame.display.set_mode((gw, gh))
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "QUIT"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "MENU"

            if not self.game.game_over:
                self.game.step()
            
            self.screen.fill(COLOR_BG)
            
            # Draw Grid
            for y in range(self.game.height):
                for x in range(self.game.width):
                    rect = (x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size)
                    cell = self.game.grid[y][x]
                    if cell == WALL:
                        pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    if (x, y) in self.game.pellets:
                        center = (int((x+0.5)*self.cell_size), int((y+0.5)*self.cell_size))
                        pygame.draw.circle(self.screen, COLOR_PELLET, center, self.cell_size//6)
            
            # Agents
            px, py = self.game.pacman
            p_center = (int((px+0.5)*self.cell_size), int((py+0.5)*self.cell_size))
            pygame.draw.circle(self.screen, COLOR_PACMAN, p_center, self.cell_size//2 - 2)
            
            gx, gy = self.game.ghost
            g_center = (int((gx+0.5)*self.cell_size), int((gy+0.5)*self.cell_size))
            pygame.draw.circle(self.screen, COLOR_GHOST, g_center, self.cell_size//2 - 2)

            # HUD
            hud_y = self.game.height * self.cell_size + 10
            score_txt = self.font.render(f"Score: {self.game.score}", True, COLOR_TEXT)
            self.screen.blit(score_txt, (10, hud_y))
            
            if self.game.game_over:
                msg_color = (0, 255, 0) if self.game.win else (255, 0, 0)
                done_txt = self.font.render(f"GAME OVER: {self.game.status_message}", True, msg_color)
                self.screen.blit(done_txt, (200, hud_y))
                
                cont_txt = self.font.render("Press ENTER to Main Menu", True, (200, 200, 200))
                self.screen.blit(cont_txt, (200, hud_y + 30))

            pygame.display.flip()
            
            if self.game.game_over:
                wait_for_input = True
                while wait_for_input:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return "QUIT"
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                                return "MENU"
                    self.clock.tick(30)
                return "MENU"

            time.sleep(SLEEP)
            self.clock.tick(60)
