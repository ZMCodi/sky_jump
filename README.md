# Sky Jump

A vertical platformer game built with Python and Tkinter where players jump between platforms to reach higher scores.

## Overview

Sky Jump is an infinite vertical platformer featuring:
- Multiple platform types (normal, moving, breaking, wrapping)
- Power-ups and score multipliers  
- Progressive difficulty scaling
- Save/load functionality
- Local leaderboard system
- Player customization

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Pillow (PIL) library

Install dependencies:
```bash
pip install Pillow
```

## Project Structure

```
sky_jump/
├── classes/
│   ├── camera_class.py      # Camera viewport management
│   ├── difficulty.py        # Dynamic difficulty scaling 
│   ├── leaderboard.py      # Score tracking and display
│   ├── menu.py            # Menu system and UI
│   ├── platform_class.py   # Platform types and behavior
│   ├── player_class.py    # Player movement and physics
│   ├── powerups.py       # Power-up system
│   ├── save.py          # Save/load game state
│   └── scores.py       # Score and boost management
├── player_faces/      # Player customization assets
├── powerup_icons/    # Power-up icon assets
├── constants.py     # Game configuration values
├── game.py         # Main game initialization
└── README.md      # This file
```

## Controls

Default controls can be customized in settings:
- Arrow Keys/WASD: Move left/right
- Up Arrow/W/Space: Jump
- ESC: Pause game
- Left Alt: Boss key
- Shift-D: Enable double jump (cheat)

## Game Features

### Platforms
- Normal (Blue): Static platforms
- Moving (Green): Move horizontally
- Breaking (Red): Break after landing
- Wrapping (Purple): Move horizontally and wrap around screen

### Power-ups
- Rocket: Vertical boost
- Multiplier: Temporary score multiplier

### Difficulty Progression
- Platform spacing increases
- Platform width decreases  
- More challenging platform types appear

### Save System
- 5 save slots available
- Saves player state, score, and game configuration
- Load games from main menu

### Customization  
- Control scheme selection
- Player color selection
- Custom face overlays

## Development Notes

### Constants
Key game parameters are defined in `constants.py`:
- Window dimensions
- Physics values  
- Game states
- Platform/power-up types

### Adding Features

#### New Platform Types
1. Add type constant in `constants.py`
2. Create platform class in `platform_class.py`
3. Add to type weights in `DifficultyManager`

#### New Power-ups  
1. Add type constant in `constants.py`
2. Add icon to `powerup_icons/`
3. Implement effect in `PowerupManager`

#### New Player faces
1. Add .png file to `player_faces`
2. Make sure picture is square to avoid distortion
