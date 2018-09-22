from random import shuffle as shuffle
import time as time
from os import system, name

def clear():
    # For windows
    if name == 'nt':
        _ = system('cls')
    # For mac and linux
    else:
        _ = system('clear')

class Deck():

    def __init__(self, deck: int=1):  # Fill deck with playing cards
        # Initalize card text
        self._deck = []
        self._suits = ['Diamonds',
                       'Hearts',
                       'Spades',
                       'Clubs']
        self._values = ['Ace',
                        '2', '3', '4', '5', '6', '7', '8', '9', '10',
                        'Jack',
                        'Queen',
                        'King']
        for i in range(0, deck):
            # Add the requested amount of cards into the list
            for value in self._values:
                for suit in self._suits:
                    self._deck.append((value + ' of ' + suit))
        self.sort()

    def get_deck(self) -> list:  # Return playing card deck
        return self._deck

    def draw(self) -> str:  # Pop the first card in the deck
        if self.size != 0:
            return self._deck.pop(0)

    def remove(self, value: str, suit: str=None):  # Remove card from deck
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

    def shuffle(self):  # Shuffle the deck
        shuffle(self._deck)

    def size(self) -> int:  # Return size of deck
        return len(self._deck)

    def sort(self): # Sort the deck
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

class Blackjack():

    # BUG: Bet will double if player holds jack?
    class Hand():

        def __init__(self, firstCard: str, secondCard: str):  # Initalize cards in hand
            self._cards = [firstCard, secondCard]
            self._bet = 0
            self._isBust = False

        def get_bet(self) -> float:  # Return the bet associated with the hand
            return self._bet

        def set_bet(self, bet: float):  # Set bet assocaited with the hand
            self._bet = bet

        def get_cards(self) -> list:  # Return cards in hand
            return self._cards

        def set_cards(self, firstCard: str, secondCard: str):  # Set cards in hand
            self._cards = [firstCard, secondCard]

        def get_isBust(self) -> bool:  # Return whether the hand is a bust or not
            return self._isBust

        def set_isBust(self, state: bool):  # Set whether the hand is a bust or not
            self._isBust = state

        def add(self, card: str):  # Add card to hand
            self._cards.append(card)

    def __init__(self, buyIn: float=500.00): # Initalize game client
        self._deck = Deck()
        self._plyrCash = buyIn
        self._inProgress = True
        self._shuffIntrvl = 0
        self._shuffRate = 5

        # Continues to loop until player exits program
        while(self._inProgress):
            # --- Player Bet ---
            # Prompt player for a bet
            clear()
            self._bet = input('User Cash Pool: $' + str(self._plyrCash) + '\nPlace bet: ')

            # If player entered key word 'exit', program will close
            if self._bet == 'exit':
                print('\nLeaving Blackjack Game\n')
                self._inProgress = False
                break

            # Check if user entered a valid float value
            if (self.isFloat(self._bet) and (float(self._bet) <= self._plyrCash)):
                # --- Shuffling Deck ---
                # Reshuffle deck according to the interval
                if self._shuffIntrvl == 0:
                    # Inform user dealer is shuffling deck
                    print('\nShuffling Deck')
                    time.sleep(1.25)
    
                    # Shuffle Deck
                    self._shuffIntrvl = self._shuffRate
                    self._deck = Deck()
                    self._deck.shuffle()
                else:
                    self._shuffIntrvl -= 1

                # --- Player's Turn ---
                # Start the dealing process
                self._plyrTrn = True
                surrender = False
                self.deal()

                # Continue players turn until they bust or they stand
                while(self._plyrTrn):
                    # Prompt player for actions
                    command = input('\n1) Stand\n2) Hit\n3) Double\n4) Split\n5) Surrender\n6) Clear Screen\n')
                    bustCount = 0

                    # Queue aciton prompted by player
                    if command == '1':
                        # End the players turn
                        self._plyrTrn = False
                    elif command == '2':
                        # Hits the player with an extra card

                        # If the player has more than one hand,
                        # prompt the player to pick which hand
                        if not(len(self._plyrHnd) == 1):
                            # Prompt player for hand index
                            hand_num = input('\nPick which hand to hit\n')

                            # Check for a valid input
                            if (hand_num.isdigit() and
                                (int(hand_num) <= len(self._plyrHnd))):
                                # Ensures player cannot hit a busted hand
                                if not(self._plyrHnd[int(hand_num)-1].get_isBust()):
                                    # Deal an extra card to the desired hand
                                    self.draw(self._plyrHnd, int(hand_num)-1)
                                else:
                                    print('\nPlayer cannot hit a busted hand')
                            else:
                                print('\nInvalid input')
                        else:
                            self.draw(self._plyrHnd, 0)

                        # Update the value of each hand and determind whether it is busted
                        for hand in self._plyrHnd:
                            if (self.calcHand(hand.get_cards()) > 21):
                                hand.set_isBust(True)
                                bustCount += 1

                        # End players turn if all hands are busted
                        if bustCount == len(self._plyrHnd):
                            self._plyrTrn = False
                    elif command == '3':
                        # Double the players bet and end their turn with a single extra card

                        # Ensures player can only double down with their starting hand
                        if ((len(self._plyrHnd) == 1) and (len(self._plyrHnd[0].get_cards()) == 2)):
                            if (self._plyrHnd[0].get_bet() * 2 <= self._plyrCash):
                                # Double their bet, deal a card and end their turn
                                self._plyrHnd[0].set_bet(self._plyrHnd[0].get_bet() * 2)
                                self.draw(self._plyrHnd, 0)
                                self._plyrTrn = False
                                
                                # Update the value of each hand and determind whether it is busted
                                for hand in self._plyrHnd:
                                    if (self.calcHand(hand.get_cards()) > 21):
                                        hand.set_isBust(True)
                                        bustCount += 1
        
                                # End players turn if all hands are busted
                                if bustCount == len(self._plyrHnd):
                                    self._plyrTrn = False
                            else:
                                print('\nPlayer does not have enough cash to double down')
                        else:
                            print('\nDouble down is only available when dealt the inital two cards')
                    elif command == '4':
                        # Split the players hand into two

                        # Ensures player can only split with their starting hand
                        if ((len(self._plyrHnd) == 1) and (len(self._plyrHnd[0].get_cards()) == 2)):
                            # Check whether the two cards are the same
                            if ((self._plyrHnd[0].get_cards()[0] == self._plyrHnd[0].get_cards()[1]) and
                                (self._plyrHnd[0].get_bet() * 2 <= self._plyrCash)):
                                # Split players hand into two and deal an extra card to both hands

                                # Draw extra cards to deal
                                dealCard = [self._deck.draw(), self._deck.draw()]
                                tempCard = self._plyrHnd[0].get_cards().pop()

                                # Distribute cards to the new hands
                                self._plyrHnd[0].add(dealCard[0][:self.index(dealCard[0])])
                                self._plyrHnd.append(self.Hand(tempCard, dealCard[1][:self.index(dealCard[1])]))
                                self._plyrHnd[1].set_bet(self._plyrHnd[0].get_bet())

                                self.dsplyPlyr()
                            else:
                                print('\nPlayer cannot split the current hand')
                        else:
                            print('\nSpliting is only available when dealt the inital two cards')
                    elif command == '5':
                        # Allow the player to forfeit with the cost of half their bet

                        # Ensure player can only surrender with their starting hand
                        if (len(self._plyrHnd) == 1) and (len(self._plyrHnd[0].get_cards()) == 2):
                            # Half the bet and mark the round as surrendered
                            self._plyrHnd[0].set_bet(round(self._plyrHnd[0].get_bet()/2, 2))
                            self._plyrTrn = False
                            surrender = True
                        else:
                            print('\nSurrendering is only available when dealt the inital two cards')
                    elif command == '6':
                        # Display information to the player
                        clear()
                        self.dsplyDlr()
                        self.dsplyPlyr()
                    else:
                        print('\nInvalid input')

                # --- Dealer's Turn ---
                # Queueing Dealer's Actions
                print("\nRevealing Dealer's Hand")
                self.dsplyDlr()

                # Wait a second for cleaner interface
                time.sleep(1.5)

                # Evaluate the hand situation
                if surrender:
                    # Player surrenderred hand
                    print('\nPlayer surrenderred their hand')
                    value = self._plyrHnd[0].get_bet()
                    self._plyrCash -= value
                    print('\n-$' + str(value))
                elif bustCount == len(self._plyrHnd):
                    # Player busted all hands
                    print('\nPlayer busted')
                    value = self._plyrHnd[0].get_bet() * 2
                    self._plyrCash -= value
                    print('\n-$' + str(value))
                else:
                    # Start showdown with dealer

                    # Continue to deal dealer cards until they hit at least 17
                    while(self.calcHand(self._dlrHnd[0].get_cards()) < 17):
                        print("\nDealer draw's a card")

                        # Deals a card for the dealer
                        self.draw(self._dlrHnd, 0)
                        self.dsplyDlr()

                        # Wait a second for cleaner interface
                        time.sleep(2)

                    dlrVal = self.calcHand(self._dlrHnd[0].get_cards())

                    # --- Showdown ---
                    # Evaluate each showdown
                    for hand in self._plyrHnd:
                        plyrVal = self.calcHand(hand.get_cards())

                        # Find the correct situtaion for the showdown
                        if plyrVal > 21:
                            # User busted their hand
                            print('\nPlayer busted')
                            value = hand.get_bet() 
                            self._plyrCash -= value
                            print('\n-$' + str(value))                        
                        elif (True if self.calcHand(self._dlrHnd[0].get_cards()) > 21 else False):
                            # If the Dealer busted, the player automatically wins
                            print('\nDealer busted, Player wins by default')
                            value = (hand.get_bet() * 1.5 if plyrVal == 21 else hand.get_bet())
                            self._plyrCash += value
                            print('\n+$' + str(value))                         
                        elif dlrVal < plyrVal:
                            # If the Dealer has a lower value hand than the player the player wins
                            print('\nPlayer wins, Dealer held a lower value')
                            value = (hand.get_bet() * 1.5 if plyrVal == 21 else hand.get_bet())
                            self._plyrCash += value
                            print('\n+$' + str(value))
                        elif dlrVal > plyrVal:
                            # If the Dealer has a higher value than the player the player loses
                            print('\nPlayer loses, Dealer held a higher value')
                            value = hand.get_bet() 
                            self._plyrCash -= value
                            print('\n-$' + str(value)) 
                        else:
                            # If all the above cases failed, the dealer and player tied and nothing will happen
                            print('\nPlayer ties, Dealer held the same value')
                prompt = input('\nPress any button to continue')
            else:
                print('\nInvalid input')

    def deal(self):  # Deal out openning cards to dealer and player
        # Deal out cards to dealer
        dCard = [self._deck.draw(), self._deck.draw()]
        self._dlrHnd = [self.Hand(dCard[0][:self.index(dCard[0])],
                                      dCard[1][:self.index(dCard[1])])]
        # Deal out cards to player
        pCard = [self._deck.draw(), self._deck.draw()]
        self._plyrHnd = [self.Hand(pCard[0][:self.index(pCard[0])],
                                    pCard[1][:self.index(pCard[1])])]
        # Set the bet with the hand
        self._plyrHnd[0].set_bet(round(float(self._bet), 2))

        # Display information to player
        self.dsplyDlr()
        self.dsplyPlyr()

    def dsplyPlyr(self):  # Show player cards
        # Form a string which holds all player cards
        handCount = 0
        for hand in self._plyrHnd:
            handCount += 1
            dsplyHand = '\nPlayer Hand ' + str(handCount) + ':'
            for card in hand.get_cards():
                dsplyHand += ' ' + card
            print(dsplyHand + ' | ' + str(self.calcHand(hand.get_cards())))

    def dsplyDlr(self):  # Show dealer cards
        # Form a string which holds all dealer cards
        dsplyHand = '\nDealer Hand:'

        if self._plyrTrn:
            dsplyHand += ' ' + self._dlrHnd[0].get_cards()[0]
        else:
            for card in self._dlrHnd[0].get_cards():
                dsplyHand += ' ' + card
        print(dsplyHand)

    def draw(self, player: list, index: int):  # Draw player an extra card
        # Add an additional card to the player's hand
        card = self._deck.draw()
        player[index].get_cards().append(card[:self.index(card)])

        # Display information to player
        self.dsplyPlyr()

        # Wait a second before prompting player for cleaner interface
        time.sleep(1)

    def calcHand(self, hand: list) -> int:  # Return the number which the value represent
        # Calculate the sum of a hand
        total = 0
        aceCount = 0
        for i in hand:
            if i == 'A':
                aceCount += 1
            elif (i == 'K') or (i == 'Q') or (i == 'J'):
                total += 10
            else:
                total += int(i)

        # Add the ace values
        for ace in range(0, aceCount):
            total += (11 if total + 11 <= 21 else 1)

        return total

    def isFloat(self, string: str) -> bool:  # Check if the string is a valid float value
        try:
            float(string)
            return True
        except ValueError:
            return False

    def index(self, string: str):  # Find the index which shortens the value of the card
        return (2 if string.startswith('10') else 1)

