"""This module handles the SaveManager class for the game

This class handles all the save and loading functionality
by saving all relevant game data in pickle files, and then
loading them back into a new game when a load game is picked
"""

# Standard library imports
import os
import pickle
import time
from datetime import datetime

# Local application imports
from classes.scores import Boost
from classes.platform_class import Platform
from classes.powerups import Powerup
from constants import WINDOW_HEIGHT


class SaveManager:
    """Manages save and load functionality
    - Pickles relevant data on save
    - Unpickles on load
    - Displays basic save info for UI
    
    Attributes:
        game (tk.Tk): Game instance for data collection
        folder (str): Folder name to save files into
        max_slots (int): Maximum number of save slots available
        available_slots (int): Number of unoccupied save slots
    """

    def __init__(self, game):
        """Creates SaveManager instance on game launch
        
        Args:
            game (tk.Tk): Game instance for data collection
        """
        self.game = game
        self.folder = "saves"
        self.max_slots = 5
        self.available_slots = self.max_slots

        # Create saves folder if it doesn't exist
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def save_game(self, slot_number):
        """Saves a game into a slot number
        
        This method saves
        - Player data
        - Platform data
        - Score and difficulty data
        - Camera data
        - Boost and powerup data
        - Game controls data
        - Save time for powerup and boost duration
        
        Args:
            slot_number (int): Save slot number to save data into

        Returns:
            bool: True if data is successfully saved, False otherwise
        """
        try:
            current_time = time.time()
            save_data = {
                'save_date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

                # Player data
                'player' : {
                    'x': self.game.player.x,
                    'y': self.game.player.y,
                    'x_velocity': self.game.player.x_velocity,
                    'y_velocity': self.game.player.y_velocity,
                    'is_jumping': self.game.player.is_jumping,
                    'is_on_ground': self.game.player.is_on_ground,
                    'double_jump_enabled': self.game.player.double_jump_enabled,
                    'is_on_second_jump': self.game.player.is_on_second_jump,
                    'boost_multipliers': self.game.player.boost_multipliers,
                    'color': self.game.player.color,
                    'face': self.game.player.face,
                    'moving_left': self.game.player.moving_left,
                    'moving_right': self.game.player.moving_right
                },
                
                # Scores and difficulty data
                'score': self.game.score_manager.get_score(),
                'difficulty_level': self.game.difficulty_manager.difficulty_level,
                'difficulty_factor': self.game.difficulty_manager.difficulty_factor,
                'height': self.game.score_manager.highest_height,
                'multiplier': self.game.score_manager.multiplier,
                'multiplier_remaining_time': (
                    self.game.score_manager.multiplier_end_time - current_time
                    ) if self.game.score_manager.multiplier_end_time else 0,

                # Camera position
                'camera_y': self.game.camera.y,

                # Controls
                'movement_var': self.game.movement_var.get(),
                'space_var': self.game.space_var.get(),

                # Platform data
                'platforms' : [],

                # Active boosts data
                'active_boosts': {},

                # Powerups data
                'powerups': []
            }

            # Get individual platform data
            for platform in self.game.platform_manager.get_platforms():
                platform_data = {
                    'x': platform.x,
                    'y': platform.y,
                    'type': platform.type,
                    'width': platform.width,
                    'velocity': platform.velocity,
                    'is_active': platform.is_active
                }
                save_data['platforms'].append(platform_data)

            # Get individual boost data
            for boost_type, boost in self.game.score_manager.active_boosts.items():
                save_data['active_boosts'][boost_type] = {
                    'type': boost.type,
                    'multiplier': boost.multiplier,
                    'elapsed_time': current_time - boost.start_time,
                    'duration': boost.duration,
                    'is_active': boost.is_active
                }

            # Get individual powerup data
            for powerup in self.game.powerup_manager.powerups:
                powerup_data = {
                    'x': powerup.x,
                    'y': powerup.y,
                    'type': powerup.type,
                    'multiplier': powerup.multiplier,
                    'duration': powerup.duration
                }
                save_data['powerups'].append(powerup_data)

            # Save to file
            save_path = os.path.join(self.folder, f"save{slot_number}.pkl")
            with open(save_path, 'wb') as file:
                pickle.dump(save_data, file)

            return True
        
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, slot_number):
        """Loads game state from specified slot
        
        This method restores all the saved data into a
        new game
        
        Args:
            slot_number (int): Save slot number to get data from
            
        Returns:
            bool: True if data is successfully loaded, False otherwise
        """
        save_path = os.path.join(self.folder, f"save{slot_number}.pkl")
        
        try:
            # Load save file
            with open(save_path, 'rb') as file:
                save_data = pickle.load(file)
                
            current_time = time.time()
            
            # Restore player state
            player_data = save_data['player']
            self.game.player.x = player_data['x']
            self.game.player.y = player_data['y']
            self.game.player.x_velocity = player_data['x_velocity']
            self.game.player.y_velocity = player_data['y_velocity']
            self.game.player.color = player_data['color']
            self.game.player.face = player_data['face']
            self.game.player.is_jumping = player_data['is_jumping']
            self.game.player.is_on_ground = player_data['is_on_ground']
            self.game.player.double_jump_enabled = player_data['double_jump_enabled']
            self.game.player.boost_multipliers = player_data['boost_multipliers']
            self.game.player.is_on_second_jump = player_data['is_on_second_jump']
            self.game.player.moving_left = player_data['moving_left']
            self.game.player.moving_right = player_data['moving_right']
            
            # Restore score manager state
            self.game.score_manager.score = save_data['score']
            self.game.score_manager.highest_height = save_data['height']
            self.game.score_manager.multiplier = save_data['multiplier']
            
            # Restore multiplier timing if it exists
            if save_data['multiplier_remaining_time'] is not None:
                self.game.score_manager.multiplier_end_time = (
                    current_time + save_data['multiplier_remaining_time']
                    )
            else:
                self.game.score_manager.multiplier_end_time = None
                
            # Clear and restore active boosts
            self.game.score_manager.active_boosts.clear()
            for boost_type, boost_data in save_data['active_boosts'].items():
                new_boost = Boost(
                    boost_type=boost_data['type'],
                    multiplier=boost_data['multiplier'],
                    duration=boost_data['duration']
                )
                new_boost.is_active = boost_data['is_active']

                # Calculate new start_time based on remaining time and add offset
                new_boost.start_time = current_time - boost_data['elapsed_time'] + 3
                self.game.score_manager.active_boosts[boost_type] = new_boost
                
            # Restore difficulty state
            self.game.difficulty_manager.difficulty_level = save_data['difficulty_level']
            self.game.difficulty_manager.difficulty_factor = save_data['difficulty_factor']
            self.game.difficulty_manager.update_platform_params()
            
            # Restore camera position
            self.game.camera.y = save_data['camera_y']

            # Restore movement settings
            self.game.movement_var.set(save_data['movement_var'])
            self.game.space_var.set(save_data['space_var'])
            
            # Clear and restore platforms
            self.game.platform_manager.platforms.clear()
            for platform_data in save_data['platforms']:
                platform = Platform(
                    self.game.canvas,
                    platform_data['x'],
                    platform_data['y'],
                    platform_data['type'],
                    platform_data['width']
                )
                platform.velocity = platform_data['velocity']
                platform.is_active = platform_data['is_active']
                self.game.platform_manager.platforms.append(platform)

            # Clear and restore powerups
            self.game.powerup_manager.powerups.clear()
            for powerup_data in save_data['powerups']:
                powerup = Powerup(
                    self.game.canvas,
                    powerup_data['x'],
                    powerup_data['y'],
                    powerup_data['type'],
                    powerup_data['multiplier'],
                    powerup_data['duration']
                )
                self.game.powerup_manager.powerups.append(powerup)
                
            return True
            
        except Exception as e:
            print(f"Error loading save file: {e}")

            return False

    def get_save_info(self):
        """Returns basic information about all save slots for UI
        
        Returns:
            dict: Contains basic save info
        """
        saves_info = {}

        # Get all save file paths
        for slot in range(1, self.max_slots + 1):
            save_path = os.path.join(self.folder, f"save{slot}.pkl")

            if os.path.exists(save_path):
                try:
                    with open(save_path, "rb") as file:
                        save_data = pickle.load(file)

                        # Set default values if data doesn't exist
                        saves_info[slot] = {
                            'exists': True,
                            'date': save_data.get('save_date', 'Unknown'),
                            'score': int(save_data.get('score', 0)),
                            'height': abs(save_data.get('height', 0) - WINDOW_HEIGHT),
                            'color': save_data.get('player', {}).get('color', 'white'),
                            'face': save_data.get('player', {}).get('face', None)
                        }
                
                except (pickle.UnpicklingError, EOFError, KeyError):
                    # Handles corrupted save files
                    saves_info[slot] = {
                        'exists': True,
                        'date': 'Corrupted Save',
                        'score': 0,
                        'height': 0,
                        'color': "white",
                        'face': None
                    }
            else:
                # Slot is empty
                saves_info[slot] = {
                    'exists': False,
                    'date': None,
                    'score': None,
                    'height': None,
                    'color': None,
                    'face': None
                }

        return saves_info