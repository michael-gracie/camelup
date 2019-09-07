# -*- coding: utf-8 -*-

"""Module with tree search decisioning"""

import logging
import sys

from copy import deepcopy
from operator import add

import numpy as np
import pandas as pd

from numpy.lib.recfunctions import append_fields

from camelup import camelup, config
from camelup import utilities as util


logger = logging.getLogger(__name__)

iter = 400

CACHE = dict()


def get_move(game, MAX_DEPTH=1):
    """Recommends the most optimal move

    Parameters
    ----------
    game : camel up game
        Camel up game class
    MAX_DEPTH : int
        Depth of tree to be built, 1 is recommended for performance considerations

    Returns
    -------
    dict
        Dictionary of move and their corresponding expected value in coins

    """
    depth = 0
    best_value = 0
    best_move = None
    player = game.state
    logger.info("Finding Best Move")
    results = dict()
    for move in game.available_moves_pruned().values():
        logger.info(f"Get Move, Depth: {depth}, Move: {move}, Player: {player}")
        val = value(game, move, depth, player, MAX_DEPTH)[player - 1]
        results[move] = val
    return results


def value(game, move, depth, player, MAX_DEPTH):
    """Value function for recursive multi agent utility

    Parameters
    ----------
    game : camel up game
        Camel up game class
    move : str
        The move that is being assessed for value
    depth : int
        The current depth in the tree
    player : int
        The current player in the tree
    MAX_DEPTH : int
        Depth of tree to be built, 1 is recommended for performance considerations

    Returns
    -------
    list
        The value of the move for all players

    """
    logger.info(f"Value, Depth: {depth}, Move: {move}, Player: {player}")
    if "roll" in move:
        logger.info(f"Return Expected Value")
        return exp_value(game, depth + 1, MAX_DEPTH)
    else:
        logger.info(f"Return Max Value")
        game_branch = deepcopy(game)
        game_branch.play(move)
        return max_value(game_branch, depth + 1, MAX_DEPTH)


def max_value(game, depth, MAX_DEPTH):
    """Calculate the max value from all possible plays

    Parameters
    ----------
    game : camel up game
        Camel up game class
    depth : int
        The current depth in the tree
    MAX_DEPTH : int
        Depth of tree to be built, 1 is recommended for performance considerations

    Returns
    -------
    list
        Utilities of the play with the max value

    """
    if depth == MAX_DEPTH:
        logger.info(f"Return Utility")
        return list(calc_utility_np(game, iter)["utility"])
    else:
        playing_player = game.state
        values = [
            value(game, move, depth, playing_player, MAX_DEPTH)
            for move in game.available_moves_pruned().values()
        ]
        print(values)
        return util.return_max_value(values, playing_player - 1)


def exp_value(game, depth, MAX_DEPTH):
    """Calculate the expected value from a roll play

    Parameters
    ----------
    game : camel up game
        Camel up game class
    depth : int
        The current depth in the tree
    MAX_DEPTH : int
        Depth of tree to be built, 1 is recommended for performance considerations

    Returns
    -------
    list
        Utilities of the expected value of the play

    """
    outcomes = [0] * game.num_players
    num_outcomes = 0
    for key, val in game.camel_dict.items():
        if val["need_roll"]:
            for die in range(0, 3):
                logger.info(f"Outcome for Camel: {key} And Roll: {die+1}")
                game_branch = deepcopy(game)
                outcome = game_branch.play(f"self.play_roll('{key}',{die+1})")
                if outcome == "Done":
                    max_val = [val["coins"] for val in game_branch.player_dict.values()]
                else:
                    max_val = max_value(game_branch, depth, MAX_DEPTH)
                outcomes = list(map(add, outcomes, max_val))
                num_outcomes += 1
    logger.info(f"{outcomes}")
    return list(map(lambda x: x / num_outcomes, outcomes))


