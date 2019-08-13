# -*- coding: utf-8 -*-

"""Module with tree search decisioning"""

from operator import add

from camelup import camelup
from camelup import utilities as util


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
    return best_move


def value(game, move, depth, player):
    if "roll" in move:
        return exp_value(game, depth + 1)[player - 1]
    elif depth == MAX_DEPTH:
        return calc_utility(game)[player - 1]
    else:
        game.play(move)
        return max_value(game, depth + 1)[player - 1]


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
                outcome = game.play(f"self.move('{key}',{die+1})")  # use outcome
                if outcome == "Done":
                    max_value = game.player_dict
                else:
                    max_value = max_value(game, depth)
                outcomes = list(map(add, outcomes, max_value))
                num_outcomes += 1
    return outcomes / num_outcomes


def calc_utility(game):
    pass
