from copy import deepcopy
from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World
from .Options import NplusplusOptions, nplusplus_option_groups
from .Items import generate_item_data_table, generate_item_groups
from .Locations import generate_location_groups, generate_location_table
from .data.LocationNames import locations, episode_names
from .data.LevelData import intro_levels
from .Levels import Level, Episode

# TODO: This id will need to be changed to not overlap with other games
nplusplus_base_id = 0xBAC0000

# TODO: Actually put effort into webhost
class NplusplusOpenWebWorld(WebWorld):
    theme = "stone"

    setup_en = Tutorial(
        tutorial_name="Start Guide",
        description="A guide to playing N++ in Archipelago.",
        language="English",
        file_name="guide_en.md",
        link="guide/en",
        authors=["JRoeseph", "XandoToaster"]
    )

    tutorials = [setup_en]

    option_groups = nplusplus_option_groups

class NplusplusOpenWorld(World):
    """
    N++ is the 2nd, 3rd, 4th, 5th, or 6th game in the N franchise depending on who you ask. Created by Metanet Software, the N franchise started as a flash game, saw multiple console releases in N+, and the franchise recieved it's penultimate game in N++. The goal of each level is simple, reach the door switch then reach the door before time expires, collecting gold along the way to extend your time.
    """

    # Class Data
    game = "N++"
    web = NplusplusOpenWebWorld()
    options_dataclass = NplusplusOptions
    options: NplusplusOptions

    base_id = 0xBAC0000

    apworld_version = 1

    location_name_to_id: dict[str, int] = generate_location_table()
    location_name_groups: dict[str, list[str]] = generate_location_groups()
    item_name_to_id: dict[str, int] = generate_item_data_table()
    item_name_groups: dict[str, list[str]] = generate_item_groups()

    location_to_level: dict[str, Level] = {}
    episodes: list[Episode] = []

    def generate_location_to_level(self) -> None:
        remaining_levels: list[Level] = deepcopy(intro_levels)
        for location in locations:
            random_level_idx: int = self.random.randint(0, len(remaining_levels)-1)
            self.location_to_level[location] = remaining_levels.pop(random_level_idx)

    def group_episodes (self) -> None:
        for episode_name in episode_names:
            self.episodes.append(Episode(episode_name, self.location_to_level[episode_name+"-00"], self.location_to_level[episode_name+"-01"], self.location_to_level[episode_name+"-02"], self.location_to_level[episode_name+"-03"], self.location_to_level[episode_name+"-04"]))

    def generate_early(self) -> None:
        self.generate_location_to_level()
        self.group_episodes()