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

    def leaderboard_screen(self):
        """Create leaderboard canvas object"""

        leaderboard_screen = []
        # Add header
        header = self.canvas.create_text(
            0, WINDOW_WIDTH, # Dummy values
            text="Rank Name Score", # TODO: right align Score
            fill=self.fill,
            font=self.font
        )

        leaderboard_screen.append(header)

        # Add each leaderboard entry
        for i in range(len(self.leaderboard)):
            name = self.leaderboard[i]["name"]
            score = self.leaderboard[i]["score"]
            row = self.canvas.create_text(
                0, WINDOW_WIDTH, # Dummy values for now
                text=f"{i + 1}. {name}  {score}", # TODO: make rank and name left align and score right align
                fill=self.fill,
                font=self.font
            )
            leaderboard_screen.append(row)

        self.canvas_object = leaderboard_screen

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

        if not self.validate_name():
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
            return leaderboard
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

