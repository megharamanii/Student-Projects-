from utils import BaseCharacter
from bot_utils import BaseBot

STAT_TO_MAX = {
    "ninja": "physical_power",
    "mage": "magic_power",
    "warrior": "hp"
}

class MaxxerBot(BaseBot):
    def __init__(self, character_to_max: str) -> None:
        self.character_to_max = character_to_max
        
        
    def make_assignment(self) -> list[dict]:      
        assignment = self.previous_character_ordering
        
        candidates = [(char_idx, char) for char_idx, char 
                        in enumerate(assignment) 
                        if char["character"]["name"] == self.character_to_max]
        if candidates:
            stat_to_maximize = STAT_TO_MAX[self.character_to_max]
            best_char_idx, best_char = max(
                candidates, key=lambda x: x[1]["character"]["stats"][stat_to_maximize])
        else:
            best_char_idx = 0 # no main characters found :(
        
        assignment.insert(-1, assignment.pop(best_char_idx))
        assignment[-1]["items"] = self.items
        
        return assignment
        
    def process_previous_round_stats(self, 
                                     is_your_win: bool, 
                                     your_team: list[BaseCharacter], 
                                     opponent_team: list[BaseCharacter]) -> None:
        pass
            
    
    
    
        
        