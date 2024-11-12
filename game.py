"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time
from random import randint as rand, uniform as randf, choice

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

        # Create player instance
        player_x = WINDOW_WIDTH // 2
        player_y = WINDOW_HEIGHT - 40
        self.player = Player(self.canvas, player_x, player_y)

        # Set up keyboard controls
        self.setup_controls()

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

        self.player.update(diff_time)

        
    def render(self):
        """
        Draw current game state to canvas
        """
        self.canvas.delete("!player")
        self.player.render()

        # TODO: add drawing code


    def quit_game(self):
        """
        Exit game cleanly
        """
        self.is_running = False
        self.destroy()


class Player:
    """
    Player class that creates the player object and its movement

    Attributes:
        canvas (tk.Canvas): Game canvas where player will be drawn
        x (float): Player x position
        y (float): Player y position
        width (int): Player width in pixels
        height (int): Player height in pixels
        color (str): Player fill color
        x_velocity (int): Player horizontal velocity
        y_velocity (int): Player vertical velocity
        is_jumping(bool): Whether player is currently jumping

    Constants:
        MOVE_SPEED (float): Speed for horizontal movement
        JUMPING_FORCE (float): Initial upward velocity when jumping
        GRAVITY (float): Downward acceleration
    """

    # Class constant
    MOVE_SPEED = 500.0
    JUMP_FORCE = -350.0
    GRAVITY = 7.0

    def __init__(self, canvas, x, y):
        """
        Initialize new player instance

        Args:
            canvas (tk.Canvas): Game canvas to draw player on
            x (float): Initial player x position
            y (float): Initial player y position
        """
        
        # Store canvas reference
        self.canvas = canvas

        # Set position, appearance and movement properties
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = "white"
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False

        # Player movement states
        self.moving_left = False
        self.moving_right = False

        # Check if player exists
        self.canvas_object = None

    def start_move_left(self):
        """Moves the player to left at MOVE_SPEED"""
        
        self.moving_left = True
        self.x_velocity = -self.MOVE_SPEED

    def stop_move_left(self):
        """Stops player movement to the left"""
        
        self.moving_left = False

        # Only stop if player is not moving right
        if not self.moving_right:
            self.x_velocity = 0

    def start_move_right(self):
        """Moves the player to right at MOVE_SPEED"""
        
        self.moving_right = True
        self.x_velocity = self.MOVE_SPEED

    def stop_move_right(self):
        """Stops player movement to the right"""
        
        self.moving_right = False

        # Only stop if player is not moving left
        if not self.moving_left:
            self.x_velocity = 0


    def jump(self):
        """
        Makes player jump if not already jumping
        """

        if not self.is_jumping:
            self.y_velocity = self.JUMP_FORCE
            self.is_jumping = True

    def update(self, diff_time):
        """
        Update player position and apply physics

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Apply gravity
        self.y_velocity += self.GRAVITY

        # Update positions based on velocity
        self.x += self.x_velocity * diff_time
        self.y += self.y_velocity * diff_time

        # Add ground collision detection
        ground_y = WINDOW_HEIGHT - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.y_velocity = 0
            self.is_jumping = False

        # Screen wrapping for horizontal movement
        canvas_width = int(self.canvas.cget('width'))
        if self.x + self.width < 0: # Player right side is off canvas left side
            self.x = canvas_width
        elif self.x > canvas_width: # Player left side is off canvas right side
            self.x = -self.width

    def render(self):
        """
        Draw player on canvas or update player position
        """

        x1 = self.x
        y1 = self.y
        x2 = x1 + self.width
        y2 = y1 + self.height

        if self.canvas_object is None:
            # First time creating player
            self.canvas_object = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill = self.color,
                outline = "grey",
                tags = "player"
            )
        else:
            # Player already exists so update position
            self.canvas.coords(self.canvas_object, x1, y1, x2, y2)

    
class Platform:
    """
    Creates a platform object that the player can jump on

    Attributes:
    canvas (tk.Canvas): Game canvas where platform will be drawn
    x (float): Platform x position
    y (float): Platform y position
    width (int): Platform width
    color (str): Platform fill colour
    velocity (float): Platform horizontal velocity
    direction (int): Platform movement direction (1 for right, -1 for left)
    is_active (bool): Determines whether platform can be collided with

    Class constants:
    HEIGHT (int): Platform height
    DEFAULT_WIDTH (int): Default platform width
    COLOR (str): Platform fill
    """

    # Platform types
    TYPE_NORMAL = "normal"
    TYPE_MOVING = "moving"
    TYPE_BREAKING = "breaking"
    TYPE_WRAPPING = "wrapping"

    # Class constants
    HEIGHT = 10
    DEFAULT_WIDTH = WINDOW_WIDTH // 2
    COLOR = {
        TYPE_NORMAL: "blue",
        TYPE_MOVING: "green",
        TYPE_BREAKING: "red",
        TYPE_WRAPPING: "purple"

    }

    

    def __init__(self, canvas, x, y, platform_type=TYPE_NORMAL):
        """
        Initializes a new platform instance

        Args:
            canvas (canvas.Tk): Game canvas to draw platform on
            x (int): Platform initial x position
            y (int): Platform initial y position
            platform_type (str): Type of platform to create
        """
        
        # Store canvas reference
        self.canvas = canvas

        # Set position and appearance
        self.x = rand(0, WINDOW_WIDTH - self.DEFAULT_WIDTH)
        self.y = y
        self.type = platform_type
        self.width = self.DEFAULT_WIDTH
        self.color = self.DEFAULT_COLOR

        # Set movement property based on platform type
        if (self.type == "MOVING" or self.type == "WRAPPING"):
            self.direction = rand(1, -1)
            self.velocity = self.direction * randf(200.0, 700.0)
        else:
            self.velocity = 0
            
        self.is_active = True

        # Check if platform exists
        self.canvas_object = None
        
    






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