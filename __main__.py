import sys
from collections import defaultdict
from operator import itemgetter

from scipy.special import softmax

import networkx as nx

from bgg_client.utils.serialization import dump_struct, load_struct


GAMES_FILENAME = 'games.pkl'
RATINGS_FILENAME = 'users_rating.pkl'


FIRST_OP, SECOND_OP = itemgetter(0), itemgetter(1)

THREAD_FORMAT_LINK = 'https://boardgamegeek.com/thread/{}'
FORUM_WEIGHT = {
    'Crowdfunding': 2.0,
    'General': 2.0,
    'News': 2.0,
    'Organized Play': 4.0,
    'Play By Forum': 1.0,
    'Reviews': 10.0,
    'Rules': 1.0,
    'Sessions': 4.0,
    'Strategy': 6.0,
    'Variants': 8.0,
}
FORUM_WEIGHT = dict(zip(FORUM_WEIGHT.keys(), softmax(list(FORUM_WEIGHT.values()))))


def graph_stat(graph, stream=sys.stdout):
    print(f'''

    ------------------------------------------------
    Graph Simple Stat:
    \tNumber of nodes: {graph.number_of_nodes()}
    \tNumber of Edges: {graph.number_of_edges()}
    \tAverage Degree: {np.mean([degree for _, degree in graph.degree()]):.3f}
    \tDegree Assortativity Coef: {nx.degree_assortativity_coefficient(graph):.3f}
    ------------------------------------------------

    ''', file=stream)

def print_thread_links(users_threads, user, game_id, stream=sys.stdout):
    for forum, threads in users_threads[user][game_id].items():
        print(forum, ':', file=stream)
        print(*['\t' + THREAD_FORMAT_LINK.format(thread) for thread in threads], sep='\n', file=stream)

def construct_reply_edges(games, users_rating, forum_weight=FORUM_WEIGHT):
    edges = defaultdict(lambda: defaultdict(float))

    for game in games:
        for title, forum in game.items():
            for thread in forum.threads:
                author = thread.author
                users = set(FIRST_OP(post) for post in thread.posts if FIRST_OP(post))

                if author not in users_rating:
                    continue
                if game.id not in users_rating[author]:
                    continue

                for user in users:
                    if user not in users_rating:
                        continue
                    if user == author:
                        continue
                    if game.id not in users_rating[user]:
                        continue
                    edges[game.id][(user, author)] += forum_weight[title]

    return edges

def pack_user_threads():
#TODO:
    users_threads = defaultdict( # User
        lambda: defaultdict( # Game
            lambda: defaultdict( # Forum
                list # Threads
            )
        )
    )

    for game in games:
        for title, forum in game.items():
            for thread in forum.threads:
                users_threads[thread.author][game.id][title] += [thread.id]


def main():
    snapshot_path = None
    game_id = None
    topk = None

    #TODO: you pick-uped this game print

    games = load_struct(GAMES_FILENAME, snapshot_path)
    users_rating = load_struct(RATINGS_FILENAME, snapshot_path)
    users_threads = None #TODO
    edges = construct_reply_edges(games, users_rating)

    graph = nx.DiGraph()
    for edge, weight in edges[game_id].items():
        graph.add_edge(FIRST_OP(edge), SECOND_OP(edge), weight=weight)
    graph_stat(graph, stream=sys.stdout)

    page_ranks = nx.pagerank(graph)
    page_ranks = sorted(page_ranks.items(), key=SECOND_OP, reverse=True)

    for user, page_rank in page_ranks[:k]:
        print('###', user, f'Page Rank: {page_rank:3.f}', file=sys.stdout)
        print_thread_links(users_threads, user, GAME_ID, stream=sys.stdout)
        print('-' * 50, '\n', file=sys.stdout)









if __name__ == '__main__':
    main()
