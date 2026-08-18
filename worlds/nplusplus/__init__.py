import json
from math import ceil
from typing import Any

from BaseClasses import Location, Tutorial, ItemClassification, CollectionState, Region
from stardew_valley.stardew_rule import false_
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule
from Options import OptionError
from .Options import NplusplusOptions, nplusplus_option_groups, InitialStartingTime, LowestDifficulty
from .Items import NplusplusItem, NplusplusItemData, generate_item_data_table, generate_item_table, generate_item_groups, level_unlock_item_data_table
from .Locations import NplusplusLocation, generate_location_groups, location_table, generate_location_data_table
from .data import ItemNames
from .data.LocationNames import locations, episode_names, level_completions, episode_completions, challenge_completions
from .data.LevelData import levels
from .Levels import Level, Episode, Challenge, Difficulty, Completion

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
    N++ is the 2nd, 3rd, 4th, 5th, or 6th game in the N franchise depending on who you ask. Created by Metanet Software, the N franchise started as a flash game, saw multiple console releases in N+, and the franchise recieved it's ultimate game in N++. The goal of each level is simple, reach the door switch then reach the door before time expires, collecting gold along the way to extend your time.
    """

    # Class Data
    game = "Nplusplus"
    web = NplusplusOpenWebWorld()
    options_dataclass = NplusplusOptions
    options: NplusplusOptions

    base_id = 0xBAC0000

    apworld_version = 1

    location_name_to_id = location_table
    location_name_groups = generate_location_groups()
    item_name_to_id = generate_item_table()
    item_name_groups = generate_item_groups()
    origin_region_name = "Intro Tab"

    location_to_level: dict[str, Level] = {}
    episodes: list[Episode] = []
    included_challenges: dict[str, list[Completion]] = {}
    challenge_locs: list[str] = []

    def generate_location_to_level(self) -> None:
        # Get all possible levels
        remaining_levels: list[Level] = self.get_picked_levels()

        # Manually pick out 5 levels under initial starting time to be the initially unlocked levels. If they don't exist,
        # pick the next shortest levels to populate the initial 5 levels and adjust the starting time accordingly
        possible_starting_levels: list[Level] = sorted(remaining_levels, key=lambda item: item.get_time(Challenge.base, self.options.HighestDifficulty))
        valid_levels: list[list[Level]] = [[], [], [], []]
        for level in possible_starting_levels:
            if level.get_time(Challenge.base, Difficulty(self.options.HighestDifficulty)) < float(self.options.InitialStartingTime):
                valid_challenges: int = 0
                for time in level.times:
                    if time.difficulty < self.options.HighestDifficulty and time.time < float(self.options.InitialStartingTime):
                        valid_challenges += 1
                if valid_challenges > 3:
                    valid_challenges = 3
                valid_levels[valid_challenges].append(level)
            else:
                break
        initial_levels: list[Level] = []
        for i in range (3,-1,-1):
            while valid_levels[i]:
                if len(initial_levels) >= 5:
                    break
                new_level: Level = valid_levels[i].pop(self.random.randint(0,len(valid_levels[i])-1))
                possible_starting_levels.remove(new_level)
                initial_levels.append(new_level)
        if len(initial_levels) < 5:
            for _ in range(len(initial_levels), 5):
                initial_levels.append(possible_starting_levels.pop(0))
            self.options.InitialStartingTime = InitialStartingTime(int(initial_levels[4].get_time(Challenge.base, Difficulty(self.options.HighestDifficulty))))
        for level in initial_levels:
            remaining_levels.remove(level)
        for episode_name in episode_names:
            to_add: int = 5
            episode_levels: list[Level] = []
            if episode_name in ["A-00", "B-00", "C-00", "D-00", "E-00"]:
                episode_levels.insert(0, initial_levels[ord(episode_name[0]) - ord('A')])
                to_add -= 1
            for _ in range(to_add):
                episode_levels.append(remaining_levels.pop(self.random.randint(0,len(remaining_levels)-1)))
            episode_levels.sort(key=lambda elevel: elevel.get_time(Challenge.base, Difficulty(self.options.HighestDifficulty)))
            for idx in range(5):
                self.location_to_level[f"{episode_name}-0{idx}"] = episode_levels[idx]
            self.episodes.append(Episode(episode_name, episode_levels[0], episode_levels[1], episode_levels[2], episode_levels[3], episode_levels[4]))

    @staticmethod
    def divide_levels_by_difficulty() -> list[list[Level]]:
        output: list[list[Level]] = [[],[],[],[],[],[],[],[],[],[],[],[]]
        for level in levels:
            for completion in level.times:
                if completion.challenge in [Challenge.base, Challenge.opt]:
                    output[completion.difficulty].append(level)
        return output

    def get_weight_list(self, count: int) -> list[float]:
        output: list[float] = [0] * 12
        lowest_difficulty: int = int(self.options.LowestDifficulty)
        highest_difficulty: int = int(self.options.HighestDifficulty)
        average_difficulty: int = int(self.options.AverageDifficulty)
        if lowest_difficulty != average_difficulty:
            ratio: float = 1/int(self.options.LowestToAverageDifficultyRatio)
            ratio_increment: float = (1-ratio)/(average_difficulty-lowest_difficulty)
            for i in range(average_difficulty-lowest_difficulty):
                output[lowest_difficulty+i] = ratio+i*ratio_increment
        output[average_difficulty] = 1
        if highest_difficulty != int(average_difficulty):
            ratio: float = 1 / int(self.options.HighestToAverageDifficultyRatio)
            ratio_increment: float = (1 - ratio) / (highest_difficulty - average_difficulty)
            for i in range(highest_difficulty - average_difficulty):
                output[average_difficulty+i+1] = 1 - (i+1)*ratio_increment
        levels_per_weight: float = count/sum(output)
        return [diff * levels_per_weight for diff in output]

    def get_picked_levels(self) -> list[Level]:
        weight_list: list[float] = self.get_weight_list(125)
        levels_by_difficulty: list[list[Level]] = NplusplusOpenWorld.divide_levels_by_difficulty()
        output: list[Level] = []
        for i in range (125):
            difficulty: int = self.get_weighted_difficulty(weight_list)
            while not levels_by_difficulty[difficulty]:
                NplusplusOpenWorld.remove_weight(weight_list, difficulty)
                difficulty = self.get_weighted_difficulty(weight_list)
                do_levels_remain: bool = False
                for diff in range(self.options.LowestDifficulty, self.options.HighestDifficulty+1):
                    if levels_by_difficulty[diff]:
                        do_levels_remain = True
                        break
                if do_levels_remain:
                    weight_list = self.get_weight_list(125-i)
                else:
                    if self.options.LowestDifficulty != 0:
                        self.options.LowestDifficulty.value -= 1
                    else:
                        self.options.HighestDifficulty.value += 1
                    if self.options.HighestDifficulty > 11:
                        raise Exception("Nplusplus: Unable to generate randomizer due to levels failing to populate")
                    weight_list = self.get_weight_list(125 - i)
            picked_level: Level = levels_by_difficulty[difficulty][0]
            for time in picked_level.times:
                if time.challenge in [Challenge.base, Challenge.opt]:
                    levels_by_difficulty[time.difficulty].remove(picked_level)
            output.append(picked_level)
            NplusplusOpenWorld.pop_weight(weight_list, difficulty)
        if len(output) != 125:
            raise Exception("Nplusplus: Failed to select 125 levels")
        return output

    def get_weighted_difficulty(self, weights: list[float]) -> int:
        roll: float = self.random.random() * sum(weights)
        for idx, weight in enumerate(weights):
            if roll <= weight:
                return idx
            roll -= weight
        return -1

    @staticmethod
    def pop_weight(weights: list[float], index: int) -> None:
        weights[index] -= 1
        if weights[index] < 0:
            weights_remaining: int = 0
            for weight in weights:
                if weight > 0:
                    weights_remaining += 1
            if weights_remaining != 0:
                weight_to_add: float = (-weights[index])/weights_remaining
                for weight in weights:
                    if weight > 0:
                        weight += weight_to_add

    @staticmethod
    def remove_weight(weights: list[float], idx: int) -> bool:
        weight_removed: float = weights[idx]
        weights[idx] = 0
        weights_remaining = 0
        for weight in weights:
            if weight > 0:
                weights_remaining += 1
        if weights_remaining == 0:
            return False
        else:
            weight_per_weight: float = weight_removed/weights_remaining
            for idx, weight in enumerate(weights):
                if weight > 0:
                    weights[idx] += weight_per_weight
        return True

    def num_picked_challenges(self) -> int:
        total: int = 0
        for level_list in self.included_challenges.values():
            total += len(level_list)
        return total

    @staticmethod
    def has_challenges(challenges_by_diff: list[list[tuple[str, Completion]]]):
        for diff in challenges_by_diff:
            if diff:
                return True
        return False

    # TODO: Remove optimal/not optimal time when adding the other
    def pick_challenges(self) -> None:
        challenges_by_diff: list[list[tuple[str, Completion]]] = [[], [], [], [], [], [], [], [], [], [], [], []]
        for location, level in self.location_to_level.items():
            for comp in level.times:
                if comp.challenge not in [Challenge.base, Challenge.opt] and Difficulty(
                        self.options.HighestDifficulty) >= comp.difficulty >= Difficulty(self.options.LowestDifficulty):
                    challenges_by_diff[comp.difficulty].append((location, comp))
        for i in range(5):
            rand_challenge_loc: str = F"{chr(ord('A') + i)}-00-00"
            starter_level: Level = self.episodes[i].levels[0]
            valid_challenges: list[Completion] = []
            for comp in starter_level.times:
                if comp.challenge in [Challenge.base, Challenge.opt]:
                    continue
                if comp.difficulty > Difficulty(self.options.HighestDifficulty):
                    continue
                if comp.time > float(self.options.InitialStartingTime):
                    continue
                valid_challenges.append(comp)
            if valid_challenges:
                self.included_challenges[rand_challenge_loc] = []
            for j in range(3):
                if not valid_challenges:
                    break
                added_challenge: Completion = self.random.choice(valid_challenges)
                valid_challenges.remove(added_challenge)
                for chal in valid_challenges:
                    if chal.challenge ^ Challenge.opt == added_challenge.challenge:
                        valid_challenges.remove(chal)
                        break
                for comp in valid_challenges:
                    if comp.challenge ^ Challenge.opt == added_challenge.challenge:
                        valid_challenges.remove(comp)
                        challenges_by_diff[added_challenge.difficulty].remove((rand_challenge_loc, added_challenge))
                        break
                self.included_challenges[rand_challenge_loc].append(added_challenge)
                self.challenge_locs.append(rand_challenge_loc + f" Challenge {j + 1} Completion")
                challenges_by_diff[added_challenge.difficulty].remove((rand_challenge_loc, added_challenge))
        weight_list: list[float] = self.get_weight_list(self.options.AdditionalChallenges - self.num_picked_challenges())
        while self.num_picked_challenges() < self.options.AdditionalChallenges and NplusplusOpenWorld.has_challenges(challenges_by_diff):
            difficulty: int = self.get_weighted_difficulty(weight_list)
            if not challenges_by_diff[difficulty]:
                if not NplusplusOpenWorld.remove_weight(weight_list, difficulty):
                    weight_list: list[float] = self.get_weight_list(self.options.AdditionalChallenges - self.num_picked_challenges())
                    for i in range(len(challenges_by_diff)):
                        if not challenges_by_diff[i]:
                            NplusplusOpenWorld.remove_weight(weight_list, i)
            else:
                idx: int = self.random.randint(0, len(challenges_by_diff[difficulty]) - 1)
                rand_challenge_loc: str
                rand_challenge: Completion
                (rand_challenge_loc, rand_challenge) = challenges_by_diff[difficulty].pop(idx)
                if rand_challenge_loc in self.included_challenges and len(self.included_challenges[rand_challenge_loc]) >= 3:
                    continue
                else:
                    if rand_challenge_loc in self.included_challenges:
                        has_dupe_challenge: bool = False
                        for comp in self.included_challenges[rand_challenge_loc]:
                            if rand_challenge.challenge ^ Challenge.opt == comp.challenge:
                                has_dupe_challenge = True
                                break
                        if has_dupe_challenge:
                            continue
                    else:
                        self.included_challenges[rand_challenge_loc] = []
                    NplusplusOpenWorld.pop_weight(weight_list, difficulty)
                    self.included_challenges[rand_challenge_loc].append(rand_challenge)
                    self.challenge_locs.append(rand_challenge_loc + f" Challenge {len(self.included_challenges[rand_challenge_loc])} Completion")

    def generate_early(self) -> None:
        if self.options.LowestDifficulty > self.options.AverageDifficulty:
            raise OptionError("Nplusplus: Lowest difficulty cannot be higher than average difficulty")
        if self.options.AverageDifficulty > self.options.HighestDifficulty:
            raise OptionError("Nplusplus: Highest difficulty cannot be lower than the average difficulty")
        self.episodes = []
        self.included_challenges = {}
        self.location_to_level = {}
        self.challenge_locs = []
        self.generate_location_to_level()
        self.pick_challenges()

    def create_regions(self) -> None:
        intro_tab: Region = Region("Intro Tab", self.player, self.multiworld)
        for loc_name, loc_data in generate_location_data_table().items():
            if loc_name in level_completions or loc_name in episode_completions or loc_name in self.challenge_locs:
                intro_tab.locations.append(NplusplusLocation(self.player, loc_name, loc_data.address, intro_tab))
        self.multiworld.regions += [intro_tab]

    def create_item(self, name: str) -> NplusplusItem:
        item_data_table: dict[str, NplusplusItemData] = generate_item_data_table()
        return NplusplusItem(name,
                             ItemClassification.progression if not name == ItemNames.palette_swap else ItemClassification.filler,
                             item_data_table[name].code, self.player)

    def create_items(self) -> None:
        item_pool: list[NplusplusItem] = []

        # Plus 1 here because there is a 1-to-1 mapping of level locations and level unlocks EXCEPT the starting level
        locs: int = len(self.challenge_locs) + 5
        needed_time: float = 0
        episode: Episode
        for episode in self.episodes:
            min_time: float = episode.minimum_no_gold_time(Difficulty(int(self.options.HighestDifficulty)))
            if min_time > needed_time:
                needed_time = min_time
        for _, completions in self.included_challenges.items():
            for completion in completions:
                if completion.time > needed_time:
                    needed_time = completion.time
        starting_time_items: list[int] = [
            ceil(needed_time * self.options.MaximumStartingTimeMultiplier / 100) - self.options.InitialStartingTime, 0, 0, 0]
        max_time_items: list[int] = [
            ceil(needed_time * self.options.MaximumTimeCapMultiplier / 100) - self.options.InitialTimeCap, 0, 0, 0]
        gold_time_items: list[int] = [self.options.MaximumGoldValue - self.options.InitialGoldValue, 0, 0, 0]
        list_of_lists: list[list[int]] = [starting_time_items, max_time_items, gold_time_items]
        # TODO: THIS SECTION MAY NEED TO BE OVERHAULED TO WEIGH EACH LIST
        while locs < (sum(starting_time_items) + sum(max_time_items) + sum(gold_time_items)):
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
        # This will always equal zero unless the initial item list was low
        filler_items: int = locs - (sum(starting_time_items) + sum(max_time_items) + sum(gold_time_items))
        item_data_table: dict[str, NplusplusItemData] = generate_item_data_table()
        for item_name in level_unlock_item_data_table.keys():
            if len(item_name) == 29 and item_name[2:4] == "00":
                item_pool += [self.create_item(item_name) for _ in range(5)]
            else:
                item_pool += [self.create_item(item_name) for _ in range(6)]
        item_pool += [self.create_item(ItemNames.start_time_1) for _ in range(starting_time_items[0])]
        item_pool += [self.create_item(ItemNames.start_time_2) for _ in range(starting_time_items[1])]
        item_pool += [self.create_item(ItemNames.start_time_5) for _ in range(starting_time_items[2])]
        item_pool += [self.create_item(ItemNames.start_time_10) for _ in range(starting_time_items[3])]
        item_pool += [self.create_item(ItemNames.max_time_1) for _ in range(max_time_items[0])]
        item_pool += [self.create_item(ItemNames.max_time_2) for _ in range(max_time_items[1])]
        item_pool += [self.create_item(ItemNames.max_time_5) for _ in range(max_time_items[2])]
        item_pool += [self.create_item(ItemNames.max_time_10) for _ in range(max_time_items[3])]
        item_pool += [self.create_item(ItemNames.gold_time_1) for _ in range(gold_time_items[0])]
        item_pool += [self.create_item(ItemNames.gold_time_2) for _ in range(gold_time_items[1])]
        item_pool += [self.create_item(ItemNames.gold_time_5) for _ in range(gold_time_items[2])]
        item_pool += [self.create_item(ItemNames.gold_time_10) for _ in range(gold_time_items[3])]
        item_pool += [self.create_item(ItemNames.palette_swap) for _ in range(filler_items)]

        self.multiworld.itempool += item_pool

    @staticmethod
    def merge_up_item(items: list[int]) -> bool:
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
            if len(location.name) == 15:
                episode_name = location.name[:4]
                episode_loc: Episode
                for episode in self.episodes:
                    if episode.name == episode_name:
                        episode_loc = episode
                        break
                set_rule(location, lambda state,en=episode_name,el=episode_loc: self.episode_accessible(state, self.player, en, el))
            else:
                level_name = location.name[:7]
                level_loc: Level = self.location_to_level[level_name]
                if len(location.name) == 18:
                    set_rule(location, lambda state, ln=level_name, ll=level_loc: self.level_accessible(state, self.player, ln, ll, Challenge.base))
                else:
                    challenge_num = int(location.name[18])
                    completion: Completion = self.included_challenges[level_name][challenge_num-1]
                    set_rule(location, lambda state, ln=level_name, ll=level_loc, cc=completion.challenge: self.level_accessible(state, self.player, ln, ll, cc))

        match self.options.Objective:
            case 0:
                self.multiworld.completion_condition[self.player] = lambda state: self.single_bingo_check(state)
            case 1:
                self.multiworld.completion_condition[self.player] = lambda state: self.triple_bingo_check(state)
            case 2:
                self.multiworld.completion_condition[self.player] = lambda state: self.single_episode_check(state)
            case 3:
                self.multiworld.completion_condition[self.player] = lambda state: self.all_episode_check(state)


    def get_bingo_board(self, state: CollectionState) -> list[list[int]]:
        rows: list[str] = ["A", "B", "C", "D", "E"]
        board: list[list[int]] = [[0] * 5] * 5
        for episode in self.episodes:
            if episode.is_possible_state(state, self.options, self.player):
                board[rows.index(episode.name[0])][int(episode.name[3])] = 1
        return board

    def single_bingo_check(self, state: CollectionState) -> bool:
        board: list[list[int]] = self.get_bingo_board(state)

        for i in range(5):
            for j in range(5):
                if board[i][j] == 0:
                    break
            else:
                return True
        for i in range(5):
            for j in range(5):
                if board[j][i] == 0:
                    break
            else:
                return True
        for i in range(5):
            if board[i][i] == 0:
                break
        else:
            return True
        for i in range(5):
            if board[i][4 - i] == 0:
                break
        else:
            return True

        return False

    def triple_bingo_check(self, state: CollectionState) -> bool:
        board: list[list[int]] = self.get_bingo_board(state)
        bingos: int = 0

        for i in range(5):
            for j in range(5):
                if board[i][j] == 0:
                    break
            else:
                bingos += 1
        for i in range(5):
            for j in range(5):
                if board[j][i] == 0:
                    break
            else:
                bingos += 1
        for i in range(5):
            if board[i][i] == 0:
                break
        else:
            bingos += 1
        for i in range(5):
            if board[i][4 - i] == 0:
                break
        else:
            bingos += 1

        return bingos >= 3

    @staticmethod
    def single_episode_check(state: CollectionState) -> bool:
        for location in state.locations_checked:
            if len(location.name) == 15:
                return True
        return False

    @staticmethod
    def all_episode_check(state: CollectionState) -> bool:
        episodes_complete: int = 0
        for location in state.locations_checked:
            if len(location.name) == 15:
                episodes_complete += 1
        if episodes_complete == 25:
            return True
        return False

    
    def level_accessible(self, state: CollectionState, player: int, level_name: str, level: Level, challenge: Challenge) -> bool:
        episode_name: str = level_name[:4]
        level_idx: int = int(level_name[5:])
        if episode_name[2:] == "00":
            if state.count(f"{episode_name} Progressive Level Unlock", player) < level_idx:
                return False
        else:
            if state.count(f"{episode_name} Progressive Level Unlock", player) < level_idx + 1:
                return False
        options: NplusplusOptions = self.options
        current_min_time: float = float(options.InitialStartingTime)
        current_min_time += state.count(ItemNames.start_time_1, player)  *  1
        current_min_time += state.count(ItemNames.start_time_2, player)  *  2
        current_min_time += state.count(ItemNames.start_time_5, player)  *  5
        current_min_time += state.count(ItemNames.start_time_10, player) * 10
        current_max_time: float = float(options.InitialTimeCap)
        current_max_time += state.count(ItemNames.max_time_1, player)  *  1
        current_max_time += state.count(ItemNames.max_time_2, player)  *  2
        current_max_time += state.count(ItemNames.max_time_5, player)  *  5
        current_max_time += state.count(ItemNames.max_time_10, player) * 10
        time: float = level.get_time(challenge, Difficulty(self.options.HighestDifficulty))
        if time <= current_min_time and time <= current_max_time:
            return True
        return False
    
    def episode_accessible(self, state: CollectionState, player: int, episode_name: str, episode: Episode) -> bool:
        if episode_name[2:] == "00":
            if state.count(f"{episode_name} Progressive Level Unlock", player) < 5:
                return False
        else:
            if state.count(f"{episode_name} Progressive Level Unlock", player) < 6:
                return False
        return episode.is_possible_state(state, self.options, player)

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
            level_challenge_data: list[int] = []
            if location in self.included_challenges:
                for completion in self.included_challenges[location]:
                    level_challenge_data.append(completion.challenge)
            challenge_data.append(level_challenge_data)
        slot_data["level_data"] = level_data
        slot_data["challenge_data"] = challenge_data
        return slot_data