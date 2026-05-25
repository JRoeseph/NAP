from enum import IntEnum

class Challenge(IntEnum):
    base        = 0b0000000000000000
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
    id: int
    gold: int
    # float stored here is the time to complete it. G++ is stored as if it was a normal challenge, 0 is just completion
    times: dict[Challenge, float]

    def __init__(self, name: str, id: int, gold: int, times: dict[Challenge, float]):
        self.name = name
        self.id = id
        self.gold = gold
        self.times = times.copy()

class Episode:
    name: str
    levels: list[Level]

    def __init__(self, name:str, lvl00: Level, lvl01: Level, lvl02: Level, lvl03: Level, lvl04: Level):
        self.name = name
        self.levels = {lvl00, lvl01, lvl02, lvl03, lvl04}

    def is_possible(self, start_time: float, max_time: float, gold_time: float) -> bool:
        current_time: float = start_time
        for level in self.levels:
            if level.times[0] > current_time:
                return False
            if level.times[Challenge.gplusplus] > current_time:
                current_time -= level.times[0]
            else:
                max_gold_time: float = current_time + gold_time * level.gold
                if max_gold_time > max_time:
                    max_gold_time = max_time
                max_gold_time -= level.times[Challenge.gplusplus]
                if max_gold_time > (current_time - level.times[0]):
                    current_time = max_gold_time
                else:
                    current_time -= level.times[0]
        return True
    
    def minimum_no_gold_time(self) -> float:
        minimum_time: float = 0
        for level in self.levels:
            minimum_time += level.times[0]
        return minimum_time

