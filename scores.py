from constants import *
from random import choice as rand, uniform as randf
import time

class ScoreManager:
    """
    Manages player score based on height in game

    Attributes
        score (int): Player score as the game progresses
        highest_height (float): Keeps track of player highest height for scoring

    """

    # Class constants
    SCORE_THRESHOLD = 1000
    BOOST_THRESHOLD = 10
    BOOSTS = ['Increase jump', 'Increase speed', 'Low gravity']

    def __init__(self):
        """Initialize scoring attributes"""

        self.score = 0
        self.highest_height = WINDOW_HEIGHT
        self.last_milestone = 0
        self.callbacks = {}
        self.active_boosts = []

    def update(self, player_height):
        """Updates score based on player height"""
        
        old_score = self.score

        # Don't update if current height is lower than max height
        if player_height > self.highest_height:
            return
        
        self.highest_height = player_height
        relative_height = abs(self.highest_height - WINDOW_HEIGHT)

        # Add point everytime player passes SCORE_THRESHOLD
        if relative_height > (self.score + 1) * self.SCORE_THRESHOLD:
            self.score += 1

        # Award a boost if player passed BOOST_THRESHOLD
        if old_score // self.BOOST_THRESHOLD != self.score // self.BOOST_THRESHOLD:
            self.trigger_boost_reward()

    def trigger_boost_reward(self):
        """Gives a random boost to player"""

        # Choose random boost to be implemented for a certain timeframe
        boost = rand(self.BOOSTS)
        boost_time = randf(25, 45)
        
        if boost == 'Increase speed':
            MOVE_SPEED = 1.2 * MOVE_SPEED
        elif boost == 'Increase jump':
            JUMP_FORCE = 1.2 * JUMP_FORCE
        elif boost == 'Low gravity':
            GRAVITY = 0.8 * GRAVITY

        # TODO: schedule trigger_boost_expiry after boost_time seconds

    def trigger_boost_expiry(self):
        """Reverts boost effects after boost expires"""

        MOVE_SPEED = TEMP_SPEED
        JUMP_FORCE = TEMP_JUMP
        GRAVITY = TEMP_GRAV
    
    def get_score(self):
        """Calculate and returns current score"""

        return self.score
    
    def reset(self):
        """Reset scoring system"""

        pass

    def get_display_text(self):
        """Displays current height and score on canvas"""

        pass