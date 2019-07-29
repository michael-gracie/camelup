# -*- coding: utf-8 -*-

"""Main module."""

import logging
import random

from copy import deepcopy

import pandas as pd

from camelup import config, gameplay


logger = logging.getLogger(__name__)


class Game:
    """
    base class - doesn't initalize anything
    """

    def __init__(self, num_players):
        self.camel_dict = dict()
        self._gen_camel_dict()
        self.player_dict = dict()
        self._gen_player_dict()
        self.tiles_dict = dict()
        self.bet_tiles = dict()
        self._gen_bet_tiles()
        self.winner_bets = dict()
        self.loser_bets = dict()
        self.state = 1
        self.num_players = num_players

    def _gen_camel_dict(self):
        base = {"height": None, "space": None, "need_roll": True}
        for camel in config.CAMELS:
            self.camel_dict[camel] = base

    def _gen_player_dict(self):
        base = {
            "winner_cards": config.CAMELS,
            "loser_cards": config.CAMELS,
            "tile": True,
            "coins": config.COINS,
            "bet_tiles": None,
        }
        for player in range(self.num_players):
            self.player_dict[player + 1] = base

    def _gen_bet_tiles(self):
        base = [5, 3, 2]
        for camel in config.CAMELS:
            self.bet_tiles[camel] = base

    def play(self):
        pass

    def end_turn(self):

        pass

    def score_turn(self):
        order = self._winner(self.camel_dict)
        for player in self.player_dict:
            tiles = player["bet_tiles"]
            return order, tiles
        pass

    def available_moves(self):
        moves = dict()
        for card in self.player_dict[self.state]["winner_cards"]:
            moves[f"Bet Game Winner {card}"] = f"self.play_winner_card({card})"
        for card in self.player_dict[self.state]["loser_cards"]:
            moves[f"Bet Game Loser {card}"] = f"self.play_loser_card({card})"
        for camel in self.bet_tiles:
            moves[
                f"Bet Round Winner {camel} - {camel[0]} Points"
            ] = f"self.play_bet_tile({camel})"
        moves["Roll"] = "self.roll(roll)"
        return moves

    def play_tile(self, tile_type, space):
        self.player_dict[self.state]["tile"] = False
        self.tiles_dict[space] = {"tile_type": tile_type, "player": self.state}

    def play_winner_card(self, camel):
        self.player_dict[self.state]["winner_cards"].remove[camel]
        self.winner_bets["camel"] = self.state

    def play_loser_card(self, camel):
        self.player_dict[self.state]["loser_cards"].remove[camel]
        self.loser_bets["camel"] = self.state

    def play_bet_tile(self, camel):
        """
        Need to redo this so that a player can take multiple tiles
        """
        if self.bet_tiles[camel]:
            pop = self.bet_tiles[camel][0]
            self.player_dict[self.state]["bet_tiles"][camel] = pop
            self.bet_tiles[camel].remove(pop)
        if self.bet_tiles[camel] == []:
            self.bet_tiles.pop(camel, None)

    def roll(self, camel, roll):
        gameplay.move(self.camel_dict, self.tiles_dict, camel, roll)
        self.player_dict[self.state]["coins"] += 1

    def _winner(self, camel_dict):
        """
        Computes the places of camels in the race
        """
        return {
            camel: place + 1
            for place, camel in enumerate(
                sorted(
                    camel_dict,
                    key=lambda x: (-camel_dict[x]["space"], -camel_dict[x]["height"]),
                )
            )
        }

    def _turn(self, sim_dict, tiles):
        """
        Simulates a single turn
        """
        need_roll = [key for key in sim_dict.keys() if sim_dict[key]["need_roll"]]
        while need_roll:
            camel = random.choice(need_roll)
            roll = random.randint(1, 3)
            logger.info("The {0} camel rolled {1}".format(camel, roll))
            gameplay.move(sim_dict, self.tiles_dict, camel, roll)
            sim_dict[camel]["need_roll"] = False
            need_roll.remove(camel)
            if sim_dict[camel]["space"] > 16:
                return self._winner(sim_dict)

    def sim_turn(self, camel_dict, tiles):
        """
        Simulates a single turn
        """
        sim_dict = deepcopy(camel_dict)
        self._turn(sim_dict, tiles)
        return self._winner(sim_dict)

    def sim_game(self, camel_dict, tiles):
        """
        Simulates a single game
        """
        sim_tiles = deepcopy(tiles)
        sim_dict = deepcopy(camel_dict)
        while True:
            self._turn(sim_dict, sim_tiles)
            for key, value in sim_dict.items():
                value["need_roll"] = True
            sim_tiles = {}

    def turn_monte(self, camel_dict, tiles, iter=1000):
        """
        Runs monte carlo for the turn
        """
        result = pd.DataFrame(self.sim_turn(camel_dict, tiles), index=[0])
        for i in range(iter - 1):
            result = result.append(self._turn(camel_dict, tiles), ignore_index=True)
        return result

    def game_monte(self, camel_dict, tiles, iter=1000):
        """
        Runs monte carlo for the turn
        """
        result = pd.DataFrame(self.sim_game(camel_dict, tiles), index=[0])
        for i in range(iter - 1):
            result = result.append(self._turn(camel_dict, tiles), ignore_index=True)
        return result
