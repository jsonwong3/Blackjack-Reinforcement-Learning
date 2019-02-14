from random import shuffle
from terminaltables import AsciiTable
from os import system, name
import time

import Deck, Hand
import BlackjackPlayer

# GETTING 21 DOESNT YIELD 1.5X
# BUGS WIRH ACE IN HAND, BUSTING WHEN IT SHOULDNT
# UI PROBLEMS
    
# Clears user interface
def clear():
    # For windows
    if name == 'nt':
        _ = system('cls')
    # For Mac and Linux
    else:
        _ = system('clear')

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
        
        # Player variables
        self._player = 'Player Object'
        self._buyIn = 500.00
        
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
                        self.display_hands()
                        for unit in self._table:
                            if not(unit.is_end_turn()):
                                time.sleep(2)
                                if unit is self._player:
                                    # Prompt user for in-game action
                                    action = input('\n1) Stand' + 
                                                    '\n2) Hit' +  
                                                    '\n3) Clear Screen\n')
                                else:
                                    action = self.execute_bot_command(unit)
                                if action == '1':
                                    self.stand(unit)
                                elif action == '2':
                                    self.hit(unit)
                                elif action == '3':
                                    clear()
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
            
    # Create a new shuffled deck
    def new_deck(self):
        # Set proper amount of decks being used
        self._deck = Deck.Deck(self._deckSize)
        self._maxCards = self._deckSize * 52
        self._deck.shuffle_deck()
    
    # Deal 2 cards to the unit provided
    def deal(self, unit, bet: float=0):
        tempHand = Hand.Hand(self._deck.draw(), self._deck.draw())
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
        print()
        print(table_instance.table)
      
    # End players turn
    def stand(self, player):
        print("\n" + player.get_name() + " stands")
        player.end_turn()

    # Draw player another card
    def hit(self, player, i: int=0):
        print("\n" + player.get_name() + " hits")
        player.get_hands()[i].add(self._deck.draw())
        self.isBust(player)
        self.display_hands()

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
                print("\n" + unit.get_name() + " busted")
                time.sleep(1.5)
                unit.set_cash(unit.get_cash() - unit.get_hands()[0].get_bet())
        if not(all_busted):
            print("\nStarting Showdown")
            time.sleep(1.5)
            self.display_hands()
            self.exexute_dealer_command(self._dealer)
            if (self._dealer.is_busted()):
                print("\nDealer busted")
                time.sleep(1.5)            
                for unit in showdown_list:
                    unit.set_cash(unit.get_cash() + unit.get_hands()[0].get_bet())
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
                        unit.set_cash(unit.get_cash() + unit.get_hands()[0].get_bet())
                        print("\n" + unit.get_name() + " won against the dealer")
                        time.sleep(1.5)

if (__name__ == "__main__"):
    isRunning = True
    
    while(isRunning):
        program = input('Select program:\n' + 
                        '1) Blackjack\n' + 
                        '2) Exit Program\n')
        if program == '1':
            print('\nStarting BlackJack Game')
            p = BlackjackDriver()
        elif program == '2':
            print('\nExiting Program')
            exit()
        else:
            pass