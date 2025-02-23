from dataclasses import dataclass
from pathlib import Path
from typing import List
import os
import yaml
from marshmallow_dataclass import class_schema

@dataclass
class EmployeeConfig:
    parse_url: str
    delay_sec: int


@dataclass
class ScheduleConfig:
    parse_url: str
    year: int
    faculties: List[str]
    course_numbers: List[int]


@dataclass
class MainConfig:
    employee: EmployeeConfig
    schedule: ScheduleConfig


config_path = os.path.join(
    Path(__file__).resolve().parent.parent,
    'config.yaml'
)


with open(config_path) as config_file:
    config_data = yaml.safe_load(config_file)


main_config: MainConfig = class_schema(MainConfig)().load(config_data)

print(main_config)
