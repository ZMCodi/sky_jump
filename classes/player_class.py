"""This module handles the Player object which is controlled by the player
    
    The player object moves within the canvas, collides
    with other canvas objects and accumulates score
    as it gets higher
"""

from constants import (
    # Player dimensions
    PLAYER_WIDTH, PLAYER_HEIGHT,
    # Physics constants
    MOVE_SPEED, JUMP_FORCE, GRAVITY,
    # Window dimensions
    WINDOW_HEIGHT, WINDOW_WIDTH
)


class Player:
    """Player class that creates the player object and its movement

    Attributes:
        canvas (tk.Canvas): Game canvas where player will be drawn
        x (float): Player x position
        y (float): Player y position
        width (int): Player width in pixels
        height (int): Player height in pixels
        color (str): Player fill color
        face (tk.PhotoImage): Player face image overlay
        x_velocity (int): Player horizontal velocity
        y_velocity (int): Player vertical velocity
        is_jumping (bool): Flag whether player is currently jumping
        is_on_ground (bool): Flag whether player is on solid surface
        double_jump_enabled (bool): Flag whether player cheat is enabled
        boost_multipliers (dict): Multipliers for all movement constants
    """

    def __init__(self, canvas, x, y):
        """Initialize new player instance

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
        self.face = None
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False
        self.is_on_ground = True

        # Manage cheat states
        self.double_jump_enabled = False
        self.is_on_second_jump = False

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

        # Only stop if player is also not moving right
        if not self.moving_right:
            self.x_velocity = 0

    def start_move_right(self):
        """Moves the player to right at MOVE_SPEED""" 
        self.moving_right = True
        self.x_velocity = MOVE_SPEED * self.boost_multipliers['speed']

    def stop_move_right(self):
        """Stops player movement to the right"""
        self.moving_right = False

        # Only stop if player is also not moving left
        if not self.moving_left:
            self.x_velocity = 0

    def activate_double_jump(self):
        """Activates double jump cheat
        
            If this cheat is activated, player
            can jump again without touching the ground
            after an initial jump
        """
        self.double_jump_enabled = True

    def jump(self):
        """
        Moves player up by JUMP_FORCE if player is not already jumping
        """
        # If player is on ground, do a normal jump
        if not self.is_jumping:
            self.y_velocity = JUMP_FORCE * self.boost_multipliers['jump']
            self.is_jumping = True
            self.is_on_second_jump = False

        # Jump again if double jump is enabled and player hasn't used second jump
        elif self.double_jump_enabled and not self.is_on_second_jump:
            self.y_velocity = JUMP_FORCE * self.boost_multipliers['jump']
            self.is_on_second_jump = True

    def update(self, diff_time):
        """
        Update player position and apply physics

        Args:
            diff_time (float): Time since last update in seconds
        """
        self.is_on_ground = False
        diff_time = min(diff_time, 1.0 / 30.0)

        # Apply gravity
        gravity_force = GRAVITY * self.boost_multipliers['gravity']
        self.y_velocity += gravity_force

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
            self.is_on_ground = True

        # Screen wrapping for horizontal movement
        canvas_width = int(self.canvas.cget('width'))
        if self.x + self.width < 0:
            self.x = canvas_width
        elif self.x > canvas_width:
            self.x = -self.width

    def handle_boost(self, boost):
        """Callback for when a boost is activated
        
            This method gets the new boost multipliers
            from the Boost object

            Args:
                boost (object): object which increases player movement speed
        """
        self.boost_multipliers[boost.type] = boost.multiplier

    def handle_boost_expire(self, boost):
        """Callback for when a boost expires
        
            Resets the boost multiplier of the expired
            boost to its initial value

            Args:
                boost (object): boost object that has expired    
        """
        self.boost_multipliers[boost.type] = 1.0

    def reset(self):
        """Resets player position on the canvas upon start of new game"""
        # Reset player position
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - PLAYER_HEIGHT

        # Reset player movement state
        self.x_velocity = 0
        self.y_velocity = 0
        self.is_jumping = False
        self.is_on_ground = True
        self.moving_left = False
        self.moving_right = False
        self.double_jump_enabled = False
        self.is_on_second_jump = False

        # Reset boost multipliers
        self.boost_multipliers = {
            'speed': 1.0,
            'jump': 1.0,
            'gravity': 1.0
        }
