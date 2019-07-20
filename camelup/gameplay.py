import logging as logging


logger = logging.getLogger(__name__)


def move(camel_dict, tiles_dict, camel, roll):
    camel_space = camel_dict[camel]["space"]
    camel_height = camel_dict[camel]["height"]
    min_height_movers, num_movers, movers = camels_to_move(
        camel_dict, camel_space, camel_height
    )
    destination = camel_space + roll
    block = False
    if destination in tiles_dict.keys():
        if tiles_dict[destination] == "skip":
            destination += 1
        elif tiles_dict[destination] == "block":
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


def reg_move(camel_dict, movers, destination, min_height_movers, max_height_dest):
    """
    Regular move to a square
    """
    for key, val in camel_dict.items():
        if key in movers:
            val["space"] = destination
            val["height"] = val["height"] - (min_height_movers - 1) + max_height_dest


def block_move(
    camel_dict, movers, destinationers, destination, min_height_movers, num_movers
):
    """
    Block move to a square
    """
    for key, val in camel_dict.items():
        if key in movers:
            val["space"] = destination
            val["height"] = val["height"] - (min_height_movers - 1)
        elif key in destinationers:
            val["height"] = val["height"] + num_movers


def camels_to_move(camel_dict, space, height):
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
    max_height_dest = 0
    destinationers = []
    for key, val in camel_dict.items():
        if val["space"] == destination:
            if val["height"] > max_height_dest:
                max_height_dest = val["height"]
            destinationers.append(key)
    return max_height_dest, destinationers