def calc_utility_np(game, iter):
    """Calc utility of current position

    Parameters
    ----------
    game : camel up game
        Camel up game class
    iter : int
        Iterations to run the monte carlo simulations

    Returns
    -------
    np.array
        Numpy structured array with expected utilities

    """
    coins = coins_to_numpy(game)
    if str(game.camel_dict) + str(game.tiles_dict) in CACHE.keys():
        turn_prob_first, turn_prob_second, turn_prob_other, exp_tile_points = CACHE[
            str(game.camel_dict) + str(game.tiles_dict)
        ][0]
        game_prob_first, game_prob_last, game_prob_other = CACHE[
            str(game.camel_dict) + str(game.tiles_dict)
        ][1]
    else:
        turn_prob_first, turn_prob_second, turn_prob_other, exp_tile_points = turn_prob_numpy(
            game, iter
        )
        game_prob_first, game_prob_last, game_prob_other = game_prob_numpy(game, iter)
        CACHE[str(game.camel_dict) + str(game.tiles_dict)] = [
            (turn_prob_first, turn_prob_second, turn_prob_other, exp_tile_points),
            (game_prob_first, game_prob_last, game_prob_other),
        ]
    winner_bets, loser_bets = winner_loser_bets_to_numpy(game)
    bet_tiles = bet_tiles_to_numpy(game)
    util.rename_np(turn_prob_first, ["counts", "prob"], "first")
    util.rename_np(turn_prob_second, ["counts", "prob"], "second")
    util.rename_np(turn_prob_other, ["counts", "prob"], "other")
    bets = util.numpy_left_join(bet_tiles, turn_prob_first, "camel")
    bets = util.numpy_left_join(bets, turn_prob_second, "camel")
    bets = util.numpy_left_join(bets, turn_prob_other, "camel")
    multiply_array = (
        (bets["value"] * bets["prob_first"])
        + (bets["bets"] * bets["prob_second"])
        - (bets["bets"] * bets["prob_other"])
    )
    bets = util.add_col_np(bets, "exp_value", multiply_array)
    bets_groupby = util.numpy_group_by_sum(bets, "player", "exp_value")
    final = util.numpy_left_join(coins, exp_tile_points, "player")
    final = util.numpy_left_join(final, bets_groupby, "player")
    game_first = util.numpy_left_join(winner_bets, game_prob_first, "camel")
    game_last = util.numpy_left_join(loser_bets, game_prob_last, "camel")
    game_winner_other = util.numpy_left_join(winner_bets, game_prob_other, "camel")
    game_loser_other = util.numpy_left_join(loser_bets, game_prob_other, "camel")
    game_first = util.add_col_np(
        game_first, "points", config.BET_SCALING[0 : game_first.shape[0]]
    )
    game_last = util.add_col_np(
        game_last, "points", config.BET_SCALING[0 : game_last.shape[0]]
    )
    game_winner_other = util.add_col_np(
        game_winner_other, "points", [1] * game_winner_other.shape[0]
    )
    game_loser_other = util.add_col_np(
        game_loser_other, "points", [1] * game_loser_other.shape[0]
    )
    final = util.numpy_left_join(
        final, calc_exp_value_np(game_first, "exp_value_first"), "player"
    )
    final = util.numpy_left_join(
        final, calc_exp_value_np(game_last, "exp_value_last"), "player"
    )
    final = util.numpy_left_join(
        final, calc_exp_value_np(game_winner_other, "exp_value_winner_other"), "player"
    )
    final = util.numpy_left_join(
        final, calc_exp_value_np(game_loser_other, "exp_value_loser_other"), "player"
    )
    multiply_array = (
        final["coins"]
        + final["exp_points"]
        + final["exp_value"]
        + final["exp_value_first"]
        + final["exp_value_last"]
        - final["exp_value_winner_other"]
        - final["exp_value_loser_other"]
    )
    final = util.add_col_np(final, "utility", multiply_array)
    return final


