
from utils import BaseCharacter, Stats, Damage, RngEngine, DamageStats
from game import read_data

from pathlib import Path
from typing import Tuple, List


N_ROUNDS = 5
N_WINS = 3
DASHES = "-" * 20

def pretty_format_teams(your_team: list[BaseCharacter], 
                        opponent_team: list[BaseCharacter]) -> str:
    """Format the currently standing teams for printing

    Arguments:
        your_team -- the characters in your team still alive
        opponent_team -- the opponent team's characters still alive

    Returns:
        the pretty formatted string of the teams
    """
    your_team = [char.name for char in reversed(your_team)]
    opponent_team = [char.name for char in opponent_team]
    return f"\n\t{your_team} -----VS----- {opponent_team}"

def calculate_damage_taken(damage: Damage, character_stats: Stats) -> Tuple[float, float]:
    """ Calculate the damage taken by a character after mitigation.

    Arguments:
        damage -- the damage object to calculate the damage taken from
        character_stats -- the character's stats to calculate the mitigation

    Returns:
        a tuple containing the amount of damage taken and the amount mitigated
        """
    if character_stats is None:
        raise ValueError("Character stats cannot be None")

    mitigated_physical = damage.physical * character_stats.armor / 100
    mitigated_magic = damage.magic * character_stats.magic_resistance / 100

    hp_lost = 0
    if damage.physical:
        hp_lost += (damage.physical - mitigated_physical)
    if damage.magic:
        hp_lost += (damage.magic - mitigated_magic)

    return -hp_lost, mitigated_physical + mitigated_magic

def calculate_miss_chance(damage: Damage, character_stats: Stats) -> float:
    """ Calculate the chance of missing the attack based on the character's stats.

    Arguments:
        damage -- the damage object to calculate the miss chance for
        character_stats -- the character's stats to calculate the miss chance from

    Returns:
        the chance of missing the attack
    """
    if damage.magic > damage.physical:
        miss_chance = character_stats.magic_resistance / 10
    else:
        miss_chance = character_stats.armor / 10
    return miss_chance

def play_turn(your_character: BaseCharacter,
              opponent_character: BaseCharacter,
              is_your_turn: bool,
              rng_engine: RngEngine) -> str:
    """ Simulate a single turn in the game, updating the character's stats and returning a description of what happened in the turn.

    Arguments:
        your_character -- your character taking the turn
        opponent_character -- the opponent's character taking the turn
        is_your_turn -- whether it is your character's turn
        rng_engine -- the rng system handling the randomness in the game

    Returns:
        a string describing the turn's outcome
    """
    if any(char.effective_stats.current_hp <= 0 for char in [your_character, opponent_character]):
        raise ValueError("One of the characters is already dead.")

    attacking_char = your_character if is_your_turn else opponent_character
    defending_char = opponent_character if is_your_turn else your_character

    special_chance = attacking_char.effective_stats.special_trigger_chance
    is_attack_special = rng_engine.rng(probability=special_chance)
    attack = attacking_char.special_attack if is_attack_special else attacking_char.basic_attack

    if attack.stat_updates_to_self is not None:
        attacking_char.effective_stats = attacking_char.effective_stats.add_stat_changes(attack.stat_updates_to_self)

    miss_chance = calculate_miss_chance(attack.damage, defending_char.effective_stats)
    is_damage_missed = rng_engine.rng(probability=miss_chance)

    if is_damage_missed:
        description = f"{attacking_char.name} missed the attack on {defending_char.name}."
    else:
        damage_taken, mitigated_damage = calculate_damage_taken(attack.damage, defending_char.effective_stats)
        defending_char.effective_stats = defending_char.effective_stats.add_stat_changes(Stats(current_hp=damage_taken))
        defending_char.damage_stats.damage_mitigated += mitigated_damage

        total_damage = attack.damage.physical + attack.damage.magic
        attacking_char.damage_stats.damage_dealt += total_damage
        defending_char.damage_stats.damage_taken += total_damage

        description = f"{attacking_char.name} hit {defending_char.name} for {total_damage:.2f} damage."

        if defending_char.effective_stats.current_hp <= 0:
            description += f" {defending_char.name} has fainted."
            attacking_char.damage_stats.kills += 1

    return description

