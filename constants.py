# Window constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Sky Jump"
BG_COLOR = "lightblue"

# Game constants
FPS = 60
FRAME_TIME = int(1000 / FPS)
FRAME_TIME_SECONDS = FRAME_TIME / 1000

# Physics constants
MOVE_SPEED = 300.0
JUMP_FORCE = -350.0
GRAVITY = 10.0

# Temp values for boosts
TEMP_SPEED = MOVE_SPEED
TEMP_JUMP = JUMP_FORCE
TEMP_GRAV = GRAVITY

# Convert to correct units for calculations
JUMP_FORCE_PER_FRAME = JUMP_FORCE * FRAME_TIME_SECONDS
GRAVITY_PER_FRAME = GRAVITY * FRAME_TIME_SECONDS
MAX_JUMP_HEIGHT = (abs(JUMP_FORCE_PER_FRAME ** 2)) / (2 * GRAVITY_PER_FRAME)

# Camera constants
SCREEN_BOTTOM = 0.2

# Player constants
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40

# Platform types
TYPE_NORMAL = "normal"
TYPE_MOVING = "moving"
TYPE_BREAKING = "breaking"
TYPE_WRAPPING = "wrapping"
BREAK_TIMER = 0.1

# Powerup types
TYPE_ROCKET = "rocket"
TYPE_MULTIPLIER = "multiplier"