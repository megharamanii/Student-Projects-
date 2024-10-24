from utils import BaseCharacter
from bot_utils import BaseBot


class HeadOnBot(BaseBot):
    def __init__(self) -> None:
        self.opponent_damage_dealers = []
        self.team_damage_dealers = []

    def make_assignment(self) -> list[dict]:

        assignment = self.previous_character_ordering
        highest_damage_char_idx = 0

        if self.team_damage_dealers:
            previous_order = self.previous_character_ordering
            self.team_damage_dealers.sort(key = lambda x: x[1])
            self.opponent_damage_dealers.sort(key = lambda x: x[1])
            for damage_dealer_idx in range(len(self.team_damage_dealers)):
                team_char_idx, _ = self.team_damage_dealers[damage_dealer_idx]
                placement_idx, _ = self.opponent_damage_dealers[damage_dealer_idx]
                assignment[placement_idx] = previous_order[team_char_idx]
            highest_damage_char_idx, _ = self.opponent_damage_dealers[-1]

        assignment[highest_damage_char_idx]["items"] = self.items

        return assignment

    def process_previous_round_stats(self,
                                     is_your_win: bool,
                                     your_team: list[BaseCharacter],
                                     opponent_team: list[BaseCharacter]) -> None:

        self.opponent_damage_dealers = [(char_idx, char.damage_stats.damage_dealt)
                                        for char_idx, char in enumerate(opponent_team)]
        self.team_damage_dealers = [(char_idx, char.damage_stats.damage_dealt)
                                        for char_idx, char in enumerate(your_team)]



