# -*- coding: utf-8 -*-

"""Main module."""

import logging
import random

from copy import deepcopy

import numpy as np
import pandas as pd

from camelup import config, gameplay
from camelup import utilities as util


logger = logging.getLogger(__name__)


class Game:
    """
    base class - doesn't initalize anything
    """

    def __init__(self, num_players):
        self.num_players = num_players
        self.camel_dict = dict()
        self._gen_camel_dict()
        self.player_dict = dict()
        self._gen_player_dict()
        self.tiles_dict = dict()
        self.bet_tiles = dict()
        self._gen_bet_tiles()
        self.winner_bets = []
        self.loser_bets = []
        self.state = 1

    def _gen_camel_dict(self):
        """Generates base camel dictionary
        """
        base = {"height": None, "space": None, "need_roll": True}
        for camel in config.CAMELS:
            self.camel_dict[camel] = base

    def _gen_player_dict(self):
        """Generates base player dictionary
        """
        base = {
            "winner_cards": config.CAMELS,
            "loser_cards": config.CAMELS,
            "tile": True,
            "coins": config.COINS,
            "bet_tiles": dict(),
        }
        for player in range(self.num_players):
            self.player_dict[player + 1] = base

    def _gen_bet_tiles(self):
        """Generates base bet tile configuration
        """
        base = [5, 3, 2]
        for camel in config.CAMELS:
            self.bet_tiles[camel] = base

    def end_game(self):
        """Ends the game
        1. Scores the round
        2. Scores the winner bets
        3. Scores the loser bets
        """
        self.score_round()
        order = list(self._winner(self.camel_dict.keys()))
        winner = order[0]
        loser = order[-1]
        rewards = config.BET_POINTS
        for bet in self.winner_bets:
            if bet[0] == winner:
                if rewards:
                    self.player_dict[bet[1]]["coins"] += rewards.pop(0)
                else:
                    self.player_dict[bet[1]]["coins"] += 1
            else:
                self.player_dict[bet[1]]["coins"] -= 1
        rewards = config.BET_POINTS
        for bet in self.loser_bets:
            if bet[0] == loser:
                if rewards:
                    self.player_dict[bet[1]]["coins"] += rewards.pop(0)
                else:
                    self.player_dict[bet[1]]["coins"] += 1
            else:
                self.player_dict[bet[1]]["coins"] -= 1
        pass

    def end_round(self):
        """The end of the round triggers the following
        1. Scores the tiles
        2. Resets the camels need_roll flag
        3. Returns the skip/block tile to the players hand
        4. Removes the bet tiles from the players hand
        5. Place the bet tiles back on the board
        """
        self.score_round()
        for val in self.camel_dict.values():
            val["need_roll"] = True
        self.tiles_dict = dict()
        for value in self.player_dict.values():
            val["tile"] = True
            val["bet_tiles"] = dict()
        self._gen_bet_tiles()

    def score_round(self):
        """Scores the round based on the tiles the players have and the position of camels.
        If the camel is in first then the player gets full points.
        If in second they get 1 point, else they lose a point
        """
        order = list(self._winner(self.camel_dict.keys()))
        for player in self.player_dict:
            tiles = player["bet_tiles"]
            for key, val in tiles.items():
                if key == order[0]:
                    self.player_dict[player]["coins"] += np.sum(val)
                if key == order[1]:
                    self.player_dict[player]["coins"] += np.count(val)
                else:
                    self.player_dict[player]["coins"] -= np.count(val)

    def available_moves(self):
        """Computes all the moves that are available.

        Returns
        -------
        list
            Moves available to play
        """
        moves = dict()
        for card in self.player_dict[self.state]["winner_cards"]:
            moves[f"Bet Game Winner {card}"] = f"self.play_winner_card({card})"
        for card in self.player_dict[self.state]["loser_cards"]:
            moves[f"Bet Game Loser {card}"] = f"self.play_loser_card({card})"
        for camel in self.bet_tiles:
            moves[
                f"Bet Round Winner {camel} - {self.bet_tiles[camel][0]} Points"
            ] = f"self.play_bet_tile({camel})"
        moves["Roll"] = "self.roll(camel, roll)"
        if self.player_dict[self.state]["tile"]:
            for spot in self.available_tiles_placements():
                moves[
                    f"Place Block Tile At {spot}"
                ] = f"self.play_tile('block', {spot})"
                moves[f"Place Skip Tile At {spot}"] = f"self.play_tile('skip', {spot})"
        return moves

    def play(self, move):
        """Play the move and update state

        Parameters
        ----------
        move : 'str'
            The move to play, formatted as a function
        """
        eval(move)
        self.state += 1
        if self.state > self.num_players:
            self.state = 1

    def available_tiles_placements(self):
        """Compute the available tiles

        Returns
        -------
        list
            List of available spaces of tiles

        """
        blocked = []
        for tile in self.tiles_dict.keys():
            blocked.append(tile)
            blocked.append(tile + 1)
            blocked.append(tile - 1)
        for camel in self.camel_dict.values():
            blocked.append(camel["space"])
        spots = list(range(1, 17))
        spaces = [spot for spot in spots if spot not in blocked & spot > min(blocked)]
        return spaces

    def play_tile(self, tile_type, space):
        """Play a skip or block tile

        Parameters
        ----------
        tile_type : str
            Type of tyle, either `block` or `skip`
        space : int
            The space to play the tile
        """
        self.player_dict[self.state]["tile"] = False
        self.tiles_dict[space] = {"tile_type": tile_type, "player": self.state}

    def play_winner_card(self, camel):
        """Play a winner card

        Parameters
        ----------
        camel : str
            The camel to bet on a win
        """
        self.player_dict[self.state]["winner_cards"].remove[camel]
        self.winner_bets.append((self.state, camel))

    def play_loser_card(self, camel):
        """Play a loser card

        Parameters
        ----------
        camel : str
            The camel to bet on a loss
        """
        self.player_dict[self.state]["loser_cards"].remove[camel]
        self.loser_bets.append((self.state, camel))

    def play_bet_tile(self, camel):
        """Play a bet tile

        Parameters
        ----------
        camel : str
            The camel to take a bet tile for
        """
        if self.bet_tiles[camel]:
            pop = self.bet_tiles[camel][0]
            util.add_list_to_dict(self.player_dict[self.state]["bet_tiles"], camel, pop)
            self.bet_tiles[camel].remove(pop)
        if self.bet_tiles[camel] == []:
            self.bet_tiles.pop(camel, None)

    def roll(self, camel, roll):
        """Moves the camel and updates scores based on a roll

        Parameters
        ----------
        camel : str
            Camel that is rolled
        roll : int
            The number that is rolled
        """
        gameplay.move(self.camel_dict, self.tiles_dict, camel, roll)
        self.player_dict[self.state]["coins"] += 1
        if self.camel_dict["camel"]["space"] > 16:
            self.end_game()

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
