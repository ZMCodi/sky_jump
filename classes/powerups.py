from constants import *
from random import uniform as randf, choice

class Powerup:
    """Represents powerup objects in the game"""

    # Class constants
    COLORS = {
        TYPE_ROCKET: "red",
        TYPE_MULTIPLIER: "gold"
    }

    def __init__ (self, canvas, x, y, powerup_type, multiplier=None, duration=None):
        """
        Initializes a new powerup instance
        
        Args:
            canvas (canvas.Tk): Game canvas to draw powerup on
            x (int): Powerup initial x position
            y (int): Powerup initial y position
            powerup_type (str): Type of powerup to create
        """
        
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 10
        self.height = self.width
        self.type = powerup_type
        self.color = self.COLORS[powerup_type]
        self.canvas_object = None
        self.is_collected = False
        self.start_time = None
        self.multiplier = multiplier
        self.duration = duration


    def apply_effect(self, player, score_manager):
        """Applies powerup effect on player"""

        if self.type == TYPE_ROCKET:
            player.y_velocity = 2 * JUMP_FORCE * player.boost_multipliers['jump']
        else:
            score_manager.activate_multiplier(self.multiplier, self.duration)

    def render(self, camera_y):
        """Renders powerup object on canvas"""

        if self.canvas_object:
            self.canvas.delete(self.canvas_object)

        # Render powerups with camera offset
        x1 = self.x
        y1 = self.y - camera_y
        x2 = x1 + self.width
        y2 = y1 + self.height

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
            bool: True if collision occurred
        """
        # Check horizontal overlap
        powerup_right = self.x + self.width
        player_right = player.x + player.width
        
        # If one rectangle is on the left side of the other
        if powerup_right < player.x or player_right < self.x:
            return False
            
        # Check vertical overlap
        powerup_bottom = self.y + self.height
        player_bottom = player.y + player.height
        
        # If one rectangle is above the other
        if powerup_bottom < player.y or player_bottom < self.y:
            return False
            
        return True
    
    def cleanup(self):
        """Cleans up collected and uncollected powerups"""

        if self.canvas_object is not None:
            self.canvas.delete(self.canvas_object)
            self.canvas_object = None
    

class PowerupManager:
    """Manages powerup generation and collection"""
    

    # Class constants
    POWERUP_SPAWN_CHANCE = 0.3
    MULTIPLIER_RANGE = (1.5, 3.0)
    MULTIPLIER_DURATION_RANGE = (10, 20)
    POWERUP_THRESHOLD = WINDOW_HEIGHT

    def __init__ (self, canvas):

        self.canvas = canvas
        self.powerups = []
        self.last_check_height = self.POWERUP_THRESHOLD


    def check_powerup(self, player):
        """Checks if powerup should spawn"""
        
        current_height = player.y
        
        # Check spawn conditions
        if current_height < self.last_check_height:
            if current_height // self.POWERUP_THRESHOLD != self.last_check_height // self.POWERUP_THRESHOLD:
                
                if randf(0, 1) < self.POWERUP_SPAWN_CHANCE:
                    spawn_height = current_height - WINDOW_HEIGHT
                    self.generate_powerup(spawn_height)
        
        self.last_check_height = current_height

    def generate_powerup(self, y_position):
        """Generates new powerups at y_position"""

        powerup_x = randf(0, WINDOW_WIDTH - 10)
        powerup_type = choice([TYPE_ROCKET, TYPE_MULTIPLIER])
        powerup_multiplier = None
        powerup_duration = None

        if powerup_type == TYPE_MULTIPLIER:
            powerup_multiplier = randf(*self.MULTIPLIER_RANGE)
            powerup_duration = randf(*self.MULTIPLIER_DURATION_RANGE)

        powerup = Powerup(self.canvas, powerup_x, y_position, powerup_type, powerup_multiplier, powerup_duration)
        self.powerups.append(powerup)


    def update(self, player, score_manager):

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
        """Renders all powerups and debug info on canvas"""
        
        # Render powerups
        for powerup in self.powerups:
            powerup.render(camera_y)

    def reset(self):
        """Cleanup all powerups on reset"""

        for powerup in self.powerups:
            powerup.cleanup()

        self.powerups = []
        self.last_check_height = self.POWERUP_THRESHOLD