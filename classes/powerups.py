"""This module handles the Powerup object and the PowerupManager

Powerups generation is random and controlled by PowerupManager.
It provides a short boost for the player upon collection
"""

import os
from random import uniform as randf, choice
from PIL import Image, ImageTk
from constants import (
    # Powerup types
    TYPE_ROCKET, TYPE_MULTIPLIER,
    # Player movement
    JUMP_FORCE,
    # Window dimensions
    WINDOW_WIDTH, WINDOW_HEIGHT
)


class Powerup:
    """Represents powerup objects in the game
    
    Attributes:
        canvas (tk.Canvas): Canvas to draw powerup on
        x (float): Powerup x position
        y (float): Powerup y position
        type (str): Powerup type whether rocket or multiplier
        color (str): Powerup fill color based on type
        icon (tk.PhotoImage): Powerup icon based on type
        folder (str): Folder storing powerup icon images
        canvas_object: Image if icon is loaded, circle otherwise
        is_collected (bool): Flag whether the powerup has been collected by player
        multiplier (float): Score multiplier of multiplier powerup
        duration (float): Multiplier powerup duration

    Constants:
        COLORS (dict): Dictionary of colors depending on multiplier type
    """
    # Class constants
    COLORS = {
        TYPE_ROCKET: "red",
        TYPE_MULTIPLIER: "gold"
    }

    def __init__(self, canvas, x, y, powerup_type, multiplier=None, duration=None):
        """
        Initializes a new powerup instance
        
        Args:
            canvas (canvas.Tk): Game canvas to draw powerup on
            x (int): Powerup initial x position
            y (int): Powerup initial y position
            powerup_type (str): Type of powerup to create
            multiplier (float): Score multiplier for multiplier powerup
            duration (float): Duration in seconds of score multiplier
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 30
        self.height = self.width
        self.type = powerup_type
        self.color = self.COLORS[powerup_type]
        self.icon = None
        self.folder = "powerup_icons"
        self.canvas_object = None
        self.is_collected = False
        self.multiplier = multiplier
        self.duration = duration
        self.load_powerup_images()

    def load_powerup_images(self):
        """Load powerup images for powerup icons"""
        try:
            icon_list = [i for i in os.listdir(self.folder) if i.endswith('.png')]
        
            for icon in icon_list:
                if icon.removesuffix(".png") == self.type:
                    icon_path = os.path.join(self.folder, icon)

                    with Image.open(icon_path) as image:
                        powerup_image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                        powerup_photo = ImageTk.PhotoImage(powerup_image)
                        name = icon.removesuffix(".png")
                        self.icon = powerup_photo
                        
        except Exception as e:
            print(f"Error loading powerup image: {e}")

    def apply_effect(self, player, score_manager):
        """Applies powerup effect on player
            - Moves player upwards for rocket powerup
            - Increases score multiplier for multiplier powerup

        Args:
            player (object): Player object in the game
            score_manager (object): Score manager object in game
        """
        if self.type == TYPE_ROCKET:
            # Stacks with boosts
            player.y_velocity = 2 * JUMP_FORCE * player.boost_multipliers['jump']
        else:
            score_manager.activate_multiplier(self.multiplier, self.duration)

    def render(self, camera_y):
        """Renders powerup object on canvas
        
        Args:
            camera_y (float): Camera y position to count for offset
        """
        if self.canvas_object:
            self.canvas.delete(self.canvas_object)

        # Render powerups with camera offset
        x1 = self.x
        y1 = self.y - camera_y
        x2 = x1 + self.width
        y2 = y1 + self.height

        if self.icon is not None:
            # Renders icon if loaded
            self.canvas_object = self.canvas.create_image(
                x1, y1,
                image=self.icon,
                anchor='nw',
                tags='powerup_icon'
            )
        else:
            # Render circles if icon not loaded
            self.canvas_object = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=self.color,
                outline="grey",
                tags = ("powerup", f"powerup_{self.type}")
            )

    def check_collision(self, player):
        """
        Check if player has collided with powerup
        
        Args:
            player: Player object
        
        Returns:
            bool: True if collision occurred, False otherwise
        """
        # Check horizontal overlap
        powerup_right = self.x + self.width
        player_right = player.x + player.width
        if powerup_right < player.x or player_right < self.x:
            return False
            
        # Check vertical overlap
        powerup_bottom = self.y + self.height
        player_bottom = player.y + player.height
        if powerup_bottom < player.y or player_bottom < self.y:
            return False
            
        return True
    
    def cleanup(self):
        """Cleans up collected and uncollected powerups"""
        if self.canvas_object is not None:
            self.canvas.delete(self.canvas_object)
            self.canvas_object = None
    

class PowerupManager:
    """Manages powerup generation, collection and other logic
    - Determines powerup generation randomly
    - Generate powerup objects
    - Updates and renders powerup each frame

    Attributes:
        canvas (tk.Canvas): Canvas to draw powerups on
        powerups (list): List of active powerups
        last_check_height (float): y position of last threshold checked
            for powerup generation

    Contants:
        POWERUP_SPAWN_CHANCE (float): Chance of a powerup spawning in a given threshold
        POWERUP_THRESHOLD (float): Height threshold the player needs to pass for powerup
            generation to be considered
        MULTIPLIER_RANGE (tuple): Range of score multiplier the multiplier 
            powerup can have
        MULTIPLIER_DURATION_RANGE (tuple): Range of duration the multiplier 
            powerup can have

    Notes:
        Powerup generation is purely random and not
        dependent on height or score. This is to prevent a powerup
        from skewing generation chances i.e. if generation is dependent
        on score, the multiplier powerup will make more powerups generate
        and if dependent on height, the rocket powerup will make more
        powerups generate.
    """
    # Class constants
    POWERUP_SPAWN_CHANCE = 0.3
    POWERUP_THRESHOLD = WINDOW_HEIGHT
    MULTIPLIER_RANGE = (1.5, 3.0)
    MULTIPLIER_DURATION_RANGE = (10, 20)

    def __init__ (self, canvas):
        """Creates the powerup manager objecy
        
        Args:
            canvas (tk.Canvas): Canvas to draw powerup on
        """
        self.canvas = canvas
        self.powerups = []
        self.last_check_height = self.POWERUP_THRESHOLD

    def check_powerup(self, player):
        """Checks if powerup should spawn
            - Check if player has passed a new POWERUP_THRESHOLD
            - If yes, get chances of powerup spawning one screen height above

        Args:
            player (object): Player object in game
        """
        current_height = player.y
        
        # Check spawn conditions
        if current_height < self.last_check_height:
            new_threshold = current_height // self.POWERUP_THRESHOLD
            old_threshold = self.last_check_height // self.POWERUP_THRESHOLD
            if new_threshold != old_threshold:          
                if randf(0, 1) < self.POWERUP_SPAWN_CHANCE:
                    spawn_height = current_height - WINDOW_HEIGHT
                    self.generate_powerup(spawn_height)
        
        self.last_check_height = current_height

    def generate_powerup(self, y_position):
        """Generates new powerups at y_position
        
        Args:
            y_position (float): y position to generate powerup at"""
        # Get random generation parameters
        powerup_x = randf(0, WINDOW_WIDTH - 10)
        powerup_type = choice([TYPE_ROCKET, TYPE_MULTIPLIER])
        powerup_multiplier = None
        powerup_duration = None

        # Additional parameters for multiplier powerups
        if powerup_type == TYPE_MULTIPLIER:
            powerup_multiplier = randf(*self.MULTIPLIER_RANGE)
            powerup_duration = randf(*self.MULTIPLIER_DURATION_RANGE)

        powerup = Powerup(self.canvas, 
                          powerup_x, y_position, 
                          powerup_type, 
                          powerup_multiplier, 
                          powerup_duration)
        self.powerups.append(powerup)

    def update(self, player, score_manager):
        """Updates all powerup to check collision and cleanup
        
        Args:
            player (object): Player object in game
            score_manager (object): Score manager object in game"""
        # Check if powerups should spawn
        self.check_powerup(player)

        # Removes powerups that are collected by the player
        powerups_to_remove = []
        for powerup in self.powerups:
            if powerup.check_collision(player):
                powerup.apply_effect(player, score_manager)
                powerup.is_collected = True
                powerup.cleanup()
                powerups_to_remove.append(powerup)

        for powerup in powerups_to_remove:
            if powerup in self.powerups:
                self.powerups.remove(powerup)

        # Removes powerups that are below camera bounds
        cleanup_bottom = player.y + 300
        tmp_powerup = []
        for powerup in self.powerups:
            if powerup.y < cleanup_bottom:
                tmp_powerup.append(powerup)

        self.powerups = tmp_powerup

    def render(self, camera_y):
        """Renders all powerups on canvas
        
        Args:
            camera_y (float): Camera y position to account for offset
        """
        for powerup in self.powerups:
            powerup.render(camera_y)

    def reset(self):
        """Cleanup all powerups on reset"""
        for powerup in self.powerups:
            powerup.cleanup()

        self.powerups = []
        self.last_check_height = self.POWERUP_THRESHOLD