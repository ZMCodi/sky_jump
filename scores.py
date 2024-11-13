from constants import *

class ScoreManager:
    """
    Manages player score based on height in game
    """

    # Class constants
    SCORE_THRESHOLD = 1000

    def __init__(self):
        """Initialize scoring attributes"""

        self.score = 0
        self.highest_height = WINDOW_HEIGHT
        self.last_milestone = 0

    def update(self, player_height):
        """Updates score based on player height"""
        
        # Don't update if current height is lower than max height
        if player_height > self.highest_height:
            return
        
        self.highest_height = player_height
        relative_height = abs(self.highest_height - WINDOW_HEIGHT)

        # Add point everytime player passes SCORE_THRESHOLD
        if relative_height > (self.score + 1) * self.SCORE_THRESHOLD:
            self.score += 1

    def get_score(self):
        """Calculate and returns current score"""

        return self.score
    
    def reset(self):
        """Reset scoring system"""

        pass