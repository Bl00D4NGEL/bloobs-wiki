from abc import ABC, abstractmethod
import csv
from dataclasses import dataclass
from typing import Optional

@dataclass
class Challenge:
    category: str
    challenge_name: str
    challenge_id: str
    challenge_type: str
    skill: str
    level_required: int
    tier: int
    requirement_amount: int
    challenge_points: int
    repeatable: str

def read_challenges_csv(filename: str) -> list[Challenge]:
    """
    Read a CSV file and parse it into a list of Challenge dataclass objects.
    """
    challenges = []
    
    # Read the file with UTF-8 encoding and handle BOM
    with open(filename, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        
        for row in reader:            
            challenges.append(Challenge(
                category=row["Category"],
                challenge_name=row["Challenge Name"],
                challenge_id=row["Challenge ID"],
                challenge_type=row["Type"],
                skill=row["Skill"],
                level_required=int(row["Level Required"]),
                tier=int(row["Tier"]),
                requirement_amount=int(row["Requirement Amount"]),
                challenge_points=int(row["Challenge Points"]),
                repeatable=row["Repeatable"],
            ))
    
    return challenges

def print_categories(challenges: list[Challenge]) -> None:
    """
    Print all unique categories from the challenges list.
    """
    categories = set(challenge.category for challenge in challenges)
    
    print("All Categories:")
    print("-" * 40)
    for category in sorted(categories):
        print(f"• {category}")
    print(f"\nTotal categories found: {len(categories)}")

def print_skills(challenges: list[Challenge]) -> None:
    """
    Print all unique skills from the challenges list.
    """
    skills = set(challenge.skill for challenge in challenges)
    
    print("All Skills:")
    print("-" * 40)
    for category in sorted(skills):
        print(f"• {category}")
    print(f"\nTotal skills found: {len(skills)}")

def format_image_cell(content: str, image_link: str| None = None, linkable_content: bool = True) -> str:
    if image_link is None:
        image_link = content

    if linkable_content:
        return f"[[File:{image_link.replace(" ", "_")}.png|32x32px]] [[{content}]]"

    return f"[[File:{image_link.replace(" ", "_")}.png|32x32px]] {content}"

class SkillFormatter(ABC):
    """Abstract base class for formatting skill challenges."""
    
    @abstractmethod
    def supported_categories(self) -> list[str]:
        pass

    def format_category(self, category: str) -> str:
        return category

    @abstractmethod
    def get_description(self, category: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        pass
    
    @abstractmethod
    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        pass

class ResourceFormatter(SkillFormatter):
    _descriptions: dict[str, str]
    _resource_names: dict[str, str]
    _resource_image_dict: dict[str, str]
    _resource_name_overrides: dict[str, str]
    _category_name_overrides: dict[str, str]

    def __init__(
        self,
        descriptions: dict[str, str],
        resource_names: dict[str, str],
        resource_image_dict: dict[str, str] = {},
        resource_name_overrides: dict[str, str] = {},
        category_name_overrides: dict[str, str] = {}
    ) -> None:
        super().__init__()
        self._descriptions = descriptions
        self._resource_names = resource_names
        self._resource_image_dict = resource_image_dict
        self._resource_name_overrides = resource_name_overrides
        self._category_name_overrides = category_name_overrides

    def supported_categories(self) -> list[str]:
        return list(self._descriptions.keys())

    def format_category(self, category: str) -> str:
        if category in self._category_name_overrides:
            return self._category_name_overrides[category]
        return super().format_category(category)

    def get_description(self, category: str) -> str | None:
        return self._descriptions[category]

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        return ["Required Level", self._resource_names[category], "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]

    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]

            resource_name = by_id[0].challenge_name
            if resource_name in self._resource_name_overrides:
                resource_name = self._resource_name_overrides[resource_name]

            if resource_name in self._resource_image_dict:
                cells.append(format_image_cell(resource_name, self._resource_image_dict[resource_name]))
            else:
                cells.append(format_image_cell(resource_name))

            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

class SimpleFormatter(SkillFormatter):
    _descriptions: dict[str, str]

    def __init__(self, descriptions: dict[str, str]) -> None:
        super().__init__()
        self._descriptions = descriptions

    def supported_categories(self) -> list[str]:
        return list(self._descriptions.keys())

    def get_description(self, category: str) -> str | None:
        return self._descriptions[category]

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        return ["Required Level", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]

    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]
            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

class WoodcuttingFormatter(SkillFormatter):
    def supported_categories(self) -> list[str]:
        return ["Trees"]

    def get_description(self, category: str) -> str | None:
        return "These challenges are progressed by successfully chopping the log from the tree listed in the challenge."

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        return ["Required Level", "Tree", "Log", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]

    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        # key = log name, value = tree name
        log_to_tree_dict = {
            "Logs": "Regular Tree",
            "Imbued Fibers": "Imbued Tree",
            "Oak Logs": "Oak Tree",
            "Willow Logs": "Willow Tree",
            "Teak Logs": "Teak Tree",
            "Maple Logs": "Maple Tree",
            "Acadia Logs": "Acadia Tree",
            "Eucalyptus Logs": "Eucalyptus Tree",
            "Rubra Logs": "Rubra Tree",
            "Yew Logs": "Yew Tree",
            "Red Maple Logs": "Red Maple Tree",
            "Magic Logs": "Magic Tree",
            "Lunarwood Logs": "Lunarwood Tree",
            "Aether Core": "Aether Tree",
            "Spicebough Logs": "Spicebough Tree",
            "Bitterpine Logs": "Bitterpine Tree",
            "Flourishing Aether Core": "Flourishing Aether Tree",
            "Dune Logs": "Dune Thicket Tree",
            "Suncoil Logs": "Suncoil Tree",
        }

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]
            log_name = by_id[0].challenge_name
            if log_name in log_to_tree_dict:
                cells.append(format_image_cell(log_to_tree_dict[log_name], None, False))
            else:
                cells.append("???")

            cells.append(format_image_cell(log_name))

            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

