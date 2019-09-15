# -*- coding: utf-8 -*-

"""Main module."""

import logging
import random

from copy import deepcopy

import numpy as np

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
            self.camel_dict[camel] = deepcopy(base)

    def _gen_player_dict(self):
        """Generates base player dictionary
        """
        base = {
            "game_cards": deepcopy(config.CAMELS),
            "tile": True,
            "coins": config.COINS,
            "bet_tiles": dict(),
            "name": "",
        }
        for player in range(self.num_players):
            self.player_dict[player + 1] = deepcopy(base)

    def _gen_bet_tiles(self):
        """Generates base bet tile configuration
        """
        base = [5, 3, 2]
        for camel in config.CAMELS:
            self.bet_tiles[camel] = deepcopy(base)

    def gen_camel_start(self):
        """Generates the start for the camel
        """
        need_place = [
            key
            for key in self.camel_dict.keys()
            if self.camel_dict[key]["space"] is None
        ]
        while need_place:
            camel = random.choice(need_place)
            roll = random.randint(1, 3)
            self.camel_dict[camel]["space"] = 0
            self.camel_dict[camel]["height"] = 0
            gameplay.move(self.camel_dict, self.tiles_dict, camel, roll)
            need_place = [
                key
                for key in self.camel_dict.keys()
                if self.camel_dict[key]["space"] is None
            ]

    def end_game(self):
        """Ends the game
        1. Scores the round
        2. Scores the winner bets
        3. Scores the loser bets
        """
        self.score_round()
        order = list(self._winner(self.camel_dict).keys())
        winner = order[0]
        loser = order[-1]
        rewards = deepcopy(config.BET_POINTS)
        for bet in self.winner_bets:
            if bet[1] == winner:
                if rewards:
                    self.player_dict[bet[0]]["coins"] += rewards.pop(0)
                else:
                    self.player_dict[bet[0]]["coins"] += 1
            else:
                self.player_dict[bet[0]]["coins"] -= 1
        rewards = deepcopy(config.BET_POINTS)
        for bet in self.loser_bets:
            if bet[1] == loser:
                if rewards:
                    self.player_dict[bet[0]]["coins"] += rewards.pop(0)
                else:
                    self.player_dict[bet[0]]["coins"] += 1
            else:
                self.player_dict[bet[0]]["coins"] -= 1
        return "Done"

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
        for val in self.player_dict.values():
            val["tile"] = True
            val["bet_tiles"] = dict()
        self._gen_bet_tiles()

    def score_round(self):
        """Scores the round based on the tiles the players have and the position of camels.
        If the camel is in first then the player gets full points.
        If in second they get 1 point, else they lose a point
        """
        order = list(self._winner(self.camel_dict).keys())
        for player, player_val in self.player_dict.items():
            for key, val in player_val["bet_tiles"].items():
                if key == order[0]:
                    self.player_dict[player]["coins"] += np.sum(val)
                elif key == order[1]:
                    self.player_dict[player]["coins"] += np.size(val)
                else:
                    self.player_dict[player]["coins"] -= np.size(val)

    def available_moves(self):
        """Computes all the moves that are available.

        Returns
        -------
        list
            Moves available to play
        """
        moves = dict()
        for card in self.player_dict[self.state]["game_cards"]:
            moves[f"Bet Game Winner {card}"] = f"self.play_winner_card('{card}')"
        for card in self.player_dict[self.state]["game_cards"]:
            moves[f"Bet Game Loser {card}"] = f"self.play_loser_card('{card}')"
        for camel in self.bet_tiles:
            moves[
                f"Bet Round Winner {camel} - {self.bet_tiles[camel][0]} Points"
            ] = f"self.play_bet_tile('{camel}')"
        moves["Roll"] = "self.play_roll(camel, roll)"
        if self.player_dict[self.state]["tile"]:
            for spot in self.available_tile_placements():
                moves[
                    f"Place Block Tile At {spot}"
                ] = f"self.play_tile('block', {spot})"
                moves[f"Place Skip Tile At {spot}"] = f"self.play_tile('skip', {spot})"
        return moves

    def available_moves_pruned(self):
        """Computes all the moves that are available, pruned for only moves that make sense.

        Can only bet on the top 2 and bottom the camels for the game.
        Can't place tiles that go past the farthest camel by 3 spaces.
        Can only bet on the top 3 camels for the turn

        Returns
        -------
        list
            Moves available to play
        """
        moves = dict()
        order = [*self._winner(self.camel_dict).keys()]
        for card in self.player_dict[self.state]["game_cards"]:
            if card in order[:2]:
                moves[f"Bet Game Winner {card}"] = f"self.play_winner_card('{card}')"
        for card in self.player_dict[self.state]["game_cards"]:
            if card in order[-2:]:
                moves[f"Bet Game Loser {card}"] = f"self.play_loser_card('{card}')"
        for camel in self.bet_tiles:
            if camel in order[0:3]:
                moves[
                    f"Bet Round Winner {camel} - {self.bet_tiles[camel][0]} Points"
                ] = f"self.play_bet_tile('{camel}')"
        moves["Roll"] = "self.play_roll(camel, roll)"
        if self.player_dict[self.state]["tile"]:
            for spot in self.available_tile_placements_pruned():
                moves[
                    f"Place Block Tile At {spot}"
                ] = f"self.play_tile('block', {spot})"
                moves[f"Place Skip Tile At {spot}"] = f"self.play_tile('skip', {spot})"
        return moves

    def available_tile_placements(self):
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
        spaces = [
            spot for spot in spots if (spot not in blocked) & (spot > min(blocked))
        ]
        return spaces

    def available_tile_placements_pruned(self):
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
        spaces = [
            spot
            for spot in spots
            if (spot not in blocked)
            & (spot > min(blocked))
            & (spot <= max(blocked) + 3)
        ]
        return spaces

    def play(self, move):
        """
        1. Plays the move
        2. Update state

        Parameters
        ----------
        move : 'str'
            The move to play, formatted as a function
        """
        output = eval(move)
        self.state += 1
        if self.state > self.num_players:
            self.state = 1
        return output

    def play_tile(self, tile_type, space):
        """Plays a skip or block tile

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
        self.player_dict[self.state]["game_cards"].remove(camel)
        self.winner_bets.append((self.state, camel))

    def play_loser_card(self, camel):
        """Play a loser card

        Parameters
        ----------
        camel : str
            The camel to bet on a loss
        """
        self.player_dict[self.state]["game_cards"].remove(camel)
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

    def play_roll(self, camel, roll):
        """
        1. Moves the camel
        2. Give points if camel landed on a block or skip tile
        3. Gives a point to the roller
        4. Updates needs roll
        5. Checks for end of game
        6. Checks for end of round

        Parameters
        ----------
        camel : str
            Camel that is rolled
        roll : int
            The number that is rolled
        """
        give_points = gameplay.move(self.camel_dict, self.tiles_dict, camel, roll)
        if give_points:
            tile_owner = self.tiles_dict[give_points]["player"]
            self.player_dict[tile_owner]["coins"] += 1
        self.player_dict[self.state]["coins"] += 1
        self.camel_dict[camel]["need_roll"] = False
        if self.camel_dict[camel]["space"] > 16:
            return self.end_game()
        if any([val["need_roll"] for val in self.camel_dict.values()]) is False:
            return self.end_round()

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
        tile_points = dict()
        while need_roll:
            camel = random.choice(need_roll)
            roll = random.randint(1, 3)
            logger.info("The {0} camel rolled {1}".format(camel, roll))
            give_points = gameplay.move(sim_dict, tiles, camel, roll)
            if give_points:
                tile_owner = tiles[give_points]["player"]
                util.add_value_dict(tile_points, tile_owner, 1)
            sim_dict[camel]["need_roll"] = False
            need_roll.remove(camel)
            if sim_dict[camel]["space"] > 16:
                return self._winner(sim_dict), tile_points
        return None, tile_points

    def sim_turn(self, camel_dict, tiles):
        """
        Simulates a single turn
        """
        sim_dict = deepcopy(camel_dict)
        tile_points = self._turn(sim_dict, tiles)[1]
        return self._winner(sim_dict), tile_points

    def sim_game(self, camel_dict, tiles):
        """
        Simulates a single game
        """
        sim_tiles = deepcopy(tiles)
        sim_dict = deepcopy(camel_dict)
        finished = None
        while finished is None:
            finished = self._turn(sim_dict, sim_tiles)[0]
            for key, value in sim_dict.items():
                value["need_roll"] = True
            sim_tiles = {}
        return finished

    def turn_monte(self, camel_dict, tiles_dict, iter=1000):
        """
        Runs monte carlo for the turn
        """
        winner, tile_points = self.sim_turn(camel_dict, tiles_dict)
        winner_result = [*winner.items()]
        tile_points_result = [*tile_points.items()]
        for i in range(iter - 1):
            winner, tile_points = self.sim_turn(camel_dict, tiles_dict)
            winner_result.extend([*winner.items()])
            tile_points_result.extend([*tile_points.items()])
        return (
            np.array(winner_result, dtype=[("camel", "U6"), ("place", float)]),
            np.array(tile_points_result, dtype=[("player", float), ("points", float)]),
        )

    def game_monte(self, camel_dict, tiles_dict, iter=1000):
        """
        Runs monte carlo for the turn
        """
        result = [*self.sim_game(camel_dict, tiles_dict).items()]
        for i in range(iter - 1):
            result.extend([*self.sim_game(camel_dict, tiles_dict).items()])
        return np.array(result, dtype=[("camel", "U6"), ("place", float)])
