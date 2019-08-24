# -*- coding: utf-8 -*-

"""Module with tree search decisioning"""

import logging

from copy import deepcopy
from operator import add

import numpy as np

from numpy.lib.recfunctions import append_fields

from camelup import camelup
from camelup import utilities as util


logger = logging.getLogger(__name__)

game = camelup.Game(3)

MAX_DEPTH = 2


def get_move(game):
    depth = 1
    best_value = 0
    best_move = None
    player = game.state
    for move in game.available_moves():
        if value(game, move, depth, player) >= best_value:
            best_value = value(game, move, depth, player)
            best_move = move
    return best_move, best_value


def value(game, move, depth, player):
    if depth == MAX_DEPTH:
        return calc_utility(game)[player - 1]
    elif "roll" in move:
        logger.info(f"Depth {depth}: Move: {move} Player: {player}")
        return exp_value(game, depth + 1)[player - 1]
    else:
        logger.info(f"Depth {depth}: Move: {move} Player: {player}")
        game_branch = deepcopy(game)
        game_branch.play(move)
        return max_value(game_branch, depth + 1)[player - 1]


def max_value(game, depth):
    playing_player = game.state
    values = [
        value(game, move, depth, playing_player) for move in game.available_moves()
    ]
    return util.return_max_value(values, playing_player)


def exp_value(game, depth):
    outcomes = [0] * game.num_players
    num_outcomes = 0
    for key, val in game.camel_dict.items():
        if val["need_roll"]:
            for die in range(0, 3):
                game_branch = deepcopy(game)
                outcome = game_branch.play(f"self.move('{key}',{die+1})")
                if outcome == "Done":
                    max_value = [
                        val["coins"] for val in game_branch.player_dict.values()
                    ]
                else:
                    max_value = max_value(game_branch, depth)
                outcomes = list(map(add, outcomes, max_value))
                num_outcomes += 1
    return outcomes / num_outcomes


def calc_utility(game):
    pass


def coins_to_numpy(game):
    return np.array(
        [(key[0], key[1]["coins"]) for key in [*game.player_dict.items()]],
        dtype=[("player", float), ("coins", float)],
    )


def bet_tiles_to_numpy(game):
    return np.array(
        [
            (key[0], camel[0], sum(camel[1]), len(camel[1]))
            for key in [*game.player_dict.items()]
            for camel in [*key[1]["bet_tiles"].items()]
        ],
        dtype=[("player", float), ("camel", "U10"), ("value", float), ("bets", float)],
    )


def turn_prob_numpy(game):
    result = game.turn_monte(game.camel_dict, game.tiles_dict, iter=1000)
    bins, counts = np.unique(result, return_counts=True)
    counts_array = np.array(counts, dtype=[("counts", float)])
    return append_fields(bins, "counts", counts_array["counts"]).filled()
