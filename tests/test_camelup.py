#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `camelup` package."""

from copy import deepcopy

import pytest

import camelup.camelup as camelup


camel_dict = {
    "red": {"height": 1, "space": 1, "need_roll": True},
    "blue": {"height": 2, "space": 1, "need_roll": True},
    "green": {"height": 1, "space": 2, "need_roll": True},
}


@pytest.fixture(params=[2, 3, 4])
def game_param(request):
    num_players = request.param
    game = camelup.Game(num_players)
    return game


@pytest.fixture
def camel_dict_copy():
    return deepcopy(camel_dict)


@pytest.fixture()
def game(camel_dict_copy):
    game = camelup.Game(3)
    game.camel_dict = camel_dict_copy
    return game


@pytest.mark.parametrize(
    "game_param,expected", [(2, 2), (3, 3), (4, 4)], indirect=["game_param"]
)
def test_gen_player_dict(game_param, expected):
    assert list(game_param.player_dict.keys()) == list(range(1, expected + 1))


def test_end_game(game):
    game.state = 1
    game.play_winner_card("red")
    game.play_winner_card("blue")
    game.play_winner_card("green")
    game.state = 3
    game.play_loser_card("red")
    game.play_winner_card("green")
    game.end_game()
    assert game.player_dict[1]["coins"] == 11
    assert game.player_dict[2]["coins"] == 5
    assert game.player_dict[3]["coins"] == 18


def test_end_round(game):
    game.tiles_dict = {1: 3}
    game.end_round()
    assert game.tiles_dict == dict()


def test_score_round(game):
    game.state = 1
    game.play_bet_tile("green")
    game.play_bet_tile("red")
    game.state = 3
    game.play_bet_tile("green")
    game.score_round()
    assert game.player_dict[1]["coins"] == 9
    assert game.player_dict[2]["coins"] == 5
    assert game.player_dict[3]["coins"] == 8


def test_available_moves(game):
    """
    14 * 2 tile placements
    5 bet tiles
    5 loser bets
    5 winner bets
    1 roll
    """
    assert len(game.available_moves()) == 44


def test_available_tile_placements(game):
    assert game.available_tile_placements() == list(range(3, 17))
    game.play_tile("block", 3)
    assert game.available_tile_placements() == list(range(5, 17))
    for space in list(range(3, 17)):
        game.play_tile("block", space)
    assert game.available_tile_placements() == list()


def test_play(game):
    game.state = 1
    game.play("self.play_tile('block', 5)")
    assert game.state == 2
    game.play("self.play_tile('block', 7)")
    assert game.state == 3
    game.play("self.play_tile('block', 9)")
    assert game.state == 1
    assert list(game.tiles_dict.keys()) == [5, 7, 9]


def test_play_tile(game):
    game.play_tile("block", 5)
    assert game.tiles_dict == {5: {"tile_type": "block", "player": 1}}


def test_play_winner_card(game):
    game.play_winner_card("red")
    assert game.winner_bets == [(1, "red")]


def test_play_loser_card(game):
    game.play_loser_card("red")
    assert game.loser_bets == [(1, "red")]


def test_play_bet_tile(game):
    game.play_bet_tile("red")
    assert game.player_dict[1]["bet_tiles"] == {"red": [5]}
    game.play_bet_tile("red")
    game.play_bet_tile("red")
    assert game.player_dict[1]["bet_tiles"] == {"red": [5, 3, 2]}
    assert "red" not in game.bet_tiles.keys()


def test_play_roll(game):
    game.state = 1
    game.play_tile("block", 3)
    game.play_roll("green", 1)
    assert game.player_dict[1]["coins"] == 7
    assert game.camel_dict["green"]["need_roll"] == False
    game.play_winner_card("green")
    game.play_roll("green", 17)
    assert game.player_dict[1]["coins"] == 16


def test_winner(game):
    assert game._winner(camel_dict) == {"green": 1, "blue": 2, "red": 3}
