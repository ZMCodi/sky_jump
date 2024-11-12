"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time

# Window constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Sky Jump"
BG_COLOR = "lightblue"

# Game constants
FPS = 60
FRAME_TIME = int(1000 / FPS)

class Game(tk.Tk):
    """
    Main game class that creates and sets up the game window, canvas and handle game loops

    Attributes:
        canvas (tk.Canvas): Main game canvas where game elements are drawn
    """
    def __init__(self):
        """Initialize game window and canvas"""
        super().__init__()

        # Configure window
        self.title(WINDOW_TITLE)
        self.resizable(False, False) # Maintain constant window dimension

        # Center window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")


        # Create and configure canvas
        self.canvas = tk.Canvas(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            bg = BG_COLOR
        )
        
        self.canvas.pack()

        # Game state variables
        self.is_running = False
        self.last_update = time.time()

        # Quit game when exit button is pressed
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

    def run(self):
        """
        Main game loop that handles the rendering and updates
        """

        self.is_running = True
        self.game_loop()

    def game_loop(self):
        """
        Actual game loop logic and timing
        """

        if self.is_running:
            # Calculate time since last update
            current_time = time.time()
            diff_time = current_time - self.last_update
            self.last_update = current_time

            # Update game state
            self.update(diff_time)

            # Render frame
            self.render()

            # Schedule next frame
            self.after(FRAME_TIME, self.game_loop)


    







if __name__ == "__main__":
    game = Game()
    game.mainloop()


# TODO: Game Classes Structure
#   - Game (main game class)
#   - Player (player character)
#   - Platform (platforms to jump on)
#   - Menu (menu system)
#   - ScoreBoard (handling scores)

# TODO: Core Game Features
#   - Game loop
#   - Window setup
#   - Player movement
#   - Platform generation
#   - Collision detection
#   - Gravity physics

# TODO: Additional Features
#   - Menu system
#   - Key binding customization
#   - Scoring system
#   - Leaderboard
#   - Save/Load functionality
#   - Pause menu
#   - Boss key
#   - Cheat codes
#   - Difficulty settings

# TODO: Main game structure below