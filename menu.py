from constants import *
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

class Menu:

    def __init__ (self, game_instance):
        self.game = game_instance
        self.canvas = self.game.canvas
        self.elements = []

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
    
    def cleanup(self):
        if not hasattr(self, 'elements'):
            self.elements = []

        for element in self.elements:
            self.canvas.delete(element)

        self.elements.clear()

    def show(self):
        """Implemented by subclasses"""

        raise NotImplementedError
    
class MainMenu(Menu):

    def show(self):
        """Shows the main menu screen"""
        self.cleanup()

        # Create semi-transparent dark overlay for better text readability
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='black', 
            stipple='gray50',
            tags='menu_overlay'
        )
        self.elements.append(overlay)
        
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
        self.elements.extend([shadow, title])
        
        # Add subtitle
        subtitle = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/4 + 50,
            text="The sky is the limit",
            fill="white",
            font=("Arial", 16)
        )
        self.elements.append(subtitle)
        
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
            lambda: self.game.start_new_game()
        )
        
        leaderboard_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "LEADERBOARD",
            lambda: self.game.show_leaderboard_screen()
        )
        
        settings_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 2,
            button_width,
            button_height,
            "SETTINGS",
            lambda: self.game.show_settings_screen()
        )
        
        load_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 3,
            button_width,
            button_height,
            "LOAD GAME",
            lambda: self.game.show_load_screen()
        )
        
        # Add controls hint at bottom
        controls_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT - 40,
            text="Press Left Alt for Boss Key  |  ESC for Pause",
            fill="white",
            font=("Arial", 12)
        )
        
        # Add all button elements to menu_elements list
        self.elements.extend([*play_button, *leaderboard_button, 
                                *settings_button, *load_button, controls_text])

        # Add version number
        version = self.canvas.create_text(
            10, WINDOW_HEIGHT - 10,
            text="v1.0",
            anchor="sw",
            fill="white",
            font=("Arial", 10)
        )
        self.elements.append(version)
            
        def show_load_screen():
            print("Load game screen - Coming soon!")

