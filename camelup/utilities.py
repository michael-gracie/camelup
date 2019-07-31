def add_list_to_dict(dct, key, value):
    """Function to create a dictionary where the values are lists and append to that list

    Parameters
    ----------
    dct : dictionary
        Dictionary with values as lists
    key : object
        Key for the dictionary
    value : object
        Value to add to the list
    """
    if key in dct.keys():
        dct[key].append(value)
    else:
        dct[key] = [value]
