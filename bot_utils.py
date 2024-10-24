import json
import abc
from pathlib import Path
from copy import deepcopy
from utils import BaseCharacter

N_ROUNDS = 5

class BaseBot(abc.ABC):
    
    def initialize(self, assignment_dir: Path) -> None:
        """Read the blank team data, resetting 

        Arguments:
            assignment_dir -- _description_
        """
        self.assignment_dir = assignment_dir
        
        with open(assignment_dir / "team_data.json", "r") as f:
            data = json.load(f)
        self.characters = data["characters"]
        self.items = data["items"]
        self._previous_character_ordering = self.characters
        self.previous_damage_stats = []
        self.is_initialized = True
        self.current_round = 1
        
    @property
    def previous_character_ordering(self) -> list[BaseCharacter]:
        """Obtain a modifiable copy of the previous round character ordering,
            useful as a base to make a new assignment

        Returns:
            the character ordering, a list of character data without any items
        """
        return deepcopy(self._previous_character_ordering)
    
    def write_assignment(self, assignment: list[dict]) -> None:
        """Write the team assignment to the current round, 
        resetting the previous assignment and current round counter

        Arguments:
            assignment -- the team assignment to write 

        Raises:
            ValueError: if this function in inappropriately called
        """
        if not self.current_round <= N_ROUNDS or not self.is_initialized:
            raise ValueError("Cannot create an assignment with invalid data")
        with open(self.assignment_dir / f"{self.current_round}.json", "w") as f:
            json.dump(assignment, f, indent=4)
        current_assignment = deepcopy(assignment)
        for char_idx in range(len(current_assignment)):
            if "items" in current_assignment[char_idx]:
                del current_assignment[char_idx]["items"]
        self._previous_character_ordering = current_assignment
        self.current_round += 1
        
    @abc.abstractmethod
    def make_assignment(self) -> list[dict]:
        """Create the finalized assignment for this round, reordering the 
            characters and placing the items.

        Returns:
            the mapping (exactly as loaded from the json files in previous labs)
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def process_previous_round_stats(self, 
                                     is_your_win: bool,
                                     your_team: list[BaseCharacter], 
                                     opponent_team: list[BaseCharacter]) -> None:
        """Process the previous round data, doing anything necessary for 
            make_assignment to work properly in the next round.
        

        Arguments:
            is_your_win -- whether your bot won the round or not
            your_team -- your team from previous assignment 
            opponent_team -- the opponent's team
        """
        raise NotImplementedError
        