class HomesteadingFormatter(SkillFormatter):
    def supported_categories(self) -> list[str]:
        return ["Crops", "Fishing", "Foraging", "Mining", "Woodcutting"]

    def get_description(self, category: str) -> str | None:
        descriptions = {
            "Crops": "These challenges are progressed by successfully growing the crop listed in the challenge.",
            "Fishing": "These challenges are progressed by successfully growing the fish listed in the challenge.",
            "Foraging": "These challenges are progressed by successfully growing the item listed in the challenge.",
            "Mining": "These challenges are progressed by successfully growing the ore listed in the challenge.",
            "Woodcutting": "These challenges are progressed by successfully growing the tree listed in the challenge.",
        }

        if category in descriptions:
            return descriptions[category]
        
        return None

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        resource_names = {
                "Crops": "Crop",
                "Fishing": "Fish",
                "Foraging": "Item",
                "Mining": "Ore",
                "Woodcutting": "Tree",
        }
        if category in resource_names:
            return ["Required Level", resource_names[category], "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]

        return []

    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        challenge_name_overrides = {
            "Bloobberry": "Bloobberries",
            "Red Bloobberry": "Red Bloobberries",
            "Orange Bloobberry": "Orange Bloobberries",
            "Yellow Bloobberry": "Yellow Bloobberries",
            "White Bloobberry": "White Bloobberries",
            "Purple Bloobberry": "Purple Bloobberries",
            "Grey Bloobberry": "Grey Bloobberries",
            "Teal Bloobberry": "Teal Bloobberries",
            "Frosted Bloobberry": "Frosted Bloobberries",
        }

        image_overrides = {
            "Imbued Crystal": "Imbued Shards",
            "Common Gem Rock": "Common Gem Rock Node",
            "Uncommon Gem Rock": "Uncommon Gem Rock Node",
            "Rare Gem Rock": "Rare Gem Rock Node",
        }

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]
            challenge_name = by_id[0].challenge_name
            if challenge_name in challenge_name_overrides:
                challenge_name = challenge_name_overrides[challenge_name]

            match category:
                case "Crops" | "Fishing" | "Foraging":
                    cells.append(format_image_cell(challenge_name))
                case "Mining" | "Woodcutting":
                    if challenge_name in image_overrides:
                        cells.append(format_image_cell(challenge_name, image_overrides[challenge_name], False))
                    else:
                        cells.append(format_image_cell(challenge_name, None, False))

            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

