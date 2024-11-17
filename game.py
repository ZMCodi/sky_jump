"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time
from random import randint as rand, uniform as randf, choice
from player_class import Player
from platform_class import PlatformManager
from camera_class import Camera
from scores import ScoreManager
from difficulty import DifficultyManager
from powerups import PowerupManager
from leaderboard import Leaderboard
from constants import *
from PIL import Image, ImageTk


class Game(tk.Tk):
    """
    Main game class that creates and sets up the game window, canvas and handle game loops

    Attributes:
        canvas (tk.Canvas): Main game canvas where game elements are drawn
    """
    def __init__(self):
        """Initialize game window and canvas"""
        super().__init__()

        # Configure window
        self.title(WINDOW_TITLE)
        self.resizable(False, False) # Maintain constant window dimension

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

        # Game state variables
        self.current_state = GAME_STATE_MENU
        self.game_components = None
        self.setup_state_variables()
        self.show_menu()

        # Boss key variables
        self.boss_key_active = False
        self.boss_overlay = None
        self.previous_state = None
        self.load_boss_image()

        # Quit game when exit button is pressed
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Set up keyboard controls
        self.setup_controls()

        self.leaderboard = Leaderboard(self.canvas)
        self.game_loop_running = False
        self.frame_accumulator = 0.0
        self.game_loop_id = None  # Track the game loop callback ID

    def create_menu_button(self, x, y, width, height, text, command):
        """Creates a custom menu button on the canvas"""
        
        # Button background
        button = self.canvas.create_rectangle(
            x - width/2, y - height/2,
            x + width/2, y + height/2,
            fill="#4a90e2",  # Nice blue color
            outline="#2171cd",
            width=2,
            tags=("button", f"button_{text.lower()}")
        )
        
        # Button text
        text_item = self.canvas.create_text(
            x, y,
            text=text,
            fill="white",
            font=("Arial Bold", 16),
            tags=("button_text", f"button_text_{text.lower()}")
        )
        
        # Bind hover effects
        def on_enter(e):
            self.canvas.itemconfig(button, fill="#2171cd")
        
        def on_leave(e):
            self.canvas.itemconfig(button, fill="#4a90e2")
        
        def on_click(e):
            command()
        
        # Bind events to both rectangle and text
        for item in (button, text_item):
            self.canvas.tag_bind(item, '<Enter>', on_enter)
            self.canvas.tag_bind(item, '<Leave>', on_leave)
            self.canvas.tag_bind(item, '<Button-1>', on_click)
        
        return button, text_item
    
    def show_menu(self):
        """Shows the main menu screen"""
        self.canvas.delete('all')
        self.menu_elements = []

        # Create semi-transparent dark overlay for better text readability
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='black', 
            stipple='gray50',
            tags='menu_overlay'
        )
        self.menu_elements.append(overlay)
        
        # Game title with shadow effect
        shadow = self.canvas.create_text(
            WINDOW_WIDTH/2 + 2, WINDOW_HEIGHT/4 + 2,
            text="SKY JUMP",
            fill="#1a1a1a",
            font=("Arial Bold", 48)
        )
        title = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/4,
            text="SKY JUMP",
            fill="#4a90e2",  # Matching blue color
            font=("Arial Bold", 48)
        )
        self.menu_elements.extend([shadow, title])
        
        # Add subtitle
        subtitle = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/4 + 50,
            text="Ready to reach new heights?",
            fill="white",
            font=("Arial", 16)
        )
        self.menu_elements.append(subtitle)
        
        # Button configuration
        button_width = 200
        button_height = 40
        button_y_start = WINDOW_HEIGHT/2
        button_spacing = 60
        
        # Create menu buttons
        play_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start,
            button_width,
            button_height,
            "PLAY",
            lambda: self.start_new_game()
        )
        
        leaderboard_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "LEADERBOARD",
            lambda: self.show_leaderboard_screen()
        )
        
        settings_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 2,
            button_width,
            button_height,
            "SETTINGS",
            lambda: self.show_settings_screen()
        )
        
        load_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 3,
            button_width,
            button_height,
            "LOAD GAME",
            lambda: self.show_load_screen()
        )
        
        # Add controls hint at bottom
        controls_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT - 40,
            text="Press 'B' for Boss Key  |  ESC for Pause",
            fill="white",
            font=("Arial", 12)
        )
        
        # Add all button elements to menu_elements list
        self.menu_elements.extend([*play_button, *leaderboard_button, 
                                *settings_button, *load_button, controls_text])

        # Add version number
        version = self.canvas.create_text(
            10, WINDOW_HEIGHT - 10,
            text="v1.0",
            anchor="sw",
            fill="white",
            font=("Arial", 10)
        )
        self.menu_elements.append(version)

        # For now, add placeholder handlers
        def show_leaderboard_screen():
            print("Leaderboard screen - Coming soon!")
            
        def show_settings_screen():
            print("Settings screen - Coming soon!")
            
        def show_load_screen():
            print("Load game screen - Coming soon!")

    def show_leaderboard_screen(self):
        """Shows the leaderboard screen"""
        self.canvas.delete('all')
        self.current_state = GAME_STATE_LEADERBOARD
        # Will implement this fully later
        self.leaderboard.leaderboard_screen(is_paused=False)
        
        # Add back button
        back_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 60,
            200, 40,
            "BACK TO MENU",
            lambda: self.show_menu()
        )
        self.menu_elements.extend(back_button)

    def show_settings_screen(self):
        """Shows the settings screen"""
        # Will implement this later
        pass

    def show_load_screen(self):
        """Shows the load game screen"""
        # Will implement this later
        pass


    def setup_state_variables(self):
        """Initializes variables needed for different states"""

        self.menu_elements = None
        self.player = None
        self.camera = None
        self.platform_manager = None
        self.score_manager = None
        self.powerup_manager = None
        self.difficulty_manager = None
        self.pause_elements = None
        self.game_over_screen = None
        
        # Other state tracking
        self.is_running = False
        self.last_update = None
        self.is_paused = False
        self.is_game_over = False

    def setup_controls(self):
        """Configure key bindings for player control"""
        # Only bind player controls if player exists
        def bind_player_controls():
            if self.player:
                self.bind('<Left>', lambda e: self.player.start_move_left())
                self.bind('<Right>', lambda e: self.player.start_move_right())
                self.bind('<space>', lambda e: self.player.jump() if not self.is_paused else None)
                self.bind('<KeyRelease-Left>', lambda e: self.player.stop_move_left())
                self.bind('<KeyRelease-Right>', lambda e: self.player.stop_move_right())
                self.bind('<Shift-D>', lambda e: self.player.activate_double_jump())
        
        # Always bind these controls
        self.bind('<Escape>', lambda e: self.pause() if self.current_state == GAME_STATE_PLAYING else None)
        self.bind('<b>', lambda e: self.activate_boss_key())
        
        bind_player_controls()


    def load_boss_image(self):
        """Load and prepare boss image overlay"""

        try:
            image = Image.open("boss_image.jpeg")
            image = image.resize((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.boss_image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Failed to load boss key image: {e}")
            self.boss_image = None

    def activate_boss_key(self):
        """Activates/deactivates boss key overlay"""
        if not self.boss_key_active:
            # Store current state
            self.previous_state = self.current_state
            
            # Hide current state elements
            self.hide_current_state_elements()
            
            # Show boss screen
            self.boss_key_active = True
            if self.boss_image:
                self.boss_overlay = self.canvas.create_image(
                    0, 0,
                    image=self.boss_image,
                    anchor="nw",
                    tags="boss_overlay"
                )
                self.title("Teams")
        else:
            # Remove boss screen
            if self.boss_overlay:
                self.canvas.delete(self.boss_overlay)
                self.boss_overlay = None
            self.boss_key_active = False
            self.title(WINDOW_TITLE)
            
            # Restore previous state
            self.show_state_elements(self.previous_state)

    def hide_current_state_elements(self):
        """Hides elements of current state"""

        if self.current_state == GAME_STATE_MENU:
            for element in self.menu_elements:
                self.canvas.delete(element)
        elif self.current_state == GAME_STATE_PLAYING:
            if not self.is_paused:
                self.is_paused = True
        elif self.current_state == GAME_STATE_PAUSED:
            self.hide_pause_menu()

    def show_state_elements(self, state):
        """Restores elements of the given state"""
        if state == GAME_STATE_MENU:
            self.show_menu()
        elif state == GAME_STATE_PLAYING:
            # Resume game if it was playing
            if self.is_paused:
                self.is_paused = False
                self.run()
        elif state == GAME_STATE_PAUSED:
            self.show_pause_menu()

    def pause(self):
        """Pauses and unpauses game"""
        if self.is_game_over:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.show_pause_menu()
        else:
            self.hide_pause_menu()
            self.last_update = time.time()  # Reset time when unpausing

    def show_pause_menu(self):
        """Shows pause menu elements"""
        # Initialize list to track pause elements
        self.pause_elements = []
        
        # Add semi-transparent overlay
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='black', 
            stipple='gray50',
            tags='pause_overlay'
        )
        self.pause_elements.append(overlay)
        
        # Pause title with shadow effect (matching main menu style)
        shadow = self.canvas.create_text(
            WINDOW_WIDTH/2 + 2, WINDOW_HEIGHT/8 + 2,  # Moved up to 1/8
            text="PAUSED",
            anchor="center",
            fill="#1a1a1a",
            font=("Arial Bold", 36)  # Slightly smaller font
        )
        title = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/8,  # Moved up to 1/8
            text="PAUSED",
            anchor="center",
            fill="#4a90e2",
            font=("Arial Bold", 36)  # Slightly smaller font
        )
        self.pause_elements.extend([shadow, title])
        
        # Score display - moved closer to title
        score_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/8 + 35,  # Closer to title
            text=f"Current Score: {int(self.score_manager.get_score())}",
            anchor="center",
            fill="white",
            font=("Arial Bold", 15)
        )
        self.pause_elements.append(score_text)
        
        # Show leaderboard with top 5 scores - positioned closer to title
        self.leaderboard.leaderboard_screen(is_paused=True)
        
        # Button configuration (smaller size and adjusted position)
        button_width = 160
        button_height = 35
        button_y_start = WINDOW_HEIGHT * 0.65  # Moved up from 0.75
        button_spacing = 42  # Slightly reduced spacing
        
        # Create buttons using custom menu button style
        resume_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start,
            button_width,
            button_height,
            "RESUME",
            lambda: self.pause()
        )
        
        restart_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "RESTART",
            lambda: self.start_new_game()
        )
        
        menu_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 2,
            button_width,
            button_height,
            "MAIN MENU",
            lambda: self.stop_game()
        )
        
        # Add all button elements to pause_elements list
        self.pause_elements.extend([*resume_button, *restart_button, *menu_button])
        
        # Add controls reminder at bottom
        controls_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT - 20,
            text="Press ESC to Resume  |  B for Boss Key",
            fill="white",
            font=("Arial", 12)
        )
        self.pause_elements.append(controls_text)

    def hide_pause_menu(self):
        """Removes pause menu elements"""
        if self.pause_elements:
            for element in self.pause_elements:
                self.canvas.delete(element)
            self.pause_elements = None
        self.leaderboard.cleanup()

    def stop_game(self):
        """Stops the game loop and cleans up with proper timing reset"""
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
            
        self.frame_accumulator = 0.0
        self.game_loop_running = False
        self.is_running = False
        self.current_state = GAME_STATE_MENU
        self.last_update = None
        self.cleanup_managers()
        self.show_menu()

    def initialize_managers(self):
        """Initialize all game managers and their connections"""
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
        """Clean up all existing manager objects"""
        # Only reset managers if they exist
        if self.platform_manager is not None:
            self.platform_manager.reset()

        if self.powerup_manager is not None:
            self.powerup_manager.reset()
        
        if self.score_manager is not None:
            # If you have any cleanup needed for score manager
            pass

        if self.difficulty_manager is not None:
            # If you have any cleanup needed for difficulty manager
            pass
            
        # Remove references to old managers
        self.difficulty_manager = None
        self.score_manager = None
        self.platform_manager = None
        self.powerup_manager = None

    def run(self):
        """Main game loop that handles the rendering and updates"""
        # Cancel any existing game loop
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
            
        # Reset frame timing
        self.frame_accumulator = 0.0
        
        # Start fresh game loop
        self.is_running = True
        self.game_loop()

    
    def game_loop(self):
        """Game loop logic and timing with fixed time step"""
        if not self.game_loop_running:
            return
            
        current_time = time.time()
        
        if self.current_state == GAME_STATE_PLAYING:
            if not self.is_paused and not self.is_game_over:
                if self.last_update:
                    # Calculate elapsed time
                    diff_time = current_time - self.last_update
                    self.frame_accumulator += diff_time

                    # Use fixed time step updates
                    while self.frame_accumulator >= FRAME_TIME_SECONDS:
                        self.update(FRAME_TIME_SECONDS)
                        self.frame_accumulator -= FRAME_TIME_SECONDS
                    
                self.render()
            elif self.is_game_over and not self.game_over_screen:
                self.show_game_over_screen()
                
        self.last_update = current_time
        
        if self.game_loop_running:
            self.game_loop_id = self.after(FRAME_TIME, self.game_loop)
    def update(self, diff_time):
        """
        Update game states

        Args:
            diff_time (float): Time since last update in seconds
        """

        # Update player first
        old_player_x = self.player.x
        self.player.update(diff_time)

        # Update camera to follow player
        self.camera.update(self.player)

        # Update score and difficulty
        score = self.score_manager.update(self.player.y)
        self.difficulty_manager.update_difficulty(score)

        # Update platform manager
        self.platform_manager.update(self.player.y, diff_time)

        # Update powerup manager
        self.powerup_manager.update(self.player, self.score_manager)

        # Check player collision with platforms
        for platform in self.platform_manager.get_platforms():
            if platform.check_collision(self.player):
                # Collision logic
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
        """
        Draw current game state to canvas
        """

        # Clears canvas
        self.canvas.delete('all')

        # Renders ground
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

        # Render powerups with camera offset
        self.powerup_manager.render(self.camera.y)

        # Add display text
        display_info = self.score_manager.get_display_text()
        

        # Add score text
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

        # Add boost text
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
        """
        Exit game cleanly
        """
        self.leaderboard.save_scores()
        self.is_running = False
        self.destroy()

    def handle_player_death(self):
        """Handles proper steps when player dies"""

        # Stop game loop
        self.is_game_over = True

    def show_game_over_screen(self):
        """Shows game over screen elements"""
        self.canvas.delete('all')
        self.game_over_screen = []
        final_score = int(self.score_manager.get_score())
        
        if self.leaderboard.is_high_score(final_score):
            # Game Over text at top
            game_over_text = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3,
                text="GAME OVER",
                anchor="center",
                fill="red",
                font=("Arial Bold", 25)
            )
            self.game_over_screen.append(game_over_text)

            # Score display
            score_text = self.canvas.create_text(
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3 + 50,
                text=f"Final Score: {final_score}",
                anchor="center",
                fill="black",
                font=("Arial Bold", 15)
            )
            self.game_over_screen.append(score_text)

            # High score entry elements
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

            # Error message text (initially empty)
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
                    self.canvas.delete('all')  # Clear everything before showing leaderboard
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
        else:
            self.show_final_leaderboard()

    def show_final_leaderboard(self):
        """Shows final leaderboard after game over"""
        # Clear previous elements
        self.canvas.delete('all')
        
        # Add game over text at the top
        game_over = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6,
            text="GAME OVER",
            anchor="center",
            fill="red",
            font=("Arial Bold", 25)
        )
        self.game_over_screen = [game_over]  # Reset game_over_screen with new elements
        
        # Show score
        final_score = int(self.score_manager.get_score())
        score_text = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4,
            text=f"Final Score: {final_score}",
            anchor="center",
            fill="black",
            font=("Arial Bold", 15)
        )
        self.game_over_screen.append(score_text)
        
        # Show full leaderboard
        self.leaderboard.leaderboard_screen(is_paused=False)
        
        # Add replay button at bottom
        replay_button = tk.Button(
            self,
            text="Play Again",
            command=self.start_new_game,
            font=("Arial Bold", 12)
        )
        button_window = self.canvas.create_window(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 100,
            window=replay_button
        )
        self.game_over_screen.append(button_window)


    def start_new_game(self):
        """Starts a new game from any state with proper cleanup"""
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
        else:
            self.player.reset()
            
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
        self.is_running = True
        self.game_loop_running = True
        
        # Set up controls
        self.setup_controls()
        
        # Start fresh game loop
        self.last_update = time.time()
        self.game_loop()




    





if __name__ == "__main__":
    game = Game()
    game.mainloop()


# TODO: Game Classes Structure
#   - Game (main game class)
#   - Player (player character)
#   - Platform (platforms to jump on)
#   - Menu (menu system)
#   - ScoreBoard (handling scores)

# TODO: Core Game Features
#   - Game loop
#   - Window setup
#   - Player movement
#   - Platform generation
#   - Collision detection
#   - Gravity physics

# TODO: Additional Features
#   - Menu system
#   - Key binding customization
#   - Scoring system
#   - Leaderboard
#   - Save/Load functionality
#   - Pause menu
#   - Boss key
#   - Cheat codes
#   - Difficulty settings

# TODO: Main game structure below