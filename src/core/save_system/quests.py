"""Quest and quest-item serialization."""

from .. import items
from .item_serialization import ItemSerializer


class QuestDataSerializer:
    """Serializes/deserializes quest data with proper item handling."""

    @staticmethod
    def _deserialize_item_reference(item_data):
        """Resolve quest item references from serialized dicts or legacy strings."""
        if isinstance(item_data, dict):
            return ItemSerializer.deserialize(item_data)

        if not isinstance(item_data, str) or not item_data:
            return item_data

        if hasattr(items, item_data):
            item_class = getattr(items, item_data)
            if hasattr(item_class, "__call__"):
                try:
                    return item_class()
                except Exception:
                    return item_data

        for attr_name in dir(items):
            attr = getattr(items, attr_name)
            if not hasattr(attr, "__call__"):
                continue
            try:
                instance = attr()
            except Exception:
                continue
            if getattr(instance, "name", None) == item_data:
                return instance

        return item_data

    @staticmethod
    def serialize_quest_dict(quest_dict: dict) -> dict:
        """Convert quest_dict with item objects to serializable format."""
        serialized = {}

        for quest_type, quests_by_category in quest_dict.items():
            serialized[quest_type] = {}

            if quest_type == "Bounty":
                # Bounty format: {enemy_name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_category.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        # Serialize bounty data if it contains items/enemies
                        serialized_bounty = dict(bounty_data)

                        # Serialize enemy to just its name
                        if "enemy" in serialized_bounty and serialized_bounty["enemy"]:
                            enemy = serialized_bounty["enemy"]
                            if hasattr(enemy, "name"):
                                serialized_bounty["enemy"] = enemy.name
                            # else: already a string, keep as-is

                        # Serialize reward item
                        if "reward" in serialized_bounty and serialized_bounty["reward"]:
                            serialized_bounty["reward"] = ItemSerializer.serialize(
                                serialized_bounty["reward"]()
                            )

                        serialized[quest_type][quest_name] = [serialized_bounty, count, completed]
                    else:
                        serialized[quest_type][quest_name] = quest_info
            else:
                # Main/Side quests: {quest_name: quest_data}
                for quest_name, quest_data in quests_by_category.items():
                    if isinstance(quest_data, dict):
                        serialized_quest = dict(quest_data)

                        # Serialize item class in 'What' field for Collect quests FIRST
                        # (before other processing to ensure it's properly handled)
                        if "What" in serialized_quest and serialized_quest.get("Type") == "Collect":
                            what = serialized_quest["What"]
                            if isinstance(what, type):
                                try:
                                    instance = what()
                                    serialized_quest["What"] = ItemSerializer.serialize(instance)
                                except Exception:
                                    serialized_quest["What"] = what.__name__
                            elif isinstance(what, str):
                                # Already a string, leave it
                                pass
                            elif hasattr(what, "name"):
                                # It's an instance, serialize it
                                serialized_quest["What"] = ItemSerializer.serialize(what)

                        # Serialize item classes in 'Reward' field
                        if "Reward" in serialized_quest:
                            reward = serialized_quest["Reward"]
                            if isinstance(reward, list):
                                # Convert item classes to serialized form
                                serialized_rewards = []
                                for r in reward:
                                    if isinstance(r, str):
                                        serialized_rewards.append(
                                            r
                                        )  # Keep string keywords like 'Gold'
                                    elif isinstance(r, type):
                                        # It's a class, serialize by instantiating
                                        try:
                                            instance = r()
                                            serialized_rewards.append(
                                                ItemSerializer.serialize(instance)
                                            )
                                        except Exception:
                                            serialized_rewards.append(r.__name__)
                                    else:
                                        # It's an instance or something else
                                        serialized_rewards.append(ItemSerializer.serialize(r))
                                serialized_quest["Reward"] = serialized_rewards
                            elif reward == "Gold":
                                pass  # Leave as-is
                            elif isinstance(reward, type):
                                serialized_quest["Reward"] = ItemSerializer.serialize(reward())

                        serialized[quest_type][quest_name] = serialized_quest
                    else:
                        serialized[quest_type][quest_name] = quest_data

        return serialized

    @staticmethod
    def deserialize_quest_dict(serialized: dict) -> dict:
        """Reconstruct quest_dict with proper item objects from serialized format."""
        quest_dict = {}

        for quest_type, quests_by_category in serialized.items():
            quest_dict[quest_type] = {}

            if quest_type == "Bounty":
                # Bounty format: {enemy_name: [bounty_data, count, completed]}
                for quest_name, quest_info in quests_by_category.items():
                    if isinstance(quest_info, list) and len(quest_info) >= 3:
                        bounty_data, count, completed = quest_info[0], quest_info[1], quest_info[2]
                        # Deserialize bounty data if it contains items/enemies
                        deserialized_bounty = dict(bounty_data)

                        # Deserialize enemy from name
                        if "enemy" in deserialized_bounty and deserialized_bounty["enemy"]:
                            enemy_name_or_str = deserialized_bounty["enemy"]
                            if isinstance(enemy_name_or_str, str):
                                # Extract just the name if it's a full string representation
                                # (e.g., "Alligator | Health: 87/87 | Mana: 28/28" -> "Alligator")
                                enemy_name = enemy_name_or_str.split(" | ")[0].strip()

                                # Reconstruct enemy from name
                                from .. import enemies as enemies_module

                                if hasattr(enemies_module, enemy_name):
                                    enemy_class = getattr(enemies_module, enemy_name)
                                    deserialized_bounty["enemy"] = enemy_class()
                                else:
                                    # Keep as string if we can't find the class
                                    deserialized_bounty["enemy"] = enemy_name

                        # Deserialize reward item
                        if "reward" in deserialized_bounty and deserialized_bounty["reward"]:
                            if isinstance(deserialized_bounty["reward"], dict):
                                # It's serialized, deserialize it to get the item class
                                item_class_name = deserialized_bounty["reward"].get("class")
                                if item_class_name:
                                    # Convert to callable class reference
                                    from .. import items as items_module

                                    if hasattr(items_module, item_class_name):
                                        deserialized_bounty["reward"] = getattr(
                                            items_module, item_class_name
                                        )
                                    else:
                                        # Fallback: keep as None if class not found
                                        deserialized_bounty["reward"] = None
                            else:
                                # It's already an item class or callable
                                deserialized_bounty["reward"] = deserialized_bounty["reward"]
                        quest_dict[quest_type][quest_name] = [deserialized_bounty, count, completed]
                    else:
                        quest_dict[quest_type][quest_name] = quest_info
            else:
                # Main/Side quests: {quest_name: quest_data}
                for quest_name, quest_data in quests_by_category.items():
                    if isinstance(quest_data, dict):
                        deserialized_quest = dict(quest_data)

                        # Deserialize item classes in 'Reward' field
                        if "Reward" in deserialized_quest:
                            reward = deserialized_quest["Reward"]
                            if isinstance(reward, list):
                                deserialized_rewards = []
                                for r in reward:
                                    if isinstance(r, str):
                                        deserialized_rewards.append(r)  # Keep string keywords
                                    elif isinstance(r, dict):
                                        # It's serialized, deserialize it
                                        deserialized_rewards.append(ItemSerializer.deserialize(r))
                                    else:
                                        deserialized_rewards.append(r)
                                deserialized_quest["Reward"] = deserialized_rewards

                        # Deserialize item class in 'What' field for Collect quests
                        if (
                            "What" in deserialized_quest
                            and deserialized_quest.get("Type") == "Collect"
                        ):
                            deserialized_quest["What"] = (
                                QuestDataSerializer._deserialize_item_reference(
                                    deserialized_quest["What"]
                                )
                            )

                        quest_dict[quest_type][quest_name] = deserialized_quest
                    else:
                        quest_dict[quest_type][quest_name] = quest_data

        return quest_dict
