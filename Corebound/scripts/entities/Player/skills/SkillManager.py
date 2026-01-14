class SkillManager:
    """Manages unlocked skills and abilities for the player."""
    
    def __init__(self):
        self.skills = {
            'double_jump': {'unlocked': False, 'name': 'Double Jump'},
            'wall_slide': {'unlocked': False, 'name': 'Wall Slide'},
            'dash': {'unlocked': False, 'name': 'Dash'},
            'fighting_style': {'unlocked': False, 'name': 'Fighting Style'},
        }
    
    def unlock_skill(self, skill_name):
        """Unlock a skill and return whether it was successful."""
        if skill_name in self.skills:
            self.skills[skill_name]['unlocked'] = True
            return True
        return False
    
    def has_skill(self, skill_name):
        """Check if a skill is unlocked."""
        return self.skills.get(skill_name, {}).get('unlocked', False)
    
    def get_unlocked_skills(self):
        """Return list of unlocked skill names."""
        return [name for name, data in self.skills.items() if data['unlocked']]
    
    def reset_skills(self):
        """Reset all skills to locked."""
        for skill in self.skills:
            self.skills[skill]['unlocked'] = False
