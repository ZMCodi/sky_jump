from constants import *

class Camera:
    """
    Handles viewport scrolling to follow player

    Attributes:
        y (float): Current camera height
        target_y (float): Target height camera should move to
        lerp_speed (float): Speed of camera movement (1.0 = instant)
    """

    def __init__(self):
        """
        Initializes camera object and starting values
        """

        self.y = 0
        self.target_y = 0
        self.lerp_speed = 0.1

    def update(self, player):
        """
        Updates camera position based on player position

        Args:
            player: Player object to follow
        """

        # Calculate where camera should be to keep player within desired screen region
        player_screen_y = WINDOW_HEIGHT * (1 - SCREEN_BOTTOM)
        self.target_y = player.y - player_screen_y

        # Smoothly move camera towards target position
        self.y += (self.target_y - self.y) * self.lerp_speed

    def world_to_screen(self, world_x, world_y):
        """
        Converts world coordinates to screen coordinates

        Args:
            world_x (float): x position in world space
            world_y (float): y position in world space

        Returns:
            tuple: (screen_x, screen_y) positions on screen
        """

        screen_x = world_x
        screen_y = world_y - self.y
        return (screen_x, screen_y)