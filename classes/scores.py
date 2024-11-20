"""This module handles the ScoreManager and Boost class

The ScoreManager calculates the player's highest height,
score, boosts and display info during the game. Boosts
give player movement boosts when they pass a certain
score threshold
"""

import time
from random import choice as rand, uniform as randf
from constants import PLAYER_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT


class ScoreManager:
    """
    Manages player score and boosts based on height in game

    Attributes:
        score (float): Player score as the game progresses
        highest_height (float): Keeps track of player highest height for scoring
        last_milestone (int): Player last score
        active_boosts (dict): Stores all active boosts on player
        multiplier (float): Score multiplier which changes if player
            picks up a multiplier powerup
        multiplier_end_time (time.time): time when multiplier ends and resets to 1.0
        callbacks (dict): Informs listeners of boost and boost expiry

    Constants:
        SCORE_THRESHOLD (float): Height threshold that player has to pass to get
            one point of score
        BOOST_THRESHOLD (int): Score threshold that player has to pass to get a boost
        BOOST_TYPES (dict): Contains boost types and their multipliers
        BOOST_DURATION_RANGE (tuple): Range for boost duration in seconds
        SCORE_TEXT_POS (tuple): Score text position in game (upper left)
        BOOST_TEXT_POS (tuple): Boost text position in game (upper right)
    """
    # Class constants
    SCORE_THRESHOLD = 100 # pixels
    BOOST_THRESHOLD = 10 # scores
    BOOSTS_TYPES = {
        'speed': {'multiplier': 1.2},
        'jump': {'multiplier': 1.2},
        'gravity': {'multiplier': 0.8}
    }
    BOOST_DURATION_RANGE = (25, 45)

    # Text display constants
    SCORE_TEXT_POS = (10, 10)
    BOOST_TEXT_POS = (WINDOW_WIDTH - 10, 10)

    def __init__(self):
        """Initialize ScoreManager object to track player score and boosts"""
        self.score = 0.0
        self.highest_height = WINDOW_HEIGHT
        self.last_milestone = 0
        self.active_boosts = {}
        self.multiplier = 1.0
        self.multiplier_end_time = None
        self.callbacks = {
            'on_boost': [],
            'on_boost_expire': [],
        }

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

    def update(self, player_height):
        """Updates score based on player height
        - Update highest height
        - Add score if player passed SCORE_THRESHOLD
        - Award boost if player passed BOOST_THRESHOLD

        Args:
            player_height (float): Player height in game
        
        Returns:
            float: Current player score
        """
        old_score = self.score

        # Don't update if current height is lower than max height
        if player_height + PLAYER_HEIGHT > self.highest_height:
            return self.score
        
        self.highest_height = player_height + PLAYER_HEIGHT
        relative_height = abs(self.highest_height - WINDOW_HEIGHT)

        # Add point everytime player passes SCORE_THRESHOLD
        if relative_height > (self.score + 1) * self.SCORE_THRESHOLD:
            self.score += 1 * self.multiplier

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
            
        # Check if multiplier has expired
        if self.multiplier_end_time and time.time() >= self.multiplier_end_time:
            self.multiplier = 1.0
            self.multiplier_end_time = None

        return self.score

    def trigger_boost_reward(self):
        """Gives a random boost to player
        
        - Ensures no same boost is given twice
        - Get boost parameters
        - Create boost
        """
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
        boost_duration = randf(*self.BOOST_DURATION_RANGE)
        boost_multiplier = self.BOOSTS_TYPES[boost_type]['multiplier']
        
        # Create boost object
        boost = Boost(boost_type, boost_multiplier, boost_duration)
        self.active_boosts[boost_type] = boost

        self.trigger_callbacks('on_boost', boost)
    
    def get_score(self):
        """Calculate and returns current score
        
        Returns:
            float: Current player score
        """
        return self.score
    
    def get_boost_display(self):
        """Returns formatted boost display information
        
        Returns:
            None: If there are no active boosts
            dict: Contains boost text info if there are active boosts
        """
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
    
    def activate_multiplier(self, multiplier, duration):
        """Activates score multiplier when player picks up multiplier powerup
        
        Args:
            multiplier (float): New mutliplier from multiplier powerup
            duration (float): Time in seconds until powerup expires
        """
        self.multiplier = multiplier
        self.multiplier_end_time = time.time() + duration

    def get_display_text(self):
        """Returns formatted score and height display text
        
        Returns:
            dict: Contains score and boost text info
        """
        relative_height = abs(self.highest_height - WINDOW_HEIGHT)
        next_milestone = (self.score + 1) * self.SCORE_THRESHOLD

        return {
            'score_info': {
                'text': f"Height: {int(relative_height)} m\n"
                        f"Score: {int(self.score)} Multiplier: {self.multiplier:.1f}X\n"
                        f"Next milestone in: {int(next_milestone - relative_height)} m",
                'pos': self.SCORE_TEXT_POS,
                'color': "black",
                'font': ("Arial Bold", 12)
            },
            'boost_info': self.get_boost_display()
        }
    
    def reset(self):
        """Resets score manager upon player death"""
        self.score = 0
        self.highest_height = WINDOW_HEIGHT
        self.last_milestone = 0
        self.active_boosts = {}
        self.multiplier = 1.0
        self.multiplier_end_time = None


class Boost:
    """
    Represents a temporary player boost
    
    Attributes:
        type (str): type of boost the player gets
        multiplier (float): boost multiplier for player movement
        start_time (time.time): current time when the boost activates
        duration (float): duration of the boost in seconds
        is_active (bool): True if boost is currently active
    """

    def __init__(self, boost_type, multiplier, duration):
        """Creates a player boost
        
        Args:
            boost_type (str): Represents boost type to create
            multiplier (float): Boost multiplier for player movement
            duration (float): Duration of boost in seconds
        """

        self.type = boost_type
        self.multiplier = multiplier
        self.start_time = time.time()
        self.duration = duration
        self.is_active = True

