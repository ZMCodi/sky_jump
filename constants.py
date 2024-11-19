"""Game constants and configuration values.

This module contains all constant values used throughout the game:
- Window and display settings
- Game state enums
- Physics parameters
- Player attributes
- Platform configurations
- Camera settings
- Powerup definitions

All values are in game units unless otherwise specified in the constant's
documentation.
"""

# Window configuration
WINDOW_WIDTH = 400 # pixels
WINDOW_HEIGHT = 800 # pixels
WINDOW_TITLE = "Sky Jump"
BG_COLOR = "lightblue"

# Frame rate settings
FPS = 60
FRAME_TIME = int(1000 / FPS) # miliseconds
FRAME_TIME_SECONDS = FRAME_TIME / 1000 # seconds

# Game states
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing" 
GAME_STATE_PAUSED = "paused"
GAME_STATE_GAME_OVER = "game_over"
GAME_STATE_LEADERBOARD = "leaderboard"
GAME_STATE_SETTINGS = "settings"
GAME_STATE_LOAD = "load"

# Physics constants
MOVE_SPEED = 300.0 # pixels per second
JUMP_FORCE = -350.0 # pixels per second (negative for upwards direction)
GRAVITY = 10.0 # pixels per second squared

# Derived physics values
JUMP_FORCE_PER_FRAME = JUMP_FORCE * FRAME_TIME_SECONDS
GRAVITY_PER_FRAME = GRAVITY * FRAME_TIME_SECONDS
MAX_JUMP_HEIGHT = (abs(JUMP_FORCE_PER_FRAME ** 2)) / (2 * GRAVITY_PER_FRAME)

# Camera settings
SCREEN_BOTTOM = 0.2 # percentage of screen height

# Player dimensions
PLAYER_WIDTH = 40 # pixels
PLAYER_HEIGHT = 40 # pixels

# Platform configurations
TYPE_NORMAL = "normal"  # Static platform
TYPE_MOVING = "moving"  # Horizontally moving platform
TYPE_BREAKING = "breaking"  # Platform that breaks after landing
TYPE_WRAPPING = "wrapping"  # Platform that wraps around screen edges
BREAK_TIMER = 0.1  # seconds before breaking platform disappears

# Powerup types
TYPE_ROCKET = "rocket"  # Vertical boost powerup
TYPE_MULTIPLIER = "multiplier"  # Score multiplier powerup