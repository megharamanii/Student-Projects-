from typing import NamedTuple
import abc
import math
import numpy as np
from dataclasses import dataclass
N_ITEMS = 3

class RngEngine:
    def __init__(self, seed: int = 56) -> None:
        """Create the RNG backend for the game

        NOTE: DO NOT create an instance of this class. 
                It is already created where needed

        Keyword Arguments:
            seed -- the psuedo rng seed to use (default: {56})
        """
        self._rand = np.random.default_rng(seed=seed)
        
    def rng(self, probability: float) -> bool:
        """Roll a dice with the probability and see if the result is 
            within that bet. 
            
            NOTE: DO NOT call this function. 
                It is already called where needed 

        Arguments:
            probability -- the probability of rolling the expected outcome, a number from [0-100]

        Returns:
            Whether or not the expected outcome was rolled. 
                True if it was, False otherwise
        """
        return self._rand.random() < (probability / 100)

class Stats(NamedTuple):
    current_hp: float = 0
    total_hp: float = 0
    armor: float = 0
    magic_resistance: float = 0
    physical_power: float = 0
    magic_power: float = 0
    special_trigger_chance: float = 0
    
    def add_stat_changes(self, changes: "Stats") -> "Stats":
        new_stats = {}
        for stat_name, [min_val, max_val] in [
                ["total_hp", [0, math.inf]],
                ["current_hp", [0, "total_hp"]],
                ["armor", [0, math.inf]],
                ["magic_resistance", [0, math.inf]],
                ["physical_power", [0, math.inf]],
                ["magic_power", [0, math.inf]],
                ["special_trigger_chance", [0, 100]]]:
            new_stat = getattr(self, stat_name) + getattr(changes, stat_name)
            if max_val == "total_hp":
                max_val = new_stats["total_hp"] # to cap current hp to new max hp
            normalized_stat = min(max_val, max(min_val, new_stat))
            new_stats[stat_name] = normalized_stat
        return Stats(**new_stats)
        
    def __str__(self) -> str:
        formatted_stats = [f"{formatted_name}: {stat:.1f}" 
            for formatted_name, stat in [
                ["Current HP", self.current_hp],
                ["Total HP", self.total_hp],
                ["Armor", self.armor],
                ["Magic Resistance", self.magic_resistance],
                ["Physical Power", self.physical_power],
                ["Magic Power", self.magic_power],
                ["Special Trigger Chance", self.special_trigger_chance]                                                
            ]
        ]
        return "\n".join(formatted_stats)
         
class Damage(NamedTuple):
    physical: float = 0
    magic: float = 0

class Attack(NamedTuple):
    damage: Damage = None
    stat_updates_to_self: Stats = None
    description: str = None

@dataclass
class DamageStats:
    """A class to store the damage stats of a character

    Attributes:
        damage_dealt: the total damage dealt by the character
        damage_taken: the total damage taken by the character
        damage_mitigated: the total damage mitigated by the character
        kills: the total number of kills the character has
        """
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    damage_mitigated: float = 0.0
    kills: int = 0

class BaseItem(abc.ABC):
    def __init__(self, base_item_stats: Stats, 
                 is_passive_active: bool = True) -> None:
        super().__init__()
        self.base_item_stats = base_item_stats
        self.is_passive_active = is_passive_active
        
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abc.abstractmethod
    def passive_name(self) -> str:
        pass
    
    @abc.abstractmethod
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        pass
    
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, BaseItem):
            return False
        else:
            return self.name == value.name
        
    def __str__(self) -> str:
        stats = str(self.base_item_stats).split("\n")
        useful_stats = []
        for stat in stats:
            _, stat_value = stat.split(":")
            stat_value = float(stat_value)
            if stat_value > 0:
                useful_stats.append(stat)
        if self.is_passive_active:
            useful_stats.append(self.passive_name)
        useful_stats = "\n".join(useful_stats)
        return f"{self.name}: \n{useful_stats}"
    

class BaseCharacter(abc.ABC):
    def __init__(self, base_stats: Stats) -> None:
        super().__init__()
        self.base_stats = base_stats
        self.added_item_stats = Stats()
        self.effective_stats = self.base_stats
        self.items = []
        self.damage_stats = DamageStats()
        
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abc.abstractmethod
    def special_attack_name() -> str:
        pass
    
    def add_item(self, item: BaseItem) -> None:
        if len(self.items) == N_ITEMS:
            raise ValueError("Attempted to add more items than allowed in game.")
            
        if "Unique Passive" in item.passive_name and item in self.items:
            item.is_passive_active = False
            
        self.items.append(item)
        self.added_item_stats = self.added_item_stats.add_stat_changes(
            item.calculate_effective_stats(self.base_stats))
        self.effective_stats = self.base_stats.add_stat_changes(
            self.added_item_stats)
        
    def __str__(self) -> str:
        formatted_stats = str(self.effective_stats).replace("\n", "\n\t")
        item_stats = ""
        for item_idx, item in enumerate(self.items):
            formatted_item_info = str(item).replace("\n", "\n\t\t\t")
            item_stats += f"\n\t\t{(item_idx + 1)}: {formatted_item_info}"
        if item_stats:
            formatted_item_stats = f"\n\t  with items {item_stats}"
        else:
            formatted_item_stats = ""
        return (f"{self.name}: \n\t{formatted_stats}" 
                f"{formatted_item_stats}")
        
    @property
    def basic_attack(self) -> Attack:
        damage = Damage(physical= self.effective_stats.physical_power)
        description = (f"{self.name} performed a Basic Attack, "
                        f"dealing {damage.physical} Physical Damage.")
        return Attack(damage = damage, description = description)
    
    @property
    @abc.abstractmethod
    def special_attack(self) -> Attack:
        pass
    