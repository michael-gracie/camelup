# -*- coding: utf-8 -*-

"""Module with tree search decisioning"""

import logging

from copy import deepcopy
from operator import add

import numpy as np
import pandas as pd

from numpy.lib.recfunctions import append_fields

from camelup import camelup, config
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


game = camelup.Game(3)

camel_dict = {
    "red": {"height": 1, "space": 1, "need_roll": True},
    "blue": {"height": 2, "space": 1, "need_roll": True},
    "green": {"height": 1, "space": 2, "need_roll": True},
}
game.camel_dict = camel_dict

game.play_winner_card("blue")
game.play_loser_card("red")
game.play_bet_tile("blue")

game.state = 2
game.play_bet_tile("blue")
game.play_winner_card("green")


def calc_utility(game, iter):
    coins = coins_to_numpy(game)
    turn_prob_first, turn_prob_second, turn_prob_other, exp_tile_points = turn_prob_numpy(
        game, iter
    )
    game_prob_first, game_prob_last, game_prob_other = game_prob_numpy(game, iter)
    winner_bets, loser_bets = winner_loser_bets_to_numpy(game)
    bet_tiles = bet_tiles_to_numpy(game)
    bets = pd.DataFrame(bet_tiles).merge(
        pd.DataFrame(turn_prob_first), on="camel", how="left", suffixes=("", "_first")
    )
    bets = bets.merge(
        pd.DataFrame(turn_prob_second), on="camel", how="left", suffixes=("", "_second")
    )
    bets = bets.merge(
        pd.DataFrame(turn_prob_other), on="camel", how="left", suffixes=("", "_other")
    )
    bets["exp_value"] = (
        bets["value"] * bets["prob"]
        + bets["bets"] * bets["prob_second"]
        - bets["bets"] * bets["prob_other"]
    )
    bets_groupby = bets.groupby("player")["exp_value"].sum().reset_index()
    final = pd.DataFrame(coins).merge(
        pd.DataFrame(exp_tile_points), on="player", how="left"
    )
    final = final.merge(bets_groupby, on="player", how="left")
    game_first = pd.DataFrame(winner_bets).merge(
        pd.DataFrame(game_prob_first), on="camel", how="inner"
    )
    game_last = pd.DataFrame(loser_bets).merge(
        pd.DataFrame(game_prob_last), on="camel", how="inner"
    )
    game_first = pd.merge(
        game_first, config.BET_SCALING, left_index=True, right_index=True
    )
    game_last = pd.merge(
        game_last, config.BET_SCALING, left_index=True, right_index=True
    )
    game_winner_other = pd.DataFrame(winner_bets).merge(
        pd.DataFrame(game_prob_other), on="camel", how="inner"
    )
    game_loser_other = pd.DataFrame(loser_bets).merge(
        pd.DataFrame(game_prob_other), on="camel", how="inner"
    )
    game_winner_other["points"] = 1
    game_loser_other["points"] = 1
    calc_exp_value(game_first), calc_exp_value(game_last), calc_exp_value(
        game_winner_other
    ), calc_exp_value(game_loser_other)
    final = game_merge_to_final(final, game_first, "first")
    final = game_merge_to_final(final, game_last, "last")
    final = game_merge_to_final(final, game_winner_other, "winner_other")
    final = game_merge_to_final(final, game_loser_other, "loser_other")
    final.fillna(0, inplace=True)
    final["utility"] = (
        final["coins"]
        + final["points"]
        + final["exp_value"]
        + final["exp_value_first"]
        + final["exp_value_last"]
        - final["exp_value_winner_other"]
        - final["exp_value_loser_other"]
    )
    return final


def calc_exp_value(df):
    df["exp_value"] = df["prob"] * df["points"]


def game_merge_to_final(final_df, game_df, suffix):
    return final_df.merge(
        game_df.groupby("player")["exp_value"].sum().reset_index(),
        on="player",
        how="left",
        suffixes=("", f"_{suffix}"),
    )


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


def create_prob_array(result, iter):
    bins, counts = np.unique(result, return_counts=True)
    counts_array = np.array(counts, dtype=[("counts", float)])
    result_array = append_fields(bins, "counts", counts_array["counts"], usemask=False)
    prob_array = np.array(result_array["counts"] / iter, dtype=[("prob", float)])
    return append_fields(result_array, "prob", prob_array["prob"], usemask=False)


def turn_prob_numpy(game, iter):
    winner_result, tile_points_result = game.turn_monte(
        game.camel_dict, game.tiles_dict, iter=iter
    )
    prob_first = create_prob_array(winner_result[winner_result["place"] == 1], iter)
    prob_second = create_prob_array(winner_result[winner_result["place"] == 2], iter)
    prob_other = create_prob_array(winner_result[winner_result["place"] > 2], iter)
    exp_tile_points = util.numpy_group_by_sum(tile_points_result, "player", "points")
    return prob_first, prob_second, prob_other, exp_tile_points


def game_prob_numpy(game, iter):
    result = game.game_monte(game.camel_dict, game.tiles_dict, iter=iter)
    loser_place = max(result["place"])
    prob_first = create_prob_array(result[result["place"] == 1], iter)
    prob_last = create_prob_array(result[result["place"] == loser_place], iter)
    prob_other = create_prob_array(
        result[(result["place"] != 1) & (result["place"] != loser_place)], iter
    )
    return prob_first, prob_last, prob_other


def winner_loser_bets_to_numpy(game):
    winner_bets = np.array(
        game.winner_bets, dtype=[("player", float), ("camel", "U10")]
    )
    loser_bets = np.array(game.loser_bets, dtype=[("player", float), ("camel", "U10")])
    return winner_bets, loser_bets
