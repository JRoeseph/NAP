from copy import deepcopy
from math import ceil
from BaseClasses import Tutorial, ItemClassification
from worlds.AutoWorld import WebWorld, World
from .Options import NplusplusOptions, nplusplus_option_groups
from .Items import NplusplusItem, NplusplusItemData, generate_item_data_table, generate_item_groups, level_unlock_item_data_table
from .Locations import generate_location_groups, generate_location_table
from data import ItemNames
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

    def create_item(self, name: str, item_data_table: dict[str, NplusplusItemData], is_filler: bool) -> NplusplusItem:
        return NplusplusItem(name, ItemClassification.progression if not is_filler else ItemClassification.filler, item_data_table[name].code, self.player)

    def create_items(self) -> None:
        item_pool: list[NplusplusItem] = []

        # This is currently hardcoded but will change when challenges are added
        locations: int = 250 - 150
        needed_time: float = 0
        episode: Episode
        for episode in self.episodes:
            min_time: float = episode.minimum_no_gold_time()
            if min_time > needed_time:
                needed_time = min_time
        options: NplusplusOptions = self.options
        starting_time_items: list[int] = [ceil(needed_time * options.MaximumStartingTimeMultiplier/100) - options.InitialStartingTime, 0, 0, 0]
        max_time_items: list[int] = [ceil(needed_time * options.MaximumTimeCapMultiplier/100) - options.InitialTimeCap, 0, 0, 0]
        gold_time_items: list[int] = [options.MaximumGoldValue, 0, 0, 0]
        list_of_lists: list[list[int]] = [starting_time_items, max_time_items, gold_time_items]
        while locations > sum(starting_time_items, max_time_items, gold_time_items):
            if len(list_of_lists) == 3:
                idx: int = self.random.randint(0, 2)
                merging_list: list[int] = list_of_lists[idx]
                if not self.merge_up_item(merging_list):
                    list_of_lists.pop(idx)
            elif len(list_of_lists) == 2:
                idx: int = self.random.randint(0, 1)
                merging_list: list[int] = list_of_lists[idx]
                if not self.merge_up_item(merging_list):
                    list_of_lists.pop(idx)
            elif len(list_of_lists) == 1:
                if not self.merge_up_item(list_of_lists[0]):
                    list_of_lists.pop(0)
            else:
                raise Exception("Unable to merge items to be under location count in Nplusplus")
        # This will always equal zero unless the inital item list was low
        filler_items: int = locations - sum(starting_time_items, max_time_items, gold_time_items)
        item_data_table = generate_item_data_table()
        item_pool += [self.create_item(item_name, item_data_table, False) for item_name in level_unlock_item_data_table.keys()]
        item_pool += [self.create_item(ItemNames.start_time_1, item_data_table, False) for _ in range(starting_time_items[0])]
        item_pool += [self.create_item(ItemNames.start_time_2, item_data_table, False) for _ in range(starting_time_items[1])]
        item_pool += [self.create_item(ItemNames.start_time_5, item_data_table, False) for _ in range(starting_time_items[2])]
        item_pool += [self.create_item(ItemNames.start_time_10, item_data_table, False) for _ in range(starting_time_items[3])]
        item_pool += [self.create_item(ItemNames.max_time_1, item_data_table, False) for _ in range(max_time_items[0])]
        item_pool += [self.create_item(ItemNames.max_time_2, item_data_table, False) for _ in range(max_time_items[1])]
        item_pool += [self.create_item(ItemNames.max_time_5, item_data_table, False) for _ in range(max_time_items[2])]
        item_pool += [self.create_item(ItemNames.max_time_10, item_data_table, False) for _ in range(max_time_items[3])]
        item_pool += [self.create_item(ItemNames.gold_time_1, item_data_table, False) for _ in range(gold_time_items[0])]
        item_pool += [self.create_item(ItemNames.gold_time_2, item_data_table, False) for _ in range(gold_time_items[1])]
        item_pool += [self.create_item(ItemNames.gold_time_5, item_data_table, False) for _ in range(gold_time_items[2])]
        item_pool += [self.create_item(ItemNames.gold_time_10, item_data_table, False) for _ in range(gold_time_items[3])]
        item_pool += [self.create_item(ItemNames.palette_swap, item_data_table, True) for _ in range(filler_items)]
    
        self.multiworld.itempool += item_pool
        
    def merge_up_item(self, items: list[int]) -> bool:
        if list[0] > 1:
            list[0] -= 2
            list[1] += 1
            return True
        elif list[1] > 1 and list[0] == 1:
            list[0] -= 1
            list[1] -= 2
            list[3] += 1
            return True
        elif list[1] > 2:
            list[1] -= 3
            list[0] += 1
            list[2] += 1
            return True
        elif list[2] > 1:
            list[2] -= 2
            list[3] += 1
            return True
        return False