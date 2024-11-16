from constants import *
import json

class Leaderboard:
    """Leaderboard bruh"""

    def __init__(self, canvas):
        
        self.canvas = canvas
        self.max_entries = 10
        self.file = "leaderboard.json"
        self.max_name_length = 10
        self.canvas_object = None
        self.leaderboard = self.get_leaderboard() # List with dict containing name and scores in descending order
        self.is_updated = False
        self.fill = "black"
        self.font = ("Arial Bold", 20)

    def leaderboard_screen(self, is_paused=False):
        """
        Create leaderboard screen with table-like formatting
        
        Args:
            is_paused (bool): If True, only show top 5 scores
        """
        leaderboard_screen = []
        
        # Define layout constants
        RANK_WIDTH = 80  # Increased from 50
        NAME_WIDTH = 150  # Decreased from 200
        SCORE_WIDTH = 100
        PADDING = 20  # Added padding between columns
        ROW_HEIGHT = 30
        START_Y = WINDOW_HEIGHT // 3 if not is_paused else WINDOW_HEIGHT // 2
        
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

        # Add title above leaderboard if in pause mode
        if is_paused:
            title = self.canvas.create_text(
                WINDOW_WIDTH // 2, START_Y - ROW_HEIGHT * 1.5,
                text="TOP SCORES",
                anchor="center",
                fill=self.fill,
                font=("Arial Bold", 24)  # Slightly larger font for title
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
        """Gets dict and writes it into leaderboard.txt"""

        # Don't do anything if leaderboard is not updated
        if not self.is_updated:
            return
                
        with open(self.file) as file:
            data = json.load(file)
        
        data["scores"] = self.leaderboard

        with open(self.file, "w") as file:
            json.dump(data, file, indent=4)
            
    def add_score(self, name, score):
        """Checks if score should be added to leaderboard"""

        if not self.validate_name(name):
            return
        
        old_leaderboard = self.leaderboard.copy()
        entry = {"name": name, "score": score}
        self.leaderboard.append(entry)
        self.leaderboard.sort(reverse=True, key=lambda e: e["score"])
        self.leaderboard = self.leaderboard[:self.max_entries]
        self.is_updated = self.leaderboard != old_leaderboard

    def get_leaderboard(self):
        """Gets line from leaderboard.txt and returns a dictionary"""

        leaderboard = []

        try:
            with open(self.file) as file:
                data = json.load(file)
                scores = data['scores']

                for item in scores:
                    score = {"name": item["name"], "score": item["score"]}
                    leaderboard.append(score)
        except FileNotFoundError:
            data = {"scores": []}
            with open(self.file, "w") as new_file:
                json.dump(data, new_file, indent=4)
        except json.JSONDecodeError:
            return leaderboard

        return leaderboard
    
    def validate_name(self, name):
        """Validates player name input"""

        if len(name) <= self.max_name_length and name.isalnum() and name != "":
            return True
        else:
            return False
        
    def get_rank(self, score):
        """Gets player current rank on leaderboard based on current score"""

        if not self.leaderboard:
            return 1
        
        # Iterate through the leaderboard and find the first score that the player is higher than
        for i in range(len(self.leaderboard)):
            if score >= self.leaderboard[i]["score"]:
                return i + 1
    
        if len(self.leaderboard) < self.max_entries:
            return len(self.leaderboard) + 1
        
        return None
    
    def is_high_score(self, score):
        """Checks if a player final score qualifies for the leaderboard"""

        if len(self.leaderboard) < self.max_entries:
            return True
        
        if score >= self.leaderboard[self.max_entries - 1]["score"]:
            return True
        
        return False

