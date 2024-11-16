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

        entry = {}
        entry["name"] = name
        entry["score"] = score
        self.leaderboard.append(entry)
        
        self.leaderboard.sort(reverse=True, key=lambda e: e["score"])

        # Remove entries over max if any
        try:
            remove = self.leaderboard[self.max_entries - 1]
            if remove["name"] == name and remove["score"] == score:
                self.is_updated = False
            self.leaderboard.remove(remove)
            self.is_updated = True
        except:
            self.is_updated = True

    def get_leaderboard(self):
        """Gets line from leaderboard.txt and returns a dictionary"""

        leaderboard = []

        with open(self.file) as file:
            data = json.load(file)
            scores = data['scores']

            for item in scores:
                score = {}
                score["name"] = item["name"]
                score["score"] = item["score"]
                leaderboard.append(score)

        return leaderboard




