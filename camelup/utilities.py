import numpy as np


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


def add_value_dict(dct, key, value):
    """Function add a value to a the value of a dictionary if it exists if not, set to values

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
        dct[key] += value
    else:
        dct[key] = value


def numpy_group_by_sum(array, index, sum_col):
    unique_groups = np.unique(array[index])
    sums = []
    for group in unique_groups:
        sums.append((group, array[array[index] == group][sum_col].sum()))
    return np.array(sums, dtype=[(f"{index}", float), (f"{sum_col}", float)])


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
