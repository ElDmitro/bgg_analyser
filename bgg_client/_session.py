import time
from requests import Session
from xml.etree import ElementTree as ET

from tqdm import tqdm

from .core.elements import Forum, Thread


BGG_ROOT_PATH = 'https://boardgamegeek.com/xmlapi2/'

FORUMLIST_SLEEP = 5
THREAD_SLEEP = 2

COLLECTION_SLEEP = 0.5
COLLECTION_TIMEOUT = 60


class BggSession(Session):
    def get_things(self, thing_class, ids):
        request_params = {
            'id': ','.join(ids),
            'type': thing_class.kind,
            'pagesize': 100,
        }
        response = self.get(BGG_ROOT_PATH + 'thing', params=request_params)
        if not response.ok:
            raise RuntimeError(response.content)

        return [thing_class.from_xml(item) for item in ET.fromstring(response.content)]

    def get_hotest(self, thing_class):
        response = self.get(BGG_ROOT_PATH + 'hot', params={'type': thing_class.kind})
        if not response.ok:
            raise RuntimeError(response.content)

        ids = [item.get('id') for item in ET.fromstring(response.content)]

        return self.get_things(thing_class, ids)

    def get_thread_posts(self, thread_id):
        response = self.get(BGG_ROOT_PATH + 'thread', params={'id': thread_id})
        if not response.ok:
            raise RuntimeError(response.content)

        tree = ET.fromstring(response.content)
        return [
            (post.get('username'), post.find('body').text)
            for post in tree.find('articles')
        ]

    def get_forum(self, forum_id):
        response = self.get(BGG_ROOT_PATH + 'forum', params={'id': forum_id})
        if not response.ok:
            raise RuntimeError(response.content)

        tree = ET.fromstring(response.content)
        threads = list()
        for thread in tree.find('threads'):
            time.sleep(THREAD_SLEEP)

            threads.append(Thread(
                thread.get('id'),
                subject=thread.get('subject'), author=thread.get('author'),
                posts=self.get_thread_posts(thread.get('id'))
            ))

        return Forum(forum_id, tree.get('title'), threads)

    def get_forumlist(self, thing_id):
        response = self.get(BGG_ROOT_PATH + 'forumlist', params={'type': 'thing', 'id': thing_id})
        if not response.ok:
            raise RuntimeError(response.content)

        tree = ET.fromstring(response.content)
        forums = list()
        for forum_tag in tqdm(tree, desc=f'Thing {thing_id} ForumList grep'):
            time.sleep(FORUMLIST_SLEEP)
            forums.append(self.get_forum(forum_tag.get('id')))

        return forums

    def get_user_rating(self, username, ids=None, timeout=COLLECTION_TIMEOUT):
        url = BGG_ROOT_PATH + 'collection'
        request_params = {
            'username': username,
            'stats': 1,
            'brief': 1,
        }
        if ids is not None:
            request_params['id'] = ','.join(ids)

        response = self.get(url, params=request_params)
        if response.status_code not in [200, 202]:
            raise RuntimeError(response.content)

        it = 0
        while response.status_code != 200:
            if (it * COLLECTION_SLEEP) >= COLLECTION_TIMEOUT:
                raise RuntimeError('Request timeout')

            time.sleep(COLLECTION_SLEEP)
            response = self.get(url, params=request_params)
            it += 1

        tree = ET.fromstring(response.content)
        rates = dict()
        for item in tree:
            id_ = item.get('objectid')
            stats = item.find('stats')
            if not stats:
                return {}

            rating = stats.find('rating').get('value')
            if rating != 'N/A':
                rates[id_] = float(rating)

        return rates
