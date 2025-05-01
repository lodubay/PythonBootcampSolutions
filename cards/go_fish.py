"""
This file contains code for the game "Go Fish" which uses the cards module.
"""

import time
import cards
from utils import clear_terminal, mc_input, int_input

def main():
    clear_terminal()
    print('Welcome to Go Fish!\n')
    nplayers = int_input('Number of players [2-6]: ', (2, 6))
    # Set up
    drawpile = cards.deck(shuffled=True)
    hsize = handsize(nplayers)
    players = []
    print('')
    for i in range(nplayers):
        name = input('Player %d name [optional]: ' % (i+1))
        players.append(Player(drawpile, i, name=name, handsize=hsize))
    # Fluff
    print('\nShuffling the deck...')
    time.sleep(1)
    print(f'Dealing {hsize} cards to each player...')
    time.sleep(1)
    input(f'{players[0].name} will go first. Pass to {players[0].name}. [Enter] ')
    # Turns: play until all cards in books
    # Public info: requests and results, number of cards in hand, number of books taken
    clear_terminal()
    turn = 0 # current turn (always increases)
    while sum([p.score for p in players]) < 13:
        # Each player's turn: 
        order = turn % nplayers # current player order (cyclical)
        p = players[order]
        next_player = players[(turn + 1) % nplayers]
        opponents = [p for p in players if p.order != order]
        # 0. if out of cards, draw a card (if any cards remain in the deck)
        if p.hand.size == 0:
            print('You are out of cards.')
            if drawpile.size > 0:
                print('Drawing 1.')
                p.hand.single_draw(drawpile)
            else:
                print('The draw pile is empty. Skipping your turn.')
                continue
        p.print_status()
        # Summarize other player info
        print('\nOpponents:')
        for p2 in opponents:
            print(f'\t{p2.name} has {p2.hand.size} cards in hand and {p2.score} book(s).')
        # 1. choose a card to request and another player to request from
        # List of valid cards to request
        valid_requests = list(set([c.value for c in p.hand.cards]))
        valid_requests.sort()
        fishval = valid_requests[mc_input(
            '\nWhich card would you like to fish for?',
            [repr_value(v) + 's' for v in valid_requests]
        )]
        if nplayers > 2:
            p2 = opponents[mc_input(
                '\nWhich player would you like to ask?', 
                [p.name for p in opponents]
            )]
        else:
            p2 = opponents[0]
        # 2. ask that player if they have any cards of a particular rank
        card_request = p.request_card(p2, fishval)
        # 3a. if yes, other player hands over all cards of that rank. go again.
        if card_request:
            print('Go again!')
            time.sleep(1)
        # 3b. if no, "go fish!" and player draws a card. 
        else:
            time.sleep(1)
            if drawpile.size > 0:
                p.hand.single_draw(drawpile)
                card_drawn = p.hand.cards[-1]
                print('You drew:', card_drawn)
            # 4a. if it's not the card you want, pass to the next player.
                if card_drawn.value == fishval:
                    print('Go again!')
                    time.sleep(1)
                else:
                    turn += 1
                    input(f'Pass to {next_player.name}. [Enter]')
                    clear_terminal()
                    print(f'Pass to {next_player.name} now!')
                    time.sleep(2)
                    clear_terminal()
            else:
                turn += 1
                input(f'The drawpile is empty. Pass to {next_player.name}. [Enter]')
                clear_terminal()
                print(f'Pass to {next_player.name} now!')
                time.sleep(2)
                clear_terminal()
        # 4b. if it is the card you want, go again
        p.check_for_books()
    # Tally the scores
    scores = [p.score for p in players]
    print('\nThe scores at the end of the game are:')
    for p in players:
        print(f'\t{p.name}: {p.score}')
    winner = players[scores.index(max(scores))]
    print(f'{winner.name} wins!!!')


