from constants import *

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
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = "white"
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False

        # Player movement states
        self.moving_left = False
        self.moving_right = False

        # Boost attributes
        self.boost_multipliers = {
            'speed': 1.0,
            'jump': 1.0,
            'gravity': 1.0
        }


    def start_move_left(self):
        """Moves the player to left at MOVE_SPEED"""
        
        self.moving_left = True
        self.x_velocity = -MOVE_SPEED * self.boost_multipliers['speed']

    def stop_move_left(self):
        """Stops player movement to the left"""
        
        self.moving_left = False

        # Only stop if player is not moving right
        if not self.moving_right:
            self.x_velocity = 0

    def start_move_right(self):
        """Moves the player to right at MOVE_SPEED"""
        
        self.moving_right = True
        self.x_velocity = MOVE_SPEED * self.boost_multipliers['speed']

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
            self.y_velocity = JUMP_FORCE * self.boost_multipliers['jump']
            self.is_jumping = True

    def update(self, diff_time):
        """
        Update player position and apply physics

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Apply gravity
        self.y_velocity += GRAVITY * self.boost_multipliers['gravity']

        # Don't allow player to jump if they are falling
        if self.y_velocity > 0:
             self.is_jumping = True

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

    def handle_boost(self, boost):
            """Callback for when a boost is activated"""

            self.boost_multipliers[boost.type] = boost.multiplier

    def handle_boost_expire(self, boost):
            """Callback for when a boost expires"""

            self.boost_multipliers[boost.type] = 1.0
