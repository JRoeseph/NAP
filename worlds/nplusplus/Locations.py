from typing import NamedTuple, Optional
from BaseClasses import Location
from .Items import nplusplus_base_id
from .data.LocationNames import level_completions, episode_completions, challenge_completions

class NplusplusLocation(Location):
  game: str = "Nplusplus"

class NplusplusLocationData(NamedTuple):
  address: Optional[int] = None

def generate_location_data_table() -> dict[str, NplusplusLocationData]:
  location_table: dict[str, NplusplusLocationData] = {}

  count: int = 0

  for location in level_completions:
    location_table[location] = NplusplusLocationData(nplusplus_base_id + count)
    count += 1
  
  count = 0

  for location in challenge_completions:
    location_table[location] = NplusplusLocationData(nplusplus_base_id + 0x2000 + count)
    count += 1

  count = 0

  for location in episode_completions:
    location_table[location] = NplusplusLocationData(nplusplus_base_id + 0xF000 + count)
    count += 1
  
  return location_table

def generate_location_groups() -> dict[str, list[str]]:
  return {
    "Level Completion": level_completions,
    "Challenge Completion": challenge_completions,
    "Episode Completion": episode_completions,
  }

location_table = {name: data.address for name, data in generate_location_data_table().items() if data.address is not None}