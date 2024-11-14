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
    SCORE_THRESHOLD = 300
    BOOST_THRESHOLD = 10
    BOOSTS_TYPES = {
        'speed': {'multiplier': 1.2},
        'jump': {'multiplier': 1.2},
        'gravity': {'multiplier': 0.8}
    }
    BOOST_DURATION_LOWER_RANGE = 25
    BOOST_DURATION_UPPER_RANGE = 45

    # Text display constants
    SCORE_TEXT_POS = (10, 10)
    BOOST_TEXT_POS = (WINDOW_WIDTH - 10, 10)

    def __init__(self):
        """Initialize scoring attributes"""

        self.score = 0
        self.highest_height = WINDOW_HEIGHT
        self.last_milestone = 0
        self.active_boosts = {}
        self.callbacks = {
            'on_boost': [],
            'on_boost_expire': [],
            'on_score': []
        }

    def register_callback(self, event_type, callback):
        """Register a callback for specific events"""

        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def trigger_callbacks(self, event_type, *args):
        """Trigger all callbacks registered for an event"""

        for callback in self.callbacks[event_type]:
            callback(*args)

    def update(self, player_height):
        """Updates score based on player height"""
        
        old_score = self.score

        # Don't update if current height is lower than max height
        if player_height + PLAYER_HEIGHT > self.highest_height:
            return self.score
        
        self.highest_height = player_height + PLAYER_HEIGHT
        relative_height = abs(self.highest_height - WINDOW_HEIGHT)

        # Add point everytime player passes SCORE_THRESHOLD
        if relative_height > (self.score + 1) * self.SCORE_THRESHOLD:
            self.score += 1

        # Award a boost if player passed BOOST_THRESHOLD
        if old_score // self.BOOST_THRESHOLD != self.score // self.BOOST_THRESHOLD:
            self.trigger_boost_reward()

        # Check for expired boosts
        current_time = time.time()
        expired_boosts = []

        for boost_type, boost in self.active_boosts.items():
            if current_time - boost.start_time >= boost.duration:
                expired_boosts.append(boost_type)
                boost.is_active = False
                self.trigger_callbacks('on_boost_expire', boost)

        # Remove expired boosts
        for boost_type in expired_boosts:
            del self.active_boosts[boost_type]

        return self.score

    def trigger_boost_reward(self):
        """Gives a random boost to player"""

        # Remove boosts that are already active
        available_boost = []
        for boost in self.BOOSTS_TYPES.keys():
            if boost not in self.active_boosts:
                available_boost.append(boost)

        # Terminates if all boosts are already active
        if not available_boost:
            return

        # Choose random boost to be implemented for a certain timeframe
        boost_type = rand(available_boost)
        boost_duration = randf(self.BOOST_DURATION_LOWER_RANGE, self.BOOST_DURATION_UPPER_RANGE)
        boost_multiplier = self.BOOSTS_TYPES[boost_type]['multiplier']
        
        # Create boost object
        boost = Boost(boost_type, boost_multiplier, boost_duration)
        self.active_boosts[boost_type] = boost

        # Notify listeners about new boost
        self.trigger_callbacks('on_boost', boost)
    
    def get_score(self):
        """Calculate and returns current score"""

        return self.score
    
    def get_boost_display(self):
        """Returns formatted boost display information"""

        if not self.active_boosts:
            return None
        
        # Format text for each active boost
        boost_text = ""
        current_time = time.time()

        for boost_type, boost in self.active_boosts.items():
            remaining_time = int(boost.duration - (current_time - boost.start_time))
            if remaining_time > 0:
                boost_name = boost_type.capitalize()
                boost_text += f"{boost_name} Boost: {remaining_time} s\n"

        if boost_text:
            return {
                'text': boost_text.strip(),
                'pos': self.BOOST_TEXT_POS,
                'color': "purple",
                'font': ("Arial Bold", 12)
            }

        return None

    def get_display_text(self):
        """Returns formatted score and height display text"""

        relative_height = abs(self.highest_height - WINDOW_HEIGHT)
        next_milestone = (self.score + 1) * self.SCORE_THRESHOLD

        return {
            'score_info': {
                'text': f"Height: {int(relative_height)} m\n"
                        f"Score: {self.score}\n"
                        f"Next milestone in: {int(next_milestone - relative_height)} m",
                'pos': self.SCORE_TEXT_POS,
                'color': "black",
                'font': ("Arial Bold", 12)
            },
            'boost_info': self.get_boost_display()
        }


class Boost:
    """
    Represents a temporary player boost
    
    Attributes:
        type (str): type of boost the player gets
        multiplier (float): 
        start_time (float): current time when the boost activates
        duration (int): duration of the boost in seconds
        is_active (bool): True if boost is currently active
    """

    def __init__ (self, boost_type, multiplier, duration):
        """Creates a player boost"""

        self.type = boost_type
        self.multiplier = multiplier
        self.start_time = time.time()
        self.duration = duration
        self.is_active = True

