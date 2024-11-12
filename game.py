"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time
from random import randint as rand, uniform as randf, choice
from player_class import Player
from platform_class import Platform
from constants import *


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

        # Create player instance
        player_x = WINDOW_WIDTH // 2
        player_y = WINDOW_HEIGHT - 40
        self.player = Player(self.canvas, player_x, player_y)

        # Set up keyboard controls
        self.setup_controls()

        # Create list to store platforms
        self.platforms = []

        # Add test platform
        test_platform = Platform(
            self.canvas,
            WINDOW_WIDTH // 4,
            WINDOW_HEIGHT - 100,
            Platform.TYPE_NORMAL
        )

        self.platforms.append(test_platform)

    def setup_controls(self):
        """
        Configure key bindings for player control
        """

        # Movement controls
        self.bind('<Left>', lambda e: self.player.start_move_left())
        self.bind('<Right>', lambda e: self.player.start_move_right())
        self.bind('<space>', lambda e: self.player.jump())

        # Handle key release for smoother movement
        self.bind('<KeyRelease-Left>', lambda e: self.player.stop_move_left())
        self.bind('<KeyRelease- Right>', lambda e: self.player.stop_move_right())

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


    def update(self, diff_time):
        """
        Update game states

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Update player
        self.player.update(diff_time)

        # Update platforms and handle cleanup
        active_platforms = []
        for platform in self.platforms:
            platform.update(diff_time)
        
            # Check collision detection between player and platform
            if platform.check_collision(self.player):
                # Collision logic
                self.player.y = platform.y - self.player.height
                self.player.y_velocity = 0
                self.player.is_jumping = False 

                # Handle breaking platforms
                if (platform.type == Platform.TYPE_BREAKING):
                    platform.is_active = False
                    platform.cleanup()
                    continue
            active_platforms.append(platform)

        # Only update active platforms
        self.platforms = active_platforms


        
    def render(self):
        """
        Draw current game state to canvas
        """

        # Render platforms
        for platform in self.platforms:
            platform.render()

        # Render player
        self.player.render()

        


    def quit_game(self):
        """
        Exit game cleanly
        """
        self.is_running = False
        self.destroy()




    





if __name__ == "__main__":
    game = Game()
    game.run()
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