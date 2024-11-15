"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time
from random import randint as rand, uniform as randf, choice
from player_class import Player
from platform_class import PlatformManager
from camera_class import Camera
from scores import ScoreManager
from difficulty import DifficultyManager
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
        player_y = WINDOW_HEIGHT - PLAYER_HEIGHT
        self.player = Player(self.canvas, player_x, player_y)

        # Set up keyboard controls
        self.setup_controls()

        # Create managers
        self.initialize_managers()

        # Create camera object
        self.camera = Camera()

        # Sets up and manage score and boosts
        self.score_manager.register_callback('on_boost', self.player.handle_boost)
        self.score_manager.register_callback('on_boost_expire', self.player.handle_boost_expire)

        # Handles player death
        self.platform_manager.register_callback('on_death', self.handle_player_death)
        self.is_game_over = False
        self.game_over_screen = None

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
        self.bind('<KeyRelease-Right>', lambda e: self.player.stop_move_right())

    def initialize_managers(self):
        """Initialize all game managers and their connections"""
        # Create managers
        self.difficulty_manager = DifficultyManager()
        self.score_manager = ScoreManager()
        self.platform_manager = PlatformManager(self.canvas, self.difficulty_manager)

        # Sets up and manage score and boosts
        self.score_manager.register_callback('on_boost', self.player.handle_boost)
        self.score_manager.register_callback('on_boost_expire', self.player.handle_boost_expire)

        # Handles player death
        self.platform_manager.register_callback('on_death', self.handle_player_death)

    def cleanup_managers(self):
        """Clean up all existing manager objects"""
        if hasattr(self, 'platform_manager'):
            # Clean up all platforms
            for platform in self.platform_manager.get_platforms():
                platform.cleanup()
            
        # Remove references to old managers
        self.difficulty_manager = None
        self.score_manager = None
        self.platform_manager = None

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
            current_time = time.time()
            
            if not self.is_game_over:
                # Only calculate diff_time and update game state if game is active
                diff_time = current_time - self.last_update
                # Cap maximum diff_time to prevent huge jumps
                diff_time = min(diff_time, FRAME_TIME_SECONDS * 3)
                self.update(diff_time)
                self.render()
            else:
                # Show game over screen if it hasn't been shown yet
                if not self.game_over_screen:
                    self.show_game_over_screen()
                    
            self.last_update = current_time
            
            # Schedule next frame
            self.after(FRAME_TIME, self.game_loop)



    def update(self, diff_time):
        """
        Update game states

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Update player first
        old_player_x = self.player.x
        self.player.update(diff_time)

        # Update camera to follow player
        self.camera.update(self.player)

        # Update score and difficulty
        score = self.score_manager.update(self.player.y)
        self.difficulty_manager.update_difficulty(score)

        # Update platform manager
        self.platform_manager.update(self.player.y, diff_time)

        # Check player collision with platforms
        for platform in self.platform_manager.get_platforms():
            if platform.check_collision(self.player):
                # Collision logic
                self.player.y = platform.y - self.player.height
                self.player.y_velocity = 0
                self.player.is_jumping = False

                # Adjust player movement with moving platforms
                if platform.type in [TYPE_MOVING, TYPE_WRAPPING]:
                    platform_movement = platform.velocity * diff_time
                    self.player.x += platform_movement

        # Check if player died
        self.platform_manager.check_player_death(self.player)


    def render(self):
        """
        Draw current game state to canvas
        """

        # Clears canvas
        self.canvas.delete('all')

        # Renders ground
        if self.player.y > 0:
            self.canvas.create_rectangle(
                0, WINDOW_HEIGHT - self.camera.y, WINDOW_WIDTH, WINDOW_HEIGHT + 150 - self.camera.y,
                fill="brown",
                tags="ground"
            )

        # Render platforms with camera offset
        for platform in self.platform_manager.get_platforms():
            platform.render(self.camera.y)

        # Render player with camera offset
        player_x1 = self.player.x
        player_y1 = self.player.y - self.camera.y
        player_x2 = player_x1 + self.player.width
        player_y2 = player_y1 + self.player.height

        # Create player
        self.canvas_object = self.canvas.create_rectangle(
            player_x1, player_y1, player_x2, player_y2,
            fill = self.player.color,
            outline = "grey",
            tags = "player"
        )

        # Add display text
        display_info = self.score_manager.get_display_text()
        

        # Add score text
        score_info = display_info['score_info']
        self.canvas.create_text(
            score_info['pos'][0], score_info['pos'][1],
            text=score_info['text'],
            anchor="nw",
            fill=score_info['color'],
            font=score_info['font']
        )

        # Add boost text
        boost_info = display_info['boost_info']
        if boost_info:
            self.canvas.create_text(
                boost_info['pos'][0], boost_info['pos'][1],
                text=boost_info['text'],
                anchor="ne",
                fill=boost_info['color'],
                font=boost_info['font']
            )

    def quit_game(self):
        """
        Exit game cleanly
        """
        self.is_running = False
        self.destroy()

    def handle_player_death(self):
        """Handles proper steps when player dies"""

        # Stop game loop
        print("Player died!")  # Debug print
        self.is_game_over = True

    def show_game_over_screen(self):
        """Shows game over screen elements"""
        # Clear everything
        self.canvas.delete('all')
        
        # Store all game over elements
        self.game_over_screen = []
        
        # Reset timing immediately when showing game over screen
        self.last_update = time.time()
        
        # Game Over text
        game_over_text = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3,
            text="GAME OVER",
            anchor="center",
            fill="red",
            font=("Arial Bold", 25)
        )
        self.game_over_screen.append(game_over_text)

        # Score text
        score_text = self.canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2,
            text=f"Final Score: {self.score_manager.get_score()}",
            anchor="center",
            fill="black",
            font=("Arial Bold", 15)
        )
        self.game_over_screen.append(score_text)

        # Create replay button
        replay_button = tk.Button(
            self,
            text="Play Again",
            command=self.start_new_game,
            font=("Arial Bold", 12)
        )
        
        button_window = self.canvas.create_window(
            WINDOW_WIDTH / 2,
            2 * WINDOW_HEIGHT / 3,
            window=replay_button
        )
        self.game_over_screen.append(button_window)
        


    def start_new_game(self):
        """Resets everything and starts the game again"""
        # Clean up canvas
        self.canvas.delete('all')
        
        if self.game_over_screen:
            for element in self.game_over_screen:
                self.canvas.delete(element)
            self.game_over_screen = None

        # Reset game state
        self.is_game_over = False
        
        # Clean up old managers and create new ones
        self.cleanup_managers()
        self.initialize_managers()
        
        # Reset player and camera
        self.player.reset()
        self.camera.reset()

        # Reset timing before restarting game loop
        self.last_update = time.time()
        
        # Restart game loop
        self.is_running = True




    





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