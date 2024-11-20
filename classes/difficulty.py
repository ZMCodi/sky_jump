"""This module handles the difficulty manager that makes the game
more challenging as the player accumulates score

This provides a balanced gameplay for beginners and advanced players"""

from random import choices as randw
from constants import (
    # Player constants
    PLAYER_WIDTH, MAX_JUMP_HEIGHT,
    # Platform types
    TYPE_NORMAL,
    TYPE_MOVING,
    TYPE_WRAPPING,
    TYPE_BREAKING
)


class DifficultyManager:
    """
    Manages game difficulty as player progresses through game
    - Increases platform spacing
    - Decreases platform width
    - Reallocate platform type distribution
    
    Attributes:
        current_score (int): Current player score
        difficulty_level (int): Current difficulty level
        difficulty_factor (float): Takes values between 0 and 1 which determines 
            platform and powerup generation based on difficulty_level

    Constants:
        DIFFICULTY_THRESHOLD (int): Number of levels the player gets 
            for difficulty factor to increase
        MAX_DIFFICULTY_FACTOR (float): Highest difficulty a player can get
        FACTOR_INCREMENT (float): How much the difficulty factor increments every time
            it increases
        MAX_DIFFICULTY_LEVEL (int): How many levels of difficulty there are
            based on MAX_DIFFICULTY_FACTOR and FACTOR_INCREMENT
    """
    # Class constants
    DIFFICULTY_THRESHOLD = 10
    MAX_DIFFICULTY_FACTOR = 1.0
    FACTOR_INCREMENT = 0.2
    MAX_DIFFICULTY_LEVEL = MAX_DIFFICULTY_FACTOR / FACTOR_INCREMENT

    def __init__(self):
        """Creates the difficulty manager object and initializes parameters"""
        # Callbacks for PlatformManager to update generation parameters
        self.callbacks = {
            'on_param_update': []
        }

        self.current_score = 0
        self.difficulty_level = 0
        self.difficulty_factor = 0.0
        self.update_platform_params()
        
    def update_platform_params(self):
        """Updates platform parameters based on current difficulty
        - Platform width range gets smaller and shorter
        - Platform spacing gets smaller so platforms generate higher
        - Platform types get distributed so more challenging types generate more
        """
        self.platform_params = {
            'width_range': (
                (1.7 - self.difficulty_factor) * PLAYER_WIDTH,
                (2 - self.difficulty_factor) * PLAYER_WIDTH),
            # Ensure spacing range stay between 0.7 to 1.0 MAX_JUMP_HEIGHT
            'spacing_range': (
                min(0.4 + self.difficulty_factor, 0.7) * MAX_JUMP_HEIGHT,
                min(0.6 + self.difficulty_factor, 1) * MAX_JUMP_HEIGHT),
            'type_weights': self.calculate_type_weights()
        }

        self.trigger_callbacks('on_param_update', self.platform_params)

    def calculate_type_weights(self):
        """Calculate weight distributions for each platform type
        - Normal platforms get more scarce
        - Other platforms generate more frequently
        
        Returns:
            type_weights (dict): Individual weights for each platform type
            """
        return {
                TYPE_NORMAL: max(0.3, 1.0 - self.difficulty_factor),
                TYPE_MOVING: min(0.4, 0.4 * self.difficulty_factor),
                TYPE_WRAPPING: min(0.4, 0.4 * self.difficulty_factor),
                TYPE_BREAKING: min(0.2, 0.2 * self.difficulty_factor)
            }

    def update_difficulty(self, score):
        """Updates difficulty level and factor based on score
        
        - Difficulty level increases when player score passes DIFFICULTY_THRESHOLD
        - Difficulty factor increases
        - Platform generation parameters update every time difficulty factor increases
        """
        # Skips if player hasnt passed difficulty threshold
        if score < self.DIFFICULTY_THRESHOLD:
            return
        
        old_difficulty_level = self.difficulty_level
        self.difficulty_level = min(score // self.DIFFICULTY_THRESHOLD, 
                                    self.MAX_DIFFICULTY_LEVEL)

        # Increase difficulty factor and calculate new platform parameters if difficulty level increases
        if old_difficulty_level != self.difficulty_level:
            self.difficulty_factor = min(self.difficulty_factor + self.FACTOR_INCREMENT, 
                                         self.MAX_DIFFICULTY_FACTOR)
            self.update_platform_params()

    def get_platform_params(self):
        """Returns platform parameters for platform generation
        
        Returns:
            dict: Platform width and spacing range and type weights
            """
        return self.platform_params
    
    def calculate_platform_type(self):
        """Determines platform type based on type weights
        
        Returns:
            str: Platform type chosen randomly based on calculated weights
        """
        weights = self.calculate_type_weights()
        return randw(list(weights.keys()), list(weights.values()))[0]

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

    def reset(self):
        """Reset difficulty when player dies
        
            Ensures new games start easy and gets progressively harder
        """
        self.current_score = 0
        self.difficulty_factor = 0.0
        self.difficulty_level = 0
        self.update_platform_params()