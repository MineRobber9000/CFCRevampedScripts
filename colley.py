import numpy as np
from numpy.linalg import inv
from scipy.special import binom
from functools import reduce

class Game:
    def __init__(self,winner,loser,winner_score,loser_score,**kwargs):
        self.__dict__.update(locals())

def mov_factor(game):
    probability = 0
    for p in range(game.loser_score + 1):
        probability += float(2 ** (game.winner_score - p - 1)) / float(2 ** (2 * game.winner_score - 1)) * binom(game.winner_score + p - 1, game.winner_score - 1)
    return 1 - probability

def process(games,weight_fn=lambda game: 1,margin=False):
    teams = reduce(lambda s, game: s | set([game.winner,game.loser]), games, set())
    ids = dict(zip(teams, range(len(teams))))
    ids_to_team = {v: k for k, v in ids.items()}
    A = 2 * np.eye(len(teams))
    b = np.ones(shape=(len(teams), 1))
    for game in games:
        mov_weight = 1 if not margin else mov_factor(game)
        winner_id, loser_id = ids[game.winner], ids[game.loser]
        A[winner_id][loser_id] -= 1 * mov_weight * weight_fn(game)
        A[loser_id][winner_id] -= 1 * mov_weight* weight_fn(game)
        A[winner_id][winner_id] += 1 * mov_weight * weight_fn(game)
        A[loser_id][loser_id] += 1 * mov_weight * weight_fn(game)
        b[winner_id][0] += 0.5 * mov_weight * weight_fn(game)
        b[loser_id][0] -= 0.5 * mov_weight * weight_fn(game)
    rank_pairs = zip(range(len(teams)), np.dot(inv(A), b).T[0])
    to_team = lambda pair: (ids_to_team[pair[0]], pair[1])
    return map(to_team, sorted(rank_pairs, key=lambda p: -p[1]))
