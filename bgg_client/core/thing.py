from dataclasses import dataclass, field
from typing import List, Dict

from .base import Thing
from .elements import Forum
from ..utils import xml


@dataclass
class ForumContainer:
    _forumlist: Dict[str, Forum] = field(init=False, repr=False, default_factory=dict)

    def __getitem__(self, title):
        return self._forumlist[title]

    def __setitem__(self, title, forum):
        if not isinstance(forum, Forum):
            raise RuntimeError('non-Forum passed')
        self._forumlist[title] = forum

    def load_forumlist(self, forumlist):
        for forum in forumlist:
            self[forum.title] = forum

    def titles(self):
        return self._forumlist.keys()

    def forums(self):
        return self._forumlist.values()

    def items(self):
        return self._forumlist.items()

    def __iter__(self):
        return iter(self._forumlist)


@dataclass
class BoardGame(Thing, ForumContainer):
    kind = 'boardgame'

    name: str
    description: str = field(repr=False)
    image: str = field(repr=False)
    yearpublished: int

    minage: int = field(repr=False)

    minplaytime: int
    maxplaytime: int

    minplayers: int
    maxplayers: int
    nplayers_best: str

    categories: List[str] = field(repr=False)

    def __str__(self):
        return f'''
        {self.image}
        {self.name} ({self.yearpublished})
        R: {self.minage}+

        {self.description}

        Playtime: {self.minplaytime} - {self.maxplaytime}
        Players: {self.minplayers} - {self.maxplayers} ({self.nplayers_best})

        {self.categories}
        '''

    @staticmethod
    def from_xml(item_xml):
        id_ = item_xml.get('id')
        attrs = dict()

        for attr in (
            ('name', str), ('description', str),
            ('yearpublished', int),
            ('minplaytime', int), ('maxplaytime', int),
            ('minplayers', int), ('maxplayers', int),
            ('minage', int),
        ):
            attr, cast = attr
            attrs[attr] = cast(item_xml.find(attr).get('value'))


        for attr in (
            ('image', str),
            ('description', str),
        ):
            attr, cast = attr
            attrs[attr] = cast(item_xml.find(attr).text)


        nplayers_tag = xml.find_tag_by_attr(item_xml, 'poll', 'name', 'suggested_numplayers')
        nplayers_poll = [
            (
                result.get('numplayers'),
                int(xml.find_tag_by_attr(result, 'result', 'value', 'Best').get('numvotes'))
            )
            for result in nplayers_tag
        ]
        attrs['nplayers_best'] = sorted(nplayers_poll, key=lambda x: x[1]).pop()[0]


        attrs['categories'] = [
            link.get('value')
            for link in xml.find_tags_by_attr(item_xml, 'link', 'type', 'boardgamecategory')
        ]

        return BoardGame(id_, **attrs)
