"""This module handles the Platform and PlatformManager classes

Platforms are objects that the player jumps on
to move upwards and gain scores while the
PlatformManager manages platform generation,
cleanup and checks player death"""

from random import uniform as randf, choice
from constants import (
    # Platform types
    TYPE_NORMAL,
    TYPE_MOVING,
    TYPE_BREAKING, 
    TYPE_WRAPPING,
    BREAK_TIMER,
    # Movement constants
    MOVE_SPEED,
    MAX_JUMP_HEIGHT,
    # Window dimensions
    WINDOW_HEIGHT,
    WINDOW_WIDTH
)


class Platform:
    """
    Creates a platform object that the player can jump on

    Attributes:
        canvas (tk.Canvas): Game canvas where platform will be drawn
        x (float): Platform x position
        y (float): Platform y position
        type (str): Platform type whether normal, moving, wrapping or breaking
        width (int): Platform width
        height (int): Platform height
        color (str): Platform fill colour
        velocity (float): Platform horizontal velocity
        direction (int): Platform starting movement direction
        (1 for right, -1 for left)
        is_active (bool): Determines whether platform can be collided with

    Class constants:
        COLORS (str): Platform fill based on type
    """

    # Class constants
    COLORS = {
        TYPE_NORMAL: "blue",
        TYPE_MOVING: "green",
        TYPE_BREAKING: "red",
        TYPE_WRAPPING: "purple"
    }

    def __init__(self, canvas, x, y, platform_type, platform_width):
        """
        Initializes a new platform instance

        Args:
            canvas (canvas.Tk): Game canvas to draw platform on
            x (float): Platform initial x position
            y (float): Platform initial y position
            platform_type (str): Type of platform to create
            platform_width (float): Platform width, gets shorter as game
            gets more difficult
        """
        
        # Store canvas reference
        self.canvas = canvas

        # Set position and appearance
        self.x = x
        self.y = y
        self.type = platform_type
        self.height = 10
        self.width = platform_width
        self.color = self.COLORS[platform_type]
        self.canvas_object = None

        # Set movement property based on platform type
        if self.type == TYPE_MOVING:
            self.direction = choice([1, -1])
            self.velocity = self.direction * randf(0.2, 0.8) * MOVE_SPEED
        elif self.type == TYPE_WRAPPING:
            self.direction = choice([1, -1])
            self.velocity = self.direction * randf(0.3, 1.0) * MOVE_SPEED
        else:
            self.velocity = 0

        self.is_active = True
        self.break_timer = None

    def update(self, diff_time):
        """Update platform position, direction and state based on their types

        Args:
            diff_time (float): Time since last update in seconds
        """
        # Don't update if platform is inactive
        if not self.is_active:
            return
        
        # Handle breaking platforms
        if self.type == TYPE_BREAKING and self.break_timer is not None:
            self.break_timer -= diff_time
            if self.break_timer <= 0:
                self.is_active = False
                return

        # Update positions based on velocity for moving and wrapping platforms
        old_x = self.x
        if self.type == TYPE_MOVING or self.type == TYPE_WRAPPING:
            self.x += self.velocity * diff_time
            canvas_width = int(self.canvas.cget('width'))

            # Screen wrapping for wrapping platforms
            if self.type == TYPE_WRAPPING:
                if self.x + self.width < 0:
                    self.x = canvas_width
                elif self.x > canvas_width:
                    self.x = -self.width

            # Change direction for moving platforms when hitting canvas edge
            if self.type == TYPE_MOVING:
                if self.x + self.width >= canvas_width or self.x <= 0:
                    self.velocity = -self.velocity
                    self.x = old_x

    def render(self, camera_y):
        """Renders platform on the game canvas
        
        Args:
            camera_y (float): Camera y coordinate to account for offset
        """
        # Don't render inactive platform
        if not self.is_active:
            return

        # Clear existing canvas object
        if self.canvas_object:
            self.canvas.delete(self.canvas_object)

        # Render platforms with camera offset
        x1 = self.x
        y1 = self.y - camera_y
        x2 = x1 + self.width
        y2 = y1 + self.height

        # Create platform
        self.canvas_object = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.color,
            outline="grey",
            tags=("platform", f"platform_{self.type}")
        )

    def check_collision(self, player):
        """
        Check if player has collided from above

        Args:
            player: Player object

        Returns:
            bool: True if valid collision occured
        """
        # No collision with inactive platforms
        if not self.is_active:
            return False
        
        # Only check collision when player is falling
        if player.y_velocity <= 0:
            return False
        
        # Check if player's bottom edge is on platform's top edge
        player_bottom = player.y + player.height
        platform_top = self.y

        # Check vertical collision with reasonable tolerance
        if player_bottom >= platform_top and player_bottom <= platform_top + 10:
            
            # Check horizontal overlap
            platform_right = self.x + self.width
            player_right = player.x + player.width
            overlap_left = max(self.x, player.x)
            overlap_right = min(platform_right, player_right)
            overlap_amount = overlap_right - overlap_left

            # Check if overlap is at least 1/3 of player width
            if overlap_amount >= player.width / 3:
                if self.type == TYPE_BREAKING and self.break_timer is None:
                    self.break_timer = BREAK_TIMER
                player.is_on_ground = True
                return True
            
        return False
    
    def cleanup(self):
        """Removes platform from canvas
        
        This method is essential to prevent too many canvas
        objects to be stored at once to prevent lagging
        """
        if self.canvas_object is not None:
            self.canvas.delete(self.canvas_object)
            self.canvas_object = None


