# A unit who plays during a Blackjack game
class BlackjackPlayer():

    # Constructor for a Blackjack player
    def __init__(self, buyIn: int=500.00, name: str="Player"):
        self._hands = []
        self._cash = buyIn
        self._name = name
        self._endTurn = False
        self._busted = False
        
    # Return players cash pool
    def get_cash(self) -> float:
        return self._cash

    # Set players cash pool
    def set_cash(self, cash: float):
        self._cash = cash

    # Add hand to player
    def add_hand(self, hand):
        self._hands.append(hand)

    # Get player hands
    def get_hands(self):
        return self._hands

    # Remove any hands player still has
    def clear_hands(self):
        self._hands = []

    # Gets player name
    def get_name(self):
        return self._name

    # Sets player name
    def set_name(self, name):
        self._name = name
    
    # Reset counter tracking if players turn is over
    def clear_turn(self):
        self._endTurn = False
        self._busted = False
        
    # End players turn
    def end_turn(self):
        self._endTurn = True

    # Return if the players turn is over
    def is_end_turn(self) -> bool:
        return self._endTurn
    
    # Set player to bust
    def bust_player(self):
        self._busted = True
    
    # Return if the player busted
    def is_busted(self) -> bool:
        return self._busted

# A dealer bot
class BlackjackDealer(BlackjackPlayer):

    # Constructor for a Blackjack dealer
    def __init__(self, buyIn, name):
        super().__init__(buyIn, name)

# A bot that plays against the dealer
class BlacjackPlayerBot(BlackjackPlayer):

    # Constructor for a Blackjack player bot
    def __init__(self, buyIn, name):
        super().__init__(buyIn, name)
        
# Check if the string is a valid int value
def is_integer(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False

