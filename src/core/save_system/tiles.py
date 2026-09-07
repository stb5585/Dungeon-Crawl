"""Map-tile state serialization."""

import ast

from .enemy import EnemyStateSerializer


class TileStateSerializer:
    """Serializes/deserializes tile state (mutable attributes)."""

    RESTORABLE_STATE_KEYS = frozenset(
        {
            "visited",
            "near",
            "open",
            "read",
            "blocked",
            "warped",
            "active",
            "defeated",
            "enemy_state",
            "drink",
            "nimue",
            "nimue_met_before",
            "trap_type",
            "trap_triggered",
            "deathcap_available",
            "deathcap_gathered",
        }
    )

    @staticmethod
    def _parse_position_key(pos_str: object) -> tuple[int, int, int] | None:
        try:
            pos = ast.literal_eval(pos_str)
        except (ValueError, SyntaxError, TypeError):
            return None

        if (
            not isinstance(pos, tuple)
            or len(pos) != 3
            or not all(isinstance(coord, int) for coord in pos)
        ):
            return None
        return pos

    @staticmethod
    def serialize_tile_state(world_dict: dict) -> dict[str, dict]:
        """Convert tile states to data dictionary, keyed by position tuple."""
        tile_states = {}

        for pos, tile in world_dict.items():
            # Store mutable state attributes
            state = {
                "visited": getattr(tile, "visited", False),
                "near": getattr(tile, "near", False),
                "open": getattr(tile, "open", False),
                "read": getattr(tile, "read", False),
                "blocked": getattr(tile, "blocked", None),
                "warped": getattr(tile, "warped", False),
            }

            if hasattr(tile, "trap_type"):
                state["trap_type"] = tile.trap_type
            if hasattr(tile, "trap_triggered"):
                state["trap_triggered"] = tile.trap_triggered
            if hasattr(tile, "trap_warned"):
                state["trap_warned"] = tile.trap_warned
            if hasattr(tile, "deathcap_available"):
                state["deathcap_available"] = tile.deathcap_available
            if hasattr(tile, "deathcap_gathered"):
                state["deathcap_gathered"] = tile.deathcap_gathered

            if hasattr(tile, "active"):
                state["active"] = tile.active

            # For tiles with enemies and defeated flag
            if hasattr(tile, "defeated"):
                state["defeated"] = tile.defeated
                if hasattr(tile, "enemy") and tile.enemy:
                    state["enemy_state"] = EnemyStateSerializer.serialize(tile.enemy)

            # For tiles with other special state (drink, nimue, etc.)
            if hasattr(tile, "drink"):
                state["drink"] = tile.drink
            if hasattr(tile, "nimue"):
                state["nimue"] = tile.nimue
            if hasattr(tile, "nimue_met_before"):
                state["nimue_met_before"] = tile.nimue_met_before

            tile_states[str(pos)] = state

        return tile_states

    @staticmethod
    def restore_tile_state(world_dict: dict, tile_states: dict) -> None:
        """Restore tile state from serialized data."""
        for pos_str, state in tile_states.items():
            if not isinstance(state, dict):
                continue

            # Parse position string back to tuple
            pos = TileStateSerializer._parse_position_key(pos_str)
            if pos is None:
                continue

            if pos not in world_dict:
                continue

            tile = world_dict[pos]

            # Restore basic attributes
            if "visited" in state:
                tile.visited = state["visited"]
            if "near" in state:
                tile.near = state["near"]
            if "open" in state:
                tile.open = state["open"]
            if "read" in state:
                tile.read = state["read"]
            if "blocked" in state:
                tile.blocked = state["blocked"]
            if "warped" in state:
                tile.warped = state["warped"]
            if "active" in state and hasattr(tile, "active"):
                tile.active = state["active"]
            if "trap_type" in state and hasattr(tile, "trap_type"):
                tile.trap_type = state["trap_type"]
            if "trap_triggered" in state and hasattr(tile, "trap_triggered"):
                tile.trap_triggered = state["trap_triggered"]
            if "trap_warned" in state and hasattr(tile, "trap_warned"):
                tile.trap_warned = state["trap_warned"]
            if "deathcap_available" in state and hasattr(tile, "deathcap_available"):
                tile.deathcap_available = state["deathcap_available"]
            if "deathcap_gathered" in state and hasattr(tile, "deathcap_gathered"):
                tile.deathcap_gathered = state["deathcap_gathered"]

            # Restore defeated flag
            if "defeated" in state and hasattr(tile, "defeated"):
                tile.defeated = state["defeated"]

            # Restore enemy state if present
            if "enemy_state" in state and hasattr(tile, "enemy"):
                tile.enemy = EnemyStateSerializer.deserialize(state["enemy_state"])

            # If defeated, ensure the boss/enemy is cleared to prevent respawns
            if getattr(tile, "defeated", False) and hasattr(tile, "enemy"):
                tile.enemy = None

            # Restore special attributes
            if "drink" in state and hasattr(tile, "drink"):
                tile.drink = state["drink"]
            if "nimue" in state and hasattr(tile, "nimue"):
                tile.nimue = state["nimue"]
            if "nimue_met_before" in state and hasattr(tile, "nimue_met_before"):
                tile.nimue_met_before = state["nimue_met_before"]

    @staticmethod
    def summarize_tile_state_payload(world_dict: dict, tile_states: object) -> dict[str, object]:
        """Return compact diagnostics for serialized tile-state data."""
        if not isinstance(tile_states, dict):
            return {
                "total_entries": 0,
                "valid_entries": 0,
                "malformed_position_count": 0,
                "malformed_state_count": 0,
                "missing_world_position_count": 0,
                "restorable_attribute_counts": {},
                "unknown_attribute_count": 0,
                "unknown_attribute_keys": (),
            }

        malformed_positions = 0
        malformed_states = 0
        missing_world_positions = 0
        valid_entries = 0
        restorable_attribute_counts: dict[str, int] = {}
        unknown_attribute_keys: set[str] = set()

        for pos_str, state in tile_states.items():
            if not isinstance(state, dict):
                malformed_states += 1
                continue
            pos = TileStateSerializer._parse_position_key(pos_str)
            if pos is None:
                malformed_positions += 1
                continue
            if pos not in world_dict:
                missing_world_positions += 1
                continue
            valid_entries += 1
            for key in state:
                if key in TileStateSerializer.RESTORABLE_STATE_KEYS:
                    restorable_attribute_counts[key] = restorable_attribute_counts.get(key, 0) + 1
                else:
                    unknown_attribute_keys.add(str(key))

        return {
            "total_entries": len(tile_states),
            "valid_entries": valid_entries,
            "malformed_position_count": malformed_positions,
            "malformed_state_count": malformed_states,
            "missing_world_position_count": missing_world_positions,
            "restorable_attribute_counts": dict(sorted(restorable_attribute_counts.items())),
            "unknown_attribute_count": len(unknown_attribute_keys),
            "unknown_attribute_keys": tuple(sorted(unknown_attribute_keys)),
        }
