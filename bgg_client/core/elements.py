from dataclasses import dataclass, field
from typing import List, Tuple

from .base import BGGElement


@dataclass
class Thread(BGGElement):
    subject: str
    author: str

    posts: List[Tuple[str, str]] = field(repr=False)

@dataclass
class Forum(BGGElement):
    title: str

    threads: List[Thread] = field(repr=False)
