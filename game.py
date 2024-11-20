"""Infinite vertical platformer game made with Tkinter.

This game is an infinite vertical platformer where the player must jump
from platform to platform to gain height and score points. Features include:
- Multiple platform types with different behaviors
- Power-ups and score multipliers
- Difficulty progression
- Save/load functionality
- Leaderboard system
- Settings customization
"""

# Standard library imports
import time
import tkinter as tk

# Third party imports
from PIL import Image, ImageTk

# Local application imports
from constants import (
    # Window constants
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, BG_COLOR,
    # Game states
    GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_SETTINGS,
    GAME_STATE_LEADERBOARD, GAME_STATE_GAME_OVER, GAME_STATE_LOAD,
    GAME_STATE_PAUSED,
    # Platform types
    TYPE_MOVING, TYPE_WRAPPING,
    # Other constants
    PLAYER_HEIGHT, FRAME_TIME_SECONDS, FRAME_TIME
)
from classes.player_class import Player
from classes.platform_class import PlatformManager
from classes.camera_class import Camera
from classes.scores import ScoreManager
from classes.difficulty import DifficultyManager
from classes.powerups import PowerupManager
from classes.leaderboard import Leaderboard
from classes.menu import MainMenu, SettingsMenu, LoadGameMenu, PauseMenu, LeaderboardMenu
from classes.save import SaveManager


