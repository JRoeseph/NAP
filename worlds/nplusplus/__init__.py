from copy import deepcopy
from math import ceil
from typing import Any
from BaseClasses import Location, Tutorial, ItemClassification, CollectionState, Region
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule
from .Options import NplusplusOptions, nplusplus_option_groups
from .Items import NplusplusItem, NplusplusItemData, generate_item_data_table, generate_item_table, generate_item_groups, level_unlock_item_data_table
from .Locations import NplusplusLocation, generate_location_groups, location_table, generate_location_data_table
from .data import ItemNames
from .data.LocationNames import locations, episode_names, level_completions, episode_completions, challenge_completions
from .data.LevelData import intro_levels
from .Levels import Level, Episode, Challenge

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

    location_name_to_id: dict[str, int] = location_table
    location_name_groups: dict[str, list[str]] = generate_location_groups()
    item_name_to_id: dict[str, int] = generate_item_table()
    item_name_groups: dict[str, list[str]] = generate_item_groups()
    origin_region_name = "Intro Tab"

    location_to_level: dict[str, Level] = {}
    episodes: list[Episode] = []
    included_challenges: dict[str, list[Challenge]] = {}
    challenge_locs: list[str] = []

    def generate_location_to_level(self) -> None:
        # Get all possible levels
        remaining_levels: list[Level] = deepcopy(intro_levels)

        # Manually pick out one under the InitialStartingTime to be the starting level, and 4 random levels to be the other 4 in the first episode
        options: NplusplusOptions = self.options
        possible_starting_levels: list[Level] = list(filter(lambda level: level.times[Challenge.base] < options.InitialStartingTime, remaining_levels))
        starting_level: Level = possible_starting_levels[self.random.randint(0, len(possible_starting_levels)-1)]
        remaining_levels.remove(starting_level)
        episode_a0_levels: list[Level] = [starting_level]
        for _ in range(4):
            episode_a0_levels.append(remaining_levels.pop(self.random.randint(0,len(remaining_levels)-1)))
        episode_a0_levels.sort(key=lambda level: level.times[Challenge.base])
        for idx in range(5):
            self.location_to_level[f"A-00-0{idx}"] = episode_a0_levels[idx]
        for episode_name in episode_names:
            if episode_name != "A-00":
                episode_levels: list[Level] = []
                for _ in range(5):
                    episode_levels.append(remaining_levels.pop(self.random.randint(0,len(remaining_levels)-1)))
                episode_levels.sort(key=lambda level: level.times[Challenge.base])
                for idx in range(5):
                    self.location_to_level[f"{episode_name}-0{idx}"] = episode_levels[idx]
                self.episodes.append(Episode(episode_name, episode_levels[0], episode_levels[1], episode_levels[2], episode_levels[3], episode_levels[4]))

    def pick_challenges(self) -> None:
        challenge_list: list[tuple[str, Challenge]] = []
        for location, level in self.location_to_level.items():
            for challenge in level.times.keys():
                if challenge != Challenge.base:
                    challenge_list.append((location, challenge))
        options: NplusplusOptions = self.options
        for _ in range(options.AdditionalChallenges):
            if not challenge_list:
                return
            while True:
                idx: int = self.random.randint(0,len(challenge_list)-1)
                rand_challenge_loc: str
                rand_challenge: Challenge
                (rand_challenge_loc, rand_challenge) = challenge_list[idx]
                if rand_challenge_loc in self.included_challenges and len(self.included_challenges[rand_challenge_loc]) >= 3:
                    challenge_list.pop(idx)
                    if not challenge_list:
                        return
                else:
                    if rand_challenge_loc not in self.included_challenges:
                        self.included_challenges[rand_challenge_loc] = []
                    self.included_challenges[rand_challenge_loc].append(rand_challenge)
                    self.challenge_locs.append(rand_challenge_loc + f" Challenge {len(self.included_challenges[rand_challenge_loc])} Completion")
                    challenge_list.pop(idx)
                    break


    def generate_early(self) -> None:
        self.generate_location_to_level()
        self.pick_challenges()

    def create_regions(self) -> None:
        intro_tab: Region = Region("Intro Tab", self.player, self.multiworld)
        for loc_name, loc_data in generate_location_data_table().items():
            if loc_name in level_completions or loc_name in episode_completions or loc_name in self.challenge_locs:
                intro_tab.locations.append(NplusplusLocation(self.player, loc_name, loc_data.address, intro_tab))
        self.multiworld.regions += [intro_tab]

    def create_item(self, name: str, item_data_table: dict[str, NplusplusItemData], is_filler: bool) -> NplusplusItem:
        return NplusplusItem(name, ItemClassification.progression if not is_filler else ItemClassification.filler, item_data_table[name].code, self.player)

    def create_items(self) -> None:
        item_pool: list[NplusplusItem] = []

        # Plus 1 here because there is a 1-to-1 mapping of level locations and level unlocks EXCEPT the starting level
        locations: int = len(self.challenge_locs) + 1
        needed_time: float = 0
        episode: Episode
        for episode in self.episodes:
            min_time: float = episode.minimum_no_gold_time()
            if min_time > needed_time:
                needed_time = min_time
        options: NplusplusOptions = self.options
        starting_time_items: list[int] = [ceil(needed_time * options.MaximumStartingTimeMultiplier/100) - options.InitialStartingTime, 0, 0, 0]
        max_time_items: list[int] = [ceil(needed_time * options.MaximumTimeCapMultiplier/100) - options.InitialTimeCap, 0, 0, 0]
        gold_time_items: list[int] = [options.MaximumGoldValue - options.InitialGoldValue, 0, 0, 0]
        list_of_lists: list[list[int]] = [starting_time_items, max_time_items, gold_time_items]
        # TODO: THIS SECTION MAY NEED TO BE OVERHAULED TO WEIGH EACH LIST
        while locations < (sum(starting_time_items) + sum(max_time_items) + sum(gold_time_items)):
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
        filler_items: int = locations - (sum(starting_time_items) + sum(max_time_items) + sum(gold_time_items))
        item_data_table = generate_item_data_table()
        for item_name in level_unlock_item_data_table.keys():
            if item_name == ItemNames.prog_a00:
                item_pool += [self.create_item(item_name, item_data_table, False) for _ in range(5)]
            else:
                item_pool += [self.create_item(item_name, item_data_table, False) for _ in range(6)]
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
        if items[0] > 1:
            items[0] -= 2
            items[1] += 1
            return True
        elif items[1] > 1 and items[0] == 1:
            items[0] -= 1
            items[1] -= 2
            items[2] += 1
            return True
        elif items[1] > 2:
            items[1] -= 3
            items[0] += 1
            items[2] += 1
            return True
        elif items[2] > 1:
            items[2] -= 2
            items[3] += 1
            return True
        return False

    def set_rules(self) -> None:
        location: Location
        for location in self.multiworld.get_locations(self.player):
            if location.name in self.challenge_locs:
                if location.name[5:].endswith("Completion"):
                    episode_name = location.name[:4]
                    episode_loc: Episode
                    for episode in self.episodes:
                        if episode.name == episode_name:
                            episode_loc = episode
                            break
                    set_rule(location, lambda state: self.episode_accessible(state, self.player, episode_name, episode_loc))
                else:
                    level_name = location.name[:7]
                    level_loc: Level = self.location_to_level[level_name]
                    if len(level_name) == 18:
                        set_rule(location, lambda state: self.level_accessible(state, self.player, level_name, level_loc, Challenge.base))
                    else:
                        challenge_num = level_name[18]
                        challenge: Challenge = self.included_challenges[level_loc][challenge_num]
                        set_rule(location, lambda state: self.level_accessible(state, self.player, level_name, level_loc, challenge))

    
    def level_accessible(self, state: CollectionState, player: int, level_name: str, level: Level, challenge: Challenge) -> bool:
        episode_name: str = level_name[:4]
        level_idx: int = int(level_name[5:])
        if episode_name == "A-00":
            if state.count("A-00 Progressive Level Unlock", player) < level_idx:
                return False
        else:
            if state.count(episode_name + " Progressive Level Unlock", player) < level_idx + 1:
                return False
        options: NplusplusOptions = self.options
        current_min_time: float = options.InitialStartingTime
        current_min_time += state.count(ItemNames.start_time_1, player)  *  1
        current_min_time += state.count(ItemNames.start_time_2, player)  *  2
        current_min_time += state.count(ItemNames.start_time_5, player)  *  5
        current_min_time += state.count(ItemNames.start_time_10, player) * 10
        current_max_time: float = options.InitialTimeCap
        current_max_time += state.count(ItemNames.max_time_1, player)  *  1
        current_max_time += state.count(ItemNames.max_time_2, player)  *  2
        current_max_time += state.count(ItemNames.max_time_5, player)  *  5
        current_max_time += state.count(ItemNames.max_time_10, player) * 10
        if level.times[challenge] <= current_min_time and level.times[challenge] <= current_max_time:
            return True
        return False
    
    def episode_accessible(self, state: CollectionState, player: int, episode_name: str, episode: Episode) -> bool:
        if episode_name == "A-00":
            if state.count("A-00 Progressive Level Unlock", player) < 5:
                return False
        else:
            if state.count(episode_name + " Progressive Level Unlock", player) < 6:
                return False
        options: NplusplusOptions = self.options
        current_min_time: float = options.InitialStartingTime
        current_min_time += state.count(ItemNames.start_time_1, player)  *  1
        current_min_time += state.count(ItemNames.start_time_2, player)  *  2
        current_min_time += state.count(ItemNames.start_time_5, player)  *  5
        current_min_time += state.count(ItemNames.start_time_10, player) * 10
        current_max_time: float = options.InitialTimeCap
        current_max_time += state.count(ItemNames.max_time_1, player)  *  1
        current_max_time += state.count(ItemNames.max_time_2, player)  *  2
        current_max_time += state.count(ItemNames.max_time_5, player)  *  5
        current_max_time += state.count(ItemNames.max_time_10, player) * 10
        current_gold_time: float = options.InitialGoldValue
        current_gold_time += state.count(ItemNames.gold_time_1, player)  *  1
        current_gold_time += state.count(ItemNames.gold_time_2, player)  *  2
        current_gold_time += state.count(ItemNames.gold_time_5, player)  *  5
        current_gold_time += state.count(ItemNames.gold_time_10, player) * 10
        return episode.is_possible(current_min_time, current_max_time, current_gold_time * (1/60))

    def fill_slot_data(self) -> dict[str, Any]:
        slot_data: dict[str, Any] = {}
        options: NplusplusOptions = self.options
        slot_data["objective"] = int(options.Objective)
        slot_data["initial_starting_time"] = int(options.InitialStartingTime)
        slot_data["initial_max_time"] = int(options.InitialTimeCap)
        slot_data["initial_gold_time"] = int(options.InitialGoldValue)
        
        level_data: list[int] = []
        challenge_data: list[list[int]]= []
        for location in locations:
            level: Level = self.location_to_level[location]
            level_data.append(level.id)
            challenge_data.append(self.included_challenges[location])
        slot_data["level_data"] = level_data
        slot_data["challenge_data"] = challenge_data
        return slot_data