class PlatformManager:
    """
    Manages platform generation, cleanup and difficulty scaling

    Attributes:
        canvas (tk.Canvas): Game canvas where platforms are drawn
        platforms (list): List of active platforms
        min_platform_spacing (float): Minimum vertical space between platforms
        max_platform_spacing (float): Maximum vertical space between platforms
        current_height (float): Current player height
        highest_platform (float): Height of highest platform
        difficulty_manager (object): Updates difficulty_factor and generation parameters
        difficulty_factor (float): Scales with height to adjust platform generation
        callbacks (dict): Informs listeners of player death
        platform_params (dict): Parameters used to generate platform
    """

    def __init__(self, canvas, difficulty_manager=None):
        """Creates the PlatformManager object
        
        Args:
            canvas (tk.Canvas): canvas to draw platforms on
            difficulty_manager (object): provides platform generation parameters 
            (defaults to None)
        """
        # Store canvas reference
        self.canvas = canvas

        self.platforms = []
        self.current_height = 0
        self.difficulty_factor = 0
        self.highest_platform = WINDOW_HEIGHT
        self.callbacks = {
            'on_death': []
        }

        # Default spacing if no difficulty manager
        self.min_platform_spacing = MAX_JUMP_HEIGHT * 0.6
        self.max_platform_spacing = MAX_JUMP_HEIGHT * 0.9

        # Sets up difficulty management to manage platform generation
        self.difficulty_manager = difficulty_manager
        if difficulty_manager:
            self.difficulty_manager.register_callback('on_param_update', 
                                                      self.update_generation_params)
            self.platform_params = self.difficulty_manager.get_platform_params()

    def update_generation_params(self, new_params):
        """Updates the generation parameters to new parameters
        
        This method ensures that generated platforms get more challenging
        as player progresses to make the gameplay more balanced. The
        updated parameters are platform spacing, width, speed and type
        distribution.

        Args:
            new_params (dict): New generation parameters generated by difficulty manager
        """
        self.platform_params = new_params
        self.min_platform_spacing = self.platform_params['spacing_range'][0]
        self.max_platform_spacing = self.platform_params['spacing_range'][1]

    def update(self, player_height, diff_time):
        """Updates platform generation and cleanup based on player height
        - Generates new platforms
        - Cleanup platforms outside of screen
        - Updates difficulty factor

        Args:
            player_height (float): Current player height
            diff_time (float): Time since last update
        """
        # Checks if new platforms are needed
        self.check_platforms(player_height)

        # Update existing platforms
        for platform in self.platforms:
            platform.update(diff_time)

        # Cleanup platforms that are too far below
        self.cleanup_platforms(player_height)

    def check_platforms(self, player_height):
        """Checks if there are enough platforms ahead. If not, generate more.

            This method ensures a steady supply of platforms within
            a reasonable distance above the player

        Args:
            player_height (float): Current player height
        """
        # Generate initial platforms if none exist
        if not self.platforms:
            self.generate_initial_platforms()
            return
        
        # Find highest platform
        self.highest_platform = min([platform.y for platform in self.platforms])

        # Generate new platforms up to one screen height above current screen
        while self.highest_platform > player_height - WINDOW_HEIGHT:
            next_platform = self.highest_platform - randf(self.min_platform_spacing,
                                                           self.max_platform_spacing)
            self.generate_platforms(next_platform)
            self.highest_platform = next_platform

    def generate_platforms(self, platform_y):
        """Generates new platform at a given y position
        - Chooses platform width, type and speed based on difficulty
        - Ensures proper spacing
        - Adds platform to management system

        Args: 
            platform_y (float): y position to generate platform at
        """
        # Get platform generation parameters
        params = self.platform_params
        min_width = params['width_range'][0]
        max_width = params['width_range'][1]
        platform_width = randf(min_width, max_width)
        available_width = WINDOW_WIDTH - platform_width
        platform_x = randf(0, available_width)
        platform_type = self.difficulty_manager.calculate_platform_type()

        # Create the platform based on parameters and add to PlatformManager
        platform = Platform(self.canvas, 
                            platform_x, platform_y, 
                            platform_type, 
                            platform_width)
        self.platforms.append(platform)

    def generate_initial_platforms(self):
        """Generates initial platforms when the game starts"""
        # Start with a platform close to the bottom
        self.generate_platforms(WINDOW_HEIGHT - MAX_JUMP_HEIGHT + 20)

        # Generate platforms 1.2 screen height ahead
        current_height = WINDOW_HEIGHT - MAX_JUMP_HEIGHT + 20
        while current_height > -WINDOW_HEIGHT * 0.2:
            current_height -= randf(self.min_platform_spacing, 
                                    self.max_platform_spacing)
            self.generate_platforms(current_height)
        
        # Update highest platform position
        self.highest_platform = current_height

    def cleanup_platforms(self, player_height):
        """Deletes platforms that are below the bottom of the camera

        This method ensures that the game doesn't lag due to
        too many canvas objects at once

        Args:
            player_height (float): current player height
        """
        # Clears platforms 300px below player height
        cleanup_bottom = player_height + 300
        tmp_platform = []
        for platform in self.platforms:
            if platform.y < cleanup_bottom:
                tmp_platform.append(platform)

        self.platforms = tmp_platform

    def get_platforms(self):
        """Returns active platforms for rendering and collision

        Returns:
            platforms (list): List of all platform objects managed by PlatformManager
        """
        return self.platforms
    
    def register_callback(self, event_type, callback):
        """Register a callback for specific events
        
        Args:
            event_type (str): Name of the event to be registered
            callback (method): Method to be called upon the callback trigger
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def trigger_callbacks(self, event_type, *args):
        """Trigger all callbacks registered for an event
        
        Args:
            event_type (str): Name of the event to be registered
            *args: Variable number of additional arguments to pass to the callback
        """
        for callback in self.callbacks[event_type]:
            callback(*args)

    def check_player_death(self, player):
        """Checks if player is lower than lowest available platform.
            if yes, trigger player death callback
            
        Args:
            player (object): The player object in the game
        """
        # Get lowest platform height
        lowest_platform = max(platform.y for platform in self.platforms)
        if not player.is_on_ground and player.y > lowest_platform + 50:
            self.trigger_callbacks('on_death')
  
    def reset(self):
        """Resets platform manager
        - Cleans up all active platforms
        - Reinitialize all attributes
        - Get new platform generation parameters
        - Generate initial platforms
        """
        for platform in self.platforms:
            platform.cleanup()

        self.platforms = []
        self.current_height = 0
        self.difficulty_factor = 0
        self.highest_platform = WINDOW_HEIGHT

        if self.difficulty_manager:
            self.platform_params = self.difficulty_manager.get_platform_params()

        self.generate_initial_platforms()