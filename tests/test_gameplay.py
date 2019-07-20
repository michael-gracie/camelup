"""Tests for gameplay"""

from copy import deepcopy

import pytest

from camelup import gameplay


camel_dict = {
    "red": {"height": 1, "space": 1, "need_roll": True},
    "blue": {"height": 2, "space": 1, "need_roll": True},
    "green": {"height": 1, "space": 3, "need_roll": True},
    "yellow": {"height": 1, "space": 4, "need_roll": True},
    "white": {"height": 2, "space": 4, "need_roll": True},
}

tiles_dict = {5: "block", 2: "skip"}


@pytest.fixture
def camel_dict_copy():
    return deepcopy(camel_dict)


to_move = [
    (4, 2, (2, 1, ["white"])),
    (4, 1, (1, 2, ["white", "yellow"])),
    (3, 1, (1, 1, ["green"])),
]


@pytest.mark.parametrize("space,height,expected", to_move)
def test_camels_to_move(space, height, expected):
    assert gameplay.camels_to_move(camel_dict, space, height)[0] == expected[0]
    assert gameplay.camels_to_move(camel_dict, space, height)[1] == expected[1]
    assert (
        gameplay.camels_to_move(camel_dict, space, height)[2].sort()
        == expected[2].sort()
    )


in_dest = [(4, (2, ["white", "yellow"])), (3, (1, ["green"])), (2, (0, []))]


@pytest.mark.parametrize("destination,expected", in_dest)
def test_camels_in_dest(destination, expected):
    assert gameplay.camels_in_dest(camel_dict, destination)[0] == expected[0]
    assert (
        gameplay.camels_in_dest(camel_dict, destination)[1].sort() == expected[1].sort()
    )


def test_block_move_reg(camel_dict_copy):
    gameplay.block_move(camel_dict_copy, ["red", "blue"], ["white", "yellow"], 4, 1, 2)
    assert camel_dict_copy["white"]["space"] == 4
    assert camel_dict_copy["yellow"]["space"] == 4
    assert camel_dict_copy["blue"]["space"] == 4
    assert camel_dict_copy["red"]["space"] == 4
    assert camel_dict_copy["white"]["height"] == 4
    assert camel_dict_copy["yellow"]["height"] == 3
    assert camel_dict_copy["blue"]["height"] == 2
    assert camel_dict_copy["red"]["height"] == 1


def test_block_move_same_square(camel_dict_copy):
    gameplay.block_move(
        camel_dict_copy, ["white", "yellow"], ["white", "yellow"], 4, 1, 2
    )
    assert camel_dict_copy["white"]["space"] == 4
    assert camel_dict_copy["yellow"]["space"] == 4
    assert camel_dict_copy["white"]["height"] == 2
    assert camel_dict_copy["yellow"]["height"] == 1


def test_block_move_same_square_only_one(camel_dict_copy):
    gameplay.block_move(camel_dict_copy, ["white"], ["white", "yellow"], 4, 2, 1)
    assert camel_dict_copy["white"]["space"] == 4
    assert camel_dict_copy["yellow"]["space"] == 4
    assert camel_dict_copy["white"]["height"] == 1
    assert camel_dict_copy["yellow"]["height"] == 2


def test_block_move_open_square(camel_dict_copy):
    gameplay.block_move(camel_dict_copy, ["white"], [], 5, 2, 1)
    assert camel_dict_copy["white"]["space"] == 5
    assert camel_dict_copy["white"]["height"] == 1


def test_reg_move_reg_square(camel_dict_copy):
    gameplay.reg_move(camel_dict_copy, ["red", "blue"], 4, 1, 2)
    assert camel_dict_copy["blue"]["space"] == 4
    assert camel_dict_copy["red"]["space"] == 4
    assert camel_dict_copy["blue"]["height"] == 4
    assert camel_dict_copy["red"]["height"] == 3


def test_reg_move_open_square(camel_dict_copy):
    gameplay.reg_move(camel_dict_copy, ["blue"], 2, 2, 0)
    assert camel_dict_copy["blue"]["space"] == 2
    assert camel_dict_copy["blue"]["height"] == 1


def test_move_with_block(camel_dict_copy):
    gameplay.move(camel_dict_copy, tiles_dict, "red", 4)
    assert camel_dict_copy["white"]["space"] == 4
    assert camel_dict_copy["yellow"]["space"] == 4
    assert camel_dict_copy["blue"]["space"] == 4
    assert camel_dict_copy["red"]["space"] == 4
    assert camel_dict_copy["white"]["height"] == 4
    assert camel_dict_copy["yellow"]["height"] == 3
    assert camel_dict_copy["blue"]["height"] == 2
    assert camel_dict_copy["red"]["height"] == 1


def test_move_with_skip(camel_dict_copy):
    gameplay.move(camel_dict_copy, tiles_dict, "blue", 1)
    assert camel_dict_copy["blue"]["space"] == 3
    assert camel_dict_copy["blue"]["height"] == 2
