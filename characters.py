from utils import BaseCharacter, Stats, Damage, Attack

class Ninja(BaseCharacter):
    @property
    def name(self) -> str:
        return "Ninja"
    
    @property
    def special_attack_name(self) -> str:
        return (
            "Special Attack: A precise poisoned dagger shot designed to "
            "incapacitate most opponents"
        )
        
    @property
    def special_attack(self) -> Attack:
        damage = Damage(physical = 
            40 + .5 * self.effective_stats.physical_power +
                .5 * self.effective_stats.magic_power
            )
        description = (f"{self.name} performed {self.special_attack_name},"
                        f" dealing {damage.physical} Physical Damage.")
        return Attack(damage = damage, description = description)
        
class Mage(BaseCharacter):
    @property
    def name(self) -> str:
        return "Mage"
    
    @property
    def special_attack_name(self) -> str:
        return "Special Attack: A lullaby to deep sleep"
    
    @property
    def special_attack(self) -> Attack:
        damage = Damage(magic = 1 + 1.25 * self.effective_stats.magic_power)
        description = (f"{self.name} performed {self.special_attack_name},"
                       f" dealing {damage.magic} Magic Damage.")
        return Attack(damage = damage, description = description)


class Warrior(BaseCharacter):
    @property
    def name(self) -> str:
        return "Warrior"
    
    @property
    def special_attack_name(self) -> str:
        return "Special Attack: A call to the shield hero"
    
    @property
    def special_attack(self) -> Attack:
        healing_done = (50 + .75 * self.effective_stats.physical_power +
                        3 * self.effective_stats.magic_power)
        description = (f"{self.name} performed {self.special_attack_name},"
                       f" healing {healing_done} HP.")
        return Attack(stat_updates_to_self = Stats(current_hp = healing_done),  
                      description = description)
    