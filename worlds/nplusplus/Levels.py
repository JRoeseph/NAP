from enum import IntEnum
from BaseClasses import CollectionState
from .Options import NplusplusOptions
from .data import ItemNames


class Difficulty(IntEnum):
    trivial = 0
    beginner = 1
    developing = 2
    developed = 3
    novice = 4
    intermediate = 5
    experienced = 6
    advanced = 7
    expert = 8
    master = 9
    grandmaster = 10
    endgame = 11

class Challenge(IntEnum):
    base    = 0b0000000000000000
    gpp     = 0b0000000000000010
    gmm     = 0b0000000000000100
    tpp     = 0b0000000000001000
    tmm     = 0b0000000000010000
    opp     = 0b0000000000100000
    omm     = 0b0000000001000000
    cpp     = 0b0000000010000000
    cmm     = 0b0000000100000000
    epp     = 0b0000001000000000
    emm     = 0b0000010000000000
    opt     = 0b1000000000000000

    @staticmethod
    def from_string(self, string: str):
        output: Challenge = Challenge.base
        for i in range(0, len(string), 3):
            match string[i:i + 3]:
                case "g++":
                    output |= Challenge.gpp
                case "g--":
                    output |= Challenge.gmm
                case "t++":
                    output |= Challenge.tpp
                case "t--":
                    output |= Challenge.tmm
                case "c++":
                    output |= Challenge.cpp
                case "c--":
                    output |= Challenge.cmm
                case "o++":
                    output |= Challenge.opp
                case "o--":
                    output |= Challenge.omm
                case "e++":
                    output |= Challenge.epp
                case "e--":
                    output |= Challenge.emm
                case _:
                    return Challenge.base
        return output

class Completion:
    challenge: Challenge
    difficulty: int
    time: float

    def __init__(self, challenge: Challenge, difficulty: int, time: float):
        self.challenge = challenge
        self.difficulty = difficulty
        self.time = time

class Level:
    name: str
    id: int
    gold: int
    # float stored here is the time to complete it. G++ is stored as if it was a normal challenge, 0 is just completion
    times: list[Completion]

    def __init__(self, name: str, id: int, gold: int, times: list[Completion]):
        self.name = name
        self.id = id
        self.gold = gold
        self.times = times.copy()

    def get_time(self, challenge: Challenge, difficulty: Difficulty) -> float:
        comps: list[Completion] = list(filter(lambda comp: comp.challenge in [challenge, challenge + Challenge.opt], self.times))
        min_time: float = 999
        for comp in comps:
            if comp.difficulty <= difficulty and comp.time < min_time:
                min_time = comp.time
        return min_time
    
class Episode:
    name: str
    levels: list[Level]

    def __init__(self, name:str, lvl00: Level, lvl01: Level, lvl02: Level, lvl03: Level, lvl04: Level):
        self.name = name
        self.levels = [lvl00, lvl01, lvl02, lvl03, lvl04]

    def is_possible_state(self, state: CollectionState, options: NplusplusOptions, player: int):
        current_min_time: float = float(options.InitialStartingTime)
        current_min_time += state.count(ItemNames.start_time_1, player) * 1
        current_min_time += state.count(ItemNames.start_time_2, player) * 2
        current_min_time += state.count(ItemNames.start_time_5, player) * 5
        current_min_time += state.count(ItemNames.start_time_10, player) * 10
        current_max_time: float = float(options.InitialTimeCap)
        current_max_time += state.count(ItemNames.max_time_1, player) * 1
        current_max_time += state.count(ItemNames.max_time_2, player) * 2
        current_max_time += state.count(ItemNames.max_time_5, player) * 5
        current_max_time += state.count(ItemNames.max_time_10, player) * 10
        current_gold_time: float = float(options.InitialGoldValue)
        current_gold_time += state.count(ItemNames.gold_time_1, player) * 1
        current_gold_time += state.count(ItemNames.gold_time_2, player) * 2
        current_gold_time += state.count(ItemNames.gold_time_5, player) * 5
        current_gold_time += state.count(ItemNames.gold_time_10, player) * 10
        current_gold_time /= 60
        return self.is_possible_time(current_min_time, current_max_time, current_gold_time, Difficulty(options.HighestDifficulty))

    def is_possible_time(self, start_time: float, max_time: float, gold_time: float, difficulty: Difficulty) -> bool:
        current_time: float = start_time
        for level in self.levels:
            if level.get_time(Challenge.base, difficulty) > current_time:
                return False
            if level.get_time(Challenge.gpp, difficulty) and level.get_time(Challenge.gpp, difficulty) > current_time:
                current_time -= level.get_time(Challenge.base, difficulty)
            else:
                max_gold_time: float = current_time + gold_time * level.gold
                if max_gold_time > max_time:
                    max_gold_time = max_time
                max_gold_time -= level.get_time(Challenge.gpp, difficulty)
                if max_gold_time > (current_time - level.get_time(Challenge.base, difficulty)):
                    current_time = max_gold_time
                else:
                    current_time -= level.get_time(Challenge.base, difficulty)
        return True
    
    def minimum_no_gold_time(self, difficulty: Difficulty) -> float:
        minimum_time: float = 0
        for level in self.levels:
            minimum_time += level.get_time(Challenge.base, difficulty)
        return minimum_time
    
    def minimum_start_time(self, gold_time: float, difficulty: Difficulty) -> float:
        # min_time is the current time relative to the max time, and peak time is the lowest the time goes below the hypothetical max time
        min_time: float = -self.levels[0].get_time(Challenge.base, difficulty)
        peak_time: float = min_time

        for idx in range(1,5):
            gold_min_time: float = min(min_time + gold_time * self.levels[idx].gold, 0) - self.levels[idx].get_time(Challenge.gpp,difficulty)
            base_min_time: float = min_time - self.levels[idx].get_time(Challenge.base, difficulty)
            gold_peak_time: float = peak_time - self.levels[idx].get_time(Challenge.gpp, difficulty)
            base_peak_time: float = peak_time - self.levels[idx].get_time(Challenge.base, difficulty)

            if gold_min_time > base_min_time:
                min_time = gold_min_time
                peak_time = gold_peak_time
            else:
                min_time = base_min_time
                peak_time = base_peak_time
        
        return -peak_time