class Game(tk.Tk):
    """Main game application class managing the game window and overall game state.

    This class handles the core game functionality including:
    - Window and canvas setup
    - Game state management (menu, playing, paused)
    - Game loop control
    - User input handling
    - Component initialization and management

    Key Controls:
        Arrow Keys/WASD: Move player left/right and jump
        Space: Alternative jump key (configurable)
        Escape: Pause game
        Left Alt: Boss key
        Shift-D: Activate double jump (cheat)

    Attributes:
        canvas (tk.Canvas): Main game canvas where all game elements are drawn
        current_state (str): Current game state (menu/playing/paused/etc)
        game_loop_running (bool): Flag indicating if game loop is active
        player (Player): Main player object instance
    """

    def __init__(self):
        """Initialize game window, canvas and core game components.
        
        Initialization sequence:
        1. Set up main window and canvas
        2. Initialize menu system and UI components
        3. Set up game state variables
        4. Configure keyboard controls
        5. Set up player customization defaults
        
        Initial game state is set to GAME_STATE_MENU and shows the main menu.
        """
        super().__init__()

        # Configure window
        self.title(WINDOW_TITLE)
        self.resizable(False, False)

        # Center window on the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Create and configure canvas
        self.canvas = tk.Canvas(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            bg = BG_COLOR
        )

        self.canvas.pack()

        # Initialize menu system
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.leaderboard = Leaderboard(self.canvas)
        self.leaderboard_menu = LeaderboardMenu(self)
        self.load_menu = LoadGameMenu(self)
        self.save_manager = SaveManager(self)
        self.pause_menu = PauseMenu(self)
        
        # Game state variables
        self.current_state = GAME_STATE_MENU
        self.setup_state_variables()

        # Set up main menu and player selection
        self.settings_menu.load_face_images()
        self.show_menu()

        # Boss key variables
        self.boss_key_active = False
        self.boss_overlay = None
        self.previous_state = None
        self.load_boss_image()

        # Quits game cleanly when exit button is pressed
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Set up keyboard controls
        self.movement_var = tk.StringVar(self)
        self.movement_var.set("arrows")
        self.space_var = tk.BooleanVar(self)
        self.space_var.set(True)
        self.setup_controls()

        # Manages framerates between new games
        self.frame_accumulator = 0.0
        self.game_loop_id = None

        # Player selection variables
        self.player_color = "white"
        self.player_face = None

    def setup_state_variables(self):
        """Initializes variables needed for different states"""
        # Initialize menu and game loop
        self.menu_elements = None
        self.game_loop_running = False

        # Initialize player and camera
        self.player = None
        self.camera = None

        # Initialize managers
        self.platform_manager = None
        self.score_manager = None
        self.powerup_manager = None
        self.difficulty_manager = None

        # Initialize game related UI
        self.pause_elements = None
        self.game_over_screen = None

        # Initialize game elements
        self.last_update = None
        self.is_paused = False
        self.is_game_over = False

    def show_menu(self):
        """Display the main menu screen.
    
        Clears the canvas, sets the game state to menu, and displays
        the main menu elements including:
        - Game title
        - Play button
        - Settings button
        - Leaderboard button
        - Load game button
        - Controls hint
        """
        self.canvas.delete('all')
        self.current_state = GAME_STATE_MENU
        self.main_menu.show()

    def show_settings_screen(self):
        """Shows settings screen when settings button is pressed
        
            Settings menu handles key binding configurations
            and player customisation
        """
        self.canvas.delete('all')
        self.current_state = GAME_STATE_SETTINGS
        self.settings_menu.show() 

    def show_leaderboard_screen(self):
        """Shows the leaderboard screen when leaderboard button is pressed
        
            Leaderboard shows top 10 scores locally
        """
        self.canvas.delete('all')
        self.current_state = GAME_STATE_LEADERBOARD
        self.leaderboard_menu.show()    

    def show_load_screen(self):
        """Shows the load game screen when load game button is pressed
        
            The screen shows the date of save, score, height and the player
            character the player used during the save.
        """
        self.canvas.delete('all')
        self.current_state = GAME_STATE_LOAD
        self.load_menu.show()

    def handle_load_game(self, slot_number):
        """
        Called when a save slot is selected in load game screen

        - Creates a new game and change all the game properties to match the saved game
        
        Args:
            slot_number (int): Save slot to load

        Returns:
            True if game is loaded succesfully
            False otherwise
        """
        # Stop any existing game loop
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
            
        # Reset game state
        self.frame_accumulator = 0.0
        self.game_loop_running = False
        self.is_game_over = False
        self.is_paused = False
        self.current_state = GAME_STATE_PLAYING
        self.last_update = None

        # Initialize components
        if not self.player:
            self.player = Player(self.canvas, WINDOW_WIDTH // 2, WINDOW_HEIGHT - PLAYER_HEIGHT)
        else:
            self.player.reset()

        if not self.camera:
            self.camera = Camera()
        else:
            self.camera.reset()

        self.start_new_game()

        # Try to load the save
        if self.save_manager.load_game(slot_number):
            self.setup_controls()
            self.game_loop_running = True
            self.last_update = time.time()
            self.frame_accumulator = 0.0
            self.game_loop()
            return True
        else:
            print("Failed to load game")
            self.show_menu()
            return False

    def setup_controls(self):
        """Configure all game key bindings.
    
        Sets up keyboard controls for:
        - Player movement (arrows or WASD)
        - Jump controls (up/w/space based on settings)
        - Game controls (pause, boss key)
        - Cheat controls (double jump)
        
        Notes:
            Existing bindings are cleared before new ones are set to prevent
            duplicate bindings when controls are reconfigured.
        """
        # Essential controls
        self.bind('<Escape>', lambda e: self.pause() if self.current_state == GAME_STATE_PLAYING else None)
        self.bind('<Alt_L>', lambda e: self.activate_boss_key())
        
        # Game related controls should only bind if player object exists
        if self.player:
            # Unbind previous controls first
            self.unbind('<Left>')
            self.unbind('<Right>')
            self.unbind('<Up>')
            self.unbind('<KeyRelease-Left>')
            self.unbind('<KeyRelease-Right>')
            self.unbind('<a>')
            self.unbind('<d>')
            self.unbind('<w>')
            self.unbind('<KeyRelease-a>')
            self.unbind('<KeyRelease-d>')
            self.unbind('<space>')
            
            # Bind new controls based on settings
            if self.movement_var.get() == "arrows":
                self.bind('<Left>', lambda e: self.player.start_move_left())
                self.bind('<Right>', lambda e: self.player.start_move_right())
                self.bind('<Up>', lambda e: self.player.jump() if not self.is_paused else None)
                self.bind('<KeyRelease-Left>', lambda e: self.player.stop_move_left())
                self.bind('<KeyRelease-Right>', lambda e: self.player.stop_move_right())
            else:
                self.bind('<a>', lambda e: self.player.start_move_left())
                self.bind('<d>', lambda e: self.player.start_move_right())
                self.bind('<w>', lambda e: self.player.jump() if not self.is_paused else None)
                self.bind('<KeyRelease-a>', lambda e: self.player.stop_move_left())
                self.bind('<KeyRelease-d>', lambda e: self.player.stop_move_right())

            # Bind space jump if enabled
            if self.space_var.get():
                self.bind('<space>', lambda e: self.player.jump() if not self.is_paused else None)

            # Always bind cheat code
            self.bind('<Shift-D>', lambda e: self.player.activate_double_jump())

    def load_boss_image(self):
        """Load and prepare boss image overlay
        
        Notes:
            Boss image must be named boss_image.jpeg and saved in root directory
        """
        try:
            image = Image.open("boss_image.jpeg")
            image = image.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.boss_image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Failed to load boss key image: {e}")
            self.boss_image = None

    def activate_boss_key(self):
        """Activates/deactivates boss key overlay
        
        Notes:
            Some states have to be managed uniquely (settings and game over)
            due to tkinter widgets showing up on the boss overlay
        """
        if not self.boss_key_active:
            # Store current state
            self.previous_state = self.current_state
            
            # Pause if game key is pressed mid-game
            if self.current_state == GAME_STATE_PLAYING and not self.is_paused:
                self.is_paused = True
            
            self.hide_current_state_elements()
            self.boss_key_active = True

            # Change to widgetless screen first for pause and game over
            if self.boss_image:
                if self.current_state == GAME_STATE_SETTINGS:
                    self.show_menu()
                
                if self.current_state == GAME_STATE_GAME_OVER:
                    self.show_final_leaderboard()

                self.boss_overlay = self.canvas.create_image(
                    0, 0,
                    image=self.boss_image,
                    anchor="nw",
                    tags="boss_overlay"
                )
                self.canvas.lift("boss_overlay")

                # Change window title to appear more convincing
                self.title("Teams")
        else:
            # Remove boss screen
            if self.boss_overlay:
                self.canvas.delete(self.boss_overlay)
                self.boss_overlay = None
            self.boss_key_active = False
            self.title(WINDOW_TITLE)
            
            # Restore previous state and handle pause
            if self.previous_state == GAME_STATE_PLAYING:
                self.current_state = GAME_STATE_PLAYING
                self.is_paused = True

                # Render the game canvas before showing pause menu
                self.render()
                self.show_pause_menu()
            
            # Go back to previous menu for special states
            elif self.previous_state == GAME_STATE_GAME_OVER:
                self.show_game_over_screen()
            elif self.previous_state == GAME_STATE_SETTINGS:
                self.show_settings_screen()
            else:
                # For other states like menu, just restore them
                self.show_state_elements(self.previous_state)

    def hide_current_state_elements(self):
        """Hides elements of current state for boss overlay"""
        if self.current_state == GAME_STATE_MENU:
            for element in self.main_menu.elements:
                self.canvas.delete(element)
        elif self.current_state == GAME_STATE_PLAYING:
            if self.pause_menu.elements:
                self.hide_pause_menu()
        elif self.current_state == GAME_STATE_PAUSED:
            self.hide_pause_menu()

    def show_state_elements(self, state):
        """Restores elements of the given state after boss overlay is destroyed"""
        if state == GAME_STATE_MENU:
            self.show_menu()
        elif state == GAME_STATE_PLAYING:
            # Don't resume game, show pause menu instead
            if self.is_paused:
                self.render() # Render game elements first
                self.show_pause_menu()
                self.current_state = GAME_STATE_PLAYING
        elif state == GAME_STATE_PAUSED:
            self.show_pause_menu()

    def pause(self):
        """Toggle the game's pause state.
    
        Switches between paused/unpaused states, shows/hides the pause menu,
        and handles time tracking for the game loop. Does nothing if the game
        is already over.
        
        Notes:
            When unpausing, the last_update time is reset to prevent large
            time jumps in the game loop.
        """
        # Cannot pause if game over
        if self.is_game_over:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.show_pause_menu()
        else:
            self.hide_pause_menu()
            self.last_update = time.time()  # Reset time when unpausing

    def show_pause_menu(self):
        """Shows pause menu elements
        
            These include
            - Current score
            - Leaderboard (top 5 only)
            - Resume button
            - Restart button
            - Main Menu button
        """
        self.pause_menu.show()        
        
    def hide_pause_menu(self):
        """Removes pause menu elements"""       
        self.pause_menu.cleanup()
        self.leaderboard.cleanup()

    def handle_save_game(self):
        """Show save slot interface from pause menu.
        
        Called when the save button is clicked in the pause menu.
        Only allows saving when the game is actively running 
        (GAME_STATE_PLAYING) to prevent saving in menus or 
        game over state.
        """
        # Only allow saving during gameplay
        if self.current_state == GAME_STATE_PLAYING:
            self.pause_menu.show_save_slots()

    def stop_game(self):
        """Stops the game loop and cleans up with proper timing reset"""
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
            
        # Reset game state variables
        self.frame_accumulator = 0.0
        self.game_loop_running = False
        self.current_state = GAME_STATE_MENU
        self.last_update = None
        self.cleanup_managers()
        self.show_menu()

    def initialize_managers(self):
        """Initialize all game managers and their interconnections.
        
        Creates and connects the following manager hierarchy:
        1. DifficultyManager - Controls game progression
        2. ScoreManager - Tracks score and manages boosts
        3. PlatformManager - Creates/updates platforms (depends on DifficultyManager)
        4. PowerupManager - Handles powerup spawning and collection
        
        Sets up callbacks for:
        - Score/boost management -> Player boost handling
        - Platform death detection -> Game over handling
        
        Notes:
            Managers must be initialized in this specific order due to
            dependencies between them (e.g., PlatformManager needs
            DifficultyManager for platform generation parameters).
        """
        # Create managers
        self.difficulty_manager = DifficultyManager()
        self.score_manager = ScoreManager()
        self.platform_manager = PlatformManager(self.canvas, self.difficulty_manager)
        self.powerup_manager = PowerupManager(self.canvas)

        # Sets up and manage score and boosts
        self.score_manager.register_callback('on_boost', self.player.handle_boost)
        self.score_manager.register_callback('on_boost_expire', self.player.handle_boost_expire)

        # Handles player death
        self.platform_manager.register_callback('on_death', self.handle_player_death)

    def cleanup_managers(self):
        """Clean up all existing manager objects
        
            This method is called when game is stopped so new games
            don't use previous managers

            Notes:
                score and difficulty managers don't need cleanups as they
                depend on player height and don't store any objects
        """
        # Only reset managers if they exist
        if self.platform_manager is not None:
            self.platform_manager.reset()

        if self.powerup_manager is not None:
            self.powerup_manager.reset()
            
        # Remove references to old managers
        self.difficulty_manager = None
        self.score_manager = None
        self.platform_manager = None
        self.powerup_manager = None
    
    def game_loop(self):
        """Main game loop that handles timing and state updates.
        
        This method implements a fixed time step game loop using an accumulator.
        It ensures that game physics and logic run at a consistent rate while
        allowing for variable rendering frame rate. The loop handles:
        - Game state checking and transitions
        - Time step accumulation for physics updates
        - Rendering updates
        - Game over state management
        
        The loop maintains timing using these key components:
        - frame_accumulator: Stores leftover time between physics updates
        - FRAME_TIME_SECONDS: Fixed time step for physics/logic updates
        - last_update: Tracks the last update time
        
        Notes:
            - Physics updates run at fixed intervals (FRAME_TIME_SECONDS)
            - Rendering occurs every frame regardless of physics updates
            - Loop automatically terminates on game over state
        """
        # Exit if game loop is not active
        if not self.game_loop_running:
            return
                
        current_time = time.time()
        
        if self.current_state == GAME_STATE_PLAYING:
            if not self.is_paused and not self.is_game_over:
                if self.last_update:
                    # Calculate time since last frame
                    diff_time = current_time - self.last_update
                    self.frame_accumulator += diff_time
                    
                    # Update physics in fixed time steps
                    while self.frame_accumulator >= FRAME_TIME_SECONDS:
                        self.update(FRAME_TIME_SECONDS)
                        self.frame_accumulator -= FRAME_TIME_SECONDS
                    
                # Render at whatever frame rate we're achieving
                self.render()
            elif self.is_game_over:
                # Cancel any pending game loop callbacks
                if self.game_loop_id:
                    self.after_cancel(self.game_loop_id)
                    self.game_loop_id = None
                if not self.game_over_screen:
                    self.show_game_over_screen()
                return
                        
        # Store current time for next frame's calculations
        self.last_update = current_time
        
        # Schedule next frame if game is still running
        if self.game_loop_running:
            self.game_loop_id = self.after(FRAME_TIME, self.game_loop)


    def update(self, diff_time):
        """Update all game states and handle game logic.
        
        The update sequence is:
        1. Update player physics and position
        2. Update camera to follow player
        3. Update score and difficulty based on height
        4. Update platform positions and states
        5. Update powerups and check collections
        6. Handle platform collisions
        7. Check for player death
        
        Args:
            diff_time (float): Time in seconds since the last update
        
        Notes:
            Platform collision handling includes special behavior for
            moving platforms, where the player's position is adjusted
            based on the platform's movement.
        """
        # Update player and camera first
        self.player.update(diff_time)
        self.camera.update(self.player)

        # Update managers
        score = self.score_manager.update(self.player.y)
        self.difficulty_manager.update_difficulty(score)
        self.platform_manager.update(self.player.y, diff_time)
        self.powerup_manager.update(self.player, self.score_manager)

        # Check player collision with platforms
        for platform in self.platform_manager.get_platforms():
            if platform.check_collision(self.player):
                self.player.y = platform.y - self.player.height
                self.player.y_velocity = 0
                self.player.is_jumping = False

                # Adjust player movement with moving platforms
                if platform.type in [TYPE_MOVING, TYPE_WRAPPING]:
                    platform_movement = platform.velocity * diff_time
                    self.player.x += platform_movement

        # Check if player died
        self.platform_manager.check_player_death(self.player)

    def render(self):
        """Draw all game elements on the canvas.
    
        Rendering is done in layers from back to front:
        1. Clear previous frame
        2. Draw ground (if visible)
        3. Draw platforms with camera offset
        4. Draw player character
            - Player rectangle
            - Face overlay (if selected)
        5. Draw powerups
        6. Draw UI elements
            - Score and height
            - Current rank
            - Active boost effects
        
        Notes:
            All game elements are rendered with camera offset to create
            scrolling effect, while UI elements are drawn at fixed positions.
        """
        # Clear canvas
        self.canvas.delete('all')

        # Render ground
        if self.player.y > 0:
            self.canvas.create_rectangle(
                0, WINDOW_HEIGHT - self.camera.y, WINDOW_WIDTH, WINDOW_HEIGHT + 150 - self.camera.y,
                fill="brown",
                tags="ground"
            )

        # Render platforms with camera offset
        for platform in self.platform_manager.get_platforms():
            platform.render(self.camera.y)

        # Render player with camera offset
        player_x1 = self.player.x
        player_y1 = self.player.y - self.camera.y
        player_x2 = player_x1 + self.player.width
        player_y2 = player_y1 + self.player.height

        # Create player
        self.canvas_object = self.canvas.create_rectangle(
            player_x1, player_y1, player_x2, player_y2,
            fill = self.player.color,
            outline = "grey",
            tags = "player"
        )

        # Render player face overlay if selected
        if self.player.face and self.player.face != "None":
            self.canvas.create_image(
                player_x1, player_y1,
                image=self.settings_menu.face_images[self.player.face],
                anchor="nw",
                tags="player_face"
            )

        # Render powerups with camera offset
        self.powerup_manager.render(self.camera.y)

        # Add display text
        display_info = self.score_manager.get_display_text()
        score_info = display_info['score_info']
        self.canvas.create_text(
            score_info['pos'][0], score_info['pos'][1],
            text=score_info['text'],
            anchor="nw",
            fill=score_info['color'],
            font=score_info['font']
        )

        self.canvas.create_text(
            10, 80,
            text=f"Current Rank: {self.leaderboard.get_rank(int(self.score_manager.get_score()))}",
            anchor="nw",
            fill="black",
            font=("Arial Bold", 12)
        )

        boost_info = display_info['boost_info']
        if boost_info:
            self.canvas.create_text(
                boost_info['pos'][0], boost_info['pos'][1],
                text=boost_info['text'],
                anchor="ne",
                fill=boost_info['color'],
                font=boost_info['font']
            )

    def quit_game(self):
        """Exits game without throwing errors"""
        self.leaderboard.save_scores()
        self.destroy()

    def handle_player_death(self):
        """Stops game loop when player dies
        
        Notes:
            This method can be more useful for further implementation
            on player death (sound effects, etc.)
        """
        self.is_game_over = True

    def show_game_over_screen(self):
        """Shows game over screen elements on player death.
        
        If player achieved a high score:
        - Shows score entry form with tkinter Entry widget
        - Validates and processes player name input
        - Updates leaderboard with new score
        
        If not a high score:
        - Shows final leaderboard directly
        
        Note:
            This method creates tkinter widgets that need to be properly
            destroyed when transitioning to other screens.
        """
        # Cleans up existing game over screen
        if hasattr(self, 'game_over_screen') and self.game_over_screen:
            for element in self.game_over_screen:
                self.canvas.delete(element)
        self.game_over_screen = None

        self.current_state = GAME_STATE_GAME_OVER
        self.canvas.delete('all')
        self.game_over_screen = []
        final_score = int(self.score_manager.get_score())
        
        # Prompts user for name if final score makes the leaderboard
        if self.leaderboard.is_high_score(final_score):
            game_over_text = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3,
                text="GAME OVER",
                anchor="center",
                fill="red",
                font=("Arial Bold", 25)
            )
            self.game_over_screen.append(game_over_text)

            score_text = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 50,
                text=f"Final Score: {final_score}",
                anchor="center",
                fill="black",
                font=("Arial Bold", 15)
            )
            self.game_over_screen.append(score_text)

            name_label = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 40,
                text="New High Score! Enter your name:",
                anchor="center",
                fill="purple",
                font=("Arial Bold", 15)
            )
            self.game_over_screen.append(name_label)
            
            name_entry = tk.Entry(
                self,
                font=("Arial Bold", 12),
                width=15,
                justify='center'
            )

            name_window = self.canvas.create_window(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                window=name_entry
            )
            
            self.game_over_screen.append(name_window)

            # Error message text if name input is invalid
            error_text = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 25,
                text="",
                anchor="center",
                fill="red",
                font=("Arial Bold", 10)
            )
            self.game_over_screen.append(error_text)
            
            def submit_score():
                name = name_entry.get()
                if self.leaderboard.validate_name(name):
                    self.leaderboard.add_score(name, final_score)
                    self.leaderboard.save_scores()
                    name_entry.destroy()
                    submit_button.destroy()
                    self.canvas.delete('all')
                    self.show_final_leaderboard()
                else:
                    self.canvas.itemconfig(
                        error_text,
                        text="Name must be 1-10 alphanumeric characters"
                    )
            
            submit_button = tk.Button(
                self,
                text="Submit",
                command=submit_score,
                font=("Arial Bold", 12)
            )
            submit_window = self.canvas.create_window(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60,
                window=submit_button
            )

            self.game_over_screen.append(submit_window)

        # Just show leaderboard if score is too low
        else:
            self.leaderboard_menu.show_final()

    def show_final_leaderboard(self):
        """Shows final leaderboard after game over"""
        self.canvas.delete('all')
        self.leaderboard_menu.show_final()
        
    def start_new_game(self):
        """Starts a new game from any state with proper cleanup
        
            This method is called from the main menu, load game menu,
            restart button in pause menu and play again button in the
            game over screen
        """
        # Cancel any existing game loop
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        
        # Reset frame timing
        self.frame_accumulator = 0.0
        
        # Clean up canvas
        self.canvas.delete('all')
        
        # Change state
        self.current_state = GAME_STATE_PLAYING
        
        # Clear any existing menus/screens
        if hasattr(self, 'game_over_screen') and self.game_over_screen:
            for element in self.game_over_screen:
                self.canvas.delete(element)
            self.game_over_screen = None
        self.hide_pause_menu()
        
        # Initialize/reset components
        if not self.player:
            self.player = Player(self.canvas, WINDOW_WIDTH // 2, WINDOW_HEIGHT - PLAYER_HEIGHT)
            self.player.color = self.player_color
            self.player.face = self.player_face
        else:
            self.player.reset()
            self.player.color = self.player_color
            self.player.face = self.player_face
            
        if not self.camera:
            self.camera = Camera()
        else:
            self.camera.reset()
        
        # Clean up old managers and create new ones
        self.cleanup_managers()
        self.initialize_managers()
        
        # Reset game state flags
        self.is_game_over = False
        self.is_paused = False
        self.game_loop_running = True
        
        # Set up controls
        self.setup_controls()
        
        # Start fresh game loop
        self.last_update = time.time()
        self.game_loop()


if __name__ == "__main__":
    game = Game()
    game.mainloop()

