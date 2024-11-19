"""This module handles the camera system for the game viewport.

The camera keeps the player within a desired range on the screen
by adjusting the view position. It uses linear interpolation (lerp)
for smooth camera movement, preventing jerky transitions as the
player moves vertically.
"""

from constants import WINDOW_HEIGHT, SCREEN_BOTTOM


class Camera:
    """
    Handles viewport scrolling to follow player

    Attributes:
        y (float): Current camera height
        target_y (float): Target height camera should move to
        lerp_speed (float): Speed of camera movement (1.0 = instant)
    """
    def __init__(self):
        """Initializes camera object and starting values"""
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
        
        # Smoothly move camera towards target position
        self.target_y = player.y - player_screen_y
        self.y += (self.target_y - self.y) * self.lerp_speed

    def reset(self):
        """Resets camera position"""
        self.y = 0
        self.target_y = 0
