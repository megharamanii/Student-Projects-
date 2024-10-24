from pathlib import Path
from maxxer_bot import MaxxerBot
from ordering_bot import HeadOnBot
from your_bot import YourBot
from random_bot import RandomBot
from backend import play_round
from utils import RngEngine
import warnings
from functools import partial

N_ROUNDS = 5
N_WINS = 3

BOT_MAPPING = {
    "random": RandomBot,
    "warrior_maxxer": partial(MaxxerBot, character_to_max = "warrior"),
    "mage_maxxer": partial(MaxxerBot, character_to_max = "mage"),
    "ninja_maxxer": partial(MaxxerBot, character_to_max = "ninja"),
    "head_on": HeadOnBot,
    "your_bot": YourBot
}

DEFAULT_STARTING_ELO = 1800

current_elo = {bot: DEFAULT_STARTING_ELO for bot in BOT_MAPPING}


def calculate_elo(your_elo: int, opponent_elo: int,
                  is_your_win: bool) -> list[int, int]:
    """Calculate the new elo for both players after a match

    Arguments:
        your_elo -- your current elo
        opponent_elo -- the opponent's current elo
        is_your_win -- whether you won the match

    Returns:
        a list of the new elo for both players
        """
    K = 32
    expected_score_your = 1 / (1 + 10 ** ((opponent_elo - your_elo) / 400))
    actual_score_your = 1 if is_your_win else 0
    new_your_elo = your_elo + K * (actual_score_your - expected_score_your)
    new_opponent_elo = opponent_elo + K * ((1 - actual_score_your) - (1 - expected_score_your))
    return [int(new_your_elo), int(new_opponent_elo)]


def play_ranked(your_algo: str, opponent_algos: list[str], n_matches: int, 
                sample_match_dir: Path) -> None:
    """Play the ranked mode of the game, battling other bots with elo at the stake.

    Arguments:
        your_algo -- the algorithm to benchmark
        opponent_algos -- the opponent algorithm(s) to benchmark against
        n_matches -- th number of matches to use
        sample_match_dir -- the directory containing the sample starting assignments
    """
    for opponent_algo in opponent_algos:
        
        if opponent_algo == your_algo: # add prefix to prevent potential overlap
            opponent_algo = f"opponent__{opponent_algo}"
            BOT_MAPPING[opponent_algo] = BOT_MAPPING[your_algo]
            current_elo[opponent_algo] = current_elo[your_algo]
            
        rng_engine = RngEngine()
        n_match_wins = 0
        starting_elo = current_elo[your_algo]
        for match_idx in range(1, n_matches + 1):
            is_your_turn_first = rng_engine.rng(probability = 50)
            your_round_wins, opponent_round_wins = 0, 0
            your_assignments = sample_match_dir / f"match_{match_idx}" / "your_assignments"
            opponent_assignments =  sample_match_dir / f"match_{match_idx}" / "opponent_assignments"
            
            your_bot = BOT_MAPPING[your_algo]()
            opponent_bot = BOT_MAPPING[opponent_algo]()
            your_bot.initialize(your_assignments)
            opponent_bot.initialize(opponent_assignments)
            
            for round in range(1, N_ROUNDS + 1):        
                your_assignment = your_bot.make_assignment()
                your_bot.write_assignment(your_assignment)
                opponent_assignment = opponent_bot.make_assignment()
                opponent_bot.write_assignment(opponent_assignment)
                
                output = play_round(
                    your_assignment = your_assignments / f"{round}.json",
                    opponent_assignment = opponent_assignments / f"{round}.json",
                    is_your_turn_first = is_your_turn_first,
                    rng_engine = rng_engine
                )
                if len(output) == 3:
                    is_round_your_win, _, (your_team, opponent_team) = output
                    your_bot.process_previous_round_stats(
                        is_round_your_win, your_team, opponent_team)
                    opponent_bot.process_previous_round_stats(
                        not is_round_your_win, opponent_team, your_team)
                else:
                    is_round_your_win, _ = output
                    warnings.warn(("List of teams from play_round not found. "
                                   "Proceeding without the bots processing "
                                   "round data. Some bots will not perform correctly."))
                
                if is_round_your_win:
                    your_round_wins += 1
                else:
                    opponent_round_wins += 1

                is_your_turn_first = not is_your_turn_first
                is_match_over = your_round_wins == N_WINS or opponent_round_wins == N_WINS
                
                if is_match_over:
                    n_match_wins += 1 if is_round_your_win else 0
                    your_elo, opponent_elo = calculate_elo(
                        your_elo = current_elo[your_algo], 
                        opponent_elo = current_elo[opponent_algo], 
                        is_your_win= is_round_your_win)
                    current_elo[your_algo] = your_elo
                    current_elo[opponent_algo] = opponent_elo
                    break
        
        # undo the prefix we may have added
        opponent_algo = opponent_algo.removeprefix('opponent__') 
        
        print((f"{your_algo} won {n_match_wins/n_matches * 100:.1f}% ({n_match_wins}/{n_matches})"
               f" of the matches against {opponent_algo}, ending with {current_elo[your_algo]}"
                f"({'+' if current_elo[your_algo] >= starting_elo else '-'}"
                f"{abs(current_elo[your_algo] - starting_elo)}) elo."))

        


if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument("--your_bot", type=str, default="your_bot",
                        help="The bot to benchmark against the opponents")
    parser.add_argument("--opponent_bots", nargs="+", 
                        help= ("The opponents to benchmark against. "
                               "If left empty, will benchmark against "
                               "every bot besides your own"), 
                        default=None)
    parser.add_argument("--n_matches", type=int, default=25,
                        help="The number of matches to play agaisnt each bot")
    parser.add_argument("--sample_match_dir", type=str, default="./samples",
                        help="The directory of the same match team data")
    args = parser.parse_args()
    opponent_bots = args.opponent_bots
    if opponent_bots is None:
        opponent_bots = list(BOT_MAPPING.keys())
    if not isinstance(opponent_bots, list):
            opponent_bots = [opponent_bots]
    sample_match_dir = Path(args.sample_match_dir)
    play_ranked(args.your_bot, opponent_bots, args.n_matches, sample_match_dir)