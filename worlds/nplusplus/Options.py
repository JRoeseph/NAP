from dataclasses import dataclass

from Options import Choice, Range, OptionGroup, PerGameCommonOptions

class Objective(Choice):
    """
    What must be done to for the randomizer to be considered 'Complete'
    """
    display_name = "Objective"
    option_single_bingo = 0
    option_triple_bingo = 1
    option_one_episode = 2
    option_all_episodes = 3
    default = 1

class InitialGoldValue(Range):
    """
    The maximum amount of frames (1/60th of a second) an individual piece of gold can be worth
    """
    display_name = "Initial Gold Value"
    range_start = 0
    range_end = 300
    default = 0

class MaximumGoldValue(Range):
    """
    The maximum amount of frames (1/60th of a second) an individual piece of gold can be worth
    """
    display_name = "Maximum Gold Value"
    range_start = 0
    range_end = 300
    default = 120

class InitialStartingTime(Range):
    """
    The amount of time you have at the beginning of a level at the beginning of the randomizer
    """
    display_name = "Intial Starting Time"
    range_start = 3
    range_end = 180
    default = 10

class MaximumStartingTimeMultiplier(Range):
    """
    The amount of additional level starting time as a percentage of the minimum time required to complete the randomizer
    """
    display_name = "Maximum Starting Time Multiplier"
    range_start = 100
    range_end = 500
    default = 150

class InitialTimeCap(Range):
    """
    The amount of time you can hit using gold at the beginning of the randomizer
    """
    display_name = "Intial Time Cap"
    range_start = 10
    range_end = 600
    default = 30

class MaximumTimeCapMultiplier(Range):
    """
    The amount of additional time cap as a percentage of the minimum time cap required to complete the randomizer
    """
    display_name = "Maximum Time Cap Multiplier"
    range_start = 100
    range_end = 500
    default = 200

class AdditionalChallenges(Range):
    """
    The maximum amount of additional challenges to be added to the levels. 125 is the minimum to ensure on average there are
    two checks per level (1 completion, 1 challenge). This is a maximum. If not enough challenges exist on the randomly
    picked levels, it will select all of them 
    """
    display_name = "Additional Challenges"
    range_start = 125
    range_end = 375
    default = 175

class LowestDifficulty(Choice):
    """
    What is the lowest difficulty of levels you want to face
    """
    display_name = "Lowest Difficulty"
    option_trivial = 0
    option_beginner = 1
    option_developing = 2
    option_developed = 3
    option_novice = 4
    option_intermediate = 5
    option_experienced = 6
    option_advanced = 7
    option_expert = 8
    option_master = 9
    option_grandmaster = 10
    option_endgame = 11
    default = 0

class HighestDifficulty(Choice):
    """
    What is the highest difficulty of levels you want to face
    """
    display_name = "Highest Difficulty"
    option_trivial = 0
    option_beginner = 1
    option_developing = 2
    option_developed = 3
    option_novice = 4
    option_intermediate = 5
    option_experienced = 6
    option_advanced = 7
    option_expert = 8
    option_master = 9
    option_grandmaster = 10
    option_endgame = 11
    default = 5

class AverageDifficulty(Choice):
    """
    What is the average difficulty of levels you want to face.
    """
    display_name = "Average Difficulty"
    option_trivial = 0
    option_beginner = 1
    option_developing = 2
    option_developed = 3
    option_novice = 4
    option_intermediate = 5
    option_experienced = 6
    option_advanced = 7
    option_expert = 8
    option_master = 9
    option_grandmaster = 10
    option_endgame = 11
    default = 5

class LowestToAverageDifficultyRatio(Range):
    display_name = "Lowest To Average Difficulty Ratio"
    range_start = 1
    range_end = 10
    default = 3

class HighestToAverageDifficultyRatio(Range):
    display_name = "Highest To Average Difficulty Ratio"
    range_start = 1
    range_end = 10
    default = 3

class TrapPercentage(Range):
    """
    TODO: The percentage of items after core progression items are added that are traps
    """
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0

nplusplus_option_groups = [
    OptionGroup("Goal Options", [
        Objective
    ]),
    OptionGroup("Timer Options", [
        InitialGoldValue,
        MaximumGoldValue,
        InitialStartingTime,
        MaximumStartingTimeMultiplier,
        InitialTimeCap,
        MaximumTimeCapMultiplier
    ]),
    OptionGroup("Location Options", [
        AdditionalChallenges,
        LowestDifficulty,
        HighestDifficulty,
        AverageDifficulty,
        LowestToAverageDifficultyRatio,
        HighestToAverageDifficultyRatio
    ]),
    OptionGroup("Trap Options", [
        TrapPercentage
    ]),
]

@dataclass
class NplusplusOptions(PerGameCommonOptions):
    Objective: Objective
    
    InitialGoldValue: InitialGoldValue
    MaximumGoldValue: MaximumGoldValue
    InitialStartingTime: InitialStartingTime
    MaximumStartingTimeMultiplier: MaximumStartingTimeMultiplier
    InitialTimeCap: InitialTimeCap
    MaximumTimeCapMultiplier: MaximumTimeCapMultiplier
    
    AdditionalChallenges: AdditionalChallenges
    LowestDifficulty: LowestDifficulty
    HighestDifficulty: HighestDifficulty
    AverageDifficulty: AverageDifficulty
    LowestToAverageDifficultyRatio: LowestToAverageDifficultyRatio
    HighestToAverageDifficultyRatio: HighestToAverageDifficultyRatio

    TrapPercentage: TrapPercentage