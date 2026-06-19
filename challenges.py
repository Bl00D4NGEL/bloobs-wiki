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
    with open(filename, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:            
            challenges.append(Challenge(
                category=row['Category'],
                challenge_name=row['Challenge Name'],
                challenge_id=row['Challenge ID'],
                challenge_type=row['Type'],
                skill=row['Skill'],
                level_required=int(row['Level Required']),
                tier=int(row['Tier']),
                requirement_amount=int(row['Requirement Amount']),
                challenge_points=int(row['Challenge Points']),
                repeatable=row['Repeatable'],
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

    def __init__(
        self,
        descriptions: dict[str, str],
        resource_names: dict[str, str],
        resource_image_dict: dict[str, str] = {},
        resource_name_overrides: dict[str, str] = {}
    ) -> None:
        super().__init__()
        self._descriptions = descriptions
        self._resource_names = resource_names
        self._resource_image_dict = resource_image_dict
        self._resource_name_overrides = resource_name_overrides

    def supported_categories(self) -> list[str]:
        return list(self._descriptions.keys())

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
        return ['Trees']

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
        out += f'''
==== {category} ====
{description}
{{| class="mw-collapsible mw-collapsed wikitable"
|-
'''
        out += "! " + "!! ".join([cell + " " for cell in header_cells]) + "\n"
        out += "|-\n"
        for cells in formatter.get_table_row_cells(category, grouped_by_id):
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
    filename = 'challenges.csv'
    
    challenges: list[Challenge] = []
    try:
        challenges = read_challenges_csv(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please make sure the file exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print(f"\nTotal challenges loaded: {len(challenges)}")

    supported_skills = {
        "Woodcutting": WoodcuttingFormatter,
        "Cooking": lambda: ResourceFormatter(
            {
                'Fish': "These challenges are progressed by successfully cooking the fish listed in the challenge.",
                'Meat': "These challenges are progressed by successfully cooking the meat listed in the challenge.",
                'Other': "These challenges are progressed by successfully cooking the food listed in the challenge.",
            },
            {
                'Fish': "Fish",
                'Meat': "Meat",
                'Other': "Food",
            },
            {
                "Chicken": "Chicken (Food)",
            }
        ),
        "Dexterity": DexterityFormatter,
        "Mining": lambda: ResourceFormatter({"Ores": "These challenges are progressed by successfully mining the ore listed in the challenge."}, {"Ores": "Ore"}),
        "Hitpoints": lambda: SimpleFormatter({"Healing": "These challenges are progressed by restoring Health."}),
        "Attack": lambda: SimpleFormatter({"Accuracy": "These challenges are progressed by successfully hitting an enemy with a melee attack."}),
        "Strength": lambda: SimpleFormatter({"Damage": "These challenges are progressed by successfully dealing damage to enemies with a melee attack."}),
        "Defence": lambda: SimpleFormatter({"Mitigation": "These challenges are progressed by successfully recuding damage from enemies."}),
        "Ranged": lambda: SimpleFormatter({"Accuracy": "These challenges are progressed by successfully hitting an enemy with a ranged attack.", "Damage": "These challenges are progressed by successfully dealing damage to enemies with a ranged attack."}),
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
            }
        ),
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
            }
        ),
        "Fishing": lambda: ResourceFormatter({"Fish": "These challenges are progressed by successfully fishing the fish listed in the challenge."}, {"Fish": "Potion"}),
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
            }
        ),
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
            }
        ),
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
            }
        ),
    }

    for [supported_skill, formatter] in supported_skills.items():
        print_challenges_for_skill(challenges, supported_skill, formatter())


if __name__ == "__main__":
    main()