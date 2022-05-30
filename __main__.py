import argparse
import os
import sys
from collections import defaultdict
from operator import itemgetter

import pandas as pd
import numpy as np
from numpy.linalg import norm
from scipy.special import softmax

import networkx as nx

from bgg_client.utils.serialization import dump_struct, load_struct
from collaborative_filtering import LatentFactorModel


GAMES_FILENAME = 'games.pkl'
RATINGS_FILENAME = 'users_rating.pkl'
LFM_MAP_FILENAME_FORMAT = 'cf__{}_mapping'
LFM_PREFIX = 'cf'


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

def pack_user_threads(games):
    users_threads = defaultdict(lambda: defaultdict(
        lambda: defaultdict(list)
    ))
    for game in games:
        for title, forum in game.items():
            for thread in forum.threads:
                users_threads[thread.author][game.id][title] += [thread.id]

    return users_threads

def pop_forum_users(ranks, user_threads, game_id, title, k):
    it, k_it = 0, 0
    result = list()
    while (it < len(ranks)) and (k_it < k):
        user = FIRST_OP(ranks[it])
        if user_threads[user][game_id][title]:
            result.append(ranks.pop(it)); k_it += 1
            continue
        it += 1

    return result


FORUM_TOP_K = 2
ANALYSIS_SLICE_K = 15


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', type=str, help='Username for which suggest')
    parser.add_argument('-g', type=str, help='GameId for which find experts')
    parser.add_argument('--snapshot-dir', type=str, default='snapshot', help='Snapshot directory path')
    args = parser.parse_args()

    username, game_id = args.u, args.g
    snapshot_path = args.snapshot_dir

    games = load_struct(GAMES_FILENAME, snapshot_path)
    users_rating = load_struct(RATINGS_FILENAME, snapshot_path)
    users_threads = pack_user_threads(games)
    edges = construct_reply_edges(games, users_rating)

    lfm = LatentFactorModel(64, 1.0, 1.0, 1000)
    lfm.load_hidden_stat(os.path.join(snapshot_path, LFM_PREFIX))
    users_map = load_struct(LFM_MAP_FILENAME_FORMAT.format('user'), snapshot_path)
    bg_map = load_struct(LFM_MAP_FILENAME_FORMAT.format('item'), snapshot_path)
    users_hidden = pd.DataFrame(lfm.user_hidden, index=users_map.index)

    graph = nx.DiGraph()
    for edge, weight in edges[game_id].items():
        graph.add_edge(FIRST_OP(edge), SECOND_OP(edge), weight=weight)

    page_ranks = nx.pagerank(graph)
    page_ranks = sorted(page_ranks.items(), key=SECOND_OP, reverse=True)
    if ANALYSIS_SLICE_K is not None:
        page_ranks = page_ranks[:ANALYSIS_SLICE_K]

    if username in users_map.index:
        experts = [user for user, _ in page_ranks]
        experts_hidden = users_hidden.loc[experts].values
        user_hidden = users_hidden.loc[username].values
        similarities = (experts_hidden @ user_hidden) / norm(experts_hidden, axis=1) / norm(user_hidden)
        page_ranks = [(user, page_rank, similarity) for (user, page_rank), similarity in zip(page_ranks, similarities)]
        page_ranks = sorted(page_ranks, key=itemgetter(2), reverse=True)
    else:
        print('\n\n!!! Your passed unknown user !!!\n\n', file=sys.stdout)
        page_ranks = [(user, page_rank, 0.0) for user, page_rank in page_ranks]

    for game in games:
        if game.id == game_id:
            print('-' * 30, 'GAME DESCRIPTION', '-' * 30, file=sys.stdout)
            print(game, file=sys.stdout)
            print('-' * 90, file=sys.stdout)

    graph_stat(graph, stream=sys.stdout)

    for forum in ('News', 'Reviews', 'Strategy'):
        print('\n\n', '-' * 40, forum.upper(), '-' * 40, file=sys.stdout)
        users_page_ranks = pop_forum_users(page_ranks, users_threads, game_id, forum, FORUM_TOP_K)
        for user, page_rank, similarity in users_page_ranks:
            print('#######', user, f'Page Rank: {page_rank:.3f}', f'Attitude Similarity: {similarity:.3f}', file=sys.stdout)
            print_thread_links(users_threads, user, game_id, stream=sys.stdout)
            print('#' * 50, '\n', file=sys.stdout)

        print('-' * 90, file=sys.stdout)


if __name__ == '__main__':
    main()
