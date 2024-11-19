"""
Infinite vertical platformer game made with tkinter
"""

import tkinter as tk
import time
from classes.player_class import Player
from classes.platform_class import PlatformManager
from classes.camera_class import Camera
from classes.scores import ScoreManager
from classes.difficulty import DifficultyManager
from classes.powerups import PowerupManager
from classes.leaderboard import Leaderboard
from classes.menu import *
from classes.save import SaveManager
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

        # Initialize menu system
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.leaderboard_menu = LeaderboardMenu(self)
        self.load_menu = LoadGameMenu(self)
        self.pause_menu = PauseMenu(self)
        self.save_manager = SaveManager(self)

        # Game state variables
        self.current_state = GAME_STATE_MENU
        self.game_components = None
        self.setup_state_variables()
        self.settings_menu.load_face_images()
        self.show_menu()

        # Boss key variables
        self.boss_key_active = False
        self.boss_overlay = None
        self.previous_state = None
        self.load_boss_image()

        # Quit game when exit button is pressed
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Set up keyboard controls
        self.movement_var = tk.StringVar(self)
        self.movement_var.set("arrows")
        self.space_var = tk.BooleanVar(self)
        self.space_var.set(True)
        self.setup_controls()

        self.leaderboard = Leaderboard(self.canvas)
        self.game_loop_running = False
        self.frame_accumulator = 0.0
        self.game_loop_id = None  # Track the game loop callback ID

        # Player selection variables
        self.player_color = "white"
        self.player_face = None

    def show_menu(self):
        """Shows main menu screen"""

        self.canvas.delete('all')
        self.current_state = GAME_STATE_MENU
        self.main_menu.show()

    def show_settings_screen(self):
        """Shows settings screen"""

        self.canvas.delete('all')
        self.current_state = GAME_STATE_SETTINGS
        self.settings_menu.show()
    

    def show_leaderboard_screen(self):
        """Shows the leaderboard screen"""
        self.canvas.delete('all')
        self.current_state = GAME_STATE_LEADERBOARD
        self.leaderboard_menu.show_paused()    


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
        def bind_player_controls():
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

                # Always bind these
                self.bind('<Shift-D>', lambda e: self.player.activate_double_jump())

        # Always bind these controls
        self.bind('<Escape>', lambda e: self.pause() if self.current_state == GAME_STATE_PLAYING else None)
        self.bind('<Alt_L>', lambda e: self.activate_boss_key())
        
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
            
            # If game is playing and not already paused, set pause flag
            if self.current_state == GAME_STATE_PLAYING and not self.is_paused:
                self.is_paused = True
            
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
            
            # Restore previous state and handle pause
            if self.previous_state == GAME_STATE_PLAYING:
                self.current_state = GAME_STATE_PLAYING
                self.is_paused = True
                # Render the game canvas before showing pause menu
                self.render()
                self.show_pause_menu()
            else:
                # For other states like menu, just restore them
                self.show_state_elements(self.previous_state)

    def hide_current_state_elements(self):
        """Hides elements of current state"""
        if self.current_state == GAME_STATE_MENU:
            for element in self.main_menu.elements:
                self.canvas.delete(element)
        elif self.current_state == GAME_STATE_PLAYING:
            if self.pause_menu.elements:
                self.hide_pause_menu()
        elif self.current_state == GAME_STATE_PAUSED:
            self.hide_pause_menu()

    def show_state_elements(self, state):
        """Restores elements of the given state"""
        if state == GAME_STATE_MENU:
            self.show_menu()
        elif state == GAME_STATE_PLAYING:
            # Don't resume game, show pause menu instead
            if self.is_paused:
                self.render()  # Render game state first
                self.show_pause_menu()
                self.current_state = GAME_STATE_PLAYING
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

        self.pause_menu.show()        
        
        
    def hide_pause_menu(self):
        """Removes pause menu elements"""
        
        self.pause_menu.cleanup()
        self.leaderboard.cleanup()

    def handle_save_game(self):
        """Called when save button is clicked in pause menu"""
        # Only allow saving during gameplay
        if self.current_state == GAME_STATE_PLAYING:
            self.pause_menu.show_save_slots()

    def handle_load_game(self, slot_number):
        """
        Called when a save slot is selected in load game screen
        
        Args:
            slot_number (int): Save slot to load
        """
        # Stop any existing game loop
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
            
        # Reset game state
        self.frame_accumulator = 0.0
        self.game_loop_running = False
        self.is_running = False
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

        # Clean up old managers and create new ones
        self.start_new_game()

        # Try to load the save
        if self.save_manager.load_game(slot_number):
            self.setup_controls()
            self.game_loop_running = True
            self.is_running = True
            self.last_update = time.time()
            self.frame_accumulator = 0.0
            self.game_loop()
            return True
        else:
            print("Failed to load game")
            self.show_menu()
            return False

    def show_load_screen(self):
        """Shows the load game screen"""
        self.canvas.delete('all')
        self.current_state = GAME_STATE_LOAD
        self.leaderboard_menu.cleanup()
        self.main_menu.cleanup()
        self.load_menu.show()  # create LoadGameMenu class

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
        if not self.game_loop_running:
            return
            
        current_time = time.time()
        
        if self.current_state == GAME_STATE_PLAYING:
            if not self.is_paused and not self.is_game_over:
                if self.last_update:
                    diff_time = current_time - self.last_update
                    self.frame_accumulator += diff_time
                    
                    while self.frame_accumulator >= FRAME_TIME_SECONDS:
                        self.update(FRAME_TIME_SECONDS)
                        self.frame_accumulator -= FRAME_TIME_SECONDS
                    
                self.render()
            elif self.is_game_over:
                if self.game_loop_id:
                    self.after_cancel(self.game_loop_id)
                    self.game_loop_id = None
                if not self.game_over_screen:
                    self.show_game_over_screen()
                return
                    
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
        # Renders player face overlay if selected
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
        if hasattr(self, 'game_over_screen') and self.game_over_screen:
            for element in self.game_over_screen:
                self.canvas.delete(element)
        self.game_over_screen = None

        self.current_state = GAME_STATE_GAME_OVER
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
            self.leaderboard_menu.show_final()

    def show_final_leaderboard(self):
        """Shows final leaderboard after game over"""
        # Clear previous elements
        self.canvas.delete('all')
        self.leaderboard_menu.show_final()
        


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



# TODO: Additional Features
#   - fix boss key issue with tkinter inputs
#   - add powerups pics
#   - add sky and ground pics
#   - properly comment everything
