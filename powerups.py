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
        self.height = 10
        self.type = powerup_type
        self.color = self.COLORS[powerup_type]
        self.canvas_object = None
        self.is_collected = False
        self.start_time = None
        self.duration = duration
        

    def apply_effect(self, player, score_manager):
        """Applies powerup effect on player"""

        if self.type == TYPE_ROCKET:
            player.y_velocity -= 5 * JUMP_FORCE * player.boost_multipliers['jump']
        else:
            # TODO: make the score manager times 1.5-3.0
            pass

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
    

class PowerupManager:
    """Manages powerup generation and collection"""

    def __init__ (self, canvas, difficulty_manager, score_manager):

        self.canvas = canvas
        self.powerups = []
        self.current_score = 0
        self.difficulty_factor = 0
        self.callbacks = {
            'on_pickup': [],
            'on_expiry': []
        }
        self.difficulty_manager = difficulty_manager

    def generate_powerup(self, y_position):
        """Generates new powerups at y_position"""

        powerup_x = randf(0, WINDOW_WIDTH - 10)
        powerup_type = choice([TYPE_ROCKET, TYPE_MULTIPLIER])
        powerup_multiplier = None
        powerup_duration = None

        if powerup_type == TYPE_MULTIPLIER:
            powerup_multiplier = self.difficulty_manager.get_powerup_params()
            powerup_duration = self.difficulty_manager.get_powerup_params()

        powerup = Powerup(self.canvas, powerup_x, y_position, powerup_type, powerup_multiplier, powerup_duration)
        self.powerups.append(powerup)


    def update(self, player, score_manager, diff_time):

        # Removes powerups that are collected by the player
        for powerup in self.powerups:
            if powerup.check_collision():
                powerup.is_collected = True
                powerup.cleanup()

        # Removes powerups that are below camera bounds
        cleanup_bottom = player.height + 300
        tmp_powerup = []
        for powerup in self.powerups:
            if powerup.y < cleanup_bottom:
                tmp_powerup.append(powerup)

        self.powerups = tmp_powerup


    def register_callback(self, event_type, callback):
        """Register a callback for specific events"""

        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def trigger_callbacks(self, event_type, *args):
        """Trigger all callbacks registered for an event"""

        for callback in self.callbacks[event_type]:
            callback(*args)