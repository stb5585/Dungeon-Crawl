###########################################
""" spell manager """

# Imports
import random
import time
from textwrap import wrap


class Ability:
    """
    name: name of the ability
    description: description of the ability that explains what it does in so many words
    cost: amount of mana required to cast spell
    combat: boolean indicating whether the ability can only be cast in combat
    passive: boolean indicating whether the ability is passively active
    typ: the type of the ability
    subtyp: the subtype of the ability
    """
    def __init__(self, name, description, cost):
        self.name = name
        self.description = "\n".join(wrap(description, 35))
        self.cost = cost
        self.combat = True
        self.passive = False
        self.typ = ""
        self.subtyp = ""

    def __str__(self):
        str_text = (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                    f"{self.description}\n"
                    f"{35*'-'}\n"
                    f"Type: {self.typ}\n"
                    f"Sub-Type: {self.subtyp}\n")
        if not self.passive:
            str_text += f"Mana Cost: {self.cost}\n"
        else:
            str_text += "Passive\n"
        str_text += f"==================================="
        return str_text
    
    def special_effect(self, caster, target, damage, crit):
        return ""


class Skill(Ability):
    """
    typ: the type of these abilities is 'Skill'
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Skill'
        self.weapon = False

    def use(self, user, target=None, cover=False):
        pass


class Spell(Ability):
    """
    typ: the type of these abilities is 'Spell'
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.typ = 'Spell'

    def cast(self, caster, target=None, cover=False):
        pass


"""
Skill section
"""
class Offensive(Skill):
    """
    subtyp: the subtype of these abilities is 'Offensive', meaning they either inflict damage or some other status
        effect
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Offensive'


class Defensive(Skill):
    """
    subtyp: the subtype of these abilities is 'Defensive', meaning they work to protect the user
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Defensive'


class Stealth(Skill):
    """
    subtyp: the subtype of these abilities is 'Stealth', meaning they work through subterfuge of some kind
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Stealth'


class Enhance(Skill):
    """
    subtyp: the subtype of these abilities is 'Enhance', meaning they enhance the user
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Enhance'


class Drain(Skill):
    """
    subtyp: the subtype of these abilities is 'Drain', meaning they drain health and/or mana from the enemy
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Drain'


class Class(Skill):
    """
    subtyp: the subtype of these abilities is 'Class', meaning they are specific to a particular class
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Class'


class Truth(Skill):
    """
    subtyp: the subtype of these abilities is 'Truth', specific to Inquisitor/Seeker classes
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Truth'


class MartialArts(Skill):
    """
    subtyp: the subtype of these abilities is 'Martial Arts', specific to Monk/Master Monk classes
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Martial Arts'


class Luck(Skill):
    """
    subtyp: the subtype of these abilities is 'Luck', meaning they rely mostly on luck (charisma)
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Luck'


class PowerUp(Skill):
    """
    subtyp: the subtype of these abilities is 'Power Up', special abilities given for retrieving the Power Core
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Power Up'


# Skills #
# Offensive
class ShieldSlam(Offensive):
    """
    Cannot crit with Shield Slam
    multiplier indicates the factor by which the damage is calculated
    """

    def __init__(self):
        super().__init__(name='Shield Slam', description='Slam the enemy with your shield, damaging with a chance to '
                                                         'stun for several turns.',
                         cost=8)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        dodge = target.dodge_chance(user) > random.random()
        if any(target.status_effects[x].active for x in ['Sleep', 'Stun', 'Prone']):
            hit = True
            dodge = False
        else:
            hit_per = user.hit_chance(target, typ='weapon')
            hit = hit_per > random.random()
        if dodge:
            use_str += f"{target.name} evades {user.name}'s attack.\n"
        else:
            dam_red = target.check_mod('armor', enemy=user)
            damage = max(1, user.stats.strength + user.equipment['OffHand'].weight)
            if hit and target.status_effects["Duplicates"].active:
                if random.randint(0, target.status_effects["Duplicates"].duration):
                    hit = False
                    use_str += (f"{user.name} swings their shield but hits a mirror image of {target.name} and it "
                                f"vanishes from existence.\n")
                    target.status_effects["Duplicates"].duration -= 1
                    if not target.status_effects["Duplicates"].duration:
                        target.status_effects["Duplicates"].active = False
            if hit and cover:
                use_str += (f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                            f"{target.name}.\n")
            elif hit:
                resist = target.check_mod('resist', enemy=user, typ='Physical')
                damage = max(0, int((damage - dam_red) * (1 - resist)))
                if hit and damage > 0:
                    if target.status_effects['Mana Shield'].active:
                        mana_loss = damage // target.status_effects['Mana Shield'].duration
                        if mana_loss > target.mana.current:
                            abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                            use_str += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                            damage -= abs_dam
                            target.mana.current = 0
                            target.status_effects['Mana Shield'].active = False
                            use_str += f"The mana shield dissolves around {target.name}.\n"
                        else:
                            use_str += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                            target.mana.current -= mana_loss
                            damage = 0
                    elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                        if damage >= target.status_effects['Power Up'].extra:
                            use_str += (f"The shield around {target.name} absorbs "
                                       f"{target.status_effects['Power Up'].extra} damage.\n")
                            damage -= target.status_effects['Power Up'].extra
                            target.status_effects['Power Up'].active = False
                            use_str += f"The shield dissolves around {target.name}.\n"
                        else:
                            use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                            target.status_effects['Power Up'].extra -= damage
                            damage = 0
                if damage == 0:
                    use_str += f"{user.name} hits {target.name} with their shield but it does no damage.\n"
                else:
                    target.health.current -= damage
                    use_str += f"{user.name} damages {target.name} with Shield Slam for {damage} hit points.\n"
                    if target.is_alive() and not target.status_effects['Stun'].active:
                        if random.randint(0, user.stats.strength) \
                                > random.randint(target.stats.strength // 2, target.stats.strength):
                            turns = max(1, user.stats.strength // 8)
                            target.status_effects['Stun'].active = True
                            target.status_effects['Stun'].duration = turns
                            use_str += f"{target.name} is stunned.\n"
                        else:
                            use_str += f"{user.name} fails to stun {target.name}.\n"
            else:
                use_str += f"{user.name} swings their shield at {target.name} but miss entirely.\n"
        return use_str


class DoubleStrike(Offensive):

    def __init__(self):
        super().__init__(name='Double Strike', description='Perform two melee attacks at normal damage.',
                         cost=14)
        self.strikes = 2  # number of strikes performed
        self.weapon = True

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        for _ in range(self.strikes):
            wd_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=1.0)
            use_str += wd_str
            if not target.is_alive():
                break
        return use_str


class TripleStrike(DoubleStrike):
    """
    Replaces Double Strike
    """

    def __init__(self):
        super().__init__()
        self.name = "Triple Strike"
        self.description = "\n".join(wrap("Perform three melee attacks at normal damage.", 35))
        self.strikes = 3
        self.cost = 26


class FlurryBlades(TripleStrike):
    """
    Replaces Triple Strike
    """

    def __init__(self):
        super().__init__()
        self.name = "Flurry of Blades"
        self.description = "\n".join(wrap("Perform four melee attacks at normal damage.", 35))
        self.strikes = 4
        self.cost = 40


class PiercingStrike(Offensive):

    def __init__(self):
        super().__init__(name='Piercing Strike', description="Pierces the enemy\'s defenses, ignoring armor and "
                                                             "defenses.",
                         cost=5)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=1.25, ignore=True)
        return use_str


class TrueStrike(Offensive):

    def __init__(self):
        super().__init__(name='True Strike', description="Attack that is guaranteed to hit.",
                         cost=12)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=1.25, hit=True)
        return use_str


class TruePiercingStrike(Offensive):

    def __init__(self):
        super().__init__(name='True Piercing Strike', description="Attack that is guaranteed to hit and that pierces "
                                                                  "the enemy\'s defenses, ignoring armor and defenses.",
                         cost=15)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=1.25, ignore=True, hit=True)
        return use_str


class Jump(Offensive):

    def __init__(self):
        super().__init__(name='Jump', description='Leap into the air and bring down your weapon onto the enemy, '
                                                  'delivering critical damage.',
                         cost=10)
        self.strikes = 1
        self.crit = 2
        self.weapon = True

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        for _ in range(self.strikes):
            wd_str, _, _ = user.weapon_damage(target, cover=cover, crit=self.crit)
            use_str += wd_str
            if not target.is_alive():
                break
        return use_str


class DoubleJump(Jump):
    """
    Replaces Jump
    """

    def __init__(self):
        super().__init__()
        self.name = "Double Jump"
        self.strikes = 2
        self.cost = 25


class TripleJump(DoubleJump):
    """
    Replaces Double Jump
    """

    def __init__(self):
        super().__init__()
        self.name = "Triple Jump"
        self.strikes = 3
        self.cost = 40


class DoubleCast(Offensive):

    def __init__(self):
        super().__init__(name='Doublecast', description='Cast multiple spells in a single turn.',
                         cost=10)
        self.cast = 2

    def use(self, user, target=None, cover=False, game=None):
        import utils
        use_str = ""
        user.mana.current -= self.cost
        j = 0
        while j < self.cast:
            spell_list = []
            for entry in user.spellbook['Spells']:
                if user.spellbook['Spells'][entry].cost <= user.mana.current:
                    if user.spellbook['Spells'][entry].name != 'Magic Missile':
                        if user.cls:
                            spell_list.append(str(entry) + '  ' + str(user.spellbook['Spells'][entry].cost))
                        else:
                            spell_list.append(str(entry))
            if len(spell_list) == 0:
                use_str += f"{user.name} does not have enough mana to cast any spells with {self.name}.\n"
                user.mana.current += self.cost
                break
            if game:
                choices = ['first', 'second', 'third']
                popup = utils.SelectionPopupMenu(game, f"Select the {choices[j]} spell", spell_list)
                spell_index = popup.navigate_popup()
                spell = user.spellbook['Spells'][spell_list[spell_index].rsplit('  ', 1)[0]]
            else:
                spell_index = random.choice(spell_list)
                spell = user.spellbook['Spells'][spell_index]
            cast_message = spell.cast(user, target=target, cover=cover)
            use_str += cast_message
            j += 1
            if not target.is_alive():
                break
        return use_str


class TripleCast(DoubleCast):
    """
    Replaces DoubleCast
    """

    def __init__(self):
        super().__init__()
        self.name = "Triplecast"
        self.cast = 3
        self.cost = 20