def calc_exp_value_np(df, exp_value):
    """Calculat the expected value based on the probability and points given

    Parameters
    ----------
    df : array
        Numpy array
    exp_value :
        Name of column for expected value

    Returns
    -------
    array
        Modified numpy array

    """
    multiply_array = df["prob"] * df["points"]
    df = util.add_col_np(df, exp_value, multiply_array)
    return util.numpy_group_by_sum(df, "player", exp_value)


def coins_to_numpy(game):
    """Game coins info to numpy array

    Parameters
    ----------
    game : camel up game
        Camel up game class

    Returns
    -------
    array
        Numpy array

    """
    return np.array(
        [(key[0], key[1]["coins"]) for key in [*game.player_dict.items()]],
        dtype=[("player", float), ("coins", float)],
    )


def bet_tiles_to_numpy(game):
    """Bet tiles to numpy array

    Parameters
    ----------
    game : camel up game
        Camel up game class

    Returns
    -------
    array
        Numpy array

    """
    return np.array(
        [
            (key[0], camel[0], sum(camel[1]), len(camel[1]))
            for key in [*game.player_dict.items()]
            for camel in [*key[1]["bet_tiles"].items()]
        ],
        dtype=[("player", float), ("camel", "U6"), ("value", float), ("bets", float)],
    )


def create_prob_array(result, iter):
    """Create probility from monte carlo results

    Parameters
    ----------
    result : array
        Array with monte carlo results
    iter : int
        Number of simulation iterations

    Returns
    -------
    array
        Numpy array

    """
    bins, counts = np.unique(result["camel"], return_counts=True)
    counts_array = np.array(counts, dtype=[("counts", float)])
    result_array = append_fields(bins, "counts", counts_array["counts"], usemask=False)
    result_array.dtype.names = ("camel", "counts")
    prob_array = np.array(result_array["counts"] / iter, dtype=[("prob", float)])
    return append_fields(result_array, "prob", prob_array["prob"], usemask=False)


def turn_prob_numpy(game, iter):
    """Create turn probability arrays

    Parameters
    ----------
    game : camel up game
        Camel up game class
    iter : int
        Number of simulation iterations

    Returns
    -------
    array
        Numpy array

    """
    winner_result, tile_points_result = game.turn_monte(
        game.camel_dict, game.tiles_dict, iter=iter
    )
    prob_first = create_prob_array(winner_result[winner_result["place"] == 1], iter)
    prob_second = create_prob_array(winner_result[winner_result["place"] == 2], iter)
    prob_other = create_prob_array(winner_result[winner_result["place"] > 2], iter)
    exp_tile_points = util.numpy_group_by_sum(tile_points_result, "player", "points")
    multiply_array = exp_tile_points["points"] / iter
    exp_tile_points = util.add_col_np(exp_tile_points, "exp_points", multiply_array)
    return prob_first, prob_second, prob_other, exp_tile_points


def game_prob_numpy(game, iter):
    """Create game probability arrays

    Parameters
    ----------
    game : camel up game
        Camel up game class
    iter : int
        Number of simulation iterations

    Returns
    -------
    array
        Numpy array

    """
    result = game.game_monte(game.camel_dict, game.tiles_dict, iter=iter)
    loser_place = max(result["place"])
    prob_first = create_prob_array(result[result["place"] == 1], iter)
    prob_last = create_prob_array(result[result["place"] == loser_place], iter)
    prob_other = create_prob_array(
        result[(result["place"] != 1) & (result["place"] != loser_place)], iter
    )
    return prob_first, prob_last, prob_other


def winner_loser_bets_to_numpy(game):
    """Create numpy array for game bets

    Parameters
    ----------
    game : camel up game
        Camel up game class

    Returns
    -------
    array
        Numpy array

    """
    winner_bets = np.array(game.winner_bets, dtype=[("player", float), ("camel", "U6")])
    loser_bets = np.array(game.loser_bets, dtype=[("player", float), ("camel", "U6")])
    return winner_bets, loser_bets