class SettingsMenu(Menu):

    def __init__ (self, game_instance):
        super().__init__(game_instance)
        self.face_images = {}
        self.preview_box = None
        self.load_face_images()

    def load_face_images(self):
        """Loads all images in player_faces folder"""
        self.face_images = {'None': None}
        face_dir = "player_faces"

        try:
            # Get only PNG files
            face_list = [f for f in os.listdir(face_dir) if f.endswith('.png')]
            
            for face in face_list:
                # Create proper file path
                face_path = os.path.join(face_dir, face)
                
                # Open and process image
                with Image.open(face_path) as image:
                    # Create both sizes
                    face_image = image.resize((PLAYER_WIDTH, PLAYER_HEIGHT), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage for tkinter
                    face_photo = ImageTk.PhotoImage(face_image)
                    
                    # Store in dictionaries
                    name = face.removesuffix(".png")
                    self.face_images[name] = face_photo
                    
        except Exception as e:
            print(f"Error loading face images: {e}")

    def show(self):
        self.cleanup()

        # Main Settings Title
        title = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/6,
            text="SETTINGS",
            anchor="center",
            fill="#4a90e2",
            font=("Arial Bold", 36)
        )
        self.elements.append(title)
        
        # Controls Section Header
        controls_header = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/4,  # Changed from WINDOW_HEIGHT/3
            text="Movement Controls",
            anchor="center",
            fill="black",
            font=("Arial Bold", 20)
        )
        
        # Create temporary variables for this screen
        temp_movement = tk.StringVar(self.game, value=self.game.movement_var.get())
        temp_space = tk.BooleanVar(self.game, value=self.game.space_var.get())
        
        # Arrow Keys Radio Button
        arrows_radio = tk.Radiobutton(
            self.game,
            text="Arrow Keys",
            variable=temp_movement,
            value="arrows",
            font=("Arial", 12)
        )
        arrows_radio_window = self.canvas.create_window(
            WINDOW_WIDTH/2 - 80, WINDOW_HEIGHT/4 + 40,
            window=arrows_radio
        )
        
        # WASD Radio Button
        wasd_radio = tk.Radiobutton(
            self.game,
            text="WASD Keys",
            variable=temp_movement,
            value="wasd",
            font=("Arial", 12)
        )
        wasd_radio_window = self.canvas.create_window(
            WINDOW_WIDTH/2 + 80, WINDOW_HEIGHT/4 + 40,
            window=wasd_radio
        )
        
        # Space Jump Checkbox
        space_check = tk.Checkbutton(
            self.game,
            text="Enable Space Jump",
            variable=temp_space,
            font=("Arial", 12)
        )
        space_check_window = self.canvas.create_window(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/4 + 80,
            window=space_check
        )

        customization_header = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/2.2,  # Positioned below movement controls
            text="Character Customization",
            anchor="center",
            fill="black",
            font=("Arial Bold", 20)
        )
        self.elements.append(customization_header)
        
        # Define default colors and their positions
        default_colors = {
            "White": "#FFFFFF",
            "Red": "#FF0000",
            "Blue": "#0000FF",
            "Green": "#00FF00",
            "Black": "#000000"
        }
        
        # Create color selection area
        color_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/2.2 + 30,
            text="Color Selection",
            anchor="center",
            fill="black",
            font=("Arial Bold", 12)
        )
        self.elements.append(color_text)
        
        # Create color buttons
        button_size = 20
        spacing = 30
        start_x = WINDOW_WIDTH/2 - (len(default_colors) * spacing)/2
        start_y = WINDOW_HEIGHT/2.2 + 60
        
        for i, (color_name, color_hex) in enumerate(default_colors.items()):
            x = start_x + i * spacing
            # Create color square
            color_button = self.canvas.create_rectangle(
                x, start_y,
                x + button_size, start_y + button_size,
                fill=color_hex,
                outline="grey",
                tags=f"color_{color_name}"
            )
            # Add click binding
            self.canvas.tag_bind(
                f"color_{color_name}",
                '<Button-1>',
                lambda e, c=color_hex: self.select_player_color(c)
            )
            self.elements.append(color_button)
        
        # Add custom color button
        custom_button = self.create_menu_button(
            WINDOW_WIDTH/2, start_y + button_size + 20,
            100, 25,
            "Custom...",
            self.show_color_picker
        )
        self.elements.extend(custom_button)
        
        # Add preview section
        preview_text = self.canvas.create_text(
            WINDOW_WIDTH/2, start_y + button_size + 60,
            text="Preview",
            anchor="center",
            fill="black",
            font=("Arial Bold", 12)
        )
        self.elements.append(preview_text)


        # Create preview box
        preview_size = PLAYER_WIDTH
        preview_x = WINDOW_WIDTH/2 - preview_size/2
        preview_y = start_y + button_size + 80
        self.preview_box = self.canvas.create_rectangle(
            preview_x, preview_y,
            preview_x + preview_size, preview_y + preview_size,
            fill=self.game.player.color if self.game.player else "white",
            outline="grey",
            tags="preview"
        )
        self.elements.append(self.preview_box)

        if self.game.player_face and self.game.player_face != 'None' and self.face_images[self.game.player_face]:
            self.canvas.create_image(
                preview_x, preview_y,
                image=self.face_images[self.game.player_face],
                anchor='nw',
                tags='preview_face'
            )

        face_header = self.canvas.create_text(
            WINDOW_WIDTH/2, preview_y + preview_size + 40,
            text="Face Selection",
            anchor="center",
            fill="black",
            font=("Arial Bold", 12)
        )
        self.elements.append(face_header)

        # Create face dropdown
        def on_face_select(event):
            selected = face_dropdown.get()
            # Update preview box - first ensure color is updated
            self.canvas.itemconfig(self.preview_box, fill=self.game.player_color)
            # Remove old face if it exists
            faces = self.canvas.find_withtag('preview_face')
            for face in faces:
                self.canvas.delete(face)
            # Add new face if one is selected
            if selected != 'None' and self.face_images[selected]:
                face_size = preview_size  # Same size as preview box
                face_x = preview_x
                face_y = preview_y
                self.canvas.create_image(
                    face_x, face_y,
                    image=self.face_images[selected],
                    anchor='nw',
                    tags='preview_face'
                )
            # Store selection
            self.game.player_face = selected

        face_var = tk.StringVar(value='None')
        face_dropdown = ttk.Combobox(
            self.game,
            textvariable=face_var,
            values=list(self.face_images.keys()),
            state='readonly',
            width=15,
            font=("Arial", 10)
        )
        face_dropdown.set('None')
        face_dropdown.bind('<<ComboboxSelected>>', on_face_select)

        face_dropdown_window = self.canvas.create_window(
            WINDOW_WIDTH/2, preview_y + preview_size + 70,
            window=face_dropdown
        )
        self.elements.append(face_dropdown_window)
        
        

        def save_and_return():
            """Save settings and return to menu"""
            self.game.movement_var.set(temp_movement.get())
            self.game.space_var.set(temp_space.get())
            self.game.setup_controls()  # Rebind controls based on new settings
            self.game.show_menu()

        # Store widget references
        self.elements.extend([arrows_radio_window, wasd_radio_window, space_check_window])
        
        # Add save and back buttons
        save_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 120,  # Position above back button
            200, 40,
            "SAVE SETTINGS",
            save_and_return
        )

        back_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 60,
            200, 40,
            "BACK TO MENU",
            lambda: self.game.show_menu()  # Don't save if just going back
        )
        
        self.elements.extend(save_button)
        self.elements.extend(back_button)

    def select_player_color(self, color):
        """Updates player color and preview"""
        if hasattr(self, 'preview_box'):
            self.canvas.itemconfig(self.preview_box, fill=color)
        
        # Store color preference
        self.game.player_color = color
        
        # Update current player if exists
        if self.game.player:
            self.game.player.color = color

    def show_color_picker(self):
        """Shows color picker dialog"""
        from tkinter import colorchooser
        current_color = self.game.player_color if hasattr(self.game, 'player_color') else "white"
        color = colorchooser.askcolor(
            title="Choose Player Color",
            color=current_color
        )
        if color[1]:  # color[1] contains the hex code
            self.select_player_color(color[1])

