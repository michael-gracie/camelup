# -*- coding: utf-8 -*-

"""Module with basic gameplay"""


import logging as logging


logger = logging.getLogger(__name__)


def move(camel_dict, tiles_dict, camel, roll):
    """Puting all the moves together

    Parameters
    ----------
    camel_dict : nested dict
        Dictionary with current camel positions
    tiles_dict : dict
        Dictonary with tiles information
    camel : str
        Name of camel that was rolled
    roll : int
        Roll on dice, ranges from 1 to 3

    Returns
    -------
    give_points : int
        The tile which was landed on and thusly should give points
    """
    camel_space = camel_dict[camel]["space"]
    camel_height = camel_dict[camel]["height"]
    min_height_movers, num_movers, movers = camels_to_move(
        camel_dict, camel_space, camel_height
    )
    destination = camel_space + roll
    block = False
    give_points = None
    if destination in tiles_dict.keys():
        if tiles_dict[destination]["tile_type"] == "skip":
            give_points = destination
            destination += 1
        elif tiles_dict[destination]["tile_type"] == "block":
            give_points = destination
            destination -= 1
            block = True
    max_height_dest, destinationers = camels_in_dest(camel_dict, destination)
    if block:
        block_move(
            camel_dict,
            movers,
            destinationers,
            destination,
            min_height_movers,
            num_movers,
        )
    else:
        reg_move(camel_dict, movers, destination, min_height_movers, max_height_dest)
    return give_points


def reg_move(camel_dict, movers, destination, min_height_movers, max_height_dest):
    """Executing a regular move

    Parameters
    ----------
    camel_dict : nested dict
        Dictionary with current camel positions
    movers : list
        List of camels that are moving
    destination : int
        Square where camels are moving
    min_height_movers : int
        The minimum height of the camels that are moving
    max_height_dest : int
        The max height of camels on the destination sqaure
    """
    for key, val in camel_dict.items():
        if key in movers:
            val["space"] = destination
            val["height"] = val["height"] - (min_height_movers - 1) + max_height_dest


def block_move(
    camel_dict, movers, destinationers, destination, min_height_movers, num_movers
):
    """Executing a move where the camel hit a block tile

    Parameters
    ----------
    camel_dict : nested dict
        Dictionary with current camel positions
    movers : list
        List of camels that are moving
    destinationers : list
        List of camels on the destination square
    destination : int
        Square where camels are moving
    min_height_movers : int
        The minimum height of the camels that are moving
    num_movers : int
        The number of camels moving
    """
    for key, val in camel_dict.items():
        if key in movers:
            val["space"] = destination
            val["height"] = val["height"] - (min_height_movers - 1)
        elif key in destinationers:
            val["height"] = val["height"] + num_movers


def camels_to_move(camel_dict, space, height):
    """Getting information about camels that need to move

    Parameters
    ----------
    camel_dict : nested dict
        Dictionary with current camel positions
    space : int
        Space the camel is on
    height : int
        Height of the camel

    Returns
    -------
    min_height_movers : int
        The minimum height of the camels that are moving
    num_movers : int
        The number of camels moving
    movers : list
        List of camels that are moving

    """
    min_height_movers = 10000
    num_movers = 0
    movers = []
    for key, val in camel_dict.items():
        if val["space"] == space and val["height"] >= height:
            if val["height"] < min_height_movers:
                min_height_movers = val["height"]
            num_movers += 1
            movers.append(key)
    return min_height_movers, num_movers, movers


def camels_in_dest(camel_dict, destination):
    """Find the camels in the destination square

    Parameters
    ----------
    camel_dict : nested dict
        Dictionary with current camel positions
    destination : int
        Square where camels are moving

    Returns
    -------
    max_height_dest : int
        The max height of camels on the destination sqaure
    destinationers : list
        List of camels on the destination square
    """
    max_height_dest = 0
    destinationers = []
    for key, val in camel_dict.items():
        if val["space"] == destination:
            if val["height"] > max_height_dest:
                max_height_dest = val["height"]
            destinationers.append(key)
    return max_height_dest, destinationers
