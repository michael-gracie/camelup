#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `camelup` package."""

import pytest

from camelup import camelup


camel_dict = {
    "red": {"height": 1, "space": 1, "need_roll": True},
    "blue": {"height": 2, "space": 1, "need_roll": True},
    "green": {"height": 1, "space": 2, "need_roll": True},
}


@pytest.fixture
def game():
    game = camelup.Game()
    return game


def test_winner(game):
    assert game._winner(camel_dict) == {"green": 1, "blue": 2, "red": 3}
