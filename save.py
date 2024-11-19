import os
import pickle
from datetime import datetime
import time

class SaveManager:
    """Manages save and load functionality"""

    def __init__ (self, game):

        # Stores game instance to access all data that needs to be collected
        self.game = game
        self.folder = "saves"
        self.max_slots = 10
        self.available_slots = self.max_slots

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def save_game(self, slot_number):
        """Saves a game into a slot number"""
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
                'face': self.game.face,
                'moving_left': self.game.player.moving_left,
                'moving_right': self.game.player.moving_right
            },
            
            # Scores and difficulty data
            'score': self.game.score_manager.get_score(),
            'difficulty_level': self.game.difficulty_manager.difficulty_level,
            'difficulty_factor': self.game.difficulty_manager.difficulty_factor,
            'highest_height': self.game.score_manager.highest_height,
            'multiplier': self.game.score_manager.multiplier,
            'multiplier_remaining_time': (self.game.score_manager.multiplier_end_time - current_time)
                                            if self.game.score_manager.multiplier_end_time else 0,

            # Camera position
            'camera_y': self.game.camera.y,

            # Platform data
            'platforms' : [],

            # Active boosts
            'active_boosts': {}
        }

        for boost_type, boost in self.game.score_manager.active_boosts.items():
            save_data['active_boosts'][boost_type] = {
                'type': boost.type,
                'multiplier': boost.multiplier,
                'remaining_time': boost.duration - (current_time - boost.start_time),
                'duration': boost.duration,
                'is_active': boost.is_active
            }
        
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

        # Save to file
        save_path = os.path.join(self.folder, f"save{slot_number}.pkl")
        with open(save_path, 'wb') as file:
            pickle.dump(save_data, file)

    def load_game(self, slot_number):
        """Loads data from a save file into a game"""

        # Get player states and properties
        # Get platform states and properties
        # Get scores and difficulty
        pass

    def get_save_info(self):
        """Returns information about all save slots"""

        saves_info = {}
        
        for slot in range(1, self.max_slots + 1):
            save_path = os.path.join(self.folder, f"save{slot}.pkl")

            if os.path.exists(save_path):
                try:
                    with open(save_path, "rb") as file:
                        save_data = pickle.load(file)

                        saves_info[slot] = {
                            'exists': True,
                            'date': save_data.get('save_date', 'Unknown'),
                            'score': save_data.get('score', 0),
                            'height': save_data.get('height', 0)
                        }
                except (pickle.UnpicklingError, EOFError, KeyError):
                    # Handles corrupted save files
                    saves_info[slot] = {
                        'exists': True,
                        'date': 'Corrupted Save',
                        'score': 0,
                        'height': 0
                    }
            else:
                # Slot is empty
                saves_info[slot] = {
                    'exists': False,
                    'date': None,
                    'score': None,
                    'height': None
                }

        return saves_info