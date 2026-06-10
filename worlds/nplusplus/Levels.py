from enum import IntEnum
from typing import Optional

class Challenge(IntEnum):
    base    = 0b0000000000000000
    gpp     = 0b0000000000000001
    gmm     = 0b0000000000000010
    tpp     = 0b0000000000000100
    tmm     = 0b0000000000001000
    cpp     = 0b0000000000010000
    cmm     = 0b0000000000100000
    opp     = 0b0000000001000000
    omm     = 0b0000000010000000
    epp     = 0b0000000100000000
    emm     = 0b0000001000000000
    opt     = 0b1000000000000000

class Completion:
    challenge: Challenge
    difficulty: int
    time: float

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

    def get_base_time(self, difficulty: int) -> float:
        comps: list[Completion] = list(filter(lambda comp: comp.challenge in [Challenge.gpp, Challenge.gpp + Challenge.opt], self.times))
        min_time: float = 999
        for comp in comps:
            if comp.difficulty <= difficulty and comp.time < min_time:
                min_time = comp.time
        return min_time
    
    def get_gpp_time(self, difficulty: int) -> Optional[float]:
        comps: list[Completion] = list(filter(lambda comp: comp.challenge in [Challenge.gpp, Challenge.gpp + Challenge.opt], self.times))
        min_time: Optional[float] = None
        for comp in comps:
            if comp.difficulty <= difficulty and (not min_time or comp.time < min_time):
                min_time = comp.time
        return min_time
    
class Episode:
    name: str
    levels: list[Level]

    def __init__(self, name:str, lvl00: Level, lvl01: Level, lvl02: Level, lvl03: Level, lvl04: Level):
        self.name = name
        self.levels = {lvl00, lvl01, lvl02, lvl03, lvl04}

    def is_possible(self, start_time: float, max_time: float, gold_time: float, difficulty: int) -> bool:
        current_time: float = start_time
        for level in self.levels:
            if level.get_base_time(difficulty) > current_time:
                return False
            if level.get_gpp_time(difficulty) and level.get_gpp_time(difficulty) > current_time:
                current_time -= level.get_base_time(difficulty)
            else:
                max_gold_time: float = current_time + gold_time * level.gold
                if max_gold_time > max_time:
                    max_gold_time = max_time
                max_gold_time -= level.get_gpp_time(difficulty)
                if max_gold_time > (current_time - level.get_base_time(difficulty)):
                    current_time = max_gold_time
                else:
                    current_time -= level.get_base_time(difficulty)
        return True
    
    def minimum_no_gold_time(self, difficulty: int) -> float:
        minimum_time: float = 0
        for level in self.levels:
            minimum_time += level.get_base_time(difficulty)
        return minimum_time
    
    def minimum_start_time(self, gold_time: float, difficulty: int) -> float:
        # min_time is the current time relative to the max time, and peak time is the lowest the time goes below the hypothetical max time
        min_time: float = -self.levels[0].get_base_time(difficulty)
        peak_time: float = min_time

        for idx in range(1,5):
            gold_min_time: float = min(min_time + gold_time * self.levels[idx].gold, 0) - self.levels[idx].get_gpp_time(difficulty)
            base_min_time: float = min_time - self.levels[idx].get_base_time(difficulty)
            gold_peak_time: float = peak_time - self.levels[idx].get_gpp_time(difficulty)
            base_peak_time: float = peak_time - self.levels[idx].get_base_time(difficulty)

            if gold_min_time > base_min_time:
                min_time = gold_min_time
                peak_time = gold_peak_time
            else:
                min_time = base_min_time
                peak_time = base_peak_time
        
        return -peak_time