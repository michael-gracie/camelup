import collections
import logging as log


class GamePlay:
    """This class manages simple moves within Camel Up

    Attributes:
        camel_dict <nested dictions>: A dictionary of camel info
        camel <str>: The color of camel that is rolled
        roll <int>: The result of the roll
        tiles <dict>: A dictionary of where tiles are placed and what kind they are
    """

    def __init__(self, camel_dict, camel, roll, tiles):
        self.camel_dict = camel_dict
        self.camel = camel
        self.roll = roll
        self.tiles = tiles
        self._move()

    def _move(self):
        """
        Moves the camels the number of spaces needed. Take the space the camel
        is on and move all camels that may be on top of it.
        """
        self.temp_dict = collections.defaultdict(dict)
        camel_space = self.camel_dict[self.camel]["space"]
        camel_height = self.camel_dict[self.camel]["height"]

        for key, val in self.camel_dict.items():
            if val["space"] == camel_space and val["height"] < camel_height:
                self.temp_dict[key]["space"] = val["space"] + self.roll
        self.temp_dict[self.camel]["space"] = camel_space + self.roll

        if self.temp_dict[self.camel]["space"] in self.tiles.keys():
            if self.tiles[self.temp_dict[self.camel]["space"]] == "block":
                for key, val in self.temp_dict.items():
                    val["space"] = val["space"] - 1
                self._destHeightBlock()
                self._sourceHeight()
                log.info(
                    "Blocked: camel changes are the following:" + str(self.temp_dict)
                )
            elif self.tiles[self.temp_dict[self.camel]["space"]] == "skip":
                for key, val in self.temp_dict.items():
                    val["space"] = val["space"] + 1
                self._destHeight()
                self._sourceHeight()
                log.info(
                    "Skipped: camel changes are the following:" + str(self.temp_dict)
                )
        else:
            self._destHeight()
            self._sourceHeight()
            log.info("Regular: camel changes are the following:" + str(self.temp_dict))
        self.camel_dict = self._update(self.camel_dict, self.temp_dict)

    def _destHeight(self):
        """
        Calculates the appropriate height of camels on the desitination space
        """
        for key, val in self.camel_dict.items():
            if key not in self.temp_dict:
                if val["space"] == self.temp_dict[self.camel]["space"]:
                    self.temp_dict[key]["height"] = (
                        self.camel_dict[key]["height"]
                        + self.camel_dict[self.camel]["height"]
                    )

    def _sourceHeight(self):
        """
        Calculates the appropriate height of camels on the source space
        """
        for key, val in self.camel_dict.items():
            if key not in self.temp_dict:
                if (
                    val["space"] == self.camel_dict[self.camel]["space"]
                    and val["height"] > self.camel_dict[self.camel]["space"]
                ):
                    self.temp_dict[key]["height"] = (
                        self.camel_dict[key]["height"]
                        - self.camel_dict[self.camel]["height"]
                    )

    def _destHeightBlock(self):
        """
        Calculates the appropriate height of camels on the source space when a
        camel hits a block
        """
        heights = [
            val["height"]
            for key, val in self.camel_dict.items()
            if val["space"] == self.temp_dict[self.camel]["space"]
            and key not in self.temp_dict.keys()
        ]

        log.info("The heights on the block space is: %s" % (heights))

        for key, val in self.temp_dict.items():
            if heights:
                if val["space"]:
                    self.temp_dict[key]["height"] = (
                        max(heights) + self.camel_dict[key]["height"]
                    )

    def _update(self, d, u):
        """
        Updates a nested dict
        d and u are nested dicts
        """
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = self._update(d.get(k, {}), v)
            else:
                d[k] = v
        return d


def move(camel_df, tiles, camel, roll):
    space = camel_df.loc[camel]["space"]
    height = camel_df.loc[camel]["height"]
    movers = camels_to_move(camel_df, space, height)
    destination = space + roll

    if destination in tiles.index:
        tile_type = tiles.loc[destination]["tile_type"]
        if tile_type == "block":
            destination -= 1
            block_move(camel_df, movers, destination)
            return
        elif tile_type == "skip":
            destination += 1
            reg_move(camel_df, movers, destination)
            return
    else:
        reg_move(camel_df, movers, destination)
        return


def camels_to_move(camel_df, space, height):
    """
    """
    return camel_df.loc[
        camel_df["space"].eq(space) & camel_df["height"].gt(height - 0.000001)
    ].index


def camels_in_dest(camel_df, destination):
    """
    Returns camels in destination
    """
    return camel_df[camel_df["space"].eq(destination)].index


def reg_move(camel_df, movers, destination):
    """
    Regular move to a square
    """
    dest_camels = camels_in_dest(camel_df, destination)
    min_height_movers = camel_df.loc[movers]["height"].min()
    if dest_camels.empty:
        max_height_dest = camel_df.loc[dest_camels]["height"].max()
    else:
        max_height_dest = 0
    camel_df.loc[movers, "space"] = destination
    camel_df.loc[movers, "height"] = (
        camel_df.loc[movers, "height"] - (min_height_movers - 1) + max_height_dest
    )


def block_move(camel_df, movers, destination):
    """
    Block move to a square
    """
    dest_camels = camels_in_dest(camel_df, destination)
    min_height_movers = camel_df.loc[movers]["height"].min()
    num_movers = camel_df.loc[movers]["height"].index.sizeb
    camel_df.loc[movers]["space"] = destination
    camel_df.loc[movers]["height"] = camel_df.loc[movers]["height"] - (
        min_height_movers - 1
    )
    if dest_camels:
        camel_df.loc[dest_camels]["height"] = (
            camel_df.loc[dest_camels]["height"] + num_movers
        )
