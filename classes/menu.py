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
            fill=self.game.player_color if self.game.player_color else "white",
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


class LoadGameMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.save_files = {}
        
        # Layout constants
        self.SLOT_WIDTH = 320
        self.SLOT_HEIGHT = 80
        self.PLAYER_PREVIEW_SIZE = 50
        self.SLOTS_PER_PAGE = 5
        self.VERTICAL_SPACING = 20
        
    def show(self):
        """Shows the load game menu"""
        self.cleanup()
        
        # Add title with shadow effect
        shadow = self.canvas.create_text(
            WINDOW_WIDTH/2 + 2, WINDOW_HEIGHT/8 + 2,
            text="LOAD GAME",
            anchor="center",
            fill="#1a1a1a",
            font=("Arial Bold", 36)
        )
        title = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/8,
            text="LOAD GAME",
            anchor="center",
            fill="#4a90e2",
            font=("Arial Bold", 36)
        )
        self.elements.extend([shadow, title])
        
        # Get available save files
        self.save_files = self.game.save_manager.get_save_info()
        
        # Create slots for existing saves
        self.create_load_slots()
        
        # Add back button
        back_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 40,
            160, 35,
            "BACK TO MENU",
            lambda: self.game.show_menu()
        )
        self.elements.extend(back_button)

    def create_load_slots(self):
        """Creates visual elements for each save slot"""
        start_y = WINDOW_HEIGHT/5
        
        # Filter to only show existing saves
        existing_saves = {slot: info for slot, info in self.save_files.items() 
                        if info['exists']}
        
        if not existing_saves:
            # Show "No saves found" message
            no_saves = self.canvas.create_text(
                WINDOW_WIDTH/2, WINDOW_HEIGHT/2,
                text="No saved games found",
                fill="white",
                font=("Arial Bold", 16)
            )
            self.elements.append(no_saves)
            return
        
        for slot, save_info in existing_saves.items():
            y = start_y + (slot-1) * (self.SLOT_HEIGHT + self.VERTICAL_SPACING)
            
            # Create slot background
            slot_bg = self.canvas.create_rectangle(
                WINDOW_WIDTH/2 - self.SLOT_WIDTH/2, y,
                WINDOW_WIDTH/2 + self.SLOT_WIDTH/2, y + self.SLOT_HEIGHT,
                fill="#4a90e2",
                outline="#2171cd",
                width=2,
                tags=f"slot_{slot}"
            )
            
            # Create player preview box
            preview_x = WINDOW_WIDTH/2 - self.SLOT_WIDTH/2 + 15
            preview_y = y + (self.SLOT_HEIGHT - self.PLAYER_PREVIEW_SIZE)/2
            player_preview = self.canvas.create_rectangle(
                preview_x, preview_y,
                preview_x + self.PLAYER_PREVIEW_SIZE, 
                preview_y + self.PLAYER_PREVIEW_SIZE,
                fill=save_info['color'],
                outline="grey"
            )

            # Add face overlay if exists
            if save_info['face'] and save_info['face'] != 'None':
                try:
                    # Load specific face image
                    face_path = os.path.join("player_faces", f"{save_info['face']}.png")
                    with Image.open(face_path) as image:
                        face_image = image.resize((self.PLAYER_PREVIEW_SIZE, self.PLAYER_PREVIEW_SIZE), Image.Resampling.LANCZOS)
                        face_photo = ImageTk.PhotoImage(face_image)
                        
                    self.canvas.create_image(
                        preview_x, preview_y,
                        image=face_photo,
                        anchor="nw",
                        tags='preview_face'
                    )
                    # Keep a reference to prevent garbage collection
                    self.elements.append(face_photo)
                except Exception as e:
                    print(f"Error loading face image: {e}")
                
            # Add save info
            text_x = preview_x + self.PLAYER_PREVIEW_SIZE + 20
            save_text = self.canvas.create_text(
                text_x, y + self.SLOT_HEIGHT/2,
                text=f"Saved: {save_info['date']}\n"
                     f"Score: {save_info['score']}\n"
                     f"Height: {int(save_info['height'])}m",
                anchor="w",
                fill="white",
                font=("Arial", 12),
                justify="left"
            )

            # Add delete button
            delete_btn = self.create_menu_button(
                WINDOW_WIDTH/2 + self.SLOT_WIDTH/2 - 50, 
                y + self.SLOT_HEIGHT/1.4,
                80, 25,
                "Delete",
                lambda s=slot: self.show_delete_confirmation(s)
            )
            
            # Add hover effect and click handler for the slot
            for item in (slot_bg, player_preview, save_text):
                self.canvas.tag_bind(item, '<Enter>', 
                    lambda e, bg=slot_bg: self.canvas.itemconfig(bg, fill="#2171cd"))
                self.canvas.tag_bind(item, '<Leave>', 
                    lambda e, bg=slot_bg: self.canvas.itemconfig(bg, fill="#4a90e2"))
                self.canvas.tag_bind(item, '<Button-1>', 
                    lambda e, s=slot: self.handle_slot_click(s))
                    
            self.elements.extend([slot_bg, player_preview, save_text, *delete_btn])

    def handle_slot_click(self, slot_number):
        """Handles clicking on a save slot"""
        if self.game.handle_load_game(slot_number):
            print(f"Successfully loaded game from slot {slot_number}")
        else:
            # Show error message
            error_msg = self.canvas.create_text(
                WINDOW_WIDTH/2, WINDOW_HEIGHT - 80,
                text="Failed to load save file!",
                fill="red",
                font=("Arial Bold", 14)
            )
            self.elements.append(error_msg)
            self.game.after(2000, lambda: self.canvas.delete(error_msg))

    def show_delete_confirmation(self, slot_number):
        """Shows confirmation dialog for deleting a save"""
        # Create semi-transparent overlay
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill="black",
            stipple="gray50",
            tags="confirm_overlay"
        )
        
        # Create confirmation dialog box
        dialog_width = 300
        dialog_height = 150
        dialog_x = WINDOW_WIDTH/2 - dialog_width/2
        dialog_y = WINDOW_HEIGHT/2 - dialog_height/2
        
        dialog = self.canvas.create_rectangle(
            dialog_x, dialog_y,
            dialog_x + dialog_width, dialog_y + dialog_height,
            fill="#4a90e2",
            outline="#2171cd",
            width=2
        )
        
        # Add confirmation message
        message = self.canvas.create_text(
            WINDOW_WIDTH/2, dialog_y + 40,
            text=f"Are you sure you want to delete\nsave slot {slot_number}?",
            fill="white",
            font=("Arial Bold", 14),
            justify="center"
        )
        
        # Add buttons
        confirm_btn = self.create_menu_button(
            dialog_x + dialog_width/4, dialog_y + 100,
            100, 30,
            "Delete",
            lambda: self.delete_save(slot_number, [overlay, dialog, message, 
                                                 *confirm_btn, *cancel_btn])
        )
        
        cancel_btn = self.create_menu_button(
            dialog_x + (dialog_width * 3/4), dialog_y + 100,
            100, 30,
            "Cancel",
            lambda: self.cleanup_confirmation([overlay, dialog, message, 
                                            *confirm_btn, *cancel_btn])
        )
        
        self.elements.extend([overlay, dialog, message, *confirm_btn, *cancel_btn])

    def cleanup_confirmation(self, elements):
        """Removes confirmation dialog elements"""
        for element in elements:
            self.canvas.delete(element)

    def delete_save(self, slot_number, dialog_elements):
        """Deletes the save file and refreshes the menu"""
        # Here you would add the actual save file deletion logic
        self.cleanup_confirmation(dialog_elements)
        # Refresh the load menu to show updated save files
        self.show()

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

        save_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            button_y_start + button_spacing * 3,
            button_width,
            button_height,
            "SAVE GAME",
            lambda: self.show_save_slots()
        )
        
        # Add all button elements to pause_elements list
        self.elements.extend([*resume_button, *restart_button, *menu_button, *save_button])
        
        # Add controls reminder at bottom
        controls_text = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT - 20,
            text="Press ESC to Resume  |  Left Alt for Boss Key",
            fill="white",
            font=("Arial", 12)
        )
        self.elements.append(controls_text)

    def show_save_slots(self):
        """Shows save slot selection interface"""
        
        # Add semi-transparent dark overlay
        overlay = self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='black', 
            tags='save_overlay'
        )
        self.elements.append(overlay)
        
        # Add title
        title = self.canvas.create_text(
            WINDOW_WIDTH/2, WINDOW_HEIGHT/5,
            text="SELECT SAVE SLOT",
            fill="#4a90e2",
            font=("Arial Bold", 28),
            tags="save_title"
        )
        self.elements.append(title)
        
        # Get save info
        saves_info = self.game.save_manager.get_save_info()
        
        # Calculate grid layout
        slots_per_row = 2
        total_rows = 5  # 10 slots total, 2 per row
        slot_width = 160
        slot_height = 80
        spacing_x = 20
        spacing_y = 15
        start_x = WINDOW_WIDTH/2 - (slot_width * 2 + spacing_x)/2
        start_y = WINDOW_HEIGHT/4
        
        # Create slot buttons
        for i in range(10):
            row = i // slots_per_row
            col = i % slots_per_row
            
            x = start_x + col * (slot_width + spacing_x)
            y = start_y + row * (slot_height + spacing_y)
            
            # Get save info for this slot
            slot_info = saves_info[i + 1]
            
            # Create slot background
            slot_bg = self.canvas.create_rectangle(
                x, y,
                x + slot_width, y + slot_height,
                fill="#4a90e2" if not slot_info['exists'] else "#2171cd",
                outline="#2171cd",
                width=2,
                tags=f"slot_{i+1}"
            )
            
            # Create slot text
            if slot_info['exists']:
                slot_text = f"Slot {i+1}\n{slot_info['date']}\nScore: {slot_info['score']}"
            else:
                slot_text = f"Empty Slot {i+1}"
                
            text = self.canvas.create_text(
                x + slot_width/2, y + slot_height/2,
                text=slot_text,
                fill="white",
                font=("Arial", 12),
                justify="center",
                tags=f"slot_text_{i+1}"
            )
            
            # Bind events
            for item in (slot_bg, text):
                self.canvas.tag_bind(item, '<Enter>', 
                    lambda e, bg=slot_bg: self.canvas.itemconfig(bg, fill="#185aa0"))
                self.canvas.tag_bind(item, '<Leave>', 
                    lambda e, bg=slot_bg, exists=slot_info['exists']: 
                        self.canvas.itemconfig(bg, fill="#2171cd" if exists else "#4a90e2"))
                self.canvas.tag_bind(item, '<Button-1>', 
                    lambda e, slot=i+1: self.handle_save_slot_select(slot))
                    
            self.elements.extend([slot_bg, text])
        
        # Add back button
        back_button = self.create_menu_button(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT - 60,
            160, 35,
            "BACK",
            self.cleanup_save_slots
        )
        self.elements.extend(back_button)

    def handle_save_slot_select(self, slot):
        """Handles when a save slot is selected"""
        
        if self.game.save_manager.save_game(slot):
            # Show success message
            msg = self.canvas.create_text(
                WINDOW_WIDTH/2, WINDOW_HEIGHT - 100,
                text="Game Saved Successfully!",
                fill="green",
                font=("Arial Bold", 14),
                tags="save_message"
            )
            self.elements.append(msg)
            
            # Remove message after 2 seconds
            self.game.after(2000, lambda: self.canvas.delete(msg))
        else:
            # Show error message
            msg = self.canvas.create_text(
                WINDOW_WIDTH/2, WINDOW_HEIGHT - 100,
                text="Failed to Save Game!",
                fill="red",
                font=("Arial Bold", 14),
                tags="save_message"
            )
            self.elements.append(msg)
            
            # Remove message after 2 seconds
            self.game.after(2000, lambda: self.canvas.delete(msg))

    def cleanup_save_slots(self):
        """Removes save slot interface and returns to pause menu"""
        self.cleanup()
        self.show()  # Show pause menu again
