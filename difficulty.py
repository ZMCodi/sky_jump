from constants import *
from random import choice as rand, uniform as randf, choices as randw

class DifficultyManager:
    """
    Manages game difficulty as player progresses through game
    
    Attributes:
        current_score (int): Current player score
        difficulty_level (int): Current difficulty level
        difficulty_factor (float): Takes values between 0 and 1 which determines platform and powerup generation based on difficulty_level
    """
    # Class constants
    DIFFICULTY_THRESHOLD = 10
    MAX_DIFFICULTY_FACTOR = 1.0
    FACTOR_INCREMENT = 0.2
    MAX_DIFFICULTY_LEVEL = MAX_DIFFICULTY_FACTOR / FACTOR_INCREMENT

    def __init__ (self):
        """Creates the difficulty manager object and initializes parameters"""
        
        self.callbacks = {
            'on_difficulty_change': [],
            'on_param_update': []
        }
        self.current_score = 0
        self.difficulty_level = 0
        self.difficulty_factor = 0.0
        self.update_platform_params()
        

    def update_platform_params(self):
        """Updates platform parameters based on current difficulty"""

        self.platform_params = {
            'width_range': (
                (1.7 - self.difficulty_factor) * PLAYER_WIDTH,
                (2 - self.difficulty_factor) * PLAYER_WIDTH),
            'speed_range': (
                (0.2 + self.difficulty_factor) * MOVE_SPEED, 
                (1 + self.difficulty_factor) * MOVE_SPEED),
            'spacing_range': (
                min(0.4 + self.difficulty_factor, 0.7) * MAX_JUMP_HEIGHT,
                min(0.6 + self.difficulty_factor, 1) * MAX_JUMP_HEIGHT), # Ensures max spacing does not exceed max jump height
            'type_weights': self.calculate_type_weights()
        }

        self.trigger_callbacks('on_param_update', self.platform_params)

    def calculate_type_weights(self):
        """Calculate weight distributions for each platform type"""

        return {
                TYPE_NORMAL: max(0.3, 1.0 - self.difficulty_factor),
                TYPE_MOVING: min(0.4, 0.4 * self.difficulty_factor),
                TYPE_WRAPPING: min(0.4, 0.4 * self.difficulty_factor),
                TYPE_BREAKING: min(0.2, 0.2 * self.difficulty_factor)
            }

    def update_difficulty(self, score):
        """Updates difficulty level and factor based on score"""

        # Skips if player hasnt passed difficulty threshold
        if score < self.DIFFICULTY_THRESHOLD:
            return
        
        old_difficulty_level = self.difficulty_level
        self.difficulty_level = min(score // self.DIFFICULTY_THRESHOLD, self.MAX_DIFFICULTY_LEVEL)

        # Increase difficulty factor and calculate new platform parameters if difficulty level increases
        if old_difficulty_level != self.difficulty_level:
            self.difficulty_factor = min(self.difficulty_factor + self.FACTOR_INCREMENT, self.MAX_DIFFICULTY_FACTOR)
            self.update_platform_params()
            self.trigger_callbacks('on_difficulty_change', self.difficulty_level, self.difficulty_factor)

    def get_platform_params(self):
        """Returns platform parameters for platform generation"""

        return self.platform_params
    
    def calculate_platform_type(self):
        """Determines platform type based on current difficulty factor"""

        weights = self.calculate_type_weights()
        
        return randw(list(weights.keys()), list(weights.values()))[0]

    def register_callback(self, event_type, callback):
        """Register a callback for specific events"""

        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def trigger_callbacks(self, event_type, *args):
        """Trigger all callbacks registered for an event"""

        for callback in self.callbacks[event_type]:
            callback(*args)

    def reset(self):
        """Reset difficulty when player dies"""

        self.current_score = 0
        self.difficulty_factor = 0.0
        self.difficulty_level = 0
        self.update_platform_params()
        self.trigger_callbacks('on_difficulty_change', 0, 0)
