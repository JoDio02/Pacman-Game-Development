import pygame
from ui import PacmanViewer

if __name__ == "__main__":
    app = PacmanViewer()
    
    app_running = True
    while app_running:
        result = app.show_menu()
        if result is None: # Quit from menu
            break
            
        g_mode, u_rand = result
        game_result = app.run_game_loop(g_mode, u_rand)
        
        if game_result == "QUIT":
            app_running = False
            
    pygame.quit()
