from BaseClasses import Location
from __init__ import nplusplus_base_id
from data.LocationNames import level_completions, episode_completions, challenge_completions

class Nplusplus(Location):
  game: str = "Nplusplus"

def generate_location_table() -> dict[str, int]:
  location_table: dict[str, int] = {}

  count: int = 0

  for location in level_completions:
    location_table[location] = nplusplus_base_id + count
    count += 1
  
  count = 0

  for location in challenge_completions:
    location_table[location] = nplusplus_base_id + 0x2000 + count
    count += 1

  count = 0

  for location in episode_completions:
    location_table[location] = nplusplus_base_id + 0xF000 + count
    count += 1
  
  return location_table

def generate_location_groups() -> dict[str, list[str]]:
  return {
    "Level Completion": level_completions,
    "Challenge Completion": challenge_completions,
    "Episode Completion": episode_completions,
  }