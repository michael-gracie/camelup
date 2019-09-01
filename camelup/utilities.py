import ast
import inspect
import re

from io import StringIO

import numpy as np


def parse_dump(string):
    """Gets information from the AST dump and return the AST object and the id

    Parameters
    ----------
    string : str
        Tree to extract the id for

    Returns
    -------
    str
        A string with the object and name info

    """
    re1 = "id='(.*?)',"
    return string.split("(")[0] + " - " + re.search(re1, string).group(1)


def create_benchmark_func(tree, performance):
    """Creating a benchmark function named benchmark_`func`

    Parameters
    ----------
    tree : str
        AST for function to create benchmark function for
    performance : dict
        Dictionary to capture function

    Returns
    -------
    str :
        Tree of the benchmark function

    """
    t = 0
    new_first_layer = list()
    for node in tree.body[0].body:
        if node.__class__ != ast.Return:
            node_dump = ast.dump(node)
            parsed_dump = parse_dump(node_dump)
            performance[parsed_dump] = list()
            start_time = ast.parse(f"t{t} = time()").body[0]
            t += 1
            end_time = ast.parse(f"t{t} = time()").body[0]
            dif = ast.parse(f"performance['{parsed_dump}'].append(t{t}-t{t-1})").body[0]
            new_first_layer.extend([start_time, node, end_time, dif])
            t += 1
        else:
            new_first_layer.extend([node])
    tree.body[0].body = new_first_layer
    tree.body[0].name = f"benchmark_{tree.body[0].name}"
    return tree


def benchmark(func, iteration, *args, **kwargs):
    """Full function to create a run benchmark that benchmarks each statement in a function

    Parameters
    ----------
    func : function
        Function to benck
    iteration : int
        Number of interation
    *args : str
        Arguments to pass to funcion
    **kwargs : str
        Keyword arguments to pass to function

    Returns
    -------
    dict
        Dictionary with the performance results

    """
    func_str = inspect.getsource(func)
    tree = ast.parse(StringIO(func_str).read())
    global performance
    performance = dict()
    exec(
        compile(create_benchmark_func(tree, performance), filename="<ast>", mode="exec")
    )
    print(ast.dump(tree))
    for i in range(iteration):
        args_str = ", ".join(args)
        kwargs_str = ", ".join("%s=%r" % x for x in kwargs.items())
        print(f"benchmark_{func.__name__}({args_str+kwargs_str})")
        eval(f"benchmark_{func.__name__}({args_str+kwargs_str})")
    return performance


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
