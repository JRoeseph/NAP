from dataclasses import dataclass

from Options import Choice, Range, OptionGroup, PerGameCommonOptions

class Objective(Choice):
    """
    What must be done to for the randomizer to be considered 'Complete'
    """
    display_name = "Objective"
    option_triple_bingo = 0
    option_all_episodes = 1
    default = 0

class MaximumGoldValue(Range):
    """
    The maximum amount of tenths of seconds an individual piece of gold can be worth
    """
    display_name = "Maximum Gold Value"
    range_start = 0
    range_end = 50
    default = 20

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
    The amount of additional challenges to be added to the levels
    """
    display_name = "Additional Challenges"
    range_start = 0
    range_end = 250
    default = 50
  
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
        MaximumGoldValue,
        InitialStartingTime,
        MaximumStartingTimeMultiplier,
        InitialTimeCap,
        MaximumTimeCapMultiplier
    ]),
    OptionGroup("Location Options", [
        AdditionalChallenges
    ]),
    OptionGroup("Trap Options", [
        TrapPercentage
    ]),
]

@dataclass
class NplusplusOptions(PerGameCommonOptions):
    Objective: Objective
    
    MaximumGoldValue: MaximumGoldValue
    InitialStartingTime: InitialStartingTime
    MaximumStartingTimeMultiplier: MaximumStartingTimeMultiplier
    InitialTimeCap: InitialTimeCap
    MaximumTimeCapMultiplier: MaximumTimeCapMultiplier
    
    AdditionalChallenges: AdditionalChallenges

    TrapPercentage: TrapPercentage