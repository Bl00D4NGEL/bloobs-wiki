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

class SkillFormatter(ABC):
    """Abstract base class for formatting skill challenges."""
    
    @abstractmethod
    def supports_category(self, category: str) -> bool:
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

class WoodcuttingFormatter(SkillFormatter):
    def supports_category(self, category: str) -> bool:
        return category == 'Trees'

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
                cells.append(f"[[File:{log_to_tree_dict[log_name].replace(" ", "_")}.png|32x32px]] {log_to_tree_dict[log_name]}")
            else:
                cells.append("???")

            cells.append(f"[[File:{log_name.replace(" ", "_")}.png|32x32px]] [[{log_name}]]")

            for challenge in by_id:
                cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

            if by_id[0].repeatable:
                cells.append("Yes")
            else:
                cells.append("No")

            rows.append(cells)

        return rows

class CookingFormatter(SkillFormatter):
    def supports_category(self, category: str) -> bool:
        return category in ['Fish', 'Meat', 'Other']

    def get_description(self, category: str) -> str | None:
        food_name_dict = {
            'Fish': "fish",
            'Meat': "meat",
            'Other': "food",
        }
        if category in food_name_dict:
            return f"These challenges are progressed by successfully cooking the {food_name_dict[category]} listed in the challenge."
        
        return None

    def get_header_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[str]:
        food_name_dict = {
            'Fish': "Fish",
            'Meat': "Meat",
            'Other': "Food",
        }
        
        if category in food_name_dict:
            return ["Required Level", food_name_dict[category], "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7", "Tier 8", "Tier 9", "Tier 10", "Repeatable"]
        
        return []
    
    def get_table_row_cells(self, category: str, challenges_by_id: dict[str, list[Challenge]]) -> list[list[str]]:
        match category:
            case 'Fish':
                handler = self.get_row_cells
            case 'Meat':
                handler = lambda challenges: self.get_row_cells(challenges, {
                    "Chicken": "Chicken (Food)",
                })
            case 'Other':
                handler = self.get_row_cells
            case _:
                return []

        rows = []
        for challenges in challenges_by_id.values():
            rows.append(handler(challenges))
                
        return rows
    
    def get_row_cells(self, challenges: list[Challenge], image_dict: Optional[dict[str, str]] = None) -> list[str]:
        cells = [f"Level {challenges[0].level_required}"]
        food_name = challenges[0].challenge_name
        if image_dict is not None and food_name in image_dict:
            cells.append(f"[[File:{image_dict[food_name].replace(" ", "_")}.png|32x32px]] [[{food_name}]]")
        else:
            cells.append(f"[[File:{food_name.replace(" ", "_")}.png|32x32px]] [[{food_name}]]")

        for challenge in challenges:
            cells.append(f"{challenge.requirement_amount} ({challenge.challenge_points})")

        if challenges[0].repeatable:
            cells.append("Yes")
        else:
            cells.append("No")
        return cells

def print_challenges_for_skill(challenges: list[Challenge], skill: str, formatter: SkillFormatter) -> None:
    filtered = [challenge for challenge in challenges if challenge.skill == skill]

    out = f"=== {skill} ===\n"
    grouped_by_category: dict[str, list[Challenge]] = {}
    for x in filtered:
        if x.category not in grouped_by_category:
            grouped_by_category[x.category] = []
        grouped_by_category[x.category].append(x)

    for by_category in grouped_by_category.values():
        category = by_category[0].category
        if formatter.supports_category(category) is False:
            continue

        grouped_by_id: dict[str, list[Challenge]] = {}
        for x in by_category:
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
        "Cooking": CookingFormatter,
    }

    for [supported_skill, formatter] in supported_skills.items():
        print_challenges_for_skill(challenges, supported_skill, formatter())


if __name__ == "__main__":
    main()