class Player:
    """
    An object representing a player. Contains hand and played instances.

    Attributes
    ----------
    order : int
        Player turn order.
    name : str
        Player name.

    Parameters
    ----------
    deck : cards.deck instance
        The deck of playing cards from which the player draws.
    order : int
        Player turn order, zero-indexed. Cannot be changed.
    name : str, optional
        Player name. If none is given, defaults to "player<order+1>".
    handsize : int, optional
        Starting size of the player's hand.
    
    """
    def __init__(self, deck, order, name='', handsize=5):
        self._order = order
        if name == '':
            name = 'Player %d' % (order+1)
        self.name = name
        self.hand = cards.hand.fromdeck(deck, handsize)
        self.played = cards.played()
    
    def check_for_books(self):
        """
        Check the player's hand for books (sets of 4 of a kind).
        """
        has_book = False
        for i, card in enumerate(self.hand.cards):
            same_value = [c for c in self.hand.cards if c.value == card.value]
            if len(same_value) == 4:
                has_book = True
                print('You got a book!', same_value)
                for svc in same_value:
                    self.hand.single_discard(self.played, self.hand.cards.index(svc))
                break # assume only 1 book per
        return has_book
    
    def give_card(self, other, index):
        """
        Give a card at the specified index to another player.
        
        Parameters
        ----------
        other : Player instance
            The other player to give the card to.
        index : int
            Index of the card to give to the other player.
        """
        if isinstance(other, Player):
            other.hand.cards.append(self.hand.cards[index])
            del self.hand._cards[index]
        else:
            raise TypeError("Parameter ``other`` must be an instance of ``Player``. Got: %s" % type(other))

    def request_card(self, other, value):
        """
        Request a card of the given face value from another player.
        
        Parameters
        ----------
        other : Player instance
            Another player instance to request from.
        value : int
            Card face value to request, range 2 - 14.
        
        Returns
        -------
        bool
            Whether or not the request was successful.
        """
        if isinstance(other, Player):
            matching_cards = []
            # while loop to avoid skipping indices
            i = 0
            while i < other.hand.size:
                if other.hand.cards[i].value == value:
                    matching_cards.append(other.hand.cards[i])
                    other.give_card(self, i)
                else:
                    i += 1
            if len(matching_cards) > 0:
                print('%s gave you: %s' % (other.name, matching_cards))
                return True
            else:
                print('Go fish!')
                return False
        else:
            raise TypeError("Parameter ``other`` must be an instance of ``Player``. Got: %s" % type(other))
    
    def print_status(self):
        """
        Print the current state of the player's hand and score to the terminal.
        """
        print('\nCurrent player:', self.name)
        print('\tHand:', self.ordered_hand)
        print('\tScore: %s' % self.score, self.books)

    @property
    def ordered_hand(self):
        """
        Re-order the player's hand by value.
        """
        ordered_cards = []
        for i in range(2, 15):
            ordered_cards += [c for c in self.hand.cards if c.value == i]
        return ordered_cards
    
    @property
    def books(self):
        """
        Type: list
            List of books (four of a kind) which the player has won.
        """
        books = []
        # Assume no cards have been played that aren't books,
        # and that self.played.cards are in order
        for card in self.played.cards[::4]:
            books.append(f'{card.value}s')
        return books
    
    @property
    def score(self):
        """
        Type: int
            The player's score, equal to the number of books won.
        """
        return len(self.books)

    @property
    def order(self):
        """
        Type: int
            Player's order in a round (0-indexed). Cannot be changed.
        """
        return self._order
    
    @property
    def name(self):
        """
        str
            Player's name.
        """
        return self._name
    
    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise TypeError("Name must be a string. Got: %s" % type(value))


def handsize(nplayers):
    """
    Determine the starting size of a hand for a given number of players.

    Parameters
    ----------
    nplayers : int
        Number of players in the game.

    Returns
    -------
    int
        Number of cards in a starting hand.
    """
    if nplayers <= 3 and nplayers >= 2:
        return 7
    elif nplayers <= 6 and nplayers >= 2:
        return 5
    else:
        raise ValueError("Number of players must be between 2 and 6.")


def repr_value(value):
    """
    Convert integer card value to a human-readable string.
    
    Parameters
    ----------
    value : int
        Card value, between 2 and 14.
    
    Returns
    -------
    str
        String representation of the card value.
    """
    if value == 11: 
        repr = "Jack" 
    elif value == 12: 
        repr = "Queen" 
    elif value == 13: 
        repr = "King"
    elif value == 14: 
        repr = "Ace" 
    elif value >= 2 and value <= 10: 
        repr = str(value)
    else:
        raise ValueError("Expected a value between 2 and 14.")
    return repr


if __name__ == '__main__':
    main()