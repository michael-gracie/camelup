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


def return_max_value(lst, index):
    """Given a list of lists, look at x index for each list and return the list with
    the max value at that index

    Parameters
    ----------
    lst : list of lists
        List of lists to select a list from
    index : int
        Index from which to evaluate

    Returns
    -------
    list
        Description of returned object.

    """
    flatten = list(map(lambda x: x[index], lst))
    max_index = flatten.index(max(flatten))
    return lst[max_index]
