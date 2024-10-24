from utils import BaseItem, Stats

class EnchantedSword(BaseItem):
    @property
    def name(self) -> str:
        return "Enchanted Sword"
    
    @property
    def passive_name(self) -> str:
        return ("Unique Passive: Lucky strike. Adds 5%(+25% of base Special "
                "Trigger Chance) to Special Trigger chance.")
        
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        if self.is_passive_active:
            passive_special_chance = 5 + (.25 * character_stats.special_trigger_chance)
        else:
            passive_special_chance = 0
        passive_stats = Stats(special_trigger_chance = passive_special_chance)
        return self.base_item_stats.add_stat_changes(passive_stats)
        
        
class ShinyStaff(BaseItem):
    @property
    def name(self) -> str:
        return "Shiny Staff"
    
    @property
    def passive_name(self) -> str:
        return ("Passive: Blessings of Echo. Adds 1(+50% of base Magic Power)"
                " to Magic Power.")
        
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        added_magic_power = 1 + .5 * character_stats.magic_power
        passive_stats = Stats(magic_power = added_magic_power)
        return self.base_item_stats.add_stat_changes(passive_stats)
    
    
class MagicCauldron(BaseItem):
    @property
    def name(self) -> str:
        return "A magic cauldron"
    
    @property
    def passive_name(self) -> str:
        return ("Unique Passive: Potion of life. Adds 10(+30% of base HP) to HP")
    
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        if self.is_passive_active:
            passive_hp = 10 + .3 * character_stats.total_hp
        else:
            passive_hp = 0
        passive_stats = Stats(current_hp=passive_hp, total_hp=passive_hp)
        return self.base_item_stats.add_stat_changes(passive_stats)
    
class Pole(BaseItem):
    @property
    def name(self) -> str:
        return "A Pole"
    
    @property
    def passive_name(self) -> str:
        return ""
     
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        return self.base_item_stats
    
    
class SolidRock(BaseItem):
    @property
    def name(self) -> str:
        return "A solid rock"
    
    @property
    def passive_name(self) -> str:
        return ""
    
    def calculate_effective_stats(self, character_stats: Stats) -> Stats:
        return self.base_item_stats
