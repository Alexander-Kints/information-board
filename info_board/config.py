import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
from marshmallow_dataclass import class_schema


@dataclass
class EmployeeConfig:
    parse_url: str
    base_photo_url: str
    default_photo: str


@dataclass
class ScheduleConfig:
    parse_url: str
    parse_url_rasp: str
    year: int
    faculties: List[str]
    course_numbers: List[int]


@dataclass
class MainConfig:
    employee: EmployeeConfig
    schedule: ScheduleConfig
    parse_delay_sec: int


config_path = os.path.join(
    Path(__file__).resolve().parent.parent,
    'config.yaml'
)


with open(config_path) as config_file:
    config_data = yaml.safe_load(config_file)


main_config: MainConfig = class_schema(MainConfig)().load(config_data)
