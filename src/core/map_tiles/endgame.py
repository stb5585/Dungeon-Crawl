"""Liminal, endgame, shop, warp, and funhouse tiles."""

from .. import items, town
from .paths import MapTile, SpecialTile
from .rooms import ChestRoom
from .rules import jester_defeated


class FinalBlocker(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not game.player_char.has_relics():
            intro_str += "An invisible force blocks your path.\n"
        else:
            intro_str += "The way has opened. Destiny awaits!\n"
        return intro_str

    def available_actions(self, player_char):
        if not player_char.has_relics():
            return []
        return []

    def special_text(self, game):
        if game.player_char.has_relics() and not self.read:
            game.special_event("Final Blocker")
            self.read = True


class LiminalGuide(SpecialTile):
    """The Hooded Figure guide in the Liminal Gap sanctuary."""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "The Hooded Figure waits here, wounded but watchful.\n"
        return intro_str

    def special_text(self, game):
        return None


class LiminalGuardianGate(SpecialTile):
    """Blocked placeholder gate for a future Guardian trial."""

    guardian_name = ""
    liminal_gate_event = ""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += f"The gate of {self.guardian_name} is sealed.\n"
        return intro_str

    def special_text(self, game):
        return None


class TriangulusGate(LiminalGuardianGate):
    guardian_name = "Triangulus"
    liminal_gate_event = "Triangulus Gate"


class QuadrataGate(LiminalGuardianGate):
    guardian_name = "Quadrata"
    liminal_gate_event = "Quadrata Gate"


class HexagonumGate(LiminalGuardianGate):
    guardian_name = "Hexagonum"
    liminal_gate_event = "Hexagonum Gate"


class LunaGate(LiminalGuardianGate):
    guardian_name = "Luna"
    liminal_gate_event = "Luna Gate"


class PolarisGate(LiminalGuardianGate):
    guardian_name = "Polaris"
    liminal_gate_event = "Polaris Gate"


class InfinitasGate(LiminalGuardianGate):
    guardian_name = "Infinitas"
    liminal_gate_event = "Infinitas Gate"


class LiminalSeventhSeat(SpecialTile):
    """The empty Seventh Seat where Voluntas is revealed."""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "An empty seat waits where the seventh principle should be.\n"
        return intro_str

    def special_text(self, game):
        return None


class LiminalAcolyte(SpecialTile):
    """The failed hero who serves as Vesperion's tragic mirror."""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "A silent Acolyte kneels in the gray light.\n"
        return intro_str

    def special_text(self, game):
        return None


class LiminalReflection(SpecialTile):
    """The Reflection/Psychopomp story gate before returning to life."""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "A mirror-dark threshold reflects paths you never walked.\n"
        return intro_str

    def special_text(self, game):
        return None


class LiminalExitBlocker(SpecialTile):
    """Blocked return path from the Liminal Gap hub."""

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "A torn threshold hangs here, but it will not open.\n"
        return intro_str

    def special_text(self, game):
        return None


class FinalRoom(SpecialTile):
    """
    Player will be given an option to fight or turn around; fight will move them to FinalBossRoom and turn around will
      move them back to FinalBlocker
    Tiles to show -
    (13,  8, 6), (14,  8, 6), (15,  8, 6), (16,  8, 6), (17,  8, 6)
    (13,  9, 6), (14,  9, 6), (15,  9, 6), (16,  9, 6), (17,  9, 6)
    (13, 10, 6), (14, 10, 6), (15, 10, 6), (16, 10, 6), (17, 10, 6)
    (13, 11, 6), (14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6)
    """

    def adjacent_visited(self, player_char):
        """"
        Changes visited parameter for area around final boss
        """

        for x in [13, 14, 15, 16, 17]:
            for y in [8, 9, 10, 11]:
                player_char.world_dict[(x, y, 6)].near = True

    def available_actions(self, player_char):
        """Return combat actions for the final boss."""
        action_list = ["Attack", "Use Item", "Flee"]
        if not player_char.abilities_suppressed():
            if player_char.usable_abilities("Spells"):
                action_list.insert(1, "Cast Spell")
            if player_char.usable_abilities("Skills"):
                action_list.insert(1, "Use Skill")
        return action_list

    def special_text(self, game):
        fight = game.special_event("Final Boss")
        if fight:
            game.player_char.move_north()
            game.player_char.move_north()
        else:
            game.player_char.move_south()


class SecretShop(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False  # Cannot enter - interact from adjacent space

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        game.player_char.state = 'normal'
        town.secret_shop(game)

    def special_text(self, game):
        if not self.read:
            game.special_event("Secret Shop")
            self.read = True

    def available_actions(self, player_char):
        return []


class UltimateArmorShop(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.looted = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} finds a forge in the depths of the dungeon.\n"
                        f"A large man stands in front of you.\n")
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        game.player_char.state = 'normal'
        town.ultimate_armor_repo(game)

    def available_actions(self, player_char):
        return []

    def special_text(self, game):
        if not self.read:
            game.special_text("Ultimate Armor")
            self.read = True


class WarpPoint(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.warped = False

    def modify_player(self, game):
        """Mark the warp tile visited; the frontend owns travel confirmation."""
        self.warped = False
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return []


class FunhouseTeleporter(SpecialTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.active = True

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

        if jester_defeated(game.player_char):
            self.active = False
            return

        if not self.active:
            return

        # Already in the funhouse; no further teleporting needed.
        if game.player_char.location_z == 7:
            return

        # Save return point for potential future exit logic.
        game.player_char.funhouse_return = (
            game.player_char.location_x,
            game.player_char.location_y,
            game.player_char.location_z,
            game.player_char.facing,
        )

        # Move player into the dedicated funhouse challenge level (level 4 boss area).
        game.player_char.location_x = 0
        game.player_char.location_y = 9
        game.player_char.location_z = 7
        game.player_char.facing = "north"

        # Trigger funhouse entry special event
        game.special_event("Funhouse Entry")

class FunhouseMimicChest(ChestRoom):
    """A special chest for the funhouse that guarantees a Mimic encounter and drops a Jester Token."""

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.locked = False
        self.enemy = None

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.open:
            intro_str += f"{game.player_char.name} finds a peculiar chest adorned with strange patterns. (Enter 'o' to open)\n"
        else:
            intro_str += "This chest has already been opened.\n"
        return intro_str

    def available_actions(self, player_char):
        if not self.open:
            if player_char.state == 'fight':
                action_list = ["Attack", "Use Item", "Flee"]
                if not player_char.abilities_suppressed():
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list.insert(1, "Defend")
                if player_char.is_disarmed():
                    action_list.insert(2, "Pickup Weapon")
                action_list = player_char.additional_actions(action_list)
                return action_list
            return []
        return []

    def generate_loot(self):
        """Generate level 4 loot for the funhouse chest (not scaled to z=7)."""
        if self.loot is None:
            # Generate loot at level 4 difficulty (not at zone level)
            self.loot = items.random_item(4)
