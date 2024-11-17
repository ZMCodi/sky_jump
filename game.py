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
        self.is_running = False
        self.is_paused = False
        self.pause_elements = None
        self.is_game_over = False
        self.last_update = time.time()

        # Boss key variables
        self.boss_key_active = False
        self.boss_overlay = None
        self.load_boss_image()

        # Quit game when exit button is pressed
        self.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Create player instance
        player_x = WINDOW_WIDTH // 2
        player_y = WINDOW_HEIGHT - PLAYER_HEIGHT
        self.player = Player(self.canvas, player_x, player_y)

        # Set up keyboard controls
        self.setup_controls()

        # Create managers
        self.initialize_managers()

        # Create camera object
        self.camera = Camera()

        # Create leaderboard
        self.leaderboard = Leaderboard(self.canvas)

        # Handles player death
        self.platform_manager.register_callback('on_death', self.handle_player_death)
        self.game_over_screen = None

    def setup_controls(self):
        """
        Configure key bindings for player control
        """

        # Movement controls
        self.bind('<Left>', lambda e: self.player.start_move_left())
        self.bind('<Right>', lambda e: self.player.start_move_right())
        self.bind('<Escape>', lambda e: self.pause())
        self.bind('<space>', lambda e: self.player.jump() if not self.is_paused else None)
        self.bind('<Shift-D>', lambda e: self.player.activate_double_jump())
        self.bind('<b>', lambda e: self.activate_boss_key())

        # Handle key release for smoother movement
        self.bind('<KeyRelease-Left>', lambda e: self.player.stop_move_left())
        self.bind('<KeyRelease-Right>', lambda e: self.player.stop_move_right())


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
        """Activates fake productive messaging screen"""

        if not self.boss_key_active and not self.is_game_over:
            if not self.is_paused:
                self.is_paused = True
            self.hide_pause_menu()
            self.boss_key_active = True

            if self.boss_image:
                self.boss_overlay = self.canvas.create_image(
                    0, 0,
                    image=self.boss_image,
                    anchor="nw",
                    tags="boss_overlay"
                )
                self.title("Teams")
            
        elif self.boss_key_active:
            if self.boss_overlay:
                self.canvas.delete(self.boss_overlay)
                self.boss_overlay = None
            self.boss_key_active = False
            self.title(WINDOW_TITLE)
            self.show_pause_menu()

    def pause(self):
        """Pauses and unpauses game"""

        if self.is_game_over:
            return
        
        self.is_paused = not self.is_paused

        # Stops game and show pause menu if paused
        if self.is_paused:
            self.show_pause_menu()
        else:
            self.hide_pause_menu()
            self.run()

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
        
        # Pause title
        pause_text = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4,  # Moved up to make room for leaderboard
            text="PAUSED",
            anchor="center",
            fill="white",
            font=("Arial Bold", 25)
        )
        self.pause_elements.append(pause_text)
        
        # Score display
        score_text = self.canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 3,  # Moved up to make room for leaderboard
            text=f"Current Score: {int(self.score_manager.get_score())}",
            anchor="center",
            fill="white",
            font=("Arial Bold", 15)
        )
        self.pause_elements.append(score_text)
        
        # Show leaderboard with top 5 scores
        self.leaderboard.leaderboard_screen(is_paused=True)
        
        # Create frame for buttons
        button_frame = tk.Frame(self)
        button_frame.configure(bg=BG_COLOR)
        
        # Create buttons
        resume_button = tk.Button(
            button_frame,
            text="Resume",
            command=self.pause,
            font=("Arial Bold", 12),
            width=10
        )
        resume_button.pack(side=tk.LEFT, padx=5)
        
        restart_button = tk.Button(
            button_frame,
            text="Restart",
            command=self.start_new_game,
            font=("Arial Bold", 12),
            width=10
        )
        restart_button.pack(side=tk.LEFT, padx=5)
        
        quit_button = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_game,
            font=("Arial Bold", 12),
            width=10
        )
        quit_button.pack(side=tk.LEFT, padx=5)
        
        # Add button frame to canvas
        button_window = self.canvas.create_window(
            WINDOW_WIDTH / 2,
            5 * WINDOW_HEIGHT / 6,  # Moved down slightly to make room for leaderboard
            window=button_frame
        )
        self.pause_elements.append(button_window)

    def hide_pause_menu(self):
        """Removes pause menu elements"""
        if self.pause_elements:
            for element in self.pause_elements:
                self.canvas.delete(element)
            self.pause_elements = None
        self.leaderboard.cleanup()

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
        if hasattr(self, 'platform_manager'):
            self.platform_manager.reset()

        if hasattr(self, 'powerup_manager'):
            self.powerup_manager.reset()
            
        # Remove references to old managers
        self.difficulty_manager = None
        self.score_manager = None
        self.platform_manager = None
        self.powerup_manager = None

    def run(self):
        """
        Main game loop that handles the rendering and updates
        """

        self.is_running = True
        self.game_loop()

    
    def game_loop(self):
        """
        Actual game loop logic and timing
        """
        if self.is_running and not self.is_paused:
            current_time = time.time()
            
            if not self.is_game_over:
                # Only calculate diff_time and update game state if game is active
                diff_time = current_time - self.last_update
                # Cap maximum diff_time to prevent huge jumps
                diff_time = min(diff_time, FRAME_TIME_SECONDS * 3)
                self.update(diff_time)
                self.render()
            else:
                # Show game over screen if it hasn't been shown yet
                if not self.game_over_screen:
                    self.show_game_over_screen()
                    
            self.last_update = current_time
            
            # Schedule next frame
            self.after(FRAME_TIME, self.game_loop)



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
        """Resets everything and starts the game again"""
        # Clean up canvas
        self.canvas.delete('all')

        was_paused = self.is_paused
        
        if self.game_over_screen:
            for element in self.game_over_screen:
                self.canvas.delete(element)
            self.game_over_screen = None
        self.hide_pause_menu()

        # Reset game state
        self.is_game_over = False
        self.is_paused = False
        
        # Clean up old managers and create new ones
        self.cleanup_managers()
        self.initialize_managers()
        
        # Reset player and camera
        self.player.reset()
        self.camera.reset()

        # Reset timing before restarting game loop
        self.last_update = time.time()
        
        # Restart game loop
        self.is_running = True

        if was_paused:
            self.run()




    





if __name__ == "__main__":
    game = Game()
    game.run()
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