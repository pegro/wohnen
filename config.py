from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel


class General(BaseModel):
    period: int


class FlatParams(BaseModel):
    area_min: int
    rooms_min: int
    rooms_max: int
    rent_base_max: int
    rent_total_max: int
    wbs: int


class Filter(BaseModel):
    allow: dict
    block: dict


class Search(BaseModel):
    sites: List[str]
    flat_params: FlatParams
    filter: Filter


class Telegram(BaseModel):
    name: str
    max_field_len: int
    api_key: str
    ids: List[int]


class Maps(BaseModel):
    center: str
    group_size: int
    key: str
    zoom: int


class Config(BaseModel):
    general: General
    search: Search
    telegram: Telegram
    maps: Maps


def load_config(config_file) -> Config:
    with open(config_file, "r") as file:
        config_raw = yaml.safe_load(file)
    return Config.parse_obj(config_raw)
