# Blackjack Hand
class Hand:

    # Constructor for a Blackjack hand
    def __init__(self, firstCard: str, secondCard: str):
        self._cards = [firstCard, secondCard]
        self._bet = 0

    # Return the bet associated with the hand
    def get_bet(self) -> float:
        return self._bet

    # Set bet assocaited with the hand
    def set_bet(self, bet: float):
        self._bet = bet

    # Return cards in hand
    def get_cards(self) -> list:
        return self._cards

    # Set cards in hand
    def set_cards(self, firstCard: str, secondCard: str):
        self._cards = [firstCard, secondCard]

    # Add card to hand
    def add(self, card: str):
        self._cards.append(card)
