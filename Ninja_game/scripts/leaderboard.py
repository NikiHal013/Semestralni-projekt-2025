import json
import os
from datetime import datetime

class Leaderboard:
    def __init__(self, data_dir="Ninja_game/data/top_times"):
        self.data_dir = data_dir
        self.max_entries = 10
        self.leaderboards = {
            "baby_mode": self.load_leaderboard("baby_mode"),
            "normal": self.load_leaderboard("normal"),
            "hard": self.load_leaderboard("hard")
        }
    
    def _get_leaderboard_path(self, difficulty):
        return os.path.join(self.data_dir, f"leaderboard_{difficulty}.json")
    
    def load_leaderboard(self, difficulty="normal"):
        leaderboard_file = self._get_leaderboard_path(difficulty)
        if os.path.exists(leaderboard_file):
            try:
                with open(leaderboard_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_leaderboard(self, difficulty="normal"):
        leaderboard_file = self._get_leaderboard_path(difficulty)
        os.makedirs(os.path.dirname(leaderboard_file), exist_ok=True)
        with open(leaderboard_file, 'w') as f:
            json.dump(self.leaderboards[difficulty], f, indent=2)
    
    def add_score(self, time_ms, level, difficulty="normal"):
        entry = {
            "time_ms": time_ms,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "formatted_time": self._format_time(time_ms)
        }
        
        self.leaderboards[difficulty].append(entry)
        self.leaderboards[difficulty].sort(key=lambda x: x["time_ms"])
        
        # Keep only top 10
        if len(self.leaderboards[difficulty]) > self.max_entries:
            self.leaderboards[difficulty] = self.leaderboards[difficulty][:self.max_entries]
        
        self.save_leaderboard(difficulty)
        
        # Return rank if in top 10
        for i, entry_data in enumerate(self.leaderboards[difficulty]):
            if entry_data["timestamp"] == entry["timestamp"]:
                return i + 1
        
        return None
    
    def get_leaderboard(self, difficulty="normal"):
        return self.leaderboards.get(difficulty, [])
    
    def _format_time(self, time_ms):
        total_ms = int(time_ms)
        minutes = (total_ms // 60000) % 60
        seconds = (total_ms // 1000) % 60
        milliseconds = total_ms % 1000
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