class DexterityFormatter(SkillFormatter):
    def supported_categories(self) -> list[str]:
        return ["Bloobathon", "Movement"]

    def get_description(self, category: str) -> str | None:
        match category:
            case "Bloobathon":
                return "These challenges are progressed by completing bloobathons."
            case "Movement":
                return "These challenges are progressed by travelling in the world for the shown distance."
            case _:
                return None

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        match category:
            case "Bloobathon":
                return ["Required Level", "Bloobathon", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]
            case "Movement":
                return ["Required Level", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]
            case _:
                return []

    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        match category:
            case "Bloobathon":
                return self.get_bloobathon_row_cells(challenges_by_id)
            case "Movement":
                return self.get_movement_row_cells(challenges_by_id)
            case _:
                return []

    def get_bloobathon_row_cells(self, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]
            challenge_name = by_id[0].challenge_name

            # override because of inconsistent challenge data
            if challenge_name == "Frostspire Bloobathon":
                challenge_name = "Frostspire Cavern Bloobathon"

            cells.append(format_image_cell(challenge_name))

            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

    def get_movement_row_cells(self, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        rows = []

        for by_id in challenges_by_id.values():
            cells = [f"Level {by_id[0].level_required}"]
            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

def print_challenges_for_skill(challenges: list[Challenge], skill: str, formatter: SkillFormatter) -> None:
    filtered = [challenge for challenge in challenges if challenge.skill == skill]

    out = f"=== {skill} ===\n"
    grouped_by_category: dict[str, list[Challenge]] = {}
    for x in filtered:
        if x.category not in grouped_by_category:
            grouped_by_category[x.category] = []
        grouped_by_category[x.category].append(x)

    for category in formatter.supported_categories():
        if category not in grouped_by_category:
            print(f"WARN: supported category {category} not in grouped challenges for skill {skill}")
            continue
        challenges = grouped_by_category[category]
        grouped_by_id: dict[str, list[Challenge]] = {}
        for x in challenges:
            if x.challenge_id not in grouped_by_id:
                grouped_by_id[x.challenge_id] = []
            grouped_by_id[x.challenge_id].append(x)

        description = formatter.get_description(category)
        header_cells = formatter.get_header_cells(category, grouped_by_id)
        out += f"""
==== {formatter.format_category(category)} ====
{description}
{{| class="mw-collapsible mw-collapsed wikitable"
|-
"""
        out += "! " + "!! ".join([cell + " " for cell in header_cells]) + "\n"
        out += "|-\n"
        for cells in formatter.get_table_row_cells(category, grouped_by_id):
            out += "| " + "|| ".join([cell + " " for cell in cells]) + "\n"
            out += "|-\n"
        out += "|}\n"
    print(out)

def print_experience_challenges(challenges: list[Challenge]) -> None:
    filtered = [challenge for challenge in challenges if challenge.challenge_type == "Experience"]

    out = f"=== Experience ===\n"
    header_cells = ["Skill", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]
    out += f"""
==== Skills ====
These challenges are progressed by gaining experience with the skill listed in the challenge.
{{| class="mw-collapsible mw-collapsed wikitable"
|-
"""
    out += "! " + "!! ".join([cell + " " for cell in header_cells]) + "\n"
    out += "|-\n"

    grouped_by_id: dict[str, list[Challenge]] = {}
    for x in filtered:
        if x.challenge_id not in grouped_by_id:
            grouped_by_id[x.challenge_id] = []
        grouped_by_id[x.challenge_id].append(x)

    skill_overrides = {
        "BowCrafting": "Bowcrafting",
        "Ranged": "Range",
        "SoulBinding": "Soulbinding",
    }

    rows = []
    for by_id in grouped_by_id.values():
        skill_name = by_id[0].skill
        if skill_name in skill_overrides:
            skill_name = skill_overrides[skill_name]

        if skill_name == "Total":
            cells = [skill_name] # no image for "Total" as there's none available on the wiki
        else:
            cells = [format_image_cell(skill_name)]

        for challenge in by_id:
            cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

        if by_id[0].repeatable:
            cells.append("Yes")
        else:
            cells.append("No")

        rows.append(cells)

    for cells in rows:
        out += "| " + "|| ".join([cell + " " for cell in cells]) + "\n"
        out += "|-\n"
    out += "|}\n"
    print(out)

def print_challenge(challenge: Challenge) -> None:
    print(f"Category: {challenge.category}")
    print(f"Challenge Name: {challenge.challenge_name}")
    print(f"Challenge ID: {challenge.challenge_id}")
    print(f"Type: {challenge.challenge_type}")
    print(f"Skill: {challenge.skill}")
    print(f"Level Required: {challenge.level_required}")
    print(f"Tier: {challenge.tier}")
    print(f"Requirement Amount: {challenge.requirement_amount}")
    print(f"Challenge Points: {challenge.challenge_points}")
    print(f"Repeatable: {challenge.repeatable}")

def main():
    filename = "challenges.csv"
    
    challenges: list[Challenge] = []
    try:
        challenges = read_challenges_csv(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please make sure the file exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print(f"\nTotal challenges loaded: {len(challenges)}")

    supported_skills = {
        "Hitpoints": lambda: SimpleFormatter({"Healing": "These challenges are progressed by restoring Health."}),
        "Dexterity": DexterityFormatter,
        "Mining": lambda: ResourceFormatter({"Ores": "These challenges are progressed by successfully mining the ore listed in the challenge."}, {"Ores": "Ore"}),
        "Attack": lambda: SimpleFormatter({"Accuracy": "These challenges are progressed by successfully hitting an enemy with a melee attack."}),
        "Foraging": lambda: ResourceFormatter({"Forage": "These challenges are progressed by successfully foraging the resource listed in the challenge."}, {"Forage": "Resource"}),
        "Smithing": lambda: ResourceFormatter(
            {
                "Bars": "These challenges are progressed by successfully smelting the bar listed in the challenge.",
                "Tools": "These challenges are progressed by successfully smelting the bar listed in the challenge.",
                "Weapons": "These challenges are progressed by successfully smelting the bar listed in the challenge.",
                "Armour": "These challenges are progressed by successfully smelting the bar listed in the challenge.",
                "Other": "These challenges are progressed by successfully smelting the bar listed in the challenge.",
            },
            {
                "Bars": "Bar",
                "Tools": "Tool",
                "Weapons": "Weapon",
                "Armour": "Armour",
                "Other": "Other",
            },
        ),
        "Strength": lambda: SimpleFormatter({"Damage": "These challenges are progressed by successfully dealing damage to enemies with a melee attack."}),
        "Herbology": lambda: ResourceFormatter(
            {
                "Unfinished": "These challenges are progressed by successfully creating the unfinished potion listed in the challenge.",
                "Potions": "These challenges are progressed by successfully creating the potion listed in the challenge.",
            },
            {
                "Unfinished": "Potion",
                "Potions": "Potion",
            },
            resource_name_overrides={
                "Vial Of Water": "Vial of Water",
                "Flask Of Water": "Flask of Water",
                "Bottle Of Water": "Bottle of Water",
                "Decanter Of Water": "Decanter of Water",
            },
        ),
        "Fishing": lambda: ResourceFormatter({"Fish": "These challenges are progressed by successfully fishing the fish listed in the challenge."}, {"Fish": "Potion"}),
        "Defence": lambda: SimpleFormatter({"Mitigation": "These challenges are progressed by successfully recuding damage from enemies."}),
        "Crafting": lambda: ResourceFormatter(
            {
                "Workbench": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Glass": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Pottery": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Jewellery": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Capes": "These challenges are progressed by successfully crafting the cape listed in the challenge.",
                "Magic Gear": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Range Gear": "These challenges are progressed by successfully crafting the item listed in the challenge.",
                "Other": "These challenges are progressed by successfully crafting the item listed in the challenge.",
            },
            {
                "Workbench": "Item",
                "Glass": "Glass",
                "Pottery": "Item",
                "Jewellery": "Item",
                "Capes": "Cape",
                "Magic Gear": "Item",
                "Range Gear": "Item",
                "Other": "Item",
            },
            resource_name_overrides={
                "Cape Of Windmark": "Cape of Windmark",
                "Cape Of Mistborn": "Cape of Mistborn",
                "Cape Of Ironfang": "Cape of Ironfang",
            },
        ),
        "Cooking": lambda: ResourceFormatter(
            {
                "Fish": "These challenges are progressed by successfully cooking the fish listed in the challenge.",
                "Meat": "These challenges are progressed by successfully cooking the meat listed in the challenge.",
                "Other": "These challenges are progressed by successfully cooking the food listed in the challenge.",
            },
            {
                "Fish": "Fish",
                "Meat": "Meat",
                "Other": "Food",
            },
            {
                "Chicken": "Chicken (Food)",
            },
        ),
        "Ranged": lambda: SimpleFormatter({"Accuracy": "These challenges are progressed by successfully hitting an enemy with a ranged attack.", "Damage": "These challenges are progressed by successfully dealing damage to enemies with a ranged attack."}),
        "BowCrafting": lambda: ResourceFormatter(
            {
                "Arrows": "These challenges are progressed by successfully crafting the arrows listed in the challenge.",
                "Bows": "These challenges are progressed by successfully crafting the bows listed in the challenge.",
                "Shafts": "These challenges are progressed by successfully crafting the shafts listed in the challenge.",
            },
            {
                "Arrows": "Arrow",
                "Bows": "Bow",
                "Shafts": "Shaft",
            },
        ),
        "Woodcutting": WoodcuttingFormatter,
        "Magic": lambda: SimpleFormatter({"Accuracy": "These challenges are progressed by successfully hitting an enemy with a magic attack.", "Damage": "These challenges are progressed by successfully dealing damage to enemies with a magic attack.", "Teleports": "These challenges are progressed by teleporting to the location listed in the challenge."}),
        "Imbuing": lambda: ResourceFormatter(
            {
                "Imbued Slate": "These challenges are progressed by successfully crafting the imbued slate listed in the challenge.",
                "Slates": "These challenges are progressed by successfully crafting the slate listed in the challenge.",
                "Staffs": "These challenges are progressed by successfully crafting the staff listed in the challenge.",
            },
            {
                "Imbued Slate": "Slate",
                "Slates": "Slate",
                "Staffs": "Staff",
            },
            resource_name_overrides={
                "Random Tier 0 Slate": "Imbued Omni Slate",
            },
        ),
        "Firemaking": lambda: ResourceFormatter(
            {
                "Cores": "These challenges are progressed by successfully crafting the core listed in the challenge.",
                "Logs": "These challenges are progressed by successfully burning the log listed in the challenge.",
            },
            {
                "Cores": "Core",
                "Logs": "Log",
            },
        ),
        "Devotion": lambda: ResourceFormatter(
            {
                "Bones": "These challenges are progressed by successfully burying the item listed in the challenge.",
                "Sacrifice": "These challenges are progressed by successfully sacrificing the item listed in the challenge.",
            },
            {
                "Bones": "Item",
                "Sacrifice": "Item",
            },
            resource_name_overrides={
                "Pile Of Bones": "Pile of Bones",
                "Scorched Pile Of Bones": "Scorched Pile of Bones",
            },
        ),
        "Thieving": lambda: ResourceFormatter(
            {
                "Stall": "These challenges are progressed by successfully thieving from the stall listed in the challenge.",
                "Pickpocket": "These challenges are progressed by successfully pickpocketing the NPC listed in the challenge.",
                "Chests": "These challenges are progressed by successfully opening the chest listed in the challenge.",
            },
            {
                "Stall": "Stall",
                "Pickpocket": "NPC",
                "Chests": "Chest",
            },
            resource_name_overrides={
                "LumberStall": "Lumber Stall",
                "Jeweled Tomb Chest": "Jeweled Tomb",
            },
        ),
        "Tracking": lambda: ResourceFormatter(
            {
                "Tracking": "These challenges are progressed by successfully tracking the creature listed in the challenge.",
            },
            {
                "Tracking": "Stall",
            },
            resource_name_overrides={
                "ElderGlow Spider": "Elderglow Spider",
            },
        ),
        "Beastmastery": lambda: ResourceFormatter(
            {
                "Enemy": "These challenges are progressed by successfully killing the enemy listed in the challenge.",
                "Enemy_Superior": "These challenges are progressed by successfully killing the enemy listed in the challenge.",
                "Enemy_Golden": "These challenges are progressed by successfully killing the enemy listed in the challenge.",
                "Enemy_Corrupted": "These challenges are progressed by successfully killing the enemy listed in the challenge.",
                "Boss": "These challenges are progressed by successfully killing the boss listed in the challenge.",
                "Boss_Superior": "These challenges are progressed by successfully killing the boss listed in the challenge.",
                "Boss_Golden": "These challenges are progressed by successfully killing the boss listed in the challenge.",
                "Boss_Corrupted": "These challenges are progressed by successfully killing the boss listed in the challenge.",
            },
            {
                "Enemy": "Enemy",
                "Enemy_Superior": "Enemy",
                "Enemy_Golden": "Enemy",
                "Enemy_Corrupted": "Enemy",
                "Boss": "Boss",
                "Boss_Superior": "Boss",
                "Boss_Golden": "Boss",
                "Boss_Corrupted": "Boss",
            },
            {
                "Banana Skirmisher": "Banana Skirmisher Soul",
                "Graveheart The Revenant Overlord": "Graveheart"
            },
            resource_name_overrides={
                "Chickens": "Chicken (Monster)",
                "Cows": "Cow",
                "Crabs": "Crab",
                "Goblins": "Goblin",
                "Bats": "Bat",
                "Goats": "Goat",
                "Hobgoblins": "Hobgoblin",
                "Pigs": "Pig",
                "Sheeps": "Sheep",
                "Wolves": "Wolf",
                "Goblin Wolf Riders": "Goblin Wolf Rider",
                "Hobgoblin Brawlers": "Hobgoblin Brawler",
                "Boars": "Boar",
                "Gnolls": "Gnoll",
                "Skittering Hands": "Skittering Hand",
                "Toxic Hounds": "Toxic Hound",
                "Dismembered Crawlers": "Dismembered Crawler",
                "Skeletons": "Skeleton",
                "Black Wolves": "Black Wolf",
                "Carcass Feeders": "Carcass Feeder",
                "Zombies": "Zombie",
                "Dark Crabs": "Dark Crab",
                "Aqua Drakes": "Aqua Drake",
                "Revenants": "Revenant",
                "Skeletal Archers": "Skeletal Archer",
                "Bound Cadavers": "Bound Cadaver",
                "Unraveling Crawlers": "Unraveling Crawler",
                "Ancient Fighters": "Ancient Fighter",
                "Bone Golems": "Bone Golem",
                "Bony Soldiers": "Bony Soldier",
                "Juvenile Entropic Dragons": "Juvenile Entropic Dragon",
                "Toxic Wolves": "Toxic Wolf",
                "Ghastly Eyes": "Ghastly Eye",
                "Twinfang the Blight Bringer": "Twinfang The Blight Bringer",
                "Graveheart": "Graveheart The Revenant Overlord",
            },
            category_name_overrides={
                "Enemy_Superior": "Enemy (Superior)",
                "Enemy_Golden": "Enemy (Golden)",
                "Enemy_Corrupted": "Enemy (Corrupted)",
                "Boss_Superior": "Boss (Superior)",
                "Boss_Golden": "Boss (Golden)",
                "Boss_Corrupted": "Boss (Corrupted)",
            },
        ),
        "SoulBinding": lambda: SimpleFormatter({"Auto Bank": "These challenges are progressed by automatically banking the amount of items listed in the challenge.", "Auto Sell": "These challenges are progressed by automatically selling items worth the amount of items listed in the challenge."}),
        "Homesteading": HomesteadingFormatter,
    }

    for [supported_skill, formatter] in supported_skills.items():
        print_challenges_for_skill(challenges, supported_skill, formatter())
    print_experience_challenges(challenges)

if __name__ == "__main__":
    main()