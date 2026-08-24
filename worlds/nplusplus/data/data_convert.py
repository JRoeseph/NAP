import csv
from enum import IntEnum
from io import TextIOWrapper

class Completion:
  challenge: str
  difficulty: str
  time: float

  def __init__(self, challenge: str, difficulty: str, time: str):
    self.challenge = challenge
    self.difficulty = difficulty
    self.time = float(time)

def string_to_challenge(challenge: str) -> str:
  output: str = ""
  if challenge == "":
    return "Challenge.base"
  if challenge == "*":
    return "Challenge.opt"
  if challenge[0] == "*":
    output += "Challenge.opt+"
    challenge = challenge[1:]
  challenge = challenge.replace("++", "pp")
  challenge = challenge.replace("--", "mm")
  for idx in range(0, len(challenge)-1, 3):
    output += f"Challenge.{challenge[idx].lower()}{challenge[(idx+1):(idx+3)]}+"
  return output[:-1]

def challenge_list_to_string(challenges: list[Completion]):
  output: str = ""
  comp: Completion
  for comp in challenges:
    output += f"Completion({string_to_challenge(comp.challenge)},Difficulty.{comp.difficulty.lower()},{comp.time}),"
  return output[:-1]

def write_level(stream: TextIOWrapper, name: str, id: int, gold: int, challenges: list[Completion]):
  stream.write(f"Level(\"{name}\", {id}, {gold}, [{challenge_list_to_string(challenges)}]),\n")

with open('NAP++ Difficulties - Level List.csv', newline='') as data:
  with open("LevelData.py", "w") as out:

    out.write("from ..Levels import Level, Completion, Challenge, Difficulty \n\n")
    out.write("############################################################################\n")
    out.write("#                                                                          #\n")
    out.write("#  DO NOT MODIFY THIS FILE MANUALLY. This file is auto-generated based on  #\n")
    out.write("#  data retrieved from the community driven level list which includes      #\n")
    out.write("#  times, difficulties, and challenges                                     #\n")
    out.write("#                                                                          #\n")
    out.write("############################################################################\n\n")
    out.write("levels: list[Level] = [\n")

    reader = csv.reader(data)
    next(reader)
    for row in reader:
      completions: list[Completion] = []
      if row[0] == "" or row[1] == "" or row[3] == "" or row[4] == "" or row[5] == "":
        continue
      completions.append(Completion("", row[4], row[5]))
      if row[6] != "" and row[7] != "":
        completions.append(Completion("*", row[6], row[7]))
      if row[8] != "" and row[9] != "":
        completions.append(Completion("g++", row[8], row[9]))
      if row[10] != "" and row[11] != "":
        completions.append(Completion("*g++", row[10], row[11]))
      for idx in range(12, len(row), 5):
        if row[idx] == "" or row[idx+1] == "" or row[idx+2] == "":
          break
        completions.append(Completion(row[idx],row[idx+1],row[idx+2]))
        if row[idx+3] != "" and row[idx+4] != "":
          completions.append(Completion(f"*{row[idx]}",row[idx+3],row[idx+4]))
      write_level(out, row[0], row[1], row[3], completions)
    out.write("]")