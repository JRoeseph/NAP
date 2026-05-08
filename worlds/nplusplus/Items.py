from typing import NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from data import ItemNames

from __init__ import nplusplus_base_id

class NplusplusItem(Item):
  game = "Nplusplus"

class NplusplusItemData(NamedTuple):
  code: Optional[int] = None
  type: ItemClassification = ItemClassification.filler

level_unlock_item_data_table: dict[str, NplusplusItemData] = {
  ItemNames.prog_a00: NplusplusItemData(nplusplus_base_id + 0x000, ItemClassification.progression),
  ItemNames.prog_a01: NplusplusItemData(nplusplus_base_id + 0x001, ItemClassification.progression),
  ItemNames.prog_a02: NplusplusItemData(nplusplus_base_id + 0x002, ItemClassification.progression),
  ItemNames.prog_a03: NplusplusItemData(nplusplus_base_id + 0x003, ItemClassification.progression),
  ItemNames.prog_a04: NplusplusItemData(nplusplus_base_id + 0x004, ItemClassification.progression),
  ItemNames.prog_b00: NplusplusItemData(nplusplus_base_id + 0x005, ItemClassification.progression),
  ItemNames.prog_b01: NplusplusItemData(nplusplus_base_id + 0x006, ItemClassification.progression),
  ItemNames.prog_b02: NplusplusItemData(nplusplus_base_id + 0x007, ItemClassification.progression),
  ItemNames.prog_b03: NplusplusItemData(nplusplus_base_id + 0x008, ItemClassification.progression),
  ItemNames.prog_b04: NplusplusItemData(nplusplus_base_id + 0x009, ItemClassification.progression),
  ItemNames.prog_c00: NplusplusItemData(nplusplus_base_id + 0x00A, ItemClassification.progression),
  ItemNames.prog_c01: NplusplusItemData(nplusplus_base_id + 0x00B, ItemClassification.progression),
  ItemNames.prog_c02: NplusplusItemData(nplusplus_base_id + 0x00C, ItemClassification.progression),
  ItemNames.prog_c03: NplusplusItemData(nplusplus_base_id + 0x00D, ItemClassification.progression),
  ItemNames.prog_c04: NplusplusItemData(nplusplus_base_id + 0x00E, ItemClassification.progression),
  ItemNames.prog_d00: NplusplusItemData(nplusplus_base_id + 0x00F, ItemClassification.progression),
  ItemNames.prog_d01: NplusplusItemData(nplusplus_base_id + 0x010, ItemClassification.progression),
  ItemNames.prog_d02: NplusplusItemData(nplusplus_base_id + 0x011, ItemClassification.progression),
  ItemNames.prog_d03: NplusplusItemData(nplusplus_base_id + 0x012, ItemClassification.progression),
  ItemNames.prog_d04: NplusplusItemData(nplusplus_base_id + 0x013, ItemClassification.progression),
  ItemNames.prog_e00: NplusplusItemData(nplusplus_base_id + 0x014, ItemClassification.progression),
  ItemNames.prog_e01: NplusplusItemData(nplusplus_base_id + 0x015, ItemClassification.progression),
  ItemNames.prog_e02: NplusplusItemData(nplusplus_base_id + 0x016, ItemClassification.progression),
  ItemNames.prog_e03: NplusplusItemData(nplusplus_base_id + 0x017, ItemClassification.progression),
  ItemNames.prog_e04: NplusplusItemData(nplusplus_base_id + 0x018, ItemClassification.progression),
}

gold_time_item_data_table: dict[str, NplusplusItemData] = {
  ItemNames.gold_time_1:   NplusplusItemData(nplusplus_base_id + 0x1000 + 0x00, ItemClassification.progression),
  ItemNames.gold_time_2:   NplusplusItemData(nplusplus_base_id + 0x1000 + 0x01, ItemClassification.progression),
  ItemNames.gold_time_5:   NplusplusItemData(nplusplus_base_id + 0x1000 + 0x02, ItemClassification.progression),
  ItemNames.gold_time_10:  NplusplusItemData(nplusplus_base_id + 0x1000 + 0x03, ItemClassification.progression),
}

start_time_item_data_table: dict[str, NplusplusItemData] = {
  ItemNames.start_time_1:  NplusplusItemData(nplusplus_base_id + 0x1100 + 0x04, ItemClassification.progression),
  ItemNames.start_time_2:  NplusplusItemData(nplusplus_base_id + 0x1100 + 0x05, ItemClassification.progression),
  ItemNames.start_time_5:  NplusplusItemData(nplusplus_base_id + 0x1100 + 0x06, ItemClassification.progression),
  ItemNames.start_time_10: NplusplusItemData(nplusplus_base_id + 0x1100 + 0x07, ItemClassification.progression),
}

max_time_item_data_table: dict[str, NplusplusItemData] = {
  ItemNames.max_time_1:    NplusplusItemData(nplusplus_base_id + 0x1200 + 0x08, ItemClassification.progression),
  ItemNames.max_time_2:    NplusplusItemData(nplusplus_base_id + 0x1200 + 0x09, ItemClassification.progression),
  ItemNames.max_time_5:    NplusplusItemData(nplusplus_base_id + 0x1200 + 0x0A, ItemClassification.progression),
  ItemNames.max_time_10:   NplusplusItemData(nplusplus_base_id + 0x1200 + 0x0B, ItemClassification.progression),
}

filler_item_data_table: dict[str, NplusplusItemData] = {
  ItemNames.palette_swap: NplusplusItemData(nplusplus_base_id + 0x4000 + 0x00, ItemClassification.filler),
}

def generate_item_data_table() -> dict[str, NplusplusItemData]:
  return {**level_unlock_item_data_table,
          **gold_time_item_data_table,
          **start_time_item_data_table,
          **max_time_item_data_table,
          **filler_item_data_table}

def generate_item_groups() -> dict[str, list[str]]:
  item_groups: dict[str, list[str]] = {
    "Level Unlocks":  list(level_unlock_item_data_table.keys()),
    "Gold Time":      list(gold_time_item_data_table.keys()),
    "Start Time":     list(start_time_item_data_table.keys()),
    "Max Time":       list(max_time_item_data_table.keys()),
    "Filler Items":   list(filler_item_data_table.keys()),
  }

  return item_groups