class MortalStrike(Offensive):
    """
    Critical strike plus bleed; duration and damage determined by the player's strength
    """

    def __init__(self):
        super().__init__(name='Mortal Strike', description='Assault the enemy, striking them with a critical hit and '
                                                           'placing a bleed effect that deals damage. Requires a 2-handed '
                                                           'weapon.',
                         cost=10)
        self.crit = 2
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target, cover=cover, crit=self.crit)
        if hit and target.is_alive() and not target.status_effects['Bleed'].active:
            bleed_dmg = int(user.stats.strength * crit)
            if random.randint(bleed_dmg // 2, bleed_dmg) > random.randint(target.stats.con // 2, target.stats.con):
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'].active = True
                target.status_effects['Bleed'].duration = max(user.stats.strength // 10, target.status_effects["Bleed"].duration)
                target.status_effects['Bleed'].extra = max(bleed_dmg, target.status_effects["Bleed"].extra)
                use_str += f"{target.name} is bleeding.\n"
        return use_str


class MortalStrike2(MortalStrike):
    """
    Devastating critical strike plus bleed; duration and damage determined by the player's strength
    """

    def __init__(self):
        super().__init__()
        self.crit = 3
        self.cost = 30


class BattleCry(Offensive):

    def __init__(self):
        super().__init__(name="Battle Cry", description="Unleash a furious scream, increasing your attack damage for "
                                                        "several turns.",
                         cost=16)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        turns = max(5, user.stats.strength // 5)
        dmg_mod = random.randint(user.stats.strength // 4, user.stats.strength)
        user.status_effects['Attack'].active = True
        user.status_effects['Attack'].duration = max(user.status_effects['Attack'].duration, turns)
        user.status_effects['Attack'].extra += dmg_mod
        return f"{user.name}'s attack damage increases by {dmg_mod}.\n"


class Charge(Offensive):
    """
    Can stun then attacks at 3/4 damage, as opposed to other abilities that attack then stun
    """

    def __init__(self):
        super().__init__(name="Charge", description="Charge the enemy, possibly stunning them for the turn and doing "
                                                    "weapon damage.",
                         cost=10)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        if random.randint(user.stats.strength // 2, user.stats.strength) > \
                random.randint(target.stats.con // 2, target.stats.con) and \
                    not target.status_effects['Stun'].active and \
                        not target.status_effects['Mana Shield'].active:
            target.status_effects["Stun"].active = True
            target.status_effects["Stun"].duration = 1
            use_str += f"{user.name} stunned {target.name}.\n"
        wd_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=0.75)
        use_str += wd_str
        return use_str


# Defensive skills
class ShieldBlock(Defensive):
    """
    Passive ability
    """

    def __init__(self):
        super().__init__(name='Shield Block', description="You are much more proficient with a shield than most, "
                                                          "increasing the amount of damage blocked by 25% when using "
                                                          "a shield.",
                         cost=0)
        self.passive = True


class Parry(Defensive):
    """
    Passive ability
    """

    def __init__(self):
        super().__init__(name='Parry', description='Passive chance to counterattack if an attack is successfully '
                                                   'dodged.',
                         cost=0)
        self.passive = True


class Disarm(Defensive):

    def __init__(self):
        super().__init__(name='Disarm', description="Surprise the enemy by attacking their weapon, knocking it out of "
                                                    "their grasp. Disarmed characters have lower chance to hit and "
                                                    "can't use certain abilities.",
                         cost=4)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            user.mana.current -= self.cost
        if target.equipment["Weapon"].subtyp not in ["Natural", "None"]:
            if not target.status_effects["Disarm"].active:
                chance = target.check_mod("luck", enemy=user, luck_factor=10)
                max_stat = max(user.stats.strength, user.stats.dex)
                if random.randint(max_stat // 2, max_stat) \
                        > random.randint(0, target.stats.dex) + chance:
                    target.status_effects['Disarm'].active = True
                    target.status_effects['Disarm'].duration = -1
                    return f"{target.name} is disarmed.\n"
                return f"{user.name} fails to disarm the {target.name}.\n"
            return f"{target.name} is already disarmed.\n"
        return f"The {target.name} cannot be disarmed.\n"


class Cover(Defensive):
    """
    Familiar only skill
    """

    def __init__(self):
        super().__init__(name="Cover", description="You stand in the way in the face of attack, protecting your master"
                                                   " from harm.",
                         cost=0)
        self.passive = True


class Goad(Defensive):

    def __init__(self):
        super().__init__(name='Goad', description="Insult the enemy, sending them into a blind rage.",
                         cost=12)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            user.mana.current -= self.cost
        if random.randint(0, user.stats.strength // 2) > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            target.status_effects['Berserk'].active = True
            target.status_effects['Berserk'].duration = max(5, user.stats.strength // 5)
            use_str = f"{target.name} is enraged.\n"
        else:
            use_str = f"{target.name} is not so easily provoked.\n"
        return use_str


# Stealth skills
class Backstab(Stealth):

    def __init__(self):
        super().__init__(name='Backstab', description="Strike a stunned opponent in the back, ignoring any defense or "
                                                      "armor and dealing devastating damage.",
                         cost=6)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=2.0, ignore=True)
        return use_str


class PocketSand(Stealth):

    def __init__(self):
        super().__init__(name='Pocket Sand', description='Throw sand in the eyes of your enemy, blinding them and '
                                                         'reducing their chance to hit on a melee attack for 5 turns.',
                         cost=8)

    def use(self, user, target=None, fam=False, cover=False):
        if not fam:
            user.mana.current -= self.cost
        if not target.status_effects['Blind'].active:
            if random.randint(user.stats.dex // 2, user.stats.dex) \
                    > random.randint(0, target.stats.dex):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = -1
                return f"{target.name} is blinded.\n"
            return f"{user.name} fails to blind {target.name}.\n"
        return f"{target.name} is already blinded.\n"


class SleepingPowder(Stealth):

    def __init__(self):
        super().__init__(name="Sleeping Powder", description="Releases a powerful toxin that puts the target to sleep.",
                         cost=11)
        self.turns = 2

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        if not target.status_effects['Sleep'].active:
            mag_def = target.check_mod('magic def', enemy=user)
            if random.randint(user.stats.dex // 2, user.stats.dex) > random.randint(0, mag_def):
                target.status_effects['Sleep'].active = True
                target.status_effects['Sleep'].duration = self.turns
                return f"{target.name} is asleep.\n"
            return f"{user.name} fails to put {target.name} to sleep.\n"
        return f"{target.name} is already asleep.\n"


class KidneyPunch(Stealth):

    def __init__(self):
        super().__init__(name='Kidney Punch', description='Punch the enemy in the kidney, rendering them stunned.',
                         cost=12)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target, cover=cover)
        if not target.status_effects['Stun'].active:
            if hit and target.is_alive() and \
                not (target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active):
                if random.randint(0, int(user.stats.dex * crit)) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    target.status_effects['Stun'].active = True
                    target.status_effects['Stun'].duration = max(2, user.stats.dex // 8)
                    use_str += f"{target.name} is stunned.\n"
                else:
                    use_str += f"{user.name} fails to stun {target.name}.\n"
        return use_str


class SmokeScreen(Stealth):

    def __init__(self):
        super().__init__(name='Smoke Screen', description='Obscure the player in a puff of smoke, allowing the '
                                                          'player to flee without fail.',
                         cost=5)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str = ""
        return use_str


class Steal(Stealth):

    def __init__(self):
        super().__init__(name='Steal', description='Relieve the enemy of their items or gold.',
                         cost=6)

    def use(self, user, target=None, crit=1, mug=False, fam=False, cover=False):
        if not (mug and fam):
            user.mana.current -= self.cost
        gold_or_item = random.choice(["Gold", "Item"])
        if gold_or_item == "Item":
            if len(target.inventory) != 0:
                chance = user.check_mod('luck', enemy=target, luck_factor=16)
                if random.randint(int(user.stats.dex * crit) // 2, int(user.stats.dex * crit)) + chance > \
                        random.randint(target.stats.dex // 2, target.stats.dex):
                    item_key = random.choice(list(target.inventory))
                    item = target.inventory[item_key][0]
                    target.modify_inventory(item, subtract=True)
                    try:
                        user.modify_inventory(item)
                    except AttributeError:
                        pass
                    return f"{user.name} steals {item_key} from {target.name}.\n"
                return "Steal fails.\n"
            return f"{target.name} doesn't have anything to steal.\n"
        gold_amount = random.randint(1, max(1, int(target.gold * 0.05)))  # max of 5% of gold
        user.gold += gold_amount
        target.gold -= gold_amount
        return f"{user.name} steals {gold_amount} gold from {target.name}.\n"


class Mug(Stealth):

    def __init__(self):
        super().__init__(name='Mug', description='Attack the enemy with a chance to steal their items.',
                         cost=20)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target, cover=cover)
        if hit:
            use_str += Steal().use(user, target, crit=crit, mug=True)
        return use_str


class Lockpick(Stealth):

    def __init__(self):
        super().__init__(name='Lockpick', description='Unlock a locked chest.',
                         cost=0)
        self.passive = True


class PoisonStrike(Stealth):

    def __init__(self):
        super().__init__(name='Poison Strike', description='Attack the enemy with a chance to poison.',
                         cost=14)
        self.damage = 0.05  # 5% of target's max health per turn
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target, cover=cover)
        if not target.status_effects['Poison'].active:
            if hit and target.is_alive():
                resist = target.check_mod('resist', enemy=user, typ='Poison')
                if resist < 1:
                    if random.randint(user.stats.dex // 2, user.stats.dex) * crit * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        turns = max(5, user.stats.dex // 5)
                        pois_dmg = int(target.health.max * self.damage * (1 - resist))
                        target.status_effects['Poison'].active = True
                        target.status_effects['Poison'].duration = max(turns, target.status_effects["Poison"].duration)
                        target.status_effects['Poison'].extra = max(pois_dmg, target.status_effects["Poison"].extra)
                        use_str += f"{target.name} is poisoned.\n"
                    else:
                        use_str += f"{target.name} resists the poison.\n"
                else:
                    use_str += f"{target.name} is immune to poison.\n"
        return use_str


class SneakAttack(Stealth):
    """
    only usable when target is prone, stunned, or asleep
    """

    def __init__(self):
        super().__init__(name="Sneak Attack", description="If the target is incapacitated, unleash a devastating "
                                                          "attack.",
                         cost=15)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        if target.incapacitated():
            use_str, _, _ = user.weapon_damage(target, dmg_mod=2.0, crit=2, ignore=True, cover=cover)
        else:
            use_str = f"{self.name} is ineffective against {target.name}."
        return use_str


# Enhance skills
class ImbueWeapon(Enhance):

    def __init__(self):
        super().__init__(name='Imbue Weapon', description='Imbue your weapon with magical energy to enhance the '
                                                          'weapon\'s damage.',
                         cost=12)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        dmg_mod = max(1., user.stats.intel / 15)
        use_str += f"{user.name}'s weapon has been imbued with arcane power, increasing damage by {dmg_mod}."
        dmg_str, _, _ = user.weapon_damage(target, cover=cover, dmg_mod=dmg_mod)
        use_str += dmg_str
        return use_str


class EnhanceBlade(Enhance):
    """
    Level * (Current Mana / Max Mana)
    """

    def __init__(self):
        super().__init__(name='Enhance Blade', description="The Spellblade has an innate ability to increase melee "
                                                           "damage based on the percentage of mana used.",
                         cost=0)
        self.passive = True


class EnhanceArmor(Enhance):

    def __init__(self):
        super().__init__(name='Enhance Armor', description='The Knight Enchanter can imbue their armor with arcane '
                                                           'power, improving their defense modified by their '
                                                           'intelligence multiplied by the percentage of their mana.',
                         cost=0)
        self.passive = True


class ManaShield(Enhance):
    """
    Reduction indicates how much damage a single mana point reduces
    """

    def __init__(self):
        super().__init__(name="Mana Shield", description="A protective shield envelopes the caster, absorbing 2 damage "
                                                         "at the expense of every 1 mana.",
                         cost=4)
        self.reduction = 2

    def use(self, user, target=None, cover=False):
        use_str = ""
        target = user
        if not target.status_effects['Mana Shield'].active:
            user.mana.current -= self.cost
            target.status_effects['Mana Shield'].active = True
            target.status_effects['Mana Shield'].duration = self.reduction
            use_str += f"A mana shield envelopes {target.name}.\n"
        else:
            use_str += f"The mana shield dissolves around {target.name}.\n"
            target.status_effects['Mana Shield'].active = False
        return use_str


class ManaShield2(ManaShield):

    def __init__(self):
        super().__init__()
        self.description = "A protective shield envelopes the caster, absorbing 4 damage at the expense of every 1 mana.",
        self.reduction = 4


class ElementalStrike(Enhance):

    def __init__(self):
        super().__init__(name="Elemental Strike", description='Attack the enemy with your weapon and a random '
                                                              'elemental spell.',
                         cost=15)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            spell_list = [Scorch(),
                          WaterJet(),
                          Tremor(),
                          Gust()]
            spell = random.choice(spell_list)
            use_str += f"The enemy is struck by the elemental force of {spell.subtyp}."
            use_str += spell.cast(user, target=target, special=True, cover=cover)
            if crit > 1 and target.is_alive():
                use_str += spell.cast(user, target=target, special=True, cover=cover)
        return use_str


# Drain skills
class HealthDrain(Drain):

    def __init__(self):
        super().__init__(name='Health Drain', description='Drain the enemy, absorbing their health.',
                         cost=10)

    def use(self, user, target=None, special=False, cover=False):
        if not special:
            user.mana.current -= self.cost
        drain = random.randint((user.health.current + user.stats.charisma) // 5,
                               (user.health.current + user.stats.charisma) // 1.5)
        chance = target.check_mod('luck', enemy=user, luck_factor=1)
        if not random.randint(user.stats.wisdom // 2, user.stats.wisdom) > random.randint(0, target.stats.wisdom // 2) + chance:
            drain = drain // 2
        drain = min(drain, target.health.current)
        target.health.current -= drain
        user.health.current += drain
        user.health.current = min(user.health.current, user.health.max)
        return f"{user.name} drains {drain} health from {target.name}.\n"


class ManaDrain(Drain):

    def __init__(self):
        super().__init__(name='Mana Drain', description='Drain the enemy, absorbing their mana.',
                         cost=0)

    def use(self, user, target=None, special=False, cover=False):
        if not special:
            user.mana.current -= self.cost
        drain = random.randint((user.mana.current + user.stats.charisma) // 5,
                               (user.mana.current + user.stats.charisma) // 1.5)
        chance = target.check_mod('luck', enemy=user, luck_factor=10)
        if not random.randint(user.stats.wisdom // 2, user.stats.wisdom) > random.randint(0, target.stats.wisdom // 2) + chance:
            drain = drain // 2
        drain = min(drain, target.mana.current)
        target.mana.current -= drain
        user.mana.current += drain
        user.mana.current = min(user.mana.current, user.mana.max)
        return f"{user.name} drains {drain} mana from {target.name}.\n"


class HealthManaDrain(Drain):
    """
    Replaces Health Drain
    """

    def __init__(self):
        super().__init__(name='Health/Mana Drain', description='Drain the enemy, absorbing the health and mana in '
                                                               'return.',
                         cost=0)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str = HealthDrain().use(user, target, special=True)
        use_str += ManaDrain().use(user, target, special=True)
        return use_str


# Class skills
class LearnSpell(Class):

    def __init__(self):
        super().__init__(name='Learn Spell', description='Enables a diviner to learn rank 1 enemy spells.',
                         cost=0)
        self.passive = True


class LearnSpell2(LearnSpell):
    """
    Replaces Learn Spell
    """

    def __init__(self):
        super().__init__()
        self.description = "\n".join(wrap("Enables a diviner to learn rank 2 enemy spells.", 35))


class Transform(Class):
    """
    Panther
    """

    def __init__(self):
        super().__init__(name='Transform', description="Transforms the druid into a Panther, assuming the spells and "
                                                       "abilities inherent to the creature.",
                         cost=0)

    def use(self, user):
        from enemies import Panther
        user.transform_type = Panther()
        return ""


class Transform2(Transform):
    """
    Direbear
    """

    def __init__(self):
        super().__init__()
        self.description = "Transforms the druid into a Direbear, assuming the spells and abilities inherent to the creature."

    def use(self, user):
        from enemies import Direbear
        user.transform_type = Direbear()
        return ""


class Transform3(Transform):
    """
    Werewolf
    """

    def __init__(self):
        super().__init__()
        self.description = "Transforms the druid into a Werewolf, assuming the spells and abilities inherent to the creature."

    def use(self, user):
        from enemies import Werewolf
        user.transform_type = Werewolf()
        return ""


class Transform4(Transform):
    """
    Red Dragon; learned only from defeating the Red Dragon
    """

    def __init__(self):
        super().__init__()
        self.description = "Transforms the druid into a Red Dragon, assuming the spells and abilities inherent to the creature."

    def use(self, user):
        from enemies import RedDragon
        user.transform_type = RedDragon()
        return ""


class Familiar(Class):

    def __init__(self):
        super().__init__(name="Familiar", description="The warlock gains the assistance of a familiar, a magic serving "
                                                      "as both a pet and a helper. The familiar's abilities rely on its"
                                                      " master's statistics and resources.",
                         cost=0)
        self.passive = True


class Familiar2(Familiar):

    def __init__(self):
        super().__init__()
        self.description = "\n".join(wrap("The warlock's familiar gains strength, unlocking additional abilities.", 35))


class Familiar3(Familiar):

    def __init__(self):
        super().__init__()
        self.description = "\n".join(wrap("The warlock's familiar gains additional strength, unlocking even more "
                                          "abilities.", 35))


class AbsorbEssence(Class):
    """
    Currently 5% chance
    Different monster types improve different stats
    Reptile: increase strength
    Aberration: increase intelligence
    Slime: increase wisdom
    Construct: increase constitution
    Humanoid: increase charisma
    Insect: increase dexterity
    Animal: increase max health
    Monster: increase max mana
    Undead: increase level
    Dragon: increase gold
    """

    def __init__(self):
        super().__init__(name='Absorb Essence', description='When a Soulcatcher kills an enemy, there is a chance that '
                                                            'they may absorb part of the enemy\'s essence, increasing '
                                                            'a random statistic.',
                         cost=0)
        self.passive = True


class Reveal(Truth):
    """
    gives player sight and increases shadow resistance by 25%
    """

    def __init__(self):
        super().__init__(name="Reveal", description="An Inquisitor is a champion of truth, exposing secrets and "
                                                     "gaining protection from shadow.",
                        cost=0)
        self.passive = True

    def use(self, user):
        user.sight = True
        user.resistance['Shadow'] += 0.25
        if user.equipment['Pendant'].name == "Pendant of Vision":
            user.modify_inventory(user.equipment['Pendant'], 1)
            user.equipment['Pendant'] = user.unequip("Pendant")


class Inspect(Truth):

    def __init__(self):
        super().__init__(name="Inspect", description="Your attention to detail allows you to inspect aspects of the "
                                                     "enemy, possibly revealing a tender spot.",
                         cost=5)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        inspect_text = target.inspect() + "\n"
        return inspect_text


class ExploitWeakness(Truth):
    """
    Adds damage multiplier to melee attack equal to the lowest resistance; if no weakness to exploit, a random status
      effect may be applied
    """

    def __init__(self):
        super().__init__(name="Exploit Weakness", description="Inspect and identify the enemy's greatest weakness and "
                                                              "exploit it.",
                         cost=10)
        self.weapon = True

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        types = list(target.resistance)
        resists = list(target.resistance.values())
        weak = min(resists)
        if weak < 0:
            mod = 1 - weak  # negative resistance will result in increased damage
            use_str = f"{user.name} targets {target.name}'s weakness to {types[resists.index(weak)].lower()} to increase their attack!\n"
        else:
            mod = 1
            effects = ["Disarm", "Blind", "Silence", "None"]
            chance = user.check_mod("luck", enemy=target, luck_factor=10)
            effect = random.choices(effects, weights=[chance, chance, chance, target.con // 5])[0]
            if effect == "None":
                use_str = f"{target.name} has no identifiable weakness. The skill is ineffective.\n"
            else:
                if effect == "Disarm":
                    use_str = f"{target.name} drops their weapon.\n"
                else:
                    use_str = f"{target.name} is affected by {effect.lower()}.\n"
                target.status_effects[effect].active = True
                target.status_effects[effect].duration = -1
        wd_str, _, _ = user.weapon_damage(target, dmg_mod=mod)
        return use_str + wd_str


class KeenEye(Truth):
    """
    Gives Inquisitor insights about their surroundings
    """

    def __init__(self):
        super().__init__(name="Keen Eye", description="As an Inquisitor, you can gain insights into your surroundings.",
                         cost=0)
        self.passive = True


class Cartography(Truth):
    """
    Reveals minimap to Seeker, regardless of whether they have visited an area
    """

    def __init__(self):
        super().__init__(name="Cartography", description="Seekers are masters at map making and gain the ability to "
                                                         "see all of the dungeon, regardless of whether an area has "
                                                         "been visited.",
                         cost=0)
        self.passive = True


# Martial Art Skills
class LegSweep(MartialArts):

    def __init__(self):
        super().__init__(name="Leg Sweep", description="Sweep the leg, tripping the enemy and leaving them prone.",
                         cost=8)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, _ = user.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            if not target.status_effects['Prone'].active:
                if random.randint(user.stats.strength // 2, user.stats.strength) > \
                        random.randint(target.stats.strength // 2, target.stats.strength) and not target.flying:
                    target.status_effects['Prone'].active = True
                    target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
                    use_str += f"{user.name} trips {target.name} and they fall prone.\n"
        return use_str


class ChiHeal(MartialArts):

    def __init__(self):
        super().__init__(name="Chi Heal", description="The monk channels his chi energy, healing 25% of their health"
                                                      " and removing all negative status effects.",
                         cost=16)

    def use(self, user, target=None, cover=False):
        target = user
        user.mana.current -= self.cost
        use_str = Heal().cast(user, target=target, special=True)
        use_str += Cleanse().cast(user, target=target, special=True)
        return use_str


class PurityBody(MartialArts):

    def __init__(self):
        super().__init__(name="Purity of Body", description="Through meditation and perserverance, the monk gains "
                                                            "control over their body, increasing resistance against poison "
                                                            "and stone.",
                         cost=0)
        self.passive = True

    def use(self, user):
        user.resistance["Poison"] = 0.5
        user.resistance["Stone"] = 0.5


class PurityBody2(MartialArts):

    def __init__(self):
        super().__init__(name="Purity of Body", description="Further meditation and perserverance, the monk masters "
                                                            "control over their body, gaining immunity against poison "
                                                            "and stone.",
                         cost=0)
        self.passive = True

    def use(self, user):
        user.resistance["Poison"] = 1.
        user.resistance["Stone"] = 1.


class Evasion(MartialArts):

    def __init__(self):
        super().__init__(name="Evasion", description="You have become highly attuned at your surroundings, anticipating "
                                                     "other's actions and increasing your chance to dodge attacks.",
                         cost=0)
        self.passive = True


# Luck
class GoldToss(Luck):
    """
    Rank 1 Enemy Spell
    Unblockable (including mana shield and cover) and unresistable but enemy has chance to catch/keep some of it
    max_thrown is a percentage
    """

    def __init__(self):
        super().__init__(name="Gold Toss", description='Toss a handful of gold at the enemy, dealing damage equal to '
                                                       'the amount of gold thrown.',
                         cost=0)
        self.rank = 1

    def use(self, user, target=None, fam=False, cover=False):
        max_thrown = min(target.health.current, user.gold)
        if user.gold == 0:
            return "Nothing happens.\n"
        d_chance = target.check_mod('luck', enemy=user, luck_factor=10)
        damage = random.randint(1, max_thrown)
        user.gold -= damage
        use_str = f"{user.name} throws {damage} gold at {target.name}.\n"
        if not random.randint(0, 1) and \
                not any(target.status_effects[x].active for x in ['Sleep', 'Stun', 'Prone']):
            catch = random.randint(min(damage, d_chance), damage)
            damage -= catch
            if catch > 0:
                target.gold += catch
                if damage > 0:
                    use_str += f"{target.name} catches some of the gold thrown, gaining {catch} gold.\n"
                else:
                    use_str += f"{target.name} catches all of the gold thrown, gaining {catch} gold.\n"
        if damage > 0:
            target.health.current -= damage
            use_str += f"{user.name} does {damage} damage to {target.name}.\n"
        return use_str


class SlotMachine(Luck):
    """
    Rank 2 Enemy Skill
    Rolls 3 10-sided dice (so to speak); 1000 possible results (000 to 999)
    Possible outcomes:
    Nothing: nothing happens
    Mark of the Beast: either user (player) or enemy (bypasses Death resistance) - (666 or 999)
    3 of a Kind: full health/mana, cleanse negative statuses - (000, 111, 222, 333, 444, 555, 777, 888)
    Straight: damage to enemy equal to numbers multiplied together (unresistable and unblockable) -
        (012 = 0, 123 = 6, 234 = 24, 345 = 60, 456 = 120, 567 = 210, 678 = 336, 789 = 504, 890 = 0)
    Palindrome: casts high level spell based on middle value - (number that follow xyx format)
    Pairs: random status effect ["Stun", "Doom", "Blind", "Disarm", "Sleep", "Reflect", "Poison", "DOT",
                           "Bleed", "Regen", "Attack", "Defense", "Magic", "Magic Defense"] -
        (two numbers that are the same but do not meet any of the other requirements i.e. 221 but not 212)
    Evens: all numbers even; gain gold equal to spin - (i.e. 246 or 680)
    Odds: all numbers odd; gain random item - (i.e. 137 or 531)
    Chance: if no other spin hits, there is a chance that the user attacks with damage mod equal to one of the spins
    """

    def __init__(self):
        super().__init__(name="Slot Machine", description='Pull the handle and see what comes up! Depending on the '
                                                          'results, different possible outcomes can occur.',
                         cost=15)
        self.rank = 2

    def use(self, game, user, target=None, fam=False):
        import utils
        use_str = ""
        popup = utils.SlotMachinePopupMenu(game, "")

        hands = {"Death": ["666", "999"],
                 "Trips": ["000", "111", "222", "333", "444", "555", "777", "888"],
                 'Straight': ["012", "123", "234", "345", "456", "567", "678", "789"],
                 'Palindrome': ['010', '020', '030', '040', '050', '060', '070', '080', '090',
                                '101', '121', '131', '141', '151', '161', '171', '181', '191',
                                '202', '212', '232', '242', '252', '262', '272', '282', '292',
                                '303', '313', '323', '343', '353', '363', '373', '383', '393',
                                '404', '414', '424', '434', '454', '464', '474', '484', '494',
                                '505', '515', '525', '535', '545', '565', '575', '585', '595',
                                '606', '616', '626', '636', '646', '656', '676', '686', '696',
                                '707', '717', '727', '737', '747', '757', '767', '787', '797',
                                '808', '818', '828', '838', '848', '858', '868', '878', '898',
                                '909', '919', '929', '939', '949', '959', '969', '979', '989']}
        user_chance = user.check_mod('luck', enemy=target, luck_factor=10)
        target_chance = target.check_mod('luck', enemy=user, luck_factor=10)
        success = False
        retries = 0
        while not success:
            spin = popup.results()
            if spin in hands['Death']:
                use_str += "The mark of the beast!\n"
                success = True
                if target_chance > user_chance + 1:
                    target = user
                resist = target.check_mod('resist', enemy=user, typ='Death')
                if resist < 1:
                    target.health.current = 0
                    use_str += f"Death has come for {target.name}!\n"
                else:
                    use_str += f"{target.name} is immune to death spells.\n"
            elif spin in hands['Trips']:
                use_str += "3 of a Kind!\n"
                success = True
                if random.randint(0, max(1, user_chance)):
                    target = user
                target.health.current = target.health.max
                target.mana.current = target.mana.max
                use_str += f"{target.name} has been revitalized! Health and mana are restored.\n"
                use_str += Cleanse().cast(target, special=True)
            elif "".join(sorted(spin)) in hands['Straight']:
                use_str += "Straight!\n"
                success = True
                if target_chance > user_chance + 1:
                    target = user
                ints = [int(x) for x in list(spin)]
                damage = 1
                for i in ints:
                    damage *= i
                target.health.current -= damage
                use_str += f"{target.name} takes {damage} damage.\n"
            elif spin in hands['Palindrome']:
                use_str += "Palindrome!\n"
                success = True
                if target_chance > user_chance + 1:
                    target = user
                spell_list = [MagicMissile3(),
                              Firestorm(),
                              IceBlizzard(),
                              Electrocution(),
                              Tsunami(),
                              Earthquake(),
                              Tornado(),
                              ShadowBolt3(),
                              Holy3(),
                              Ultima()]
                spell = spell_list[int(spin[1])]
                use_str += f"{spell.name} is cast!\n"
                use_str += spell.cast(user, target=target, special=True)
            elif len(set(spin)) == 2:
                use_str += 'Pairs!\n'
                success = True
                duration = int(min(set(list(spin)), key=list(spin).count))  # number of turns effect will last
                if duration == 0:
                    duration = 10
                amount = int(max(set(list(spin)), key=list(spin).count))  # amount it will affect target
                if amount == 0:
                    amount = 10
                amount **= 2
                effects = ["Stun", "Doom", "Blind", "Disarm", "Sleep", "Reflect", "Poison", "DOT",
                           "Bleed", "Regen", "Attack", "Defense", "Magic", "Magic Defense"]
                if not random.randint(0, 1):
                    target = user
                effect = random.choice(effects)
                use_str += f"{effect} has been randomly selected to affect {target.name}.\n"
                target.status_effects[effect].active = True
                if effect in ["Blind", "Silence", "Disarm"]:
                    target.status_effects[effect].duration = -1
                else:
                    target.status_effects[effect].duration = max(duration, target.status_effects[effect].duration)
                if effect == "Poison":
                    amount *= int(target.health.max * 0.01)
                target.status_effects[effect].extra = amount
                if effect in ["Attack", "Defense", "Magic", "Magic Defense"]:
                    use_str += f"{target.name}'s {effect.lower()} is temporarily increased by {amount}.\n"
            elif all(int(x) % 2 == 0 for x in list(spin)):
                use_str += "Evens!\n"
                success = True
                if user_chance + 1 >= target_chance:
                    target = user
                target.gold += (int(spin) * 10)
                use_str += f"{target.name} gains {int(spin)} gold!\n"
            elif all(int(x) % 2 == 1 for x in list(spin)):
                use_str += "Odds!\n"
                success = True
                level = min(list(spin))
                if user_chance + 1 >= target_chance:
                    target = user
                from items import random_item
                item = random_item(int(level))
                try:
                    target.modify_inventory(item)
                except AttributeError:
                    pass
                use_str += f"{target.name} gains {item.name}.\n"
            elif random.randint(0, user_chance):
                use_str += "Chance!\n"
                success = True
                mod = int(random.choice(list(spin)))
                use_str += f"{user.name} gains {mod} attack.\n"
                wd_str, _, _ = user.weapon_damage(target, dmg_mod=1)
                use_str += wd_str
            else:
                if random.randint(0, user_chance) and retries < 2:
                    textbox = utils.TextBox(game)
                    textbox.print_text_in_rectangle("No luck, try again.")
                    time.sleep(1)
                    textbox.clear_rectangle()
                    retries += 1
                else:
                    success = True
                    use_str += "Nothing happens.\n"
        return use_str


class Blackjack(Luck):

    def __init__(self):
        super().__init__(name="Blackjack", description="Play a round of blackjack with the Jester; different things "
                                                       "happen depending on the result.",
                         cost=7)

    def use(self, game, user, target=None, cover=False):
        import utils
        user.mana.current -= self.cost
        use_str = ""
        popup = utils.BlackjackPopupMenu(game, f"{user.name} Hand  {target.name} Hand")
        result = popup.navigate_popup()
        prizes = {"Win": ["Regen", "Gold", ""],
                  "Break": ["Ultima"],
                  "Draw": []}
        if result == "Target Win":
            use_str += f"{target.name} wins the hand!\n"
        elif result == "Target Break":
            use_str += f"Oh no, {target.name} busted...\n"
        elif result == "User Break":
            target = user
            use_str += f"Oh no, {user.name} busted...\n"
        elif result == "User Win":
            target = user
            use_str += f"{user.name} wins the hand!\n"
        else:
            use_str += f"It's a draw!\n"
        return use_str


# Power Up skills
class BloodRage(PowerUp):
    """
    Berserker Power Up
    attack increases as health decreases; if below 30% health, bonus to defense
    """

    def __init__(self):
        super().__init__(name="Blood Rage", description="A berserker's rage knows no bounds, their power growing as "
                                                        "their blood is spilled. Attack power increases as health "
                                                        "decreases and gains an increase to defense below 30%.",
                         cost=0)
        self.passive = True


class DivineAegis(PowerUp):
    """
    Crusader Power Up
    create shell that absorbs damage and increases healing; if the shield survives the full duration, it will explode
      and deal holy damage to the enemy
    """

    def __init__(self):
        super().__init__(name="Divine Aegis", description="The power of faith envelopes your body for a time, "
                                                          "shielding you from harm and increases healing spells "
                                                          "while active. If the shield survives the duration, it will"
                                                          " explode in a brilliant light, dealing holy damage equal "
                                                          "to the remaining damage absorption.",
                         cost=20)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        dam_abs = random.randint(user.health.max // 4, user.health.max // 2)
        user.status_effects["Power Up"].active = True
        user.status_effects["Power Up"].duration = 5
        user.status_effects["Power Up"].extra = dam_abs
        return f"A shield envelopes {user.name}.\n"


class DragonsFury(PowerUp):
    """
    Dragoon Power Up
    attack and defense double for each successive hit; a miss resets this buff
    """

    def __init__(self):
        super().__init__(name="Dragon's Fury", description="The power up unleashed the dragon within, a power that "
                                                           "continues to grow. With each successive hit",
                         cost=0)
        self.passive = True


class SpellMastery(PowerUp):
    """
    Wizard Power Up
    automatically triggers when no spells can be cast due to low mana; all spells
          become free for a short time and mana regens based on damage dealt
    """

    def __init__(self):
        super().__init__(name="Spell Mastery", description="The Wizard is so good at spell casting that even running out"
                                                           " of mana won't stop them. This ability automatically triggers"
                                                           " when no spells can be cast due to low mana, making spells "
                                                           "free for a time. While active mana is regenerated based on "
                                                           "damage dealt.",
                         cost=0)
        self.passive = True


class VeilShadows(PowerUp):
    """
    Shadowcaster Power Up
    become one with the darkness, making the player invisible to most enemies and making them harder to hit; increases
         damage of initial attack if first
    """

    def __init__(self):
        super().__init__(name="Veil of Shadows", description="Darkness becomes light and light falls to darkness, "
                                                             "concealing the Shadowcaster from all but the most keen "
                                                             "eyes. The player gains invisibility and a bonus to damage"
                                                             " at the beginning of battle if they have initiative.",
                         cost=0)
        self.passive = True


class ArcaneBlast(PowerUp):
    """
    Knight Enchanter Power Up
    blast the enemy with a powerful attack, draining all remaining mana points; mana
          will regen in full over the next 4 turns (25% per turn)
    """

    def __init__(self):
        super().__init__(name="Arcane Blast", description="The power of the arcane can be devastating, especially "
                                                          "when its full force is realized. The Knight Enchanter "
                                                          "can expend its remaining energy in a powerful blast, at the"
                                                          " expense of all remaining mana. If the enemy remains, mana "
                                                          "will regenerate in full over the next 4 turns.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        use_str = ""
        dam_red = target.check_mod('magic def', enemy=user) // 10
        damage = random.randint(user.mana.current // dam_red, user.mana.current)
        user.mana.current = 0
        user.status_effects['Power Up'].active = True
        user.status_effects['Power Up'].duration = 4
        if target.status_effects["Mana Shield"].active:
            mana_loss = damage // target.status_effects['Mana Shield'].duration
            if mana_loss > target.mana.current:
                abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                use_str += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                damage -= abs_dam
                target.mana.current = 0
                target.status_effects['Mana Shield'].active = False
                use_str += f"The mana shield dissolves around {target.name}.\n"
            else:
                use_str += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                target.mana.current -= mana_loss
                damage = 0
        if damage > 0:
            target.health.current -= damage
            use_str += f"{user.name} blasts {target.name} for {damage} damage, draining all remaining mana.\n"
        return use_str


class StrokeLuck(PowerUp):
    """
    Rogue Power Up
    the Rogue is incredibly lucky, gaining bonuses to all luck-based checks, as well as dodge and critical chance
    """

    def __init__(self):
        super().__init__(name="Stroke of Luck", description="The master of tricks and subterfuge also has Lady Luck on "
                                                            "its side, gaining a bonus to all luck-based rolls.",
                         cost=0)
        self.passive = True


class EyesUnseen(PowerUp):
    """
    Seeker Power Up
    gain increased awareness of battle situations, increasing critical chance as well as chance to dodge/parry attacks
    """

    def __init__(self):
        super().__init__(name="Eyes of the Unseen", description="The Seeker excels at rooting out the evil that hides "
                                                                "in the shadows. Studying these enemies has improved "
                                                                "their own game, improving battle awareness and increasing"
                                                                " both critical and dodge chance.",
                         cost=0)
        self.passive = True


class BladeFatalities(PowerUp):
    """
    Ninja Power Up
    sacrifice percentage of health to imbue blade with the spirit of Muramasa, increasing damage dealt and absorbing
         it into the user
    """

    def __init__(self):
        super().__init__(name="Blade of Fatalities", description="The spirit of Muramasa demands a sacrifice but will"
                                                                 " grant ultimate power. The user will give up 25% of "
                                                                 "their health for increased damage and draining health"
                                                                 " into the user.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        per_health = int(0.25 * user.health.current)
        use_str = f"{user.name} sacrifices {per_health} health to imbue their blades with the spirit of Muramasa!\n"
        user.status_effects['Power Up'].active = True
        user.status_effects['Power Up'].duration = 5
        user.status_effects['Power Up'].extra = max(per_health // 5, 5)
        return use_str


class HolyRetribution(PowerUp):
    """
    Templar Power Up
    the Templar is surrounded by holy swords, reflecting 25% percent of damage back at the attacker; while
          the shield is active, attack damage is increased
    """

    def __init__(self):
        super().__init__(name="Holy Retribution", description="The power of Elysia repels you...or the enemy's attacks"
                                                              " in this case. Holy blades reflect 25% of weapon damage"
                                                              " back to the attacker. While active, the player also "
                                                              "receives a boost to attack damage.",
                         cost=25)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        user.status_effects["Power Up"].active = True
        user.status_effects["Power Up"].duration = 5
        return f"{user.name} is surrounded by holy blades.\n"


class GreatGospel(PowerUp):
    """
    Archbishop Power Up
    regens health and mana over time, and restores status; increases resistance and holy damage for duration
    """

    def __init__(self):
        super().__init__(name="Great Gospel", description="A white orb with a hint of green descends upon you, surrounding"
                                                          " you character with a benevolent aura. This aura removes all"
                                                          " status effects and regens both health and mana of the user. "
                                                          "While active, resistance and holy damage are increased.",
                         cost=35)

    def use(self, user, target=None, cover=False):
        use_str = f"{user.name} gains a holy aura.\n"
        user.mana.current -= self.cost
        user.status_effects["Power Up"].active = True
        user.status_effects["Power Up"].duration = 5
        use_str += Cleanse().cast(user, special=True)
        return use_str


class DimMak(PowerUp):
    """
    Master Monk Power Up
    unleash a powerful attack that deals heavy damage and can either stun or in some cases kill the target; if the
        target is killed, the user will absorb the enemy's essence and will be regenerated by its max health and mana
    """

    def __init__(self):
        super().__init__(name="Dim Mak", description="The life force of chi is typically ruled by restraint however "
                                                     "there is one exception, the powerful Dim Mak or touch of death."
                                                     " This ability has a chance to either stun or kill its target, with"
                                                     " death allowing the user to absorb the essence of the enemy, "
                                                     "gaining health and mana.",
                         cost=50)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        wd_str, _, _ = user.weapon_damage(target, crit=3, dmg_mod=1.5, ignore=True, hit=True)
        use_str += wd_str
        if target.is_alive():
            if not (random.randint(0, target.con) + target.check_mod("luck", enemy=user, luck_factor=5)) and \
                target.check_mod("resist", enemy=user, typ="Death") < 1:
                    use_str += f"{target.name} sustains a lethal blow and collapses to the ground.\n"
                    target.health.current = 0
            else:
                if random.random() > target.check_mod("resist", enemy=user, typ="Physical"):
                    use_str += f"{target.name} is stunned.\n"
                    target.status_effects["Stun"].active = True
                    target.status_effects["Stun"].duration = user.stats.wisdom // 10
            if target.is_alive():
                return use_str
        user.health.current = min(user.health.max, user.health.current + target.health.max)
        user.mana.current = min(user.mana.max, user.mana.current + target.mana.max)
        use_str += f"{user.name} gains the essence of {target.name}, gaining health and mana.\n"
        return use_str


class LunarFrenzy(PowerUp):
    """
    Lycan Power Up
    the longer the Lycan is transformed, the further into madness they fall, increasing
          damage and regenerating health on critical hits; if the Lycan stays transformed for longer than 5 turns, they 
          will be unable to transform back until after the battle
    """

    def __init__(self):
        super().__init__(name="Lunar Frenzy", description="Transformation is a powerful ability, achievable as a Druid "
                                                          "but perfected by the Lycan. You gain an increased brutality "
                                                          "while transformed, dealing increasing damage and healing on "
                                                          "critical hits the longer you are changed. This does come at "
                                                          "a cost, as you will reach a point where you can no longer "
                                                          "change back until after combat.",
                         cost=0)
        self.passive = True


class TetraDisaster(PowerUp):
    """
    Geomancer Power Up
    unleash a powerful attack consisting of all 4 elements; this will also increase resistance of caster to the 
        4 elements by 50%
    """

    def __init__(self):
        super().__init__(name="Tetra-Disaster", description="The 4 elements of the natural world are mighty on their "
                                                            "own but together they can wreak an incredible level of "
                                                            "destruction. Unleash them all at once with this powerful "
                                                            "spell, increasing resistance of each by 50%.",
                         cost=20)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        elements = ["Fire", "Water", "Wind", "Earth"]
        for spell in user.spellbook["Spells"].values():
            if spell.subtyp in elements:
                use_str += spell().use(user, target=target, special=True)
        user.status_effects["Power Up"].active = True
        user.status_effects["Power Up"].duration = 5
        return use_str


class SoulHarvest(PowerUp):
    """
    Soulcatcher Power Up
    each enemy killed of a particular type will improve conbat expertise against that enemy type, improving attack,
        defense, magic, and magic defense
    """

    def __init__(self):
        super().__init__(name="Soul Harvest", description="The souls of the dead contain traces of its host's power. "
                                                          "The Soulcatcher knows this and uses it to their advantage. "
                                                          "Each enemy killed of a particular type increases the combat "
                                                          "effectiveness against that enemy type.",
                         cost=0)
        self.passive = True


# Enemy skills
class Lick(Skill):

    def __init__(self):
        super().__init__(name="Lick", description="Lick the target, dealing damage and inflicting random status "
                                                  "effect(s).",
                         cost=10)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, _ = user.weapon_damage(target, cover=cover, dmg_mod=1.25)
        if hit:
            status_effects = ['Prone', 'Silence', 'Stun', 'Blind', 'Sleep']
            if random.randint(user.stats.strength // 2, user.stats.strength) > \
                    random.randint(target.stats.con // 2, target.stats.con):
                random_effect = random.choice(status_effects)
                if not target.status_effects[random_effect].active:
                    target.status_effects[random_effect].active = True
                    if random_effect in ["Silence", "Blind"]:
                        target.status_effects[random_effect].duration = -1
                    else:
                        target.status_effects[random_effect].duration = random.randint(2, max(3, user.stats.strength // 8))
                    use_str += f"{target.name} is affected by {random_effect.lower()}.\n"
        return use_str


class AcidSpit(Skill):
    """
    dodge reduces damage by half
    """

    def __init__(self):
        super().__init__(name="Acid Spit", description="Spit a corrosive substance on the target, dealing initial "
                                                       "damage plus damage over time.",
                         cost=6)
        self.damage = 8

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= (self.cost * user.level.pro_level)
        dmg = self.damage * max(1, user.level.pro_level) + (user.stats.intel // 2)
        dam_red = target.check_mod('magic def', enemy=user)
        damage = random.randint(dmg // 2, dmg) - dam_red
        if user.hit_chance(target, typ='magic'):
            if target.dodge_chance(user) > random.random():
                use_str += f"{target.name} partially dodges the attack, only taking half damage.\n"
                damage //= 2
            if damage > 0:
                use_str += f"{target.name} takes {damage} damage from the acid.\n"
                target.health.current -= damage
                target.status_effects["DOT"].active = True
                target.status_effects["DOT"].duration = 2
                target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
                use_str += f"{target.name} is covered in a corrosive substance.\n"
            else:
                use_str += "The acid is ineffective.\n"
        else:
            use_str += f"{user.name} misses {target.name} with {self.name}.\n"
        return use_str


class Web(Skill):

    def __init__(self):
        super().__init__(name="Web", description="Expel a thick, sticky substance onto the enemy, leaving them prone.",
                         cost=6)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        if random.randint(user.stats.dex // 2, user.stats.dex) > \
                random.randint(target.stats.strength // 2, target.stats.strength):
            if not target.status_effects['Prone'].active:
                target.status_effects['Prone'].active = True
                target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
            else:
                target.status_effects['Prone'].duration += 1
            return f"{target.name} is trapped in a web and is prone.\n"
        return f"{target.name} evades the web.\n"


class Howl(Skill):

    def __init__(self):
        super().__init__(name="Howl", description="The wolf howls at the moon, terrifying the enemy.",
                         cost=10)

    def use(self, user, target=None, cover=False):
        turns = max(1, user.stats.strength // 10)
        use_str = f"{user.name} howls at the moon.\n"
        user.mana.current -= self.cost
        if not target.status_effects["Stun"].active:
            if random.randint(0, user.stats.strength) > random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects["Stun"].active = True
                target.status_effects['Stun'].duration = turns
                use_str += f"{user.name} stunned {target.name}.\n"
            else:
                use_str += f"{target.name}'s resolve is steadfast.\n"
        else:
            use_str += f"{target.name} is already stunned.\n"
        return use_str


class Shapeshift(Skill):

    def __init__(self):
        super().__init__(name='Shapeshift', description="Some enemies can change their appearance and type. This is the"
                                                        " skill they use to do so.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        while True:
            s_creature = random.choice(user.transform)()
            if user.cls.name != s_creature.cls.name:
                break
        user.cls = s_creature.cls
        user.stats = s_creature.stats
        user.equipment = s_creature.equipment
        user.spellbook = s_creature.spellbook
        user.resistance = s_creature.resistance
        user.flying = s_creature.flying
        user.invisible = s_creature.invisible
        user.sight = s_creature.sight
        user.spellbook['Skills']['Shapeshift'] = Shapeshift()
        return f"{user.name} changes shape, becoming a {s_creature.name}.\n"


class Trip(Skill):

    def __init__(self):
        super().__init__(name="Trip", description="Grab the enemy's leg and trip them to the ground, leaving them "
                                                  "prone.",
                         cost=6)

    def use(self, user, target=None, special=False, cover=False):
        if not special:
            user.mana.current -= self.cost
        if not target.status_effects["Prone"].active:
            if random.randint(0, user.stats.dex) > \
                    random.randint(target.stats.dex // 2, target.stats.dex) and not target.flying:
                target.status_effects['Prone'].active = True
                target.status_effects['Prone'].duration = max(1, user.stats.strength // 20)
                return f"{user.name} trips {target.name} and they fall prone.\n"
            if not special:
                return f"{user.name} fails to trip {target.name}.\n"
        else:
            if not special:
                return f"{target.name} is already prone.\n"
        return ""


class NightmareFuel(Skill):

    def __init__(self):
        super().__init__(name="Nightmare Fuel", description="Invade the enemy's dreams, messing with their mind and "
                                                            "dealing damage.",
                         cost=20)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        crit = 1
        if target.status_effects['Sleep'].active:
            if random.randint(user.stats.intel // 2, user.stats.intel) > \
                    random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                if random.random() > 0.5:  # 50% chance to crit
                    use_str += "Critical hit!\n"
                    crit = 2
                damage = int(target.status_effects['Sleep'].duration * user.stats.intel * crit)
                damage = max(1, random.randint(damage // 2, damage))
                target.health.current -= damage
                use_str += f"{user.name} invades {target.name}'s dreams, dealing {damage} damage.\n"
            else:
                use_str += f"{target.name} resists the spell.\n"
        else:
            use_str += "The spell does nothing.\n"
        return use_str


class WidowsWail(Skill):
    """
    Special skill of waitress; does more damage as the user's HP diminishes
    """

    def __init__(self):
        super().__init__(name="Widow's Wail", description="The agony of loss is released, affecting both the target "
                                                          "and user. Both will take non-elemental damage based on the "
                                                          "current health of the user.",
                         cost=12)
        self.damage = 20
        self.max_damage = 200

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        dmg = int((user.health.max / user.health.current) * self.damage)
        damage = min(self.max_damage, dmg)
        if random.randint(user.stats.intel // 2, user.stats.intel) > \
            random.randint(user.stats.wisdom // 2, user.stats.wisdom):
            use_str += f"Anguish overwhelms {user.name}, taking {damage} damage.\n"
            user.health.current -= damage
        if random.randint(user.stats.intel // 2, user.stats.intel) > \
            random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            use_str += f"Anguish overwhelms {target.name}, taking {damage} damage.\n"
            target.health.current -= damage
        return use_str


class ThrowRock(Skill):

    def __init__(self):
        super().__init__(name="Throw Rock", description="Grab the nearest rock or stone and chuck it at the enemy, with"
                                                        " a chance to knock the target prone.",
                         cost=7)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        size = random.randint(0, 4)  # size of rock thrown
        sizes = ['tiny', 'small', 'medium', 'large', 'massive']
        use_str = f"{user.name} throws a {sizes[size]} rock at {target.name}.\n"
        a_chance = user.check_mod('luck', enemy=target, luck_factor=10)
        d_chance = target.check_mod('luck', enemy=user, luck_factor=15)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        dam_red = target.check_mod('armor', enemy=user)
        resist = target.check_mod('resist', enemy=user, typ='Physical')
        hit_per = user.hit_chance(target, typ='weapon')
        hit = hit_per > random.random()
        if target.incapacitated():
            dodge = False
            hit = True
        if dodge:
            use_str += f"{target.name} evades the attack.\n"
        else:
            if hit and target.status_effects["Duplicates"].active:
                if random.randint(0, target.status_effects["Duplicates"].duration):
                    hit = False
                    use_str += (f"{user.name} throws a rock but hits a mirror image of {target.name} and it vanishes "
                                f"from existence.\n")
                    target.status_effects["Duplicates"].duration -= 1
                    if not target.status_effects["Duplicates"].duration:
                        target.status_effects["Duplicates"].active = False
            if hit and cover:
                use_str += (f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                            f"{target.name}.\n")
            elif hit:
                crit = 1
                if (a_chance - d_chance) * 0.1 > random.random():
                    crit = 2
                    use_str += "Critical hit!\n"
                damage = random.randint(user.stats.strength // 4, user.stats.strength // 3) * (size + 1) * crit
                damage = max(0, int((damage - dam_red) * (1 - resist)))
                if target.status_effects['Mana Shield'].active:
                    mana_loss = damage // target.status_effects['Mana Shield'].duration
                    if mana_loss > target.mana.current:
                        abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                        use_str += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                        damage -= abs_dam
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                        use_str += f"The mana shield dissolves around {target.name}.\n"
                    else:
                        use_str += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                        target.mana.current -= mana_loss
                        damage = 0
                elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                    if damage >= target.status_effects['Power Up'].extra:
                        use_str += (f"The shield around {target.name} absorbs "
                                    f"{target.status_effects['Power Up'].extra} damage.\n")
                        damage -= target.status_effects['Power Up'].extra
                        target.status_effects['Power Up'].active = False
                        use_str += f"The shield dissolves around {target.name}.\n"
                    else:
                        use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                        target.status_effects['Power Up'].extra -= damage
                        damage = 0
                if damage > 0:
                    target.health.current -= damage
                    use_str += f"{target.name} is hit by the rock and takes {damage} damage.\n"
                    if not target.status_effects["Prone"].active:
                        if random.randint(user.stats.strength // 2, user.stats.strength) > \
                                random.randint(target.stats.strength // 2, target.stats.strength):
                            target.status_effects['Prone'].active = True
                            target.status_effects['Prone'].duration = max(1, size)
                            use_str += f"{target.name} is knocked over and falls prone.\n"
                else:
                    use_str += f"{target.name} shrugs off the damage.\n"
            else:
                use_str += f"{user.name} misses {target.name} with the throw.\n"
        return use_str


class Stomp(Skill):

    def __init__(self):
        super().__init__(name="Stomp", description="Stomp on the enemy, dealing damage with a chance to stun.",
                         cost=8)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        resist = target.check_mod('resist', enemy=user, typ='Physical')
        a_chance = user.check_mod('luck', enemy=target, luck_factor=10)
        d_chance = target.check_mod('luck', enemy=user, luck_factor=15)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        stun = any(target.status_effects[x] for x in ['Stun', 'Sleep', 'Prone'])
        if stun:
            dodge = False
            hit = True
        else:
            hit_per = user.hit_chance(target, typ='weapon')
            hit = hit_per > random.random()
        if dodge:
            return f"{target.name} evades the attack.\n"
        if hit and target.status_effects["Duplicates"].active:
            if random.randint(0, target.status_effects["Duplicates"].duration):
                hit = False
                use_str += (f"{user.name} stomps but hits a mirror image of {target.name} and it vanishes from "
                            f"existence.\n")
                target.status_effects["Duplicates"].duration -= 1
                if not target.status_effects["Duplicates"].duration:
                    target.status_effects["Duplicates"].active = False
        if cover and hit:
            use_str += (f"{target.familiar.name} steps in front of the attack, absorbing the damage directed at "
                        f"{target.name}.\n")
        elif hit:
            crit = 1
            if (a_chance - d_chance) * 0.1 > random.random():
                crit = 2
                use_str += "Critical hit!\n"
            damage = int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist) * crit)
            if target.status_effects['Mana Shield'].active:
                mana_loss = damage // target.status_effects['Mana Shield'].duration
                if mana_loss > target.mana.current:
                    abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                    use_str += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                    damage -= abs_dam
                    target.mana.current = 0
                    target.status_effects['Mana Shield'].active = False
                    use_str += f"The mana shield dissolves around {target.name}.\n"
                else:
                    use_str += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                    target.mana.current -= mana_loss
                    damage = 0
            elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                if damage >= target.status_effects['Power Up'].extra:
                    use_str += (f"The shield around {target.name} absorbs "
                                f"{target.status_effects['Power Up'].extra} damage.\n")
                    damage -= target.status_effects['Power Up'].extra
                    target.status_effects['Power Up'].active = False
                    use_str += f"The shield dissolves around {target.name}.\n"
                else:
                    use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                    target.status_effects['Power Up'].extra -= damage
                    damage = 0
            if damage > 0:
                target.health.current -= damage
                use_str += f"{user.name} stomps {target.name}, dealing {damage} damage.\n"
                if not target.status_effects["Stun"].active:
                    if random.randint(user.stats.strength // 2, user.stats.strength) > \
                            random.randint(target.stats.con // 2, target.stats.con):
                        turns = max(2, user.stats.strength // 10)
                        target.status_effects["Stun"].active = True
                        target.status_effects['Stun'].duration = turns
                        use_str += f"{user.name} stunned {target.name}.\n"
            else:
                use_str += f"{user.name} stomps {target.name} but deals no damage.\n"
        else:
            use_str += f"{user.name} misses {target.name}.\n"
        return use_str


class Screech(Skill):
    """
    Only silences if damage is dealt
    """

    def __init__(self):
        super().__init__(name="Screech", description="Let out an ear-piercing screech, damaging the foe and silencing"
                                                     " them.",
                         cost=15)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        damage = 0
        if random.randint(user.stats.dex // 2, user.stats.dex) + user.stats.intel > \
                random.randint(target.stats.con // 2, target.stats.con) + target.stats.wisdom:
            resist = target.check_mod('resist', enemy=user, typ='Physical')
            damage = int(user.stats.intel * (1 - resist))
            if damage > 0:
                target.health.current -= damage
                use_str += f"The deafening screech hurts {target.name} for {damage} damage.\n"
                if not target.status_effects["Silence"].active:
                    target.status_effects['Silence'].active = True
                    target.status_effects['Silence'].duration = -1
                    use_str += f"{target.name} has been silenced.\n"
        if damage <= 0:
            use_str += "The spell is ineffective.\n"
        return use_str


class Detonate(Skill):
    """
    Cannot fully resist the damage except with an active shield
    """

    def __init__(self):
        super().__init__(name="Detonate", description="Systems are failing and retreat is not an option. Protocol "
                                                      "states the prime directive is destruction of the enemy by any "
                                                      "means necessary. Self-destruct sequence initiated.",
                         cost=0)

    def use(self, user, target=None, cover=False):
        use_str = (f"{user.name} explodes, sending shrapnel in all directions.")
        resist = target.check_mod('resist', enemy=user, typ='Physical')
        damage = max(user.health.current // 2, int(user.health.current * (1 - resist))) * random.randint(1, 4)
        if target.status_effects['Mana Shield'].active:
            mana_loss = damage // target.status_effects['Mana Shield'].duration
            if mana_loss > target.mana.current:
                abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                use_str += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                damage -= abs_dam
                target.mana.current = 0
                target.status_effects['Mana Shield'].active = False
                use_str += f"The mana shield dissolves around {target.name}.\n"
            else:
                use_str += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                target.mana.current -= mana_loss
                damage = 0
        elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
            if damage >= target.status_effects['Power Up'].extra:
                use_str += (f"The shield around {target.name} absorbs "
                            f"{target.status_effects['Power Up'].extra} damage.\n")
                damage -= target.status_effects['Power Up'].extra
                target.status_effects['Power Up'].active = False
                use_str += f"The shield dissolves around {target.name}.\n"
            else:
                use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                target.status_effects['Power Up'].extra -= damage
                damage = 0
        if damage > 0:
            t_chance = target.check_mod('luck', enemy=user, luck_factor=20)
            if random.randint(0, target.stats.dex // 15) + t_chance:
                damage = max(1, damage // 2)
                use_str += f"{target.name} dodges the shrapnel, only taking half damage.\n"
            use_str += f"{target.name} takes {damage} damage from the shrapnel.\n"
        else:
            use_str += f"{target.name} was unhurt by the explosion.\n"
        user.health.current = 0
        return use_str


class Crush(Skill):
    """
    Can't be covered or blacked by Mana Shield
    """

    def __init__(self):
        super().__init__(name="Crush", description="Take the enemy into your clutches and attempt to squeeze the life "
                                                   "from them.",
                         cost=25)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        resist = target.check_mod('resist', enemy=user, typ='Physical')
        a_chance = user.check_mod('luck', enemy=target, luck_factor=15)
        d_chance = target.check_mod('luck', enemy=user, luck_factor=10)
        dodge = (random.randint(0, target.stats.dex // 2) + d_chance >
                 random.randint(user.stats.dex // 2, user.stats.dex) + a_chance)
        stun = any(target.status_effects[x] for x in ['Stun', 'Sleep', 'Prone'])
        if stun:
            hit = True
            dodge = False
        else:
            a_hit = user.stats.dex + user.stats.strength
            d_hit = target.stats.dex + target.stats.strength
            hit = (random.randint(a_hit // 2, a_hit) + a_chance >
                   random.randint(d_hit // 2, d_hit) + d_chance)
        if dodge:
            return f"{target.name} evades the attack.\n"
        if hit and target.status_effects["Duplicates"].active:
            if random.randint(0, target.status_effects["Duplicates"].duration):
                hit = False
                use_str += (f"{user.name} grabs for {target.name} but gets a mirror image instead and it vanishes "
                            f"from existence.\n")
                target.status_effects["Duplicates"].duration -= 1
                if not target.status_effects["Duplicates"].duration:
                    target.status_effects["Duplicates"].active = False
        if hit:
            use_str = f"{user.name} grabs {target.name}.\n"
            crit = 1
            if (a_chance - d_chance) * 0.1 > random.random():
                crit = 2
                use_str += "Critical hit!\n"
            damage = max(int(target.health.current * 0.25),
                            int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist) * crit))
            target.health.current -= damage
            use_str += f"{user.name} crushes {target.name}, dealing {damage} damage.\n"
            if random.randint(user.stats.strength // 2, user.stats.strength) > \
                    random.randint(target.stats.dex // 2, target.stats.dex) + d_chance:
                fall_damage = int(random.randint(user.stats.strength // 2, user.stats.strength) * (1 - resist))
                target.health.current -= fall_damage
                use_str += f"{user.name} throws {target.name} to the ground, dealing {fall_damage} damage.\n"
            else:
                use_str += f"{target.name} rolls as they hit the ground, preventing any fall damage.\n"
            return use_str
        return f"{user.name} grabs for {target.name} but misses.\n"


class ConsumeItem(Skill):

    def __init__(self):
        super().__init__(name="Consume Item", description="You enjoy the finer things in life, which includes metal, "
                                                          "wood, and leather. Steal an item from the enemy and consume"
                                                          " it, absorbing the power of the item.",
                         cost=14)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        u_chance = user.check_mod('luck', enemy=target, luck_factor=10)
        t_chance = target.check_mod('luck', enemy=user, luck_factor=10)
        if random.randint(0, user.stats.dex) + u_chance > random.randint(target.stats.dex // 2, target.stats.dex) + t_chance:
            if len(target.inventory) != 0 and random.randint(0, u_chance):
                item_key = random.choice(list(target.inventory))
                item = target.inventory[item_key][0]
                target.modify_inventory(item, subtract=True)
                use_str += f"{user.name} steals {item_key} from {target.name} and consumes it.\n"
                duration = max(1, int(1 / item.rarity))
                amount = max(1, int(2 / item.rarity))
                if item.typ == 'Weapon':
                    stat = 'Attack'
                    use_str += f"{user.name}'s {stat.lower()} increases by {amount}.\n"
                elif item.typ == 'Armor':
                    stat = 'Defense'
                    use_str += f"{user.name}'s {stat.lower()} increases by {amount}.\n"
                elif item.typ == 'OffHand':
                    if item.subtyp == 'Tome':
                        stat = 'Magic'
                    else:
                        stat = 'Magic Defense'
                    use_str += f"{user.name}'s {stat.lower()} increases by {amount}.\n"
                elif item.typ == 'Accessory':
                    if item.subtyp == 'Ring':
                        stat = random.choice(['Attack', 'Defense'])
                    else:
                        stat = random.choice(['Magic', 'Magic Defense'])
                    use_str += f"{user.name}'s {stat.lower()} increases by {amount}.\n"
                elif item.typ == 'Potion':
                    if item.subtyp != 'Stat':
                        stat = 'Regen'
                        use_str += f"{user.name} regenerated HP over {duration} turns.\n"
                    else:
                        stat = 'Poison'
                        use_str += f"{user.name} is poisoned.\n"
                        amount = int(target.health.max * 0.05)
                else:
                    stat = random.choice(['Silence', 'Stun', 'Blind', 'Sleep'])
                    use_str += f'{user.name} is affected by {stat.lower()}.\n'
                user.status_effects[stat].active = True
                if stat in ["Blind", "Silence"]:
                    user.status_effects[stat].duration = -1
                else:
                    user.status_effects[stat].duration = duration + 1
                    user.status_effects[stat].extra = amount
            else:
                gold = random.randint(target.gold // 100, target.gold // 50) * u_chance
                regen = gold // 10
                use_str += f"{user.name} steals {gold} gold from {target.name} and consumes it.\n"
                use_str += f"{user.name} regains {regen} health and mana.\n"
                user.health.current += regen
                user.health.current = min(user.health.current, user.health.max)
                user.mana.current += regen
                user.mana.current = min(user.mana.current, user.mana.max)
        else:
            use_str += f"{user.name} can't steal anything.\n"
        return use_str


class DestroyMetal(Skill):
    def __init__(self):
        super().__init__(name="Destroy Metal", description="Target metal items and destroy them.",
                         cost=27)

    def use(self, user, target=None, cover=False):
        use_str = ""
        user.mana.current -= self.cost
        metal_items = ['Fist', 'Dagger', 'Sword', 'Ninja Blade', 'Longsword', 'Battle Axe', 'Polearm',
                       'Shield', 'Heavy', 'Ring', 'Pendant', 'Key']
        destroy_list = []
        destroy_loc = 'inv'
        for item in [target.inventory[x][0] for x in target.inventory]:
            if item.subtyp in metal_items and not item.ultimate and item.rarity > 0:
                destroy_list.append(item)
        if len(destroy_list) == 0:
            destroy_loc = 'equip'
            for item in target.equipment.values():
                if item.subtyp in metal_items and not item.ultimate and item.rarity > 0:
                    destroy_list.append(item)
        try:
            destroy_item = random.choice(destroy_list)
            t_chance = target.check_mod('luck', enemy=user, luck_factor=5)
            if not random.randint(0, int(2 / destroy_item.rarity) + t_chance):
                from items import remove_equipment
                if destroy_loc == 'inv':
                    use_str += f"{user.name} destroys a {destroy_item.name} out of {target.name}'s inventory.\n"
                    target.modify_inventory(destroy_item, subtract=True)
                elif destroy_loc == 'equip':
                    if destroy_item.typ not in ['Weapon', 'Accessory']:
                        use_str += f"{user.name} destroys {target.name}'s {destroy_item.typ}.\n"
                        target.equipment[destroy_item.typ] = remove_equipment(destroy_item.typ)
                    elif destroy_item.typ == 'Accessory':
                        use_str += f"{user.name} destroys {target.name}'s {destroy_item.subtyp}.\n"
                        target.equipment[destroy_item.subtyp] = remove_equipment(destroy_item.subtyp)
                    else:
                        if target.equipment['OffHand'] == destroy_item:
                            target.equipment['OffHand'] = remove_equipment('OffHand')
                            use_str += f"{user.name} destroys {target.name}'s offhand weapon.\n"
                        else:
                            target.equipment[destroy_item.typ] = remove_equipment(destroy_item.typ)
                            use_str += f"{user.name} destroys {target.name}'s {destroy_item.typ}.\n"
                else:
                    raise AssertionError("You shouldn't reach here.")
            else:
                use_str += f"{user.name} fails to destroy any items.\n"
        except IndexError:
            use_str += f"{target.name} isn't carrying any metal items.\n"
        return use_str


class Turtle(Skill):

    def __init__(self):
        super().__init__(name="Turtle", description="Hunker down into a ball, reducing all damage to 0 and regenerating"
                                                    " health.",
                         cost=0)
        self.passive = True


class GoblinPunch(Skill):
    """
    does damage based on the strength difference between the user and target; the higher the target's strength is
      compared to the user, the more damage it will cause
    """

    def __init__(self):
        super().__init__(name="Goblin Punch", description="Attack the target multiple times with a flurry of punches, "
                                                          "dealing damage based on the strength difference between the "
                                                          "user and target.",
                         cost=0)
        self.max_punches = 5

    def use(self, user, target=None, cover=False):
        use_str = ""
        num_attacks = max(1, random.randint(user.level.pro_level, self.max_punches))
        str_diff = max(1 + user.level.pro_level, (target.stats.strength - user.stats.strength) // 2)
        for _ in range(num_attacks):
            if user.hit_chance(target, typ='unarmed') > random.random():
                target.health.current -= str_diff
                use_str += f"{user.name} punches {target.name} for {str_diff} damage.\n"
            else:
                use_str += f"{user.name} punches air, missing {target.name}.\n"
        return use_str


class BrainGorge(Skill):
    """
    ignores mana shield
    """

    def __init__(self):
        super().__init__(name="Brain Gorge", description="Attack the enemy and attempt to latch on and eat its brain; a"
                                                         " successful attack can lower intelligence.",
                         cost=30)

    def use(self, user, target=None, cover=False):
        user.mana.current -= self.cost
        use_str, hit, crit = user.weapon_damage(target)
        if hit:
            t_chance = target.check_mod('luck', enemy=user, luck_factor=15)
            use_str += f"{user.name} latches onto {target.name}.\n"
            if target.incapacitated() or \
                (random.randint(user.stats.strength // 2, user.stats.strength) >
                 random.randint(target.stats.con // 2, target.stats.con) + t_chance):
                resist = target.check_mod('resist', enemy=user, typ='Physical')
                damage = int(random.randint(user.stats.strength // 4, user.stats.strength) * (1 - resist) * crit)
                target.health.current -= damage
                if damage > 0:
                    use_str += f"{user.name} does an additional {damage} damage to {target.name}.\n"
                    if not target.is_alive() or \
                            (random.randint(user.stats.intel // 2, user.stats.intel) >
                             random.randint(target.stats.wisdom // 2, target.stats.wisdom) + \
                                target.check_mod('magic def', enemy=user)):
                        target.stats.intel -= 1
                        use_str += f"{user.name} eats a part of {target.name}'s brain, lowering their intelligence by 1.\n"
        return use_str


class Counterspell(Skill):

    def __init__(self):
        super().__init__(name="Counterspell", description="If the Behemoth is the target of an attack spell, it will "
                                                          "counter with a spell of its own.",
                         cost=0)
        self.passive = True

    def use(self, user, target=None, cover=False):
        spell = random.choice(user.spellbook['Spells'].values())
        if spell.subtyp == "Heal":
            target = user
        return spell.cast(user, target=target, cover=cover)


class FinalAttack(Skill):

    def __init__(self):
        super().__init__(name="Final Attack", description="Upon death, the behemoth unleashes the powerful Meteor "
                                                          "spell.",
                         cost=0)
        self.passive = True


class ChooseFate(Skill):
    """
    The player gets to choose what the Devil does on his turn; your choices affect the Devil's stats
    Each time Attack is selected, the damage mod goes up (increases attack and armor)
    Each time a spell is selected, the magic mod goes up (increases magic, healing, and magic defense)
    Each time a skill is selected, the damage and magic mod goes down
    """

    def __init__(self):
        super().__init__(name="Choose Fate", description="The Devil likes to toy with his food, letting the player "
                                                         "decide what he will do for that turn.",
                         cost=0)

    def use(self, game, user, target=None, cover=False):
        import utils
        use_str = ""
        choose_message = "I'm bored, you choose."
        options = ['Attack', 'Hellfire', 'Crush']
        popup = utils.SelectionPopupMenu(game, choose_message, options)
        option_index = popup.navigate_popup()
        mod_up = random.randint(10, 25)
        if options[option_index] == 'Attack':
            wd_str, _, _ = user.weapon_damage(target, dmg_mod=1.5)
            use_str += wd_str
            user.damage_mod += mod_up
            use_str += "Hahaha, my power increases!\n"
        elif options[option_index] == 'Hellfire':
            user.spell_mod += mod_up
            Hellfire().cast(user, target=target)
            use_str += "The devastation will only get worse from here.\n"
        elif options[option_index] == "Crush":
            Crush().use(user, target)
            mod_down = random.randint(0, 10)
            if user.damage_mod > 0:
                user.damage_mod -= mod_down
            if user.spell_mod > 0:
                user.spell_mod -= mod_down
            use_str += "Interesting choice...maybe I'll show pity.\n"
        else:
            raise AssertionError("You shouldn't reach here.")
        return use_str


"""
Spell section
"""
# Spell types
class Attack(Spell):

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.turns = None

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        cast_message = ""
        if not (special or fam or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        reflect = target.status_effects['Reflect'].active
        spell_mod = caster.check_mod('magic', enemy=target)
        dodge = target.dodge_chance(caster) > random.random()
        hit_per = caster.hit_chance(target, typ='magic')
        hit = hit_per > random.random()
        if target.incapacitated():
            dodge = False
            hit = True
        if dodge and not reflect:
            cast_message += f"{target.name} dodged the {self.name} and was unhurt.\n"
        elif cover:
            cast_message += (f"{target.familiar.name} steps in front of the attack,"
                             f" absorbing the damage directed at {target.name}.\n")
        else:
            if hit and target.status_effects["Duplicates"].active:
                if random.randint(0, target.status_effects["Duplicates"].duration):
                    hit = False
                    use_str += f"{self.name} hits a mirror image of {target.name} and it vanishes from existence.\n"
                    target.status_effects["Duplicates"].duration -= 1
                    if not target.status_effects["Duplicates"].duration:
                        target.status_effects["Duplicates"].active = False
            if hit:
                damage = int(self.damage + spell_mod)
                if reflect:
                    target = caster
                    cast_message += f"{self.name} is reflected back at {caster.name}!\n"
                resist = target.check_mod('resist', enemy=caster, typ=self.subtyp)
                dam_red = target.check_mod('magic def', enemy=caster)
                crit = 1
                if not random.randint(0, self.crit):
                    crit = 2
                damage *= crit
                if crit == 2:
                    cast_message += "Critical Hit!\n"
                if caster.cls.name == "Archbishop" and caster.status_effects['Power Up'].active and self.subtyp == "Holy":
                    damage = int(damage * 1.25)
                if target.status_effects['Mana Shield'].active:
                    mana_loss = damage // target.status_effects['Mana Shield'].duration
                    if mana_loss > target.mana.current:
                        abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                        cast_message += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                        damage -= abs_dam
                        target.mana.current = 0
                        target.status_effects['Mana Shield'].active = False
                        cast_message += f"The mana shield dissolves around {target.name}.\n"
                    else:
                        cast_message += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                        target.mana.current -= mana_loss
                        damage = 0
                elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                    if damage >= target.status_effects['Power Up'].extra:
                        use_str += (f"The shield around {target.name} absorbs "
                                    f"{target.status_effects['Power Up'].extra} damage.\n")
                        damage -= target.status_effects['Power Up'].extra
                        target.status_effects['Power Up'].active = False
                        use_str += f"The shield dissolves around {target.name}.\n"
                    else:
                        use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                        target.status_effects['Power Up'].extra -= damage
                        damage = 0
                if damage < 0:
                    target.health.current -= damage
                    cast_message += f"{target.name} absorbs {self.subtyp} and is healed for {abs(damage)} health.\n"
                else:
                    damage = int(damage * (1 - resist))
                    damage -= random.randint(dam_red // 4, dam_red)
                    if damage <= 0:
                        cast_message += f"The spell was ineffective and does no damage.\n"
                        damage = 0
                    elif random.randint(0, target.stats.con // 2) > \
                            random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)):
                        damage //= 2
                        if damage > 0:
                            cast_message += f"{target.name} shrugs off the spell and only receives half of the damage.\n"
                            cast_message += f"{caster.name} damages {target.name} for {damage} hit points.\n"
                        else:
                            cast_message += f"The spell was ineffective and does no damage.\n"
                    else:
                        cast_message += f"{caster.name} damages {target.name} for {damage} hit points.\n"
                    target.health.current -= damage
                    if target.is_alive() and damage > 0 and not reflect:
                        cast_message += self.special_effect(caster, target, damage, crit)
                    elif target.is_alive() and damage > 0 and reflect:
                        cast_message += self.special_effect(caster, caster, damage, crit)
                if 'Counterspell' in target.spellbook['Spells'] and not random.randint(0, 4):  # TODO
                    cast_message += f"{target.name} uses Counterspell.\n"
                    cast_message += Counterspell().use(target, caster)
            else:
                cast_message += f"The spell misses {target.name}.\n"
            if caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active and damage > 0:
                cast_message += f"{caster.name} regens {damage} mana.\n"
                caster.mana.current += damage
                if caster.mana.current > caster.mana.max:
                    caster.mana.current = caster.mana.max
        return cast_message


class HolySpell(Spell):

    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost)
        self.damage = damage
        self.crit = crit
        self.subtyp = 'Holy'


class SupportSpell(Spell):
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Support'


class DeathSpell(Spell):
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Death'


class StatusSpell(Spell):
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Status'


class HealSpell(Spell):

    def __init__(self, name, description, cost, heal, crit):
        super().__init__(name, description, cost)
        self.heal = heal
        self.crit = crit
        self.turns = 0
        self.subtyp = 'Heal'
        self.combat = False

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        cast_message = ""
        if not fam:
            target = caster
        if not (special or fam):
            caster.mana.current -= self.cost
        crit = 1
        heal_mod = caster.check_mod('heal')
        heal = int((random.randint(target.health.max // 2, target.health.max) + heal_mod) * self.heal)
        if self.turns:
            self.hot(target, heal)
        else:
            if not random.randint(0, self.crit):
                cast_message += "Critical Heal!\n"
                crit = 2
            heal *= crit
            target.health.current += heal
            cast_message += f"{caster.name} heals {target.name} for {heal} hit points.\n"
            if target.health.current >= target.health.max:
                target.health.current = target.health.max
                cast_message += f"{target.name} is at full health.\n"
        return cast_message


class MovementSpell(Spell):
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Movement'


class IllusionSpell(Spell):
    """
    subtyp: the subtype of these abilities is 'Illusion', meaning they rely on deception
    """
    def __init__(self, name, description, cost):
        super().__init__(name, description, cost)
        self.subtyp = 'Illusion'


# Spells
class MagicMissile(Attack):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Magic Missile', description='Orbs of energy shoots forth from the caster, dealing '
                                                           'non-elemental damage.',
                         cost=5, damage=8, crit=8)
        self.subtyp = 'Non-elemental'
        self.missiles = 1

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        cast_message = ""
        if not (special or fam or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        spell_mod = caster.check_mod('magic', enemy=target)
        hits = []
        for i in range(self.missiles):
            hits.append(False)
            dodge = target.dodge_chance(caster) > random.random()
            hit_per = caster.hit_chance(target, typ='magic')
            hits[i] = hit_per > random.random()
            if target.incapacitated():
                dodge = False
                hits[i] = True
            damage = self.damage + spell_mod
            crit = 1
            if not random.randint(0, self.crit):
                crit = 2
            damage *= crit
            if crit == 2:
                cast_message += "Critical Hit!\n"
            if dodge:
                cast_message += f"{target.name} dodged the {self.name} and was unhurt.\n"
            elif cover:
                cast_message += (f"{target.familiar.name} steps in front of the attack, "
                                 f"absorbing the damage directed at {target.name}.\n")
            else:
                if hits[i] and target.status_effects["Duplicates"].active:
                    if random.randint(0, target.status_effects["Duplicates"].duration):
                        hits[i] = False
                        use_str += f"{self.name} hits a mirror image of {target.name} and it vanishes from existence.\n"
                        target.status_effects["Duplicates"].duration -= 1
                        if not target.status_effects["Duplicates"].duration:
                            target.status_effects["Duplicates"].active = False
                if hits[i]:
                    if target.status_effects['Mana Shield'].active:
                        mana_loss = damage // target.status_effects['Mana Shield'].duration
                        if mana_loss > target.mana.current:
                            abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                            cast_message += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                            damage -= abs_dam
                            target.mana.current = 0
                            target.status_effects['Mana Shield'].active = False
                            cast_message += f"The mana shield dissolves around {target.name}.\n"
                        else:
                            cast_message += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                            target.mana.current -= mana_loss
                            damage = 0
                    elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                        if damage >= target.status_effects['Power Up'].extra:
                            use_str += (f"The shield around {target.name} absorbs "
                                       f"{target.status_effects['Power Up'].extra} damage.\n")
                            damage -= target.status_effects['Power Up'].extra
                            target.status_effects['Power Up'].active = False
                            use_str += f"The shield dissolves around {target.name}.\n"
                        else:
                            use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                            target.status_effects['Power Up'].extra -= damage
                            damage = 0
                    dam_red = target.check_mod('magic def', enemy=caster)
                    damage -= random.randint(dam_red // 2, dam_red)
                    if damage <= 0:
                        cast_message += f"{self.name} was ineffective and does no damage.\n"
                        damage = 0
                    elif random.randint(0, target.stats.con // 2) > \
                            random.randint(caster.stats.intel // 2, caster.stats.intel):
                        damage //= 2
                        if damage > 0:
                            cast_message += f"{target.name} shrugs off the {self.name} and only receives half of the damage.\n"
                            cast_message += f"{caster.name} damages {target.name} for {damage} hit points.\n"
                        else:
                            cast_message += f"{self.name} was ineffective and does no damage.\n"
                    else:
                        cast_message += f"{caster.name} damages {target.name} for {damage} hit points.\n"
                    target.health.current -= damage
                    if not target.is_alive():
                        break
                else:
                    cast_message += f"The spell misses {target.name}.\n"
                if caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active and damage > 0:
                    cast_message += f"{caster.name} regens {damage} mana.\n"
                    caster.mana.current += damage
                    if caster.mana.current > caster.mana.max:
                        caster.mana.current = caster.mana.max
        if any(hits):
            if 'Counterspell' in target.spellbook['Spells'] and not random.randint(0, 4):  # TODO
                cast_message += f"{target.name} uses Counterspell.\n"
                cast_message += Counterspell().use(target, caster)
        return cast_message


class MagicMissile2(MagicMissile):

    def __init__(self):
        super().__init__()
        self.cost = 18
        self.missiles = 2


class MagicMissile3(MagicMissile):

    def __init__(self):
        super().__init__()
        self.cost = 40
        self.missiles = 3


class Ultima(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Ultima', description='Envelopes the enemy in a magical void, dealing massive non-'
                                                    'elemental damage.',
                         cost=35, damage=50, crit=4)
        self.subtyp = 'Non-elemental'
        self.rank = 2


class Maelstrom(Attack):
    """
    Enemy Spell - Behemoth
    """

    def __init__(self):
        super().__init__(name='Maelstrom', description="A massive maelstrom engulfs the target, reducing target HP to "
                                                       "10% of max or 25% on a successful save.",
                         cost=40, damage=0, crit=1)
        self.subtyp = 'Non-elemental'

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        caster.mana.current -= self.cost
        if random.randint(0, caster.intel) > random.randint(target.wisdom // 2, target.wisdom):
            hp_per = int(target.health.max * 0.10)
        else:
            hp_per = int(target.health.max * 0.25)
        target.health.current = min(target.health.current, hp_per)
        if hp_per > target.health.current:
            cast_message = f"{target.name} has their health reduced to 25%.\n"
        else:
            cast_message = f"The spell is ineffective.\n"
        return cast_message


class Meteor(Attack):
    """
    Enemy spell - Final Attack for Behemoth
    """

    def __init__(self):
        super().__init__(name='Meteor', description='A large, extra-terrestrial rock falls from the heavens, crushing '
                                                    'the target for immense damage.',
                         cost=0, damage=75, crit=3)
        self.subtyp = 'Non-elemental'


class FireSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Fire'
    
    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint(0, caster.stats.intel // 2) > \
            random.randint(target.stats.wisdom // 4, target.stats.wisdom):
                special_str += f"{target.name} is set ablaze.\n"
                dmg = random.randint(damage // 4, damage // 2)
                target.status_effects["DOT"].active = True
                target.status_effects["DOT"].duration = max(2, target.status_effects["DOT"].duration)
                target.status_effects["DOT"].extra = max(dmg, target.status_effects["DOT"].extra)
        return special_str


class Firebolt(FireSpell):
    """
    Arcane fire spells have lower crit but hit harder on average
    """

    def __init__(self):
        super().__init__(name='Firebolt', description='A mote of fire propelled at the foe.',
                         cost=2, damage=8, crit=10)
        self.school = 'Arcane'


class Fireball(Firebolt):

    def __init__(self):
        super().__init__()
        self.name = "Fireball"
        self.description = "A giant ball of fire that consumes the enemy."
        self.cost = 10
        self.damage = 25


class Firestorm(Fireball):

    def __init__(self):
        super().__init__()
        self.name = 'Firestorm'
        self.description = 'Fire rains from the sky, incinerating the enemy.'
        self.cost = 20
        self.damage = 40


class Scorch(FireSpell):

    def __init__(self):
        super().__init__(name='Scorch', description='Light a fire and watch the enemy burn!',
                         cost=6, damage=14, crit=9)
        self.school = 'Elemental'


class MoltenRock(Scorch):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Molten Rock'
        self.description = 'A giant, molten boulder is hurled at the enemy, dealing great fire damage.'
        self.cost = 16
        self.damage = 28
        self.rank = 1


class Volcano(MoltenRock):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Volcano'
        self.description = 'A mighty eruption burst out from beneath the enemy\' feet, dealing massive fire damage.'
        self.cost = 24
        self.damage = 48
        self.rank = 2


class IceSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Ice'
    
    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint(0, caster.stats.intel // 2) > \
            random.randint(target.stats.wisdom // 4, target.stats.wisdom):
                dmg = random.randint(damage // 2, damage)
                special_str += f"{target.name} is chilled to the bone, taking an extra {dmg} damage.\n"
                target.health.current -= dmg
        return special_str


class IceLance(IceSpell):
    """
    Arcane ice spells have lower average damage but have the highest chance to crit
    """

    def __init__(self):
        super().__init__(name='Ice Lance', description='A javelin of ice launched at the enemy.',
                         cost=4, damage=4, crit=2)
        self.school = 'Arcane'


class Icicle(IceLance):

    def __init__(self):
        super().__init__()
        self.name = 'Icicle'
        self.description = 'Frozen shards rain from the sky.'
        self.cost = 9
        self.damage = 15


class IceBlizzard(Icicle):

    def __init__(self):
        super().__init__()
        self.name = 'Ice Blizzard'
        self.description = 'The enemy is encased in a blistering cold, penetrating into its bones.'
        self.cost = 18
        self.damage = 25


class ElectricSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Electric'

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint(0, caster.stats.intel // 2) > \
            random.randint(target.stats.wisdom // 4, target.stats.wisdom):
                special_str += f"{target.name} gets shocked and is stunned.\n"
                target.status_effects["Stun"].active = True
                target.status_effects["Stun"].duration = max(1 + crit, target.status_effects["Stun"].duration)
        return special_str


class Shock(ElectricSpell):
    """
    Arcane electric spells have better crit than fire and better damage than ice
    """

    def __init__(self):
        super().__init__(name='Shock', description='An electrical arc from the caster\'s hands to the enemy.',
                         cost=6, damage=10, crit=4)
        self.school = 'Arcane'


class Lightning(Shock):

    def __init__(self):
        super().__init__()
        self.name = 'Lightning'
        self.description = 'Throws a bolt of lightning at the enemy.'
        self.cost = 15
        self.damage = 18


class Electrocution(Lightning):

    def __init__(self):
        super().__init__()
        self.name = 'Electrocution'
        self.description = 'A million volts of electricity passes through the enemy.'
        self.cost = 25
        self.damage = 32


class WaterSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Water'

    def special_effect(self, caster, target, damage, crit):  # TODO add prone status
        special_str = ""
        return special_str


class WaterJet(WaterSpell):

    def __init__(self):
        super().__init__(name='Water Jet', description='A jet of water erupts from beneath the enemy\'s feet.',
                         cost=4, damage=12, crit=3)
        self.school = 'Elemental'


class Aqualung(WaterJet):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Aqualung'
        self.description = 'Giant water bubbles surround the enemy and burst, causing great water damage.'
        self.cost = 13
        self.damage = 20
        self.rank = 1


class Tsunami(Aqualung):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Tsunami'
        self.description = 'A massive tidal wave cascades over your foes.'
        self.cost = 26
        self.damage = 32
        self.rank = 2


class EarthSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Earth'

    def special_effect(self, caster, target, damage, crit):  # TODO
        special_str = ""
        return special_str


class Tremor(EarthSpell):

    def __init__(self):
        super().__init__(name='Tremor', description='The ground shakes, causing objects to fall and damage the enemy.',
                         cost=3, damage=8, crit=8)
        self.school = 'Elemental'


class Mudslide(Tremor):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Mudslide'
        self.description = 'A torrent of mud and earth sweep over the enemy, causing earth damage.'
        self.cost = 16
        self.damage = 30
        self.rank = 1


class Earthquake(Mudslide):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Earthquake'
        self.description = 'The cave wall and ceiling are brought down by a massive seismic event, dealing '\
            'devastating earth damage.'
        self.cost = 26
        self.damage = 50
        self.rank = 2


class Sandstorm(EarthSpell):
    """
    Enemy Spell
    """

    def __init__(self):
        super().__init__(name='Sandstorm', description='Engulf the enemy in a sandstorm, doing damage and blinding '
                                                       'them.',
                         cost=22, damage=32, crit=6)

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if not target.status_effects["Blind"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
                    random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = -1
                special_str += f"{target.name} is blinded by the {self.name}.\n"
        return special_str


class WindSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Wind'

    def special_effect(self, caster, target, damage, crit):  # TODO add eject enemy effect
        special_str = ""
        return special_str


class Gust(WindSpell):

    def __init__(self):
        super().__init__(name='Gust', description='A strong gust of wind whips past the enemy.',
                         cost=7, damage=15, crit=6)
        self.school = 'Elemental'


class Hurricane(Gust):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Hurricane'
        self.description = 'A violent storm berates your foes, causing great wind damage.'
        self.cost = 22
        self.damage = 26
        self.rank = 1


class Tornado(Hurricane):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__()
        self.name = 'Tornado'
        self.description = 'You bring down a cyclone that pelts the enemy with debris and causes massive wind damage.'
        self.cost = 40
        self.damage = 40
        self.rank = 2


# Shadow spells
class ShadowSpell(Attack):
    def __init__(self, name, description, cost, damage, crit):
        super().__init__(name, description, cost, damage, crit)
        self.subtyp = 'Shadow'

    def special_effect(self, caster, target, damage, crit):  # TODO chance to drain enemy to heal user
        special_str = ""
        return special_str


class ShadowBolt(ShadowSpell):

    def __init__(self):
        super().__init__(name='Shadow Bolt', description='Launch a bolt of magic infused with dark energy, damaging the'
                                                         ' enemy.',
                         cost=8, damage=15, crit=5)
        self.school = 'Shadow'


class ShadowBolt2(ShadowBolt):

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 35
        self.crit = 4


class ShadowBolt3(ShadowBolt):

    def __init__(self):
        super().__init__()
        self.cost = 30
        self.damage = 45
        self.crit = 3


class Corruption(ShadowSpell):

    def __init__(self):
        super().__init__(name='Corruption', description='Damage the enemy and add a debuff that does damage over time.',
                         cost=16, damage=12, crit=5)

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint((caster.stats.charisma * crit) // 2, (caster.stats.charisma * crit)) \
                > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            turns = max(1, caster.stats.charisma // 10)
            target.status_effects["DOT"].active = True
            target.status_effects["DOT"].duration = max(turns, target.status_effects["DOT"].duration)
            target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
            special_str += f"{caster.name}'s magic penetrates {target.name}'s defenses.\n"
        return special_str


class Terrify(ShadowSpell):

    def __init__(self):
        super().__init__(name='Terrify', description='Get in the mind of the enemy, terrifying them into inaction and '
                                                     'doing damage in the process.',
                         cost=18, damage=10, crit=4)

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if not target.status_effects["Stun"].active:
            if random.randint(0, (caster.stats.charisma * crit)) > \
                random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                turns = max(crit, caster.stats.charisma // 10)
                target.status_effects["Stun"].active = True
                target.status_effects["Stun"].duration = turns
                special_str += f"{caster.name} stunned {target.name}.\n"
        return special_str


# Death spells
class Doom(DeathSpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Doom', description='Places a timer on the enemy\'s life, ending it when the timer '
                                                  'expires.',
                         cost=15)
        self.timer = 5

    def cast(self, caster, target=None, special=False, cover=False):
        cast_message = ""
        if not special:
            caster.mana.current -= self.cost
        resist = target.check_mod('resist', enemy=caster, typ=self.subtyp)
        chance = target.check_mod('luck', enemy=caster, luck_factor=10)
        if resist < 1:
            if not target.status_effects["Doom"].active:
                if random.randint(caster.stats.charisma // 4, caster.stats.charisma) * (1 - resist) \
                        > random.randint(target.stats.wisdom // 2, target.stats.wisdom) + chance:
                    target.status_effects["Doom"].active = True
                    target.status_effects["Doom"].duration = self.timer
                    cast_message += f"A timer has been placed on {target.name}'s life.\n"
                else:
                    if not special:
                        cast_message += "The magic has no effect.\n"
        else:
            if not special:
                cast_message += f"{target.name} is immune to death spells.\n"
        return cast_message


class Desoul(DeathSpell):
    """
    Can't be reflected
    """

    def __init__(self):
        super().__init__(name='Desoul', description='Removes the soul from the enemy, instantly killing it.',
                         cost=50)

    def cast(self, caster, target=None, special=False, cover=False):
        cast_message = ""
        if not special:
            caster.mana.current -= self.cost
        resist = target.check_mod('resist', enemy=caster, typ=self.subtyp)
        chance = target.check_mod('luck', enemy=caster, luck_factor=10)
        if resist < 1:
            if random.randint(0, caster.stats.charisma) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                cast_message += f"{target.name} has their soul ripped right out and falls to the ground dead.\n"
            else:
                if not special:
                    cast_message += "The spell has no effect.\n"
        else:
            if not special:
                cast_message += f"{target.name} is immune to death spells.\n"
        return cast_message


class Petrify(DeathSpell):
    """
    Rank 2 Enemy Spell; Can't be reflected except by Medusa Shield
    """

    def __init__(self):
        super().__init__(name='Petrify', description='Gaze at the enemy and turn them into stone.',
                         cost=50)
        self.rank = 2

    def cast(self, caster, target=None, special=False, cover=False):
        cast_message = ""
        if not special:
            caster.mana.current -= self.cost
        if target.equipment['OffHand'].name == 'MEDUSA SHIELD':
            cast_message += f"{target.name} uses the Medusa Shield to reflect {self.name} back at {caster.name}!"
            target = caster
        resist = target.check_mod('resist', enemy=caster, typ="Stone")
        chance = target.check_mod('luck', enemy=caster, luck_factor=1)
        if resist < 1:
            if random.randint(0, caster.stats.charisma) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                cast_message += f"{target.name} is turned to stone!"
            else:
                if not special:
                    cast_message += "The spell has no effect.\n"
        else:
            if not special:
                cast_message += f"{target.name} is immune to petrify.\n"
        return cast_message


class Disintegrate(DeathSpell):
    """
    Can't be reflected or absorbed by Mana Shield
    """

    def __init__(self):
        super().__init__(name='Disintegrate', description='An intense blast focused directly at the target, '
                                                          'obliterating them or doing great damage.',
                         cost=65)

    def cast(self, caster, target=None, cover=False):
        cast_message = ""
        caster.mana.current -= self.cost
        resist = target.check_mod('resist', enemy=caster, typ=self.subtyp)
        chance = target.check_mod('luck', enemy=caster, luck_factor=15)
        if resist < 1:
            if random.randint(0, caster.stats.charisma) * (1 - resist) \
                    > random.randint(target.stats.con // 2, target.stats.con) + chance:
                target.health.current = 0
                cast_message += f"The intense blast from disintegrate leaves {target.name} in a heap of ashes.\n"
        if target.is_alive():
            damage = int(caster.stats.charisma + (target.health.current * 0.25))
            if random.randint(0, chance):
                cast_message += f"{target.name} dodges the brunt of the blast, taking only half damage.\n"
                damage //= 2
            target.health.current -= damage
            cast_message += f"The blast from {self.name.lower()} hurts {target.name} for {damage} damage.\n"
        return cast_message


# Holy spells
class Smite(HolySpell):
    """
    Can't be reflected; holy damage crit based on melee crit and can be absorbed by mana shield TODO
    """

    def __init__(self):
        super().__init__(name='Smite', description='The power of light rebukes the enemy, adding bonus holy damage to '
                                                   'a successful attack roll.',
                         cost=10, damage=10, crit=4)
        self.school = 'Holy'

    def cast(self, caster, target=None, cover=False):
        caster.mana.current -= self.cost
        cast_message, hit, crit = caster.weapon_damage(target, cover=cover)
        if hit and target.is_alive():
            spell_mod = caster.check_mod('magic', enemy=target)
            dam_red = target.check_mod('magic def', enemy=caster)
            resist = target.check_mod('resist', enemy=caster, typ='Holy')
            damage = int(self.damage + spell_mod)
            damage *= crit
            if target.status_effects['Mana Shield'].active:
                mana_loss = damage // target.status_effects['Mana Shield'].duration
                if mana_loss > target.mana.current:
                    abs_dam = target.mana.current * target.status_effects['Mana Shield'].duration
                    cast_message += f"The mana shield around {target.name} absorbs {abs_dam} damage.\n"
                    damage -= abs_dam
                    target.mana.current = 0
                    target.status_effects['Mana Shield'].active = False
                    cast_message += f"The mana shield dissolves around {target.name}.\n"
                else:
                    cast_message += f"The mana shield around {target.name} absorbs {damage} damage.\n"
                    target.mana.current -= mana_loss
                    damage = 0
            elif target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active:
                if damage >= target.status_effects['Power Up'].extra:
                    use_str += (f"The shield around {target.name} absorbs "
                                f"{target.status_effects['Power Up'].extra} damage.\n")
                    damage -= target.status_effects['Power Up'].extra
                    target.status_effects['Power Up'].active = False
                    use_str += f"The shield dissolves around {target.name}.\n"
                else:
                    use_str += f"The shield around {target.name} absorbs {damage} damage.\n"
                    target.status_effects['Power Up'].extra -= damage
                    damage = 0
            damage = int(damage * (1 - resist))
            if damage < 0:
                target.health.current -= damage
                cast_message += f"{target.name} absorbs {self.subtyp} and is healed for {abs(damage)} health.\n"
            else:
                damage -= random.randint(dam_red // 2, dam_red)
                if damage <= 0:
                    damage = 0
                    cast_message += f"{self.name} was ineffective and does no damage.\n"
                elif random.randint(0, target.stats.con // 2) > \
                        random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)):
                    damage //= 2
                    if damage > 0:
                        cast_message += f"{target.name} shrugs off the {self.name} and only receives half of the damage.\n"
                        cast_message += f"{caster.name} smites {target.name} for {damage} hit points.\n"
                    else:
                        cast_message += f"{self.name} was ineffective and does no damage.\n"
                else:
                    cast_message += f"{caster.name} smites {target.name} for {damage} hit points.\n"
                target.health.current -= damage
        return cast_message


class Smite2(Smite):

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 20
        self.crit = 3


class Smite3(Smite):

    def __init__(self):
        super().__init__()
        self.cost = 32
        self.damage = 35
        self.crit = 2


class Holy(Attack):

    def __init__(self):
        super().__init__(name='Holy', description="The enemy is bathed in a holy light, cleansing it of evil. There "
                                                  "is a chance on critical hit that the target will be blinded for a "
                                                  "duration.",
                         cost=4, damage=10, crit=10)
        self.subtyp = 'Holy'

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if crit:
            special_str += f"{target.name} is blinded by the light!\n"
            target.status_effects["Blind"].active = True
            target.status_effects["Blind"].duration = 2
        return special_str


class Holy2(Holy):

    def __init__(self):
        super().__init__()
        self.cost = 12
        self.damage = 24
        self.crit = 8


class Holy3(Holy):

    def __init__(self):
        super().__init__()
        self.cost = 28
        self.damage = 45
        self.crit = 6


class TurnUndead(HolySpell):
    """
    crit will double chance of kill or double damage
    can't be absorbed or reflected
    """

    def __init__(self):
        super().__init__(name="Turn Undead", description="A holy chant is recited with a chance to banish any nearby "
                                                         "undead from existence.",
                         cost=8, damage=5, crit=5)

    def cast(self, caster, target=None, cover=False):
        cast_message = ""
        caster.mana.current -= self.cost
        if target.enemy_typ == "Undead":
            crit = 1
            chance = max(2, target.check_mod('luck', enemy=caster, luck_factor=6))
            if not random.randint(0, self.crit):
                cast_message += "Critical hit!\n"
                crit = 2
                chance -= 1
            if not random.randint(0, chance):
                target.health.current = 0
                cast_message += f"The {target.name} has been rebuked, destroying the undead monster.\n"
            else:
                spell_mod = caster.check_mod('magic', enemy=target)
                dam_red = target.check_mod('magic def', enemy=caster)
                resist = target.check_mod('resist', enemy=caster, typ='Holy')
                damage = int(self.damage + spell_mod)
                damage *= crit
                damage = int(damage * (1 - resist))
                damage -= dam_red
                target.health.current -= damage
                cast_message += f"{caster.name} damages {target.name} for {damage} hit points.\n"
        else:
            cast_message += "The spell does nothing.\n"
        return cast_message


class TurnUndead2(TurnUndead):

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.damage = 13
        self.crit = 3


# Heal spells
class Heal(HealSpell):
    """
    Critical heal will double healing amount
    """

    def __init__(self):
        super().__init__(name='Heal', description='A glowing light envelopes your body and heals you for a percentage '
                                                  'of the target\'s health.',
                         cost=6, heal=0.33, crit=5)

    def cast_out(self, game):
        cast_message = (f"{game.player_char.name} casts {self.name}.\n")
        if game.player_char.health.current == game.player_char.health.max:
            cast_message += f"You are already at full health.\n"
            return cast_message
        game.player_char.mana.current -= self.cost
        crit = 1
        heal_mod = game.player_char.check_mod('heal')
        heal = int(game.player_char.health.max * self.heal + heal_mod)
        if not random.randint(0, self.crit):
            cast_message += f"Critical Heal!\n"
            crit = 2
        heal *= crit
        game.player_char.health.current += heal
        cast_message += f"{game.player_char.name} heals themself for {heal} hit points.\n"
        if game.player_char.health.current >= game.player_char.health.max:
            game.player_char.health.current = game.player_char.health.max
            cast_message += f"{game.player_char.name} is at full health.\n"
        return cast_message


class Heal2(Heal):

    def __init__(self):
        super().__init__()
        self.cost = 12
        self.heal = 0.66
        self.crit = 3


class Heal3(Heal):

    def __init__(self):
        super().__init__()
        self.cost = 25
        self.heal = 1.
        self.crit = 2


class Regen(HealSpell):

    def __init__(self):
        super().__init__(name='Regen', description='Cooling waters stimulate your natural healing ability, regenerating'
                                                   ' health over time.',
                         cost=8, heal=0.25, crit=5)
        self.combat = True
        self.turns = 3

    def hot(self, caster, heal):
        caster.status_effects['Regen'].active = True
        caster.status_effects['Regen'].duration = max(self.turns, caster.status_effects["Regen"].duration)
        caster.status_effects['Regen'].extra = max(heal, caster.status_effects["Regen"].extra)


class Regen2(Regen):

    def __init__(self):
        super().__init__()
        self.cost = 18
        self.heal = 0.4


class Regen3(Regen):

    def __init__(self):
        super().__init__()
        self.cost = 30
        self.heal = 0.75


# Support spells
class Bless(SupportSpell):

    def __init__(self):
        super().__init__(name="Bless", description="A prayer is spoken, bestowing a mighty blessing upon the caster's "
                                                   "weapon, increasing melee damage.",
                         cost=8)

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        if not fam:
            target = caster
        if not (fam or special):
            caster.mana.current -= self.cost
        duration = max(2, caster.stats.wisdom // 10)
        amount = max(5, caster.stats.wisdom // 2)
        target.status_effects['Attack'].active = True
        target.status_effects['Attack'].duration = duration
        target.status_effects['Attack'].extra = amount
        return f"{target.name}'s attack increases by {amount}.\n"


class Boost(SupportSpell):
    """
    Increases magic damage
    """

    def __init__(self):
        super().__init__(name="Boost", description="Supercharge the magic capabilities of the target, increasing magic"
                                                   " damage.",
                         cost=22)

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        if not fam:
            target = caster
        if not (special or fam or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        target.status_effects['Magic'].active = True
        target.status_effects['Magic'].duration = max(2, caster.stats.intel // 10)
        target.status_effects['Magic'].extra = max(1, caster.stats.intel // 2)
        return f"{target.name}'s magic increases by {target.status_effects['Magic'].extra}.\n"


class Shell(SupportSpell):
    """
    Increases magic defense
    """

    def __init__(self):
        super().__init__(name="Shell", description="The target is shrouded in a magical veil, lessening the damage from"
                                                   " magic attacks.",
                         cost=26)

    def cast(self, caster, target=None, special=False, cover=False):
        if target is None:
            target = caster
        if not special:
            caster.mana.current -= self.cost
        target.status_effects['Magic Defense'].active = True
        target.status_effects['Magic Defense'].duration = max(2, caster.stats.intel // 10)
        target.status_effects['Magic Defense'].extra = max(1, caster.stats.intel // 2)
        return f"{target.name}'s magic defense increases by {target.status_effects['Magic Defense'].extra}.\n"


class Reflect(SupportSpell):

    def __init__(self):
        super().__init__(name="Reflect", description="A magical shield surrounds the user, reflecting incoming spells "
                                                     "back at the caster.",
                         cost=14)

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            target = caster
            if not caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active:
                caster.mana.current -= self.cost
        target.status_effects['Reflect'].active = True
        target.status_effects['Reflect'].duration = max(4, caster.stats.intel // 10)
        return f"A magic force field envelopes {target.name}.\n"


class Resurrection(SupportSpell):

    def __init__(self):
        super().__init__(name="Resurrection", description="The ultimate boon bestowed upon only the chosen few. Life "
                                                          "returns where it once left.",
                         cost=0)
        self.passive = True

    def cast(self, caster, target=None, cover=False):
        cast_message = ""
        if target is None:
            target = caster
            max_heal = target.health.max - target.health.current
            if target.mana.current > max_heal:
                target.health.current = target.health.max
                target.mana.current -= max_heal
                cast_message += f"{target.name} expends mana and is healed to full life!"
            else:
                target.health.current += target.mana.current
                cast_message += f"{target.name} expends all mana and is healed for {target.mana.current} hit points!"
                target.mana.current = 0
        else:
            heal = int(target.health.max * 0.1)
            target.health.current = heal
            cast_message += f"{target.name} is brought back to life and is healed for {heal} hit points.\n"
        caster.mana.current -= self.cost
        return cast_message


class Cleanse(SupportSpell):

    def __init__(self):
        super().__init__(name="Cleanse", description="You feel all ailments leave your body like a draught of panacea.",
                         cost=20)

    def cast(self, caster, target=None, special=False, fam=False, cover=False):
        if target is None:
            target = caster
        if not (special or fam):
            caster.mana.current -= self.cost
        target.status_effects['Stun'].active = False
        target.status_effects['Doom'].active = False
        target.status_effects['Blind'].active = False
        target.status_effects['Sleep'].active = False
        target.status_effects['Poison'].active = False
        target.status_effects['DOT'].active = False
        target.status_effects['Bleed'].active = False
        return f"All negative status effects have been cured for {target.name}!\n"


class ResistAll(SupportSpell):

    def __init__(self):
        super().__init__(name="Resist All", description="",
                         cost=25)

    def cast(self, caster, target=None, special=False):
        return f"All spell resistances are increased by 50% for {target.name}.\n"


class DivineProtection(SupportSpell):

    def __init__(self):
        super().__init__(name="Divine Protection", description="A shimmering aura envelops the user, shielding them "
                                                               "with the celestial power of the Divine. While active, "
                                                               "Divine Protection fortifies defenses, significantly "
                                                               "reducing incoming physical damage.",
                         cost=12)

    def cast(self, caster, target=None, cover=False):
        caster.mana.current -= self.cost
        def_plus = random.randint(5, 10) + (caster.stats.wisdom // 5)
        caster.status_effects["Defense"].active = True
        caster.status_effects["Defense"].duration = max(5, caster.status_effects["Defense"].duration)
        caster.status_effects["Defense"].extra += def_plus
        return f"A golden aura protects {target.name}, increasing defense by {def_plus}.\n"


# Movement spells
class Sanctuary(MovementSpell):

    def __init__(self):
        super().__init__(name='Sanctuary', description='Return to town from anywhere in the dungeon.',
                         cost=100)

    def cast_out(self, game):
        game.player_char.mana.current -= self.cost
        game.player_char.health.current = game.player_char.health.max
        game.player_char.mana.current = game.player_char.mana.max
        game.player_char.location_x, game.player_char.location_y, game.player_char.location_z = (5, 10, 0)
        return f"{game.player_char.name} casts Sanctuary and is transported back to town.\n"


class Teleport(MovementSpell):
    """
    TODO
    """

    def __init__(self):
        super().__init__(name='Teleport', description='Teleport the user to a previously set location on the same level.',
                         cost=50)
        self.combat = False

    def cast_out(self, game):
        import utils
        teleport_message = "Do you want to set your location or teleport to the previous location?"
        options = ['Set', 'Teleport']
        popup = utils.SelectionPopupMenu(game, teleport_message, options)
        option_index = popup.navigate_popup()
        if options[option_index] == 'Set':
            cast_message = f"This location has been set for teleport by {game.player_char.name}.\n"
            game.player_char.teleport = game.player_char.location_x, game.player_char.location_y, game.player_char.location_z
        else:
            cast_message = f"{game.player_char.name} teleports to set location.\n"
            game.player_char.mana.current -= self.cost
            game.player_char.location_x, game.player_char.location_y, game.player_char.location_z = game.player_char.teleport
        return cast_message


# Illusion spells
class MirrorImage(IllusionSpell):

    def __init__(self):
        super().__init__(name="Mirror Image", description="Create an illusion to fool the enemy into seeing multiple "
                                                          "of the user, sometimes causing the enemy to target the "
                                                          "wrong one. The illusion lasts until until the user is hit.",
                         cost=8)
        self.duplicates = 2

    def cast(self, caster, target=None, cover=False):
        cast_message = f"{caster.name} creates duplicates of themself to fool {target.name}."
        caster.status_effects["Duplicates"].active = True
        caster.status_effects["Duplicates"].duration = self.duplicates
        return cast_message


class MirrorImage2(MirrorImage):

    def __init__(self):
        super().__init__()
        self.cost = 20
        self.duplicates = 4


# Status spells
class BlindingFog(StatusSpell):
    """
    Rank 1 Enemy Spell
    """

    def __init__(self):
        super().__init__(name="Blinding Fog", description="The enemy is surrounding in a thick fog, lowering the chance"
                                                          " to hit on a melee attack.",
                         cost=7)
        self.subtyp = 'Status'
        self.turns = 2
        self.rank = 1

    def cast(self, caster, target=None, cover=False):
        caster.mana.current -= self.cost
        if not target.status_effects["Blind"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                target.status_effects['Blind'].active = True
                target.status_effects['Blind'].duration = -1
                return f"{target.name} is blinded.\n"
            return "The spell had no effect.\n"
        return f"{target.name} is already blinded.\n"


class PoisonBreath(Attack):
    """
    Rank 2 Enemy Spell
    """

    def __init__(self):
        super().__init__(name="Poison Breath", description="Your spew forth a toxic breath, dealing poison damage and "
                                                           "poisoning the target.",
                         cost=20, damage=15, crit=5)
        self.subtyp = 'Poison'
        self.school = 'Poison'
        self.rank = 2

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)) \
                > random.randint(target.stats.con // 2, target.stats.con) and \
                    not target.status_effects['Mana Shield'].active and \
                        not (target.cls.name == "Crusader" and target.power_up and target.status_effects['Power Up'].active):
            turns = max(2, caster.stats.intel // 10)
            damage = int(damage * (target.health.max * 0.005))  # 0.5% of max health times the damage
            target.status_effects['Poison'].active = True
            target.status_effects['Poison'].duration = max(turns, target.status_effects["Poison"].duration)
            target.status_effects['Poison'].extra = max(damage, target.status_effects["Poison"].extra)
            special_str += f"{caster.name} poisons {target.name}.\n"
        return special_str


class DiseaseBreath(StatusSpell):
    """
    Enemy Spell; not learnable by player
    """

    def __init__(self):
        super().__init__(name="Disease Breath", description="A diseased cloud emanates onto the enemy, with a chance to"
                                                            " lower the enemy's constitution permanently.",
                         cost=25)
        self.school = 'Disease'

    def cast(self, caster, target=None, cover=False):
        cast_message = "The spell does nothing.\n"
        caster.mana.current -= self.cost
        t_chance = target.check_mod('luck', enemy=caster, luck_factor=10)
        if random.randint(0, caster.stats.intel) > random.randint(target.stats.con // 2, target.stats.con):
            if not random.randint(0, target.stats.con + t_chance):
                cast_message = f"The disease cripples {target.name}, lowering their constitution by 1.\n"
                target.stats.con -= 1
        return cast_message


class Sleep(StatusSpell):

    def __init__(self):
        super().__init__(name="Sleep", description="A magical tune lulls the target to sleep.",
                         cost=9)
        self.turns = 3

    def cast(self, caster, target=None, special=False, cover=False):
        if not (special or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        if not target.status_effects["Sleep"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) \
                    > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Sleep'].active = True
                target.status_effects['Sleep'].duration = self.turns
                return f"{target.name} is asleep.\n"
            return f"{caster.name} fails to put {target.name} to sleep.\n"
        return f"{target.name} is already asleep.\n"


class Stupefy(StatusSpell):

    def __init__(self):
        super().__init__(name="Stupefy", description="Hit the enemy so hard, they go stupid and cannot act.",
                         cost=14)
        self.turns = 2

    def cast(self, caster, target=None, fam=False, cover=False):
        if not fam:
            caster.mana.current -= self.cost
        if not target.status_effects["Stun"].active:
            if random.randint(0, caster.stats.intel) \
                    > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Stun'].active = True
                target.status_effects['Stun'].duration = self.turns
                return f"{target.name} is stunned.\n"
            return f"{caster.name} fails to stun {target.name}.\n"
        return f"{target.name} is already stunned.\n"


class WeakenMind(StatusSpell):

    def __init__(self):
        super().__init__(name="Weaken Mind", description="Attack the enemy's mind, diminishing their ability to deal "
                                                         "damage and defend against magic.",
                         cost=20)

    def cast(self, caster, target=None, cover=False):
        cast_message = ""
        if not caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active:
            caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
            random.randint(target.stats.con // 2, target.stats.con):
            for stat in ['Magic', 'Magic Defense']:
                stat_mod = random.randint(max(1, caster.stats.intel // 5), max(5, caster.stats.intel // 2))
                target.status_effects[stat].active = True
                target.status_effects[stat].duration += random.randint(1, max(2, caster.stats.intel // 10))
                target.status_effects[stat].extra -= stat_mod
                cast_message += f"{target.name}'s {stat.lower()} is lowered by {stat_mod}.\n"
        return cast_message


class Enfeeble(StatusSpell):

    def __init__(self):
        super().__init__(name="Enfeeble", description="Cripple your foe, reducing their attack and defense rating.",
                         cost=12)

    def cast(self, caster, target=None, fam=False, cover=False):
        cast_message = ""
        if not (fam or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > random.randint(target.stats.con // 2, target.stats.con):
            for stat in ['Attack', 'Defense']:
                stat_mod = random.randint(max(1, caster.stats.intel // 5), max(5, caster.stats.intel // 2))
                target.status_effects[stat].active = True
                target.status_effects[stat].duration += random.randint(1, max(2, caster.stats.intel // 10))
                target.status_effects[stat].extra -= stat_mod
                cast_message += f"{target.name}'s {stat.lower()} is lowered by {stat_mod}.\n"
        else:
            cast_message += f"{target.name} resists the spell.\n"
        return cast_message


class Dispel(StatusSpell):

    def __init__(self):
        super().__init__(name="Dispel", description="Cast an anti-magic spell on your foe, removing any positive status"
                                                    " effects.",
                         cost=20)

    def cast(self, caster, target=None, special=False, cover=False):
        if not (special or (caster.cls.name == "Wizard" and caster.status_effects['Power Up'].active)):
            caster.mana.current -= self.cost
        if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
            random.randint(0, target.stats.wisdom):
            target.status_effects["Regen"].active = False
            target.status_effects["Reflect"].active = False
            target.status_effects["Attack"].active = False
            target.status_effects["Defense"].active = False
            target.status_effects["Magic"].active = False
            target.status_effects["Magic Defense"].active = False
            return f"All positive status effects removed from {target.name}.\n"
        return f"{target.name} resists the spell.\n"


class Silence(StatusSpell):

    def __init__(self):
        super().__init__(name="Silence", description="Tongue-tie the enemy's brain, making spell casting impossible.",
                         cost=20)

    def cast(self, caster, target=None, special=False, cover=False):
        if not special:
            caster.mana.current -= self.cost
        if not target.status_effects["Silence"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
                random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Silence'].active = True
                target.status_effects['Silence'].duration = -1
                return f"{target.name} has been silenced.\n"
            return "The spell is ineffective.\n"
        return f"{target.name} is already silenced.\n"


class Berserk(StatusSpell):

    def __init__(self):
        super().__init__(name="Berserk", description="Enrage the enemy, increasing damage but lowering accuracy and "
                                                     "making them only attack.",
                         cost=15)

    def cast(self, caster, target=None, special=False, cover=False):
        if not special:
            caster.mana.current -= self.cost
        if not target.status_effects["Berserk"].active:
            if random.randint(caster.stats.intel // 2, caster.stats.intel) > \
                random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                target.status_effects['Berserk'].active = True
                target.status_effects['Berserk'].duration = random.randint(1, max(2, caster.stats.intel // 10))
                return f"{target.name} is enraged.\n"
            return "The spell is ineffective.\n"
        return f"{target.name} is already enraged.\n"


# Enemy spells
class Hellfire(Attack):
    """
    Devil's spell; the fire is non-elemental
    """

    def __init__(self):
        super().__init__(name="Hellfire", description="The flames of Hell lick at the toes of the enemy, inflicting "
                                                      "immense initial damage as well as damage over time.",
                         cost=25, damage=100, crit=2)
        self.subtyp = 'Non-elemental'

    def special_effect(self, caster, target, damage, crit):
        special_str = ""
        if random.randint((caster.stats.intel * crit) // 2, (caster.stats.intel * crit)) \
                > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
            turns = max(2, caster.stats.intel // 10)
            target.status_effects["DOT"].active = True
            target.status_effects["DOT"].duration = max(turns, target.status_effects["DOT"].duration)
            target.status_effects["DOT"].extra = max(damage, target.status_effects["DOT"].extra)
            special_str += f"The flames of Hell continue to burn {target.name}.\n"
        return special_str


# Parameters
skill_dict = {"Warrior": {"3": ShieldSlam,
                          "8": PiercingStrike,
                          "10": Disarm,
                          "15": Charge,
                          "23": Parry,
                          "25": TrueStrike,
                          "28": BattleCry},
              "Weapon Master": {"1": MortalStrike,
                                "6": DoubleStrike,
                                "21": TruePiercingStrike},
              "Berserker": {"5": MortalStrike2,
                            "20": TripleStrike},
              "Paladin": {"6": ShieldBlock,
                          "13": Goad,
                          "18": DoubleStrike},
              "Crusader": {"5": MortalStrike,
                           "22": TripleStrike,
                           "40": TruePiercingStrike},
              "Lancer": {"2": Jump,
                         "15": DoubleJump},
              "Dragoon": {"1": TruePiercingStrike,
                          "10": ShieldBlock,
                          "20": TripleJump},
              "Sentinel": {"1": ShieldBlock,
                                  "3": Goad},
              "Stalwart Defender": {},
              "Mage": {"25": ManaShield},
              "Sorcerer": {"10": DoubleCast,
                           "18": MirrorImage},
              "Wizard": {"5": ManaShield2,
                         "15": TripleCast,
                         "30": MirrorImage2},
              "Warlock": {"1": Familiar,
                          "5": HealthDrain,
                          "15": ManaDrain,
                          "20": Familiar2},
              "Shadowcaster": {"10": HealthManaDrain,
                               "20": Familiar3},
              "Spellblade": {"1": EnhanceBlade,
                             "10": ImbueWeapon,
                             "15": Parry,
                             "28": TrueStrike},
              "Knight Enchanter": {"1": EnhanceArmor,
                                   "10": DoubleStrike},
              "Footpad": {"3": Disarm,
                          "5": SmokeScreen,
                          "6": PocketSand,
                          "8": Backstab,
                          "10": Steal,
                          "12": KidneyPunch,
                          "16": DoubleStrike,
                          "19": SleepingPowder,
                          "25": Parry},
              "Thief": {"5": Lockpick,
                        "12": GoldToss,
                        "15": Mug,
                        "20": PoisonStrike},
              "Rogue": {"5": SneakAttack,
                        "10": SlotMachine,
                        "12": TripleStrike},
              "Inquisitor": {"1": Reveal,
                             "2": PiercingStrike,
                             "5": Inspect,
                             "10": ExploitWeakness,
                             "14": KeenEye,
                             "15": ShieldBlock,
                             "22": TrueStrike},
              "Seeker": {"1": Cartography,
                         "16": TripleStrike,
                         "25": TruePiercingStrike},
              "Assassin": {"8": PoisonStrike,
                           "15": Lockpick,
                           "18": TripleStrike},
              "Ninja": {"8": Mug,
                        "25": FlurryBlades},
              "Healer": {},
              "Cleric": {"6": ShieldSlam,
                         "12": ShieldBlock,
                         "27": TrueStrike},
              "Templar": {"1": Parry,
                          "4": PiercingStrike,
                          "6": Goad,
                          "14": Charge,
                          "22": DoubleStrike,
                          "45": TruePiercingStrike},
              "Priest": {"10": ManaShield},
              "Archbishop": {"5": DoubleCast,
                             "15": ManaShield2},
              "Monk": {"1": ChiHeal,
                       "3": DoubleStrike,
                       "5": LegSweep,
                       "7": TrueStrike,
                       "10": PurityBody,
                       "25": Parry},
              "Master Monk": {"1": Evasion,
                              "10": TripleStrike,
                              "15": PurityBody2},
              "Pathfinder": {},
              "Druid": {"2": Transform,
                        "10": Transform2,
                        "15": MortalStrike},
              "Lycan": {"1": Transform3,
                        "11": Charge,
                        "15": BattleCry,
                        "25": MortalStrike2},
              "Diviner": {"1": LearnSpell,
                          "18": DoubleCast},
              "Geomancer": {"1": LearnSpell2,
                            "25": TripleCast},
              "Shaman": {"1": ElementalStrike,
                         "6": PiercingStrike,
                         "14": DoubleStrike,
                         "19": TrueStrike},
              "Soulcatcher": {"1": AbsorbEssence,
                              "2": Parry,
                              "9": TripleStrike,
                              "29": TruePiercingStrike},
              }

spell_dict = {"Warrior": {},
              "Weapon Master": {},
              "Berserker": {},
              "Paladin": {"1": Heal,
                          "4": Smite,
                          "16": Heal2,
                          "24": DivineProtection},
              "Crusader": {"3": Smite2,
                           "8": Heal3,
                           "16": Cleanse,
                           "18": Smite3,
                           "20": Dispel},
              "Lancer": {},
              "Dragoon": {},
              "Sentinel": {},
              "Stalwart Defender": {},
              "Mage": {"2": Firebolt,
                       "6": MagicMissile,
                       "8": IceLance,
                       "13": Shock,
                       "16": Enfeeble},
              "Sorcerer": {"2": Icicle,
                           "6": Reflect,
                           "8": Lightning,
                           "10": Sleep,
                           "15": Fireball,
                           "16": Dispel,
                           "18": MagicMissile2,
                           "20": WeakenMind},
              "Wizard": {"4": Firestorm,
                         "7": Boost,
                         "10": IceBlizzard,
                         "15": Electrocution,
                         "20": Teleport,
                         "25": MagicMissile3},
              "Warlock": {"1": ShadowBolt,
                          "4": Corruption,
                          "10": Terrify,
                          "12": ShadowBolt2,
                          "15": Doom,
                          "19": Dispel},
              "Shadowcaster": {"8": ShadowBolt3,
                               "18": Desoul},
              "Spellblade": {"20": Reflect},
              "Knight Enchanter": {"1": EnhanceArmor,
                                   "3": Fireball,
                                   "9": Icicle,
                                   "12": Lightning,
                                   "20": Dispel},
              "Footpad": {},
              "Thief": {},
              "Rogue": {},
              "Inquisitor": {"3": Dispel,
                             "8": Silence,
                             "12": Enfeeble,
                             "15": Reflect},
              "Seeker": {"1": Teleport,
                         "4": ResistAll,
                         "10": Sanctuary,
                         "16": WeakenMind},
              "Assassin": {},
              "Ninja": {"20": Desoul},
              "Healer": {"2": Heal,
                         "3": TurnUndead,
                         "8": Regen,
                         "10": Holy,
                         "26": Heal2},
              "Cleric": {"1": Smite,
                         "5": Bless,
                         "14": Cleanse,
                         "15": Silence,
                         "16": Smite2,
                         "19": TurnUndead2},
              "Templar": {"6": Regen2,
                          "10": Smite3,
                          "18": Dispel},
              "Priest": {"1": Regen2,
                         "3": Holy2,
                         "6": Shell,
                         "11": Cleanse,
                         "15": Bless,
                         "17": Dispel,
                         "21": Berserk,
                         "30": Heal3},
              "Archbishop": {"4": Holy3,
                             "6": Silence,
                             "7": Regen3,
                             "20": Resurrection},
              "Monk": {"15": Shell},
              "Master Monk": {"2": Reflect,
                              "12": Dispel},
              "Pathfinder": {"5": Tremor,
                             "11": WaterJet,
                             "14": Gust,
                             "19": Scorch},
              "Druid": {"5": Regen},
              "Lycan": {"8": Dispel},
              "Diviner": {"3": Enfeeble,
                          "14": Dispel,
                          "23": Berserk},
              "Geomancer": {"10": WeakenMind,
                            "15": Boost},
              "Shaman": {"9": Regen},
              "Soulcatcher": {"6": Dispel,
                              "12": Desoul},
              }
