from bot_utils import BaseBot
from utils import BaseCharacter
class YourBot(BaseBot):
    """
    Your bot should be a subclass of BaseBot and implement the following methods:

    make_assignment(self) -> list[dict]:
        This method should return a list of dictionaries, where each dictionary represents a character and has the following
        keys:
            - "character_id": The id of the character (int)
            - "items": A list of item ids that should be assigned to the character (list[int])
            - "assigned_to": The id of the character that the character is assigned to (int)

        The list should have the same length as the number of characters in the game, and each character should be assigned to
        exactly one character. The characters should be assigned to the opponent's characters, and the assignment should be

    process_previous_round_stats(self, is_your_win: bool, your_team: list[BaseCharacter], opponent_team: list[BaseCharacter]) -> None:

        This method will be called after each round, and should be used to process the stats of the previous round. The stats
        of the previous round are passed as arguments. The method should update the bot's internal state based on the stats.

        is_your_win: A boolean indicating whether your team won the previous round
        your_team: A list of BaseCharacter objects representing the characters in your team
        opponent_team: A list of BaseCharacter objects representing the characters in the opponent's team

    """
    def __init__(self) -> None:
        self.opponent_damage_dealers = []
        self.team_damage_dealers = []

    def make_assignment(self) -> list[dict]:
        """
        This method should return a list of dictionaries, where each dictionary represents a character and has the following
        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a character and has the following
                        keys:
                            - "character_id": The id of the character (int)
                            - "items": A list of item ids that should be assigned to the character (list[int])
                            - "assigned_to": The id of the character that the character is assigned to (int)
        """
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

        """
        This method will be called after each round, and should be used to process the stats of the previous round. The stats
        Args:
            is_your_win:
            your_team:
            opponent_team:

        Returns:

        """

        self.opponent_damage_dealers = [(char_idx, char.damage_stats.damage_dealt)
                                        for char_idx, char in enumerate(opponent_team)]
        self.team_damage_dealers = [(char_idx, char.damage_stats.damage_dealt)
                                        for char_idx, char in enumerate(your_team)]



