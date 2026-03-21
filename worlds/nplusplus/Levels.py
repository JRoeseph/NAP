from enum import IntEnum

class Challenge(IntEnum):
    gplusplus   = 0b0000000000000001
    gminusminus = 0b0000000000000010
    tplusplus   = 0b0000000000000100
    tminusminus = 0b0000000000001000
    cplusplus   = 0b0000000000010000
    cminusminus = 0b0000000000100000
    oplusplus   = 0b0000000001000000
    ominusminus = 0b0000000010000000
    eplusplus   = 0b0000000100000000
    eminusminus = 0b0000001000000000

class Level:
    name: str
    gold: int
    base_time: float
    # float stored here is the time to complete it. G++ is stored as if it was a normal challenge
    challenges: dict[Challenge, float]

    def __init__(self, name: str, gold: int, base_time: float, challenges: dict[Challenge, float]):
        self.name = name
        self.gold = gold
        self.base_time = base_time
        self.challenges = challenges.copy()

class Episode:
    name: str
    levels: list[Level]

    def __init__(self, name:str, lvl00: Level, lvl01: Level, lvl02: Level, lvl03: Level, lvl04: Level):
        self.name = name
        self.levels[0] = lvl00
        self.levels[1] = lvl01
        self.levels[2] = lvl02
        self.levels[3] = lvl03
        self.levels[4] = lvl04

    def is_possible(self, start_time: float, max_time: float, gold_time: float) -> bool:
        current_time: float = start_time
        for level in self.levels:
            if level.base_time > current_time:
                return False
            if level.challenges[Challenge.gplusplus] > current_time:
                current_time -= level.base_time
            else:
                max_gold_time: float = current_time + gold_time * level.gold
                if max_gold_time > max_time:
                    max_gold_time = max_time
                max_gold_time -= level.challenges[Challenge.gplusplus]
                if max_gold_time > (current_time - level.base_time):
                    current_time = max_gold_time
                else:
                    current_time -= level.base_time
        return True
    
    def minimum_no_gold_time(self) -> float:
        minimum_time: float = 0
        for level in self.levels:
            minimum_time += level.base_time
        return minimum_time

