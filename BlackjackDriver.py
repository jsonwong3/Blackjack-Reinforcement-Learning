from random import shuffle
from terminaltables import AsciiTable
from os import system, name
import time

import BlackjackPlayer

# Clears user interface
def clear():
    # For windows
    if name == 'nt':
        _ = system('cls')
    # For Mac and Linux
    else:
        _ = system('clear')

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

# Check if the string is a valid float value
def is_float(string: str) -> bool:
    try:
        float(string)
        return True
    except ValueError:
        return False
    
# Check if the string is a valid int value
def is_integer(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False
    
# Blackjack Driver
class BlackjackDriver():

    # Constructor for a Blackjack client
    def __init__(self):
        # Track which window the user the currently interacting with
        self._inProgress = True
        self._mainMenu = True
        self._optionMenu = False
        self._inGame = False
        
        # Game variables
        self._dealer = 'Dealer Object'
        self._table = []
        self._numOfBot = 0
        self._command_list = []
        self._round_num = 0
        
        # Player variables
        self._player = 'Player Object'
        self._buyIn = 500.00
        endturn = False
        
        # Deck variables
        self._deck = 'Deck Object'
        self._deckSize = 1
        self._maxCards = 52
        
        # Continues to loop until player exits program
        while(self._inProgress):
            # Main Menu
            while(self._mainMenu):
                clear()
                # Prompt player for actions
                command = input('1) Play Game\n' +
                                '2) Options\n' + 
                                '3) Exit\n')
                
                # Change into diffrent windows 
                if command == '1':
                    self._inGame = True
                    self._mainMenu = False
                    self.set_up()
                elif command == '2':
                    self._optionMenu = True
                    self._mainMenu = False
                elif command == '3':
                    self._mainMenu = False
                    self._inProgress = False
            
            # In-Game
            while(self._inGame):
                clear()
    
                # Prompt player for a bet
                command = input('\nPlayer Cash Pool: $' + str(self._player.get_cash()) + '\nPlace bet: ')
                
                # If player entered key word 'exit', program will close
                if command == 'exit':
                    print('\nLeaving Blackjack Game\n')
                    self._inGame = False
                    self._mainMenu = True
                    break
                
                if (is_float(command) and float(command) <= self._player.get_cash()):
                    # Shuffle back the deck once at least half of the deck is ran through
                    if (self._deck.size() < self._maxCards/2):
                        print('\nShuffle Deck ...')
                        time.sleep(0.75)
                        self.new_deck
            
                    self.clean_up()
                    
                    # Deal out cards to the table
                    for unit in self._table:
                        if (unit is self._player):
                            self.deal(unit, float(command))
                        else:
                            self.deal(unit)
                    self.deal(self._dealer)

                    while not(self.all_players_end()):
                        clear()
                        self._round_num += 1
                        self._command_list.append("\n --- Round " + str(self._round_num) + " ---")
                        self.display_hands()
                        for unit in self._table:
                            if not(unit.is_end_turn()):
                                time.sleep(1.5)
                                if unit is self._player:
                                    endturn = False
                                    while not(endturn):
                                        # Prompt user for in-game action
                                        action = input('\n1) Stand' + 
                                                        '\n2) Hit' +  
                                                        '\n3) Clear Screen\n\n')
                                else:
                                    action = self.execute_bot_command(unit)
                                if action == '1':
                                    self.stand(unit)
                                    endturn = True
                                elif action == '2':
                                    self.hit(unit)
                                    endturn = True
                                elif action == '3':
                                    clear()
                            self.display_hands()
                        time.sleep(1)
                    self.showdown() 
                    continue_prompt = input("\nPress any button to start next round")
            # Options Menu
            while(self._optionMenu):
                clear()
                # Prompt player for actions
                command = input('1) Change buy-in amount\n' +
                                '2) Change number of bots\n' + 
                                '3) Change size of deck\n' + 
                                '4) Exit\n')
                
                # Execute changes for player
                if command == '1':
                    # Display current buy-in amount
                    print('Current buy-in: ' + str(self._buyIn) + '\n')
                    
                    # Request for the new buy-in amount
                    command = input('Enter new buy-in amount: ')
                    if (is_float(command) and float(command) > 0):
                        self._buyIn = float(command)
                        print('Changes will be applied to the next game\n')
                    else:
                        print('Invalid input\n')
                elif command == '2':
                    # Display current number of bots
                    print('Current number of bots: ' + str(self._numOfBot) + '\n')
                    
                    # Request for the new amount of bots
                    command = input('Enter new amount of bots, capped at 4: ')
                    if (is_integer(command) and int(command) <= 4) and int(command) >= 0:
                        self._numOfBot = int(command)
                        print('Changes will be applied to the next game\n')
                    else:
                        print('Invalid input\n')                    
                elif command == '3':
                    # Display current size of the deck
                    print('Current size of the deck: ' + str(self._deckSize) + '\n')
                    
                    # Request for the size of the deck
                    command = input('Enter new size of the deck, capped at 3: ')
                    if (is_integer(command) and int(command) <= 3 and int(command) >= 1):
                        self._deckSize = int(command)
                        print('Changes will be applied to the next game\n')
                    else:
                        print('Invalid input\n')
                elif command == '4':
                    self._optionMenu = False
                    self._mainMenu = True
                else:
                    pass
            
    # Setting up the table           
    def set_up(self):
        # Add player to the table
        self._player = BlackjackPlayer.BlackjackPlayer(self._buyIn)
        self._table.append(self._player)
        
        # Initalize dealer
        dealer = BlackjackPlayer.BlackjackDealer(0, "Dealer")
        self._dealer = dealer
        
        index = 1
        # Add (if any) bots to the table
        for i in range(self._numOfBot):
            bot = BlackjackPlayer.BlacjackPlayerBot(0, ("Bot-" + str(index)))
            self._table.append(bot)
            index += 1
            
        # Randomize order of play
        shuffle(self._table)
        
        # Get new deck
        self.new_deck()
    
    # Remove any hands in play
    def clean_up(self):
        for unit in self._table:
            unit.clear_hands()
            unit.clear_turn()
        self._dealer.clear_hands()
        self._command_list = []
        self._round_num = 0

    # Create a new shuffled deck
    def new_deck(self):
        # Set proper amount of decks being used
        self._deck = Deck(self._deckSize)
        self._maxCards = self._deckSize * 52
        self._deck.shuffle_deck()
    
    # Deal 2 cards to the unit provided
    def deal(self, unit, bet: float=0):
        tempHand = Hand(self._deck.draw(), self._deck.draw())
        tempHand.set_bet(bet)
        unit.add_hand(tempHand)
    

    # Displays everyones hand
    def display_hands(self):
        title = "-Blackjack Table-"
        
        names = []
        hands = []        
        for player in self._table:
            name = player.get_name()
            if player.is_busted():
                name += " BUSTED"
            names.append(name)
                
            hand = ""
            for i in player.get_hands()[0].get_cards():
                hand += i + "\n"
            hands.append(hand.strip())
        names.append(self._dealer.get_name())
        
        hand = ""
        if self.all_players_end():
            for i in self._dealer.get_hands()[0].get_cards():
                hand += i + "\n"
            hands.append(hand.strip())
        else:
            hand = self._dealer.get_hands()[0].get_cards()[0] + '\n Unknown'
            hands.append(hand.strip())
    
        table_data = [names, hands]
        
        table_instance = AsciiTable(table_data, title)
        table_instance.justify_columns[1] = 'right'
        
        clear()
        print()
        print(table_instance.table)
        for text in self._command_list:
            print(text)
            
    # End players turn
    def stand(self, player):
        self._command_list.append("\n" + player.get_name() + " stands")
        player.end_turn()

    # Draw player another card
    def hit(self, player, i: int=0):
        self._command_list.append("\n" + player.get_name() + " hits")
        player.get_hands()[i].add(self._deck.draw())
        self.isBust(player)

    # Check if every player finished their turn
    def all_players_end(self) -> bool:
        is_end = True
        for unit in self._table:
            if not(unit.is_end_turn()):
                is_end = False
        return is_end
    
    # Determind bots action
    def execute_bot_command(self, player) -> str:
        if self.calculate_hand(player.get_hands()[0]) <= 16:
            return '2'
        else:
            return '1'

    # Calculates the sum of the provided hand
    def calculate_hand(self, hand) -> int:
        sum_of_hand = 0
        ace_count = 0
        for i in hand.get_cards():
            value = i.split(" ")[0]
            if (is_integer(value)):
                sum_of_hand += int(value)
            elif (value == "Ace"):
                ace_count += 1
            else:
                sum_of_hand += 10
            
            while (ace_count > 0):
                if sum_of_hand < 11:
                    sum_of_hand += 11
                else:
                    sum_of_hand += 1
                ace_count -= 1
        return sum_of_hand

    # Check if player busted
    def isBust(self, player):
        value = self.calculate_hand(player.get_hands()[0])
        if value > 21:
            player.end_turn()
            player.bust_player()
 
    # Determind dealers action
    def exexute_dealer_command(self, dealer):
        while(self.calculate_hand(dealer.get_hands()[0]) < 17):
            self.hit(dealer)
            self.display_hands()
            time.sleep(1.5)

    # Check if every player busted
    def all_players_bust(self) -> bool:
        is_bust = True
        for unit in self._table:
            if not(unit.is_busted()):
                is_bust = False
        return is_bust
    
    # Execute showdown
    def showdown(self):
        showdown_list = []
        all_busted = True
        for unit in self._table:
            if not(unit.is_busted()):
                all_busted = False
                showdown_list.append(unit)
            else:
                self._command_list.append("\n" + unit.get_name() + " busted")
                time.sleep(1.5)
                unit.set_cash(unit.get_cash() - unit.get_hands()[0].get_bet())
        if not(all_busted):
            self._command_list.append("\n --- Starting Showdown ---")
            time.sleep(1.5)
            self.display_hands()
            self.exexute_dealer_command(self._dealer)
            if (self._dealer.is_busted()):
                print("\nDealer busted, everyone in the showdown wins")
                time.sleep(1.5)            
                for unit in showdown_list:
                    bet = unit.get_hands()[0].get_bet()
                    unit_hand_value = self.calculate_hand(unit.get_hands()[0])
                    reward = bet * 1.5 if unit_hand_value == 21 else bet
                    unit.set_cash(unit.get_cash() + reward)
            else:
                dealer_hand_value = self.calculate_hand(self._dealer.get_hands()[0])
                for unit in showdown_list:
                    unit_hand_value = self.calculate_hand(unit.get_hands()[0])
                    if dealer_hand_value == unit_hand_value:
                        print("\n" + unit.get_name() + " tied with the dealer")
                        time.sleep(1.5)
                    elif dealer_hand_value > unit_hand_value:
                        unit.set_cash(unit.get_cash() - unit.get_hands()[0].get_bet())
                        print("\n" + unit.get_name() + " lost against the dealer")
                        time.sleep(1.5)
                    elif dealer_hand_value < unit_hand_value:
                        bet = unit.get_hands()[0].get_bet()
                        reward = bet * 1.5 if unit_hand_value == 21 else bet
                        unit.set_cash(unit.get_cash() + reward)
                        print("\n" + unit.get_name() + " won against the dealer")
                        time.sleep(1.5)

    
if (__name__ == "__main__"):
    BlackjackDriver()
    #isRunning = True
    #while(isRunning):
        #program = input('Select program:\n' + 
         #               '1) Blackjack\n' + 
          #              '2) Exit Program\n')
        #if program == '1':
         #   print('\nStarting BlackJack Game')
          #  p = BlackjackDriver()
        #elif program == '2':
         #   print('\nExiting Program')
          #  exit()
        #else:
         #   pass
