from utils import BaseCharacter
from bot_utils import BaseBot
import numpy as np


class RandomBot(BaseBot):
    def __init__(self, seed: int = 16) -> None:
        self.rand = np.random.default_rng(seed)
        
    def make_assignment(self) -> list[dict]:
        assignment = self.previous_character_ordering
        self.rand.shuffle(assignment)
        item_assignments = self.rand.choice(len(assignment), size=(len(self.items),))
        for item_idx, char_idx in enumerate(item_assignments):
            if not "items" in assignment[char_idx]:
                assignment[char_idx]["items"] = []
            assignment[char_idx]["items"].append(self.items[item_idx])
        
        return assignment
    
    def process_previous_round_stats(self, 
                                     is_your_win: bool, 
                                     your_team: list[BaseCharacter], 
                                     opponent_team: list[BaseCharacter]) -> None:
        pass