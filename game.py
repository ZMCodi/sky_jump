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

    def update(self, diff_time):
        """
        Update game states

        Args:
            diff_time (float): Time since last update in seconds
        """

        # TODO: add update logic
        pass

    def render(self):
        """
        Draw current game state to canvas
        """
        self.canvas.delete("all")

        # TODO: add drawing code

        # test code
        self.canvas.create_rectangle(10, 10, 50, 50, fill="white")

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
    MOVE_SPEED = 5.0
    JUMP_FORCE = -15.0
    GRAVITY = 0.8

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
        self.color = "blue"
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False

        # Check if player exists
        self.canvas_object = None

    def move_left(self):
        """
        Moves the player to left at MOVE_SPEED
        """
            
        self.x_velocity = -self.MOVE_SPEED

    def move_right(self):
        """
        Moves the player to right at MOVE_SPEED
        """
            
        self.x_velocity = self.MOVE_SPEED

    def stop_horizontal_movement(self):
        """
        Stops player horizontal movement
        """
            
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

        if self.canvas_object == None:
            # First time creating player
            self.canvas_object = self.canvas.create_rectangle(
                x1, x2, y1, y2,
                fill = self.color,
                outline = "grey"
            )
        else:
            # Player already exists so update position
            self.canvas.coords(self.canvas_object, x1, y1, x2, y2)

    







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