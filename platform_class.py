from constants import *
from random import uniform as randf, choice

class Platform:
    """
    Creates a platform object that the player can jump on

    Attributes:
    canvas (tk.Canvas): Game canvas where platform will be drawn
    x (float): Platform x position
    y (float): Platform y position
    width (int): Platform width
    height (int): Platform height
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
    DEFAULT_WIDTH = WINDOW_WIDTH // 2
    COLORS = {
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
        self.x = x
        self.y = y
        self.type = platform_type
        self.height = 10
        self.width = self.DEFAULT_WIDTH
        self.color = self.COLORS[platform_type]

        # Set movement property based on platform type
        if (self.type == self.TYPE_MOVING or self.type == self.TYPE_WRAPPING):
            self.direction = choice([1, -1])
            self.velocity = self.direction * randf(0.2 * MOVE_SPEED, 0.8 * MOVE_SPEED)
        else:
            self.velocity = 0

        self.is_active = True

        # Check if platform exists
        self.canvas_object = None


    def update(self, diff_time):
        """
        Update platform position, direction and state

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Update positions based on velocity for moving and wrapping platforms
        if (self.type == self.TYPE_MOVING or self.type == self.TYPE_WRAPPING):
            self.x += self.velocity * diff_time

        # Screen wrapping for wrapping platforms
        if (self.type == self.TYPE_WRAPPING):
            canvas_width = int(self.canvas.cget('width'))
            if self.x + self.width < 0: # Platform right side is off canvas left side
                self.x = canvas_width
            elif self.x > canvas_width: # Platform left side is off canvas right side
                self.x = -self.width

        
        # Change direction for moving platforms when hitting canvas edge
        if (self.type == self.TYPE_MOVING):
            canvas_width = int(self.canvas.cget('width'))
            if (self.x + self.width >= canvas_width or self.x <= 0): # Platform right side collides with canvas left edge or vice versa
                self.velocity = -self.velocity

    def check_collision(self, player):
        """
        Check if player has collided from above

        Args:
            player: Player object

        Returns:
            bool: True if valid collision occured
        """

        if not self.is_active:
            return False
        
        # Only check collision when player is falling
        if (player.y_velocity <= 0):
            return False
        
        # Check if player's bottom edge is on platform's top edge
        player_bottom = player.y + player.height
        platform_top = self.y

        # Check vertical collision
        if (player_bottom >= platform_top and player_bottom <= platform_top + 10): # Gives a reasonable amount of tolerance
            
            # Check horizontal overlap
            platform_right = self.x + self.width
            player_right = player.x + player.width
            overlap_left = max(self.x, player.x)
            overlap_right = min(platform_right, player_right)
            overlap_amount = overlap_right - overlap_left

            # Check if overlap is at least half of player width
            if (overlap_amount >= player.width / 2):
                return True
            
        return False
        

    
    def render(self):
        """
        Draw platform on canvas or update platform position
        """

        x1 = self.x
        y1 = self.y
        x2 = x1 + self.width
        y2 = y1 + self.height

        if self.canvas_object is None:
            # First time creating platform
            self.canvas_object = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill = self.color,
                outline = "grey",
                tags = ("platform", f"platform_{self.type}")
            )
        else:
            # Platform already exists so update position
            self.canvas.coords(self.canvas_object, x1, y1, x2, y2)

    def cleanup(self):
        """Removes platform from canvas"""

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
        difficulty_factor (float): Scales with height to adjust platform generation
    """

    def __init__(self, canvas):
        
        # Store canvas reference
        self.canvas = canvas
        self.platforms = []
        self.current_height = 0
        self.difficulty_factor = 0

        # TODO: Create logic for spacing calculation
        self.min_platform_spacing = 10
        self.max_platform_spacing = 100

    def update(self, player_height):
        """
        Updates platform generation and cleanup based on player height
        - Generates new platforms
        - Cleanup platforms outside of screen
        - Updates difficulty factor
        """

        # Checks if new platforms are needed
        self.check_platforms()

        # Update existing platforms
        for platform in self.platforms:
            platform.update(FRAME_TIME)

    def check_platforms(self):
        """
        Checks if there are enough platforms ahead. If not, generate more.
        """

        # Generate initial platforms if none exist
        if not self.platforms:
            self.generate_initial_platforms()
            return
        
        # Find highest platform
        self.highest_platform = min([platform.y for platform in self.platforms])

        # Generate new platforms if there is too much space at the top
        while self.highest_platform > self.min_platform_spacing:
            next_platform = self.highest_platform - randf(self.max_platform_spacing, self.min_platform_spacing)
            self.generate_platforms(next_platform)
            self.highest_platform = next_platform

    def generate_platforms(self, platform_y):
        """
        Generates new platform at y_position
        - Chooses platform type and speed based on difficulty
        - Ensures proper spacing
        - Adds platform to management system
        """

        # Get random x position on canvas
        platform_x = randf(0, WINDOW_WIDTH - Platform.DEFAULT_WIDTH)

        # Create and add the platform (normal platforms only for now)
        platform = Platform(self.canvas, platform_x, platform_y, Platform.TYPE_NORMAL)
        self.platforms.append(platform)

    def generate_initial_platforms(self):
        """
        Generates initial platforms when the game starts
        """

        # Start with a platform close to the bottom
        self.generate_platforms(WINDOW_HEIGHT - 100)

        # Generate 5 more platforms until the top of the screen
        current_height = WINDOW_HEIGHT - 100
        for i in range(5):
            current_height -= randf(self.min_platform_spacing, self.max_platform_spacing)
            self.generate_platforms(current_height)


    def cleanup_platforms(self, camera_bottom):
        """
        Deletes platforms that are below the bottom of the camera
        """

        # TODO: implement this method
        pass

    def calc_platform_probability(self):
        """
        Calculates probability distribution for different platform based on 
        difficulty factor
        """

        # TODO: implement this method
        pass