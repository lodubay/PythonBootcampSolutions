"""
This script prepares the Morse Code challenge message for each group.
"""
import os
import random

GROUPSIZE = 4 # number of students in each group


def main():
    filedir = os.path.dirname(__file__)
    # Read message file
    message = []
    with open(os.path.join(filedir, 'MESSAGE.txt'), 'r') as f:
        message = f.readlines()
    message = ''.join(message)
    # Split into randomly ordered segments
    segment_lengths = [int(len(message) / GROUPSIZE) for i in range(GROUPSIZE)]
    extra_length = len(message) % GROUPSIZE
    for i in range(extra_length):
        segment_lengths[i] += 1
    segments = [
        message[sum(segment_lengths[:i]):sum(segment_lengths[:i+1])] 
        for i in range(GROUPSIZE)
    ]
    # Enforce shuffled order that doesn't match original
    new_order = list(range(GROUPSIZE))
    while True:
        random.shuffle(new_order)
        if not all([new_order[i] == i for i in range(GROUPSIZE)]):
            break
    # Convert each segment to Morse code and write to file
    morse_key = import_key(os.path.join(filedir, 'KEY.txt'))
    for i, order in enumerate(new_order):
        coded_message = encode(segments[i], morse_key)
        fname = f'SEGMENT{order+1}.txt'
        with open(os.path.join(filedir, fname), 'w') as f:
            f.write(coded_message)
    # Test
    decoded_segments = []
    for order in new_order:
        coded_message = []
        fname = f'SEGMENT{order+1}.txt'
        with open(os.path.join(filedir, fname), 'r') as f:
            coded_message = f.readlines()
        coded_message = ''.join(coded_message)
        decoded_segments.append(decode(coded_message, morse_key))
    print(''.join(decoded_segments))


def import_key(fname):
    """
    Import the Morse Code key and convert it to a dictionary.

    Parameters
    ----------
    fname : str, optional
        Relative path to file containing the key.
    
    Returns
    -------
    dict
        Morse Code key (keys are letters and symbols, values are code)
    """
    # Read Morse Code key
    morse_key = {}
    with open(fname, 'r') as f:
        for l in f.readlines():
            key, val = l.split('\t')
            morse_key[key] = val.split('\n')[0]
    # Add a space between words
    morse_key[' '] = '/'
    return morse_key


def encode(message, key):
    """
    Encode the given message in Morse code.
    
    Parameters
    ----------
    message : str
        Message to encode.
    key : dict
        Morse Code key, with letters as keys and encodings as values.
    
    Returns
    -------
    str
        Encoded message, with letters separated by spaces and words by slashes.
    """
    # Clean message
    message = ' '.join(message.split('\n'))
    encoded = []
    for char in message:
        try:
            encoded.append(key[char.upper()])
        except KeyError:
            print(f'Warning: skipping untranslateable character "{char}".')
            continue
    return ' '.join(encoded)


def decode(encoded, key):
    """
    Decode the given encoded message in Morse Code.
    
    Parameters
    ----------
    encoded : str
        Encoded message, with letters separated by spaces and words by slashes.
    key : dict
        Morse code key, with letters as keys and encodings as values.
    
    Returns
    -------
    str
        Decoded message.
    """
    # Invert key
    inv_key = {v: k for k, v in key.items()}
    # Split message into letters
    letters = encoded.split(' ')
    decoded = []
    for letter in letters:
        try:
            decoded.append(inv_key[letter])
        except KeyError:
            print(f'Warning: untranslateable code "{letter}" will appear as "#".')
            decoded.append('#')
    return ''.join(decoded)


if __name__ == '__main__':
    main()
