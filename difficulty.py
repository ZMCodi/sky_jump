from constants import *
from random import choice as rand, uniform as randf
from platform_class import Platform

class DifficutlyManager:
    """
    Manages game difficulty as player progresses through game
    
    Attributes:
        current_score (int): Current player score
        difficulty_level (int): Current difficulty level
        difficulty_factor (float): Takes values between 0 and 1 which determines platform and powerup generation based on difficulty_level
    """
    # Class constants
    DIFFICULTY_THRESHOLD = 10

    def __init__ (self):
        """Creates the difficulty manager object and initializes parameters"""
        self.current_score = 0
        self.difficulty_level = 0
        self.difficulty_factor = 0
        self.platform_params = {
            'width_range': ((1.5 - self.difficulty_factor) * PLAYER_WIDTH, (2 - self.difficulty_factor) * PLAYER_WIDTH),
            'speed_range': ((0.2 + self.difficulty_factor) * MOVE_SPEED, (1 + self.difficulty_factor) * MOVE_SPEED),
            'spacing_range': ((0.5 - self.difficulty_factor) * MAX_JUMP_HEIGHT, min(0.6 + self.difficulty_factor, 1) * MAX_JUMP_HEIGHT), # Ensures max spacing does not exceed max jump height
            'type_weights': {
                Platform.TYPE_NORMAL: 1.0,
                Platform.TYPE_MOVING: 0.0,
                Platform.TYPE_WRAPPING: 0.0,
                Platform.TYPE_BREAKING: 0.0
            }
        }

    def update_difficulty(self, score):
        """Updates difficulty level and factor based on score"""

        # Skips if player hasnt passed difficulty threshold
        if score < self.DIFFICULTY_THRESHOLD:
            return
        
        old_difficulty_level = self.difficulty_level
        
        self.difficulty_level = score // self.DIFFICULTY_THRESHOLD

        # Increase difficulty factor if difficulty level increases
        if old_difficulty_level != self.difficulty_level:
            self.difficulty_factor = min(self.difficulty_factor + 0.2, 1.0)

    def get_platform_params(self):
        """Returns platform parameters for platform generation"""

        return self.platform_params
    
    def calculate_platform_type(self):
        """Determines platform type based on current difficulty factor"""

        # TODO: implement
        pass