def play_round(your_assignment: Path,
               opponent_assignment: Path,
               is_your_turn_first: bool,
               rng_engine: RngEngine) -> Tuple[bool, List[str], Tuple[List[BaseCharacter], List[BaseCharacter]]]:
    """
    Simulates an entire round of combat between your bot's team and the opponent's team.

    Arguments:
        your_assignment -- the path to the JSON file containing your team's assignment for this round.
        opponent_assignment -- the path to the JSON file containing the opponent's team's assignment for this round.
        is_your_turn_first -- a boolean indicating whether your bot takes the first turn.
        rng_engine -- the random number generator engine to use.
    Returns:
        A tuple where the first element is a boolean indicating if your bot won the round,
        the second element is a list of strings describing each turn in the round,
        and the third element is a tuple of both teams' final states.
    """

    your_team = read_data(your_assignment)
    opponent_team = read_data(opponent_assignment)

    your_index = 0
    opponent_index = 0
    is_your_turn = is_your_turn_first

    battle_log = []

    while your_index < len(your_team) and opponent_index < len(opponent_team):
        your_character = your_team[your_index]
        opponent_character = opponent_team[opponent_index]
        turn_description = play_turn(your_character, opponent_character, is_your_turn, rng_engine)
        battle_log.append(turn_description)
        if opponent_character.effective_stats.current_hp <= 0:
            opponent_index += 1
        if your_character.effective_stats.current_hp <= 0:
            your_index += 1
        is_your_turn = not is_your_turn
    your_win = your_index < len(your_team)

    return your_win, battle_log, (your_team, opponent_team)



def play_match(your_assignments: Path,
               opponent_assignments: Path,
               rng_engine: RngEngine) -> tuple[bool, list[str]]:
    """Play the match out under the game engine. 

    Arguments:
        your_assignments -- your assignments for all rounds in the match
        opponent_assignments -- the opponent's assignments for all rounds in the match
        rng_engine -- the rng system handling the randomness in the game

    Returns:
        a tuple of the outcome and a list of the match breakdown:
            - whether you won or not: True if you did, False otherwise
            - the turn-by-turn breakdown of what happened throughout
    """
    
    is_your_turn_first = rng_engine.rng(probability= 50)
    your_wins, opponent_wins = 0, 0
    play_by_play_description = []
    for round in range(1, N_ROUNDS + 1):        
        play_by_play_description.append(f"\n{DASHES} Round {round}. {DASHES}")
        is_round_your_win, round_description = play_round(
            your_assignment = your_assignments / f"{round}.json",
            opponent_assignment = opponent_assignments / f"{round}.json",
            is_your_turn_first = is_your_turn_first,
            rng_engine = rng_engine
        )
        round_description = [f"\t{turn_description}" for turn_description in round_description]
        play_by_play_description.extend(round_description)
        
        if is_round_your_win:
            your_wins += 1
            round_outcome = "WIN"
        else:
            opponent_wins += 1
            round_outcome = "LOSS"
        play_by_play_description.append(
            f"\nOutcome: {round_outcome}. Series Score: {your_wins}-{opponent_wins}.")
        is_your_turn_first = not is_your_turn_first
        
        is_match_over = your_wins == N_WINS or opponent_wins == N_WINS
        if is_match_over:
            play_by_play_description.append(
                f"\n{DASHES} {round_outcome} {your_wins}-{opponent_wins}. {DASHES}")
            break
        
    return (your_wins > opponent_wins, play_by_play_description)
    
    
if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument("--your_assignments", 
                        type=str, 
                        help="The location of the team assignment file to read",
                        default="./your_assignments",
                        required=False)
    parser.add_argument("--opponent_assignments", 
                        type=str, 
                        help="The location of the team assignment file to read",
                        default="./opponent_assignments",
                        required=False)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    your_assignments = Path(args.your_assignments)
    opponent_assignments = Path(args.opponent_assignments)
    rng_engine = RngEngine()
    match_outcome, description = play_match(your_assignments=your_assignments, 
               opponent_assignments=opponent_assignments, 
               rng_engine=rng_engine)
    if args.out is not None:
        with open(args.out, "w") as f:
            print(*description, sep="\n", file=f)
    else:
        print(*description, sep="\n")