class LeaderboardMenu(Menu):

    def show_paused(self):
        self.cleanup()
        self.game.leaderboard.leaderboard_screen(is_paused=False)
        
        # Add back button
        back_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 60,
            200, 40,
            "BACK TO MENU",
            lambda: self.game.show_menu()
        )
        self.elements.extend(back_button)

    def show_final(self):
        self.cleanup()
        # Add game over text at the top
        game_over = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6,
            text="GAME OVER",
            anchor="center",
            fill="red",
            font=("Arial Bold", 25)
        )
        self.game.game_over_screen = [game_over]  # Reset game_over_screen with new elements
        
        # Show score
        final_score = int(self.game.score_manager.get_score())
        score_text = self.canvas.create_text(
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4,
            text=f"Final Score: {final_score}",
            anchor="center",
            fill="black",
            font=("Arial Bold", 15)
        )
        self.game.game_over_screen.append(score_text)
        
        # Show full leaderboard
        self.game.leaderboard.leaderboard_screen(is_paused=False)
        
        # Button configuration
        button_width = 160
        button_height = 35
        button_y_start = WINDOW_HEIGHT - 120  # Moved up to accommodate new buttons
        button_spacing = 42
        
        # Create play again button using custom menu button style
        play_again_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start,
            button_width,
            button_height,
            "PLAY AGAIN",
            lambda: self.game.start_new_game()
        )
        
        # Create main menu button
        main_menu_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "MAIN MENU",
            lambda: self.game.stop_game()
        )
        
        # Add all button elements to game_over_screen list
        self.game.game_over_screen.extend([*play_again_button, *main_menu_button])



class PauseMenu(Menu):
    def show(self):
        self.cleanup()

        # Add semi-transparent overlay
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='black', 
            stipple='gray50',
            tags='pause_overlay'
        )
        self.elements.append(overlay)
        
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
        self.elements.extend([shadow, title])
        
        # Score display - moved closer to title
        score_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/8 + 35,  # Closer to title
            text=f"Current Score: {int(self.game.score_manager.get_score())}",
            anchor="center",
            fill="white",
            font=("Arial Bold", 15)
        )
        self.elements.append(score_text)
        
        # Show leaderboard with top 5 scores - positioned closer to title
        self.game.leaderboard.leaderboard_screen(is_paused=True)
        
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
            lambda: self.game.pause()
        )
        
        restart_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing,
            button_width,
            button_height,
            "RESTART",
            lambda: self.game.start_new_game()
        )
        
        menu_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 2,
            button_width,
            button_height,
            "MAIN MENU",
            lambda: self.game.stop_game()
        )
        
        # Add all button elements to pause_elements list
        self.elements.extend([*resume_button, *restart_button, *menu_button])
        
        # Add controls reminder at bottom
        controls_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT - 20,
            text="Press ESC to Resume  |  Left Alt for Boss Key",
            fill="white",
            font=("Arial", 12)
        )
        self.elements.append(controls_text)
