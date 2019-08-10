# -*- coding: utf-8 -*-

"""Module with tree search decisioning"""

from camelup import camelup


game = camelup.Game(3)


def get_move(game):
    depth = 1
    best_value = 0
    best_move = None
    for move in game.available_moves():
        if value(game, move, depth) >= best_value:
            best_value = value(game, move, depth)
            best_move = move
    return best_move


def value(game, move, depth):
    game.move(move)
    if depth == "d":
        return calc_utility(game)
    elif game is None:
        return game.player_dict
    elif move == "roll":
        return exp_value(game, depth + 1)
    else:
        return max_value(game, depth + 1)


def max_value(game, depth):
    values = [value(game, move, depth) for move in game.available_moves()]
    return max(values)


def exp_value(game, depth):
    values = [value(game, move, depth) for move in game.available_moves()]
    return values / len(values)


def calc_utility(game):
    pass
