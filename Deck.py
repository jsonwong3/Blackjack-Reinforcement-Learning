from random import shuffle
# Standard 52-Card Deck
class Deck:

    suits = ['Diamonds', 'Hearts', 'Spades', 'Clubs']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
              'Jack', 'Queen', 'King', 'Ace']
    
    # Constructor for a deck of the given size
    def __init__(self, size: int=1):
        self._deck = []
        self._suits = ['Diamonds', 'Hearts', 'Spades', 'Clubs']
        self._values = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
                        'Jack', 'Queen', 'King', 'Ace']        
        for i in range(0, size):
            # Add the requested amount of cards into the list
            for value in self._values:
                for suit in self._suits:
                    self._deck.append((value + ' of ' + suit))
        self.sort()
        
    # Return playing card deck
    def get_deck(self) -> list:
        return self._deck
    
    # Pop the first card in the deck
    def draw(self) -> str:
        if self.size != 0:
            return self._deck.pop(0)

    # Remove card from deck
    def remove(self, value: str, suit: str=None):
        # If the suit is not given, remove the first card which
        # holds the given numberic value
        # If the suit is given, remove the first card which holds
        # both the given numberic value and suit value
        if suit is None:
            removed = False
            i = 0
            while (not(removed) and i < self.size()):
                if self._deck[i].startswith(value):
                    self._deck = self._deck[:i] + self._deck[i+1:]
                    removed = True
                else:
                    i += 1
        else:
            self._deck.remove((value + ' of ' + suit))

   # Shuffle the deck
    def shuffle_deck(self):
        shuffle(self._deck)

    # Return size of deck
    def size(self) -> int:
        return len(self._deck)
    
    # Sort the deck via bubble sort
    def sort(self):
        self._values = {'1': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

        # Use bubble sort to sort deck
        for i in range(len(self._deck)-1,0,-1):
            for j in range(i):
                # Find numberic value of each card
                if self._deck[j][0] in self._values:
                    first = self._values[self._deck[j][0]]
                else:
                    first = int(self._deck[j][0])

                if self._deck[j+1][0] in self._values:
                    second = self._values[self._deck[j+1][0]]
                else:
                    second = int(self._deck[j+1][0])

                # Swap positions of cards if the second card
                # is less than the first
                if first > second:
                    temp = self._deck[j]
                    self._deck[j] = self._deck[j+1]
                    self._deck[j+1] = temp