class BlackjackHelper():

    def __init__(self, size: int=1):
        self._size = size
        self.reset()
        self._possibleCrds = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        self._royals = ['J', 'Q', 'K', 'A']
        self._inProgress = True
        while(self._inProgress):
            # Prompt user for action
            clear()
            command = input('1) Win Chance\n2) Bust Chance\n3) Shuffle Deck\n4) Remove Cards\n5) Show Deck\n6) Change Size\n')

            # Queue action prompted by user
            if command == 'exit':
                # Exit program
                print('\nLeaving Blackjack Helper\n')
                self._inProgress = False
                break
            elif command == '1':
                # Return the percentage of every outcome given the current situation
                cards_in_play = input('\nFolloing the format: "<Player Cards> | <Dealer Cards> | <Other Cards in Play>"\n' +
                                      'Enter every card in play\n')
                # Seperate the cards into 3 grps
                grp = cards_in_play.upper().split('|')
                grp[0] = grp[0][:len(grp[0])-1].split(' ')
                grp[1] = grp[1][1:len(grp[1])-1].split(' ')
                grp[2] = grp[2][1:].split(' ')
                if '' in grp[2]:
                    grp[2].remove('')
                
                if ((set(grp[0]).issubset(set(self._possibleCrds)) == True) or (set(grp[0]).issubset(set(self._royals)) == True) and
                    (set(grp[1]).issubset(set(self._possibleCrds)) == True) or (set(grp[1]).issubset(set(self._royals)) == True) and
                    (set(grp[2]).issubset(set(self._possibleCrds)) == True) or (set(grp[2]).issubset(set(self._royals)) == True)):
                    self.analyze(grp[0], grp[1], grp[2])
                else:
                    print('\nInvalid input')                    
                prompt = input('\nPress any button to continue') 
            elif command == '2':
                # Return the percentage of every outcome if the player hits
                cards_in_play = input('\nFollowing the format: "<Player Cards> | <Dealer Cards> | <Other Cards in Play>"\n' +
                                   'Enter every card in play\n')
                try:
                    # Seperate the cards into 3 grps
                    grp = cards_in_play.upper().split('|')
                    grp[0] = grp[0][:len(grp[0])-1].split(' ')
                    grp[1] = grp[1][1:len(grp[1])-1].split(' ')
                    grp[2] = grp[2][1:].split(' ')
                    if '' in grp[2]:
                        grp[2].remove('')
                        
                    if ((set(grp[0]).issubset(set(self._possibleCrds)) == True) or (set(grp[0]).issubset(set(self._royals)) == True) and
                        (set(grp[1]).issubset(set(self._possibleCrds)) == True) or (set(grp[1]).issubset(set(self._royals)) == True) and
                        (set(grp[2]).issubset(set(self._possibleCrds)) == True) or (set(grp[2]).issubset(set(self._royals)) == True)):
                        self.calcPrcnt(grp[0], grp[1], grp[2])
                    else:
                        print('\nInvalid input')
                except:
                    print('\nInvalid input')                
                prompt = input('\nPress any button to continue') 
            elif command == '3':
                # Replace deck with a new one, mimicing a reshuffle
                print('\nReshuffling deck')
                self.reset()
                prompt = input('\nPress any button to continue')
            elif command == '4':
                # Permanently remove cards from current deck
                cards_to_remove = input('\nEnter cards which you want to remove seperated by spaces\n')
                try:
                    # Seperate the cards
                    grp = cards_to_remove.upper().split(' ')
                    
                    if ((set(grp).issubset(set(self._possibleCrds)) == True) or (set(grp).issubset(set(self._royals))) == True):
                        self.remove(grp)
                    else:
                        print('\nInvalid input')
                except:
                    print('\nInvalid input')
                prompt = input('\nPress any button to continue')            
            elif command == '5':
                # Display deck
                self.dsplyDck()
                prompt = input('\nPress any button to continue') 
            elif command == '6':
                size = input('Enter size of deck\n')
                try:
                    self._size = int(size)
                    print('\nDeck size has been changed, size will change upon next shuffle')
                except:
                    print('\nInvalid input')
                prompt = input('\nPress any button to continue')
            else:
                print('Invalid input')
                prompt = input('\nPress any button to continue')

    def remove(self, values: list):  # Remove all values within the string
        for i in values:
            if ((i == 'J') or (i == 'Q') or (i == 'K')):
                i = '10'
            elif i == 'A':
                i = '11'
        for number in values:
            self._tally[number] -= 1
            self._total -= 1

    def reset(self):  # Reset all the cards in the deck
        self._tally = {'2': (4 * self._size), '3': (4 * self._size), '4': (4 * self._size), '5': (4 * self._size),
                       '6': (4 * self._size), '7': (4 * self._size), '8': (4 * self._size),'9': (4 * self._size),
                       '10': (16 * self._size), '11': (4 * self._size)}
        self._total = 52 * self._size

    def calcPrcnt(self, plyrHand: list, dlrHand: list, others: list) -> str:  # Calculate the percentage of each result
        tmpTally = self._tally.copy()
        tmpSize = self._total

        # Remove cards already in play
        mergedlist = plyrHand + dlrHand + others
        for card in mergedlist:
            if ((card == 'K') or (card == 'Q') or (card == 'J')):
                tmpTally['10'] -= 1
            elif card == 'A':
                tmpTally['11'] -= 1
            else:
                tmpTally[card] -= 1
            tmpSize -= 1   

        # Calculate player hand value
        handVal = self.calcHand(plyrHand)
        
        # Calculate chance of each outcome
        bestDraw = 21 - handVal
        chance_for_21 = 0
        chance_to_bust = 0
        chance_to_not_bust = 0

        if bestDraw < 1:
            chance_to_bust = tmpSize
        elif bestDraw > 11:
            chance_to_not_bust = tmpSize
        elif ((bestDraw == 11) or (bestDraw == 1)):
            chance_for_21 == tmpTally['11']
            chance_to_not_bust = tmpSize
        elif bestDraw == 10:
            chance_for_21 = tmpTally['10']
            chance_to_not_bust = tmpSize
        else:
            chance_for_21 = tmpTally[str(bestDraw)]
            for i in range(1, bestDraw):
                chance_to_not_bust += tmpTally[self._possibleCrds[i]]
            chance_to_not_bust += tmpTally['11']
            chance_to_bust = tmpSize - chance_to_not_bust

        # Construct string to output
        result = ('\nExactly 21: ' + str(round(chance_for_21/ tmpSize * 100, 3)) + '%\n')
        result += 'Chance to Bust: ' + str(round(chance_to_bust/ tmpSize * 100, 3)) + '%\n'
        result += 'Chance not to Bust: ' + str(round(chance_to_not_bust/ tmpSize * 100,3))
        
        print(result)

    def calcHand(self, hand: list) -> int:  # Return the number which the value represent
        # Calculate the sum of a hand
        total = 0
        aceCount = 0
        for i in hand:
            if i == 'A':
                aceCount += 1
            elif (i == 'K') or (i == 'Q') or (i == 'J'):
                total += 10
            else:
                total += int(i)

        # Add the ace values
        for ace in range(0, aceCount):
            total += (11 if total + 11 <= 21 else 1)

        return total

    def dsplyDck(self):  # Display all remaining cards in deck
        print('\nValue : Count')
        for key in self._tally:
            print('%s : %s' % (key, self._tally[key]))

    def analyze(self, plyrHand: list, dlrHand: list, others: list):
        tmpTally = self._tally.copy()
        tmpSize = self._total

        # Remove cards already in play
        mergedlist = plyrHand + dlrHand + others
        for card in mergedlist:
            if ((card == 'K') or (card == 'Q') or (card == 'J')):
                tmpTally['10'] -= 1
            elif card == 'A':
                tmpTally['11'] -= 1
            else:
                tmpTally[card] -= 1
            tmpSize -= 1    

        outcomes = {'Win': 0.0, 'Lose': 0.0, 'Tie': 0.0}
        plyrVal = self.calcHand(plyrHand)
        dlrVal = self.calcHand(dlrHand)
        
        self.outcome(tmpTally, tmpSize, outcomes, plyrVal, dlrVal)

        print('\nStanding Outcomes:\n' + 
              'Win: ' + str(round(outcomes['Win'] * 100, 3)) + '%\n' +  
              'Lose: ' + str(round(outcomes['Lose'] * 100, 3)) + '%\n' +
              'Tie: ' + str(round(outcomes['Tie'] * 100, 3)) + '%')
        
    def outcome(self, tally: dict, unit: int, outcomes: dict, plyrVal: int, dlrVal: int):
        # Find the value which busts the dealer
        bustVal = (21 - dlrVal if dlrVal > 10 else 10)
        bustCount = 0
        # Add up all possibilities which busts the dealer
        for i in range(bustVal, 10):
            bustCount += self._tally[str(i)]
        outcomes['Win'] += bustCount/ unit
        
        # Find the value which ties the dealer
        tieVal = plyrVal - dlrVal
        if tieVal in self._possibleCrds:
            tieCount = (self._tally[str(tieVal)] if tieVal != 1 else self._tally['11']) if str(tieVal) in self._possibleCrds else 0
            outcomes['Tie'] += tieCount/ unit
        else:
            tieVal = 11

        # Find the value which forces the dealer to draw another card
        below17Val = (17 - dlrVal if dlrVal > 5 else 11)

        winCount = 0
        for i in range(below17Val, tieVal):
            winCount += (self._tally['11'] if i == 1 else self._tally[str(i)])
        outcomes['Win'] += winCount/ unit
        
        loseCount = 0
        for i in range(tieVal+1, bustVal+1):
            loseCount += (self._tally['11'] if i == 1 else self._tally[str(i)])
        outcomes['Lose'] += loseCount/ unit
        
        for i in range(1, below17Val):
            tempTally = tally.copy()
            
        
if (__name__ == "__main__"):
    isRunning = True

    while(isRunning):
        program = input('Select program:\n1) Blackjack\n2) Blackjack Helper\n3) Exit Program\n')
        if program == '1':
            print('\nStarting BlackJack Game')
            p = Blackjack()
        elif program == '2':
            print('\nStarting Blackjack Helper')
            p = BlackjackHelper()
        elif program == '3':
            print('\nExiting Program')
            exit()
        else:
            pass