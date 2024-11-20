"""This module handles the leaderboard management for the game

It checks the players final score, determine whether it 
qualifies for the leaderboard and adjusts the leaderboard.json file
to store player names and score in descending score order"""

import json
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Leaderboard:
    """Manages leaderboard UI in main menu and pause menu
    and data entry on player death
    
    Attributes:
        canvas (tk.Canvas): Canvas to draw leaderboard elements on
        max_entries (int): Maximum number of entries on the leaderboard
        file (str): File name that stores the leaderboard data locally
        max_name_length (int): Maximum characters for player name entry
        canvas_object (list): Contains all text canvas object
        leaderboard (list): Contains dictionary with name and 
            scores in descending score order
        is_updated (bool): Flag for whether leaderboard gets updated or not
        """

    def __init__(self, canvas):
        """Initializes the leaderboard object that keeps track of player scores
        
        Args:
            canvas (tk.Canvas): Canvas to draw leaderboard on
        """
        self.canvas = canvas
        self.max_entries = 10
        self.file = "leaderboard.json"
        self.max_name_length = 10
        self.canvas_object = None
        self.leaderboard = self.get_leaderboard()
        self.is_updated = False
        self.fill = "black"
        self.font = ("Arial Bold", 20)

    def leaderboard_screen(self, is_paused=False):
        """
        Create leaderboard screen with table-like formatting
        
        Args:
            is_paused (bool): If True, only show top 5 scores and position higher
        """
        leaderboard_screen = []
        
        # Define layout constants
        RANK_WIDTH = 80
        NAME_WIDTH = 150
        SCORE_WIDTH = 100
        PADDING = 20
        ROW_HEIGHT = 30
        
        # Adjust vertical position based on pause state
        START_Y = WINDOW_HEIGHT // 3 if not is_paused else WINDOW_HEIGHT // 3
        
        # Calculate total width
        TOTAL_WIDTH = RANK_WIDTH + NAME_WIDTH + SCORE_WIDTH + (PADDING * 2)
        
        # Calculate starting x position to center the whole table
        table_start_x = WINDOW_WIDTH // 2 - TOTAL_WIDTH // 2
        
        # Calculate column positions with padding
        rank_x = table_start_x
        name_x = rank_x + RANK_WIDTH + PADDING
        score_x = name_x + NAME_WIDTH + PADDING

        # Create header
        header = self.canvas.create_text(
            rank_x, START_Y,
            text="RANK",
            anchor="w",
            fill=self.fill,
            font=self.font
        )
        
        header_name = self.canvas.create_text(
            name_x, START_Y,
            text="NAME",
            anchor="w",
            fill=self.fill,
            font=self.font
        )
        
        header_score = self.canvas.create_text(
            score_x, START_Y,
            text="SCORE",
            anchor="w",
            fill=self.fill,
            font=self.font
        )
        
        leaderboard_screen.extend([header, header_name, header_score])

        # Add separator line
        separator = self.canvas.create_line(
            rank_x, START_Y + ROW_HEIGHT/2,
            score_x + SCORE_WIDTH, START_Y + ROW_HEIGHT/2,
            fill=self.fill,
            width=2
        )
        leaderboard_screen.append(separator)

        # Determine how many entries to show
        display_entries = self.leaderboard[:5] if is_paused else self.leaderboard

        # Add entries
        for i, entry in enumerate(display_entries):
            y_pos = START_Y + (i + 1) * ROW_HEIGHT
            
            # Rank number (left-aligned)
            rank = self.canvas.create_text(
                rank_x, y_pos,
                text=f"{i + 1}.",
                anchor="w",
                fill=self.fill,
                font=self.font
            )
            
            # Name (left-aligned)
            name = self.canvas.create_text(
                name_x, y_pos,
                text=entry["name"],
                anchor="w",
                fill=self.fill,
                font=self.font
            )
            
            # Score (right-aligned with padding)
            score = self.canvas.create_text(
                score_x + SCORE_WIDTH, y_pos,
                text=str(entry["score"]),
                anchor="e",
                fill=self.fill,
                font=self.font
            )
            
            leaderboard_screen.extend([rank, name, score])

        # Add title only during pause mode
        if is_paused:
            title = self.canvas.create_text(
                WINDOW_WIDTH // 2, START_Y - ROW_HEIGHT * 1.5,
                text="TOP SCORES",
                anchor="center",
                fill=self.fill,
                font=("Arial Bold", 24)
            )
            leaderboard_screen.append(title)

        self.canvas_object = leaderboard_screen

    def cleanup(self):
        """Removes all leaderboard elements from canvas"""
        if self.canvas_object:
            for element in self.canvas_object:
                self.canvas.delete(element)
            self.canvas_object = None

    def save_scores(self):
        """Gets dictionary and writes it into leaderboard.json"""
        # Don't update leaderboard.json if leaderboard is not updated
        if not self.is_updated:
            return
                
        with open(self.file) as file:
            data = json.load(file)
        
        data["scores"] = self.leaderboard

        # Indent for better readability
        with open(self.file, "w") as file:
            json.dump(data, file, indent=4)
            
    def add_score(self, name, score):
        """Checks if score should be added to leaderboard
            - Validate name
            - Create copy of old leaderboard
            - Add entry and score
            - Sort in descending score order
            - Slice list to only include up to max_entries
            - Compare new leaderboard with old leaderboard

        Args:
            name (str): Player name entered
            score (int): Player final score
        """
        # Don't add entry if name is invalid
        if not self.validate_name(name):
            return
        
        old_leaderboard = self.leaderboard.copy()
        entry = {"name": name, "score": score}
        self.leaderboard.append(entry)
        self.leaderboard.sort(reverse=True, key=lambda e: e["score"])
        self.leaderboard = self.leaderboard[:self.max_entries]
        self.is_updated = self.leaderboard != old_leaderboard

    def get_leaderboard(self):
        """Gets object from leaderboard.json and returns the list of scores
        
        Returns:
            list: contains dictionary of name and scores in descending score order
        """
        leaderboard = []

        try:
            with open(self.file) as file:
                data = json.load(file)
                scores = data['scores']

                for item in scores:
                    score = {"name": item["name"], "score": item["score"]}
                    leaderboard.append(score)
        # Create new file if leaderboard.json not found
        except FileNotFoundError:
            data = {"scores": []}
            with open(self.file, "w") as new_file:
                json.dump(data, new_file, indent=4)
        # Return empty list if leaderboard.json file is corrupted
        except json.JSONDecodeError:
            return leaderboard

        return leaderboard
    
    def validate_name(self, name):
        """Validates player name input
        - Alphanumeric
        - Within max_name_length in length
        
        Args:
            name (str): Player name input

        Returns:
            bool: True if name is valid, False otherwise
        """
        if len(name) <= self.max_name_length and name.isalnum() and name != "":
            return True
        else:
            return False
        
    def get_rank(self, score):
        """Gets player current rank on leaderboard based on current score
        for in-game display text
        
        Args:
            score (int): Player current score
            
        Returns:
            int: Player current ranking on leaderboard
            None: No rank if the player is ranked below max_entries place
        """
        # First rank if no leaderboard yet
        if not self.leaderboard:
            return 1
      
        # Iterate through the leaderboard and 
        # find the first score that the player is higher than
        for i in range(len(self.leaderboard)):
            if score >= self.leaderboard[i]["score"]:
                return i + 1
    
        # Gives the last rank if leaderboard is not filled yet
        if len(self.leaderboard) < self.max_entries:
            return len(self.leaderboard) + 1
        
        return None
    
    def is_high_score(self, score):
        """Checks if a player final score qualifies for the leaderboard
        
        Args:
            score (int): Player final score
            
        Returns:
            bool: True if score qualifies, False otherwise"""
        # Always true if leaderboard is not filled yet
        if len(self.leaderboard) < self.max_entries:
            return True
        
        # Only check with lowest rank on leaderboard
        if score >= self.leaderboard[self.max_entries - 1]["score"]:
            return True
        
        return False