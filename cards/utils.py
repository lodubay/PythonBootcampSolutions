"""
This file contains utility methods.

Contents
--------
"""

import os


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def mc_input(text, options):
    """
    Request a user input from the given list of options.
    
    Parameters
    ----------
    text : str
        First line of text requesting user input.
    options : list of strings
        List of options for responses (not enumerated).
    
    Returns
    -------
    int
        Index of option chosen (0-indexed).
    """
    options = [f'\t({i+1}) ' + option for i, option in enumerate(options)]
    fulltext = '\n'.join([text] + options + ['Your choice: '])
    return int_input(fulltext, range=(1, len(options))) - 1


def int_input(text, range=None):
    """
    Request an integer input, optionally in a given range.
    
    Parameters
    ----------
    text : str
        Text to present to user with input request.
    range : tuple of ints, optional
        Range of values to accept, inclusive, if not None. The default is None.
    
    Returns
    -------
    int
        Integer response from user.
    """
    while True:
        try:
            response = int(input(text))
            if range is not None:
                if response < range[0] or response > range[1]:
                    raise ValueError
            break
        except ValueError:
            message = 'Invalid input. Expected an integer'
            if range is None:
                message += '.'
            else:
                message += ' in the range %d - %d.' % range
            print(message)
    return response
