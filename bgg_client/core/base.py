from dataclasses import dataclass


@dataclass
class BGGElement:
    id: str


@dataclass
class Thing:
    kind = 'thing'

    id: str
