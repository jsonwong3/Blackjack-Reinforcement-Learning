import numpy as np
from constants import HANDS, CARDS, REWARD

def enviroment(p_key, d_key, action, choose_action):
    '''
    Process the agents action and computes the agents updated hand value.
    If the agent hits another card, the function will recursively find the
    next most optimal action referring to a 2 carded hand with the same value
    as the agents hand

    Inputs:
    ------------------------------------------------------------
    p_key: int
        Index of the agents hand in reference to the Q-Table

    d_key: int
        Index of the dealers hand in reference to the Q-Table

    action: int
        Index of the action the agent has choosen

    choose_action: function
        Called as choose_action(p_key, d_key, max_idx) to pick each action after a hit

    Output:
    ------------------------------------------------------------
    final_value: int
       Final value of the agents hand
    '''
    p_val = HANDS[p_key][1]
    A_count = min(1, HANDS[p_key][0].count('A'))                        # At most one ace is still counted as 11

    final_value, next_key = p_val, p_key

    if action != 0:
        # Draws additional card
        next_card = int(np.random.choice(CARDS))
        if next_card == 11:
            A_count += 1
        final_value = p_val + next_card

        # Reduce value of ace if required
        while final_value > 21 and A_count > 0:
            final_value -= 10
            A_count -= 1

        # Continue to find the next optimal action using the new key assigned
        if final_value < 21 and action == 1:
            # Find 2 carded hand with same value in search for next optimal action
            if A_count > 0:
                next_key = [i for i, v in enumerate(HANDS[:10]) if v[1] == final_value][0]
            else:
                next_key = 10 + [i for i, v in enumerate(HANDS[10:]) if v[1] == final_value][0]

            # Get optimal action excluding doubling down
            next_action = choose_action(next_key, d_key, 2)
            final_value, dump_key = enviroment(next_key, d_key, next_action, choose_action)

    return final_value, next_key

def showdown(p_value, d_key, action, natural=False):
    '''
    Execute the dealers turn and return the appropriate reward

    Inputs:
    ------------------------------------------------------------
    p_value: int
        Final value of the agents hand

    d_key: int
        Index of the dealers hand in reference to the Q-Table

    action: int
        Index of the inital action the agent has choosen

    Output:
    ------------------------------------------------------------
    final_reward: int
       Reward which the agent receives

    d_value: int
       Final value of the dealers hand
    '''

    d_value = d_key + 2
    A_count = int(d_key == 9)
    bet = REWARD * max(1, action)
    d_cards = 1

    while d_value < 17:
        # Draws additional card
        next_card = int(np.random.choice(CARDS))
        if next_card == 11:
            A_count += 1
        d_value += next_card

        # Reduce value of ace if required
        while d_value > 21 and A_count > 0:
            d_value -= 10
            A_count -= 1
        d_cards += 1

    d_natural = d_cards == 2 and d_value == 21

    # Evaluate the showdown and determine the reward
    if natural and d_natural:
        bet = 0
    elif d_natural:
        bet = -REWARD                       # Dealer peeks: only the original bet is lost
    elif natural:
        bet = bet * 1.5
    elif p_value > 21:
        bet = -bet
    elif p_value == d_value:
        bet = 0
    elif d_value > 21:
        pass
    elif p_value < d_value:
        bet = -bet
    elif p_value > d_value:
        pass

    return bet, d_value

def card_name(card):
    return 'A' if card == 11 else str(card)

def hand_key(c1, c2):
    '''
    Index into HANDS for a two carded hand
    '''
    if c1 == 11 and c2 == 11:
        return 0                                    # AA
    if 11 in (c1, c2):
        return c1 + c2 - 11 - 1                     # A2..A10 -> 1..9
    return c1 + c2 + 6                              # Hard 4..20 -> 10..26

def ask_action(p_key, d_key, max_idx=3):
    '''
    Ask the user for an action, same signature as the agents choose_action
    '''
    if p_key == 9:                                  # Blackjack always stands
        print('Blackjack!')
        return 0

    soft = ' (soft)' if p_key < 10 else ''
    options = {'s': 0, 'h': 1, 'd': 2} if max_idx == 3 else {'s': 0, 'h': 1}
    prompt = '[s]tand, [h]it' + (', [d]ouble' if max_idx == 3 else '') + ': '

    print(f'Your total: {HANDS[p_key][1]}{soft}   Dealer shows: {card_name(d_key + 2)}')
    while True:
        choice = input(prompt).strip().lower()
        if choice in options:
            return options[choice]

def play():
    '''
    Play blackjack from the command line
    '''
    winnings = 0
    while True:
        c1, c2, up = (int(np.random.choice(CARDS)) for _ in range(3))
        p_key, d_key = hand_key(c1, c2), up - 2

        print(f'\nYour cards: {card_name(c1)} {card_name(c2)}   Dealer shows: {card_name(up)}')
        action = ask_action(p_key, d_key)
        hand_value, _ = enviroment(p_key, d_key, action, ask_action)
        reward, d_value = showdown(hand_value, d_key, action, p_key == 9)

        print(f'Your final total: {hand_value}{" (bust)" if hand_value > 21 else ""}   '
              f'Dealer final total: {d_value}{" (bust)" if d_value > 21 else ""}')
        result = 'Win' if reward > 0 else 'Lose' if reward < 0 else 'Push'
        winnings += reward
        print(f'{result} {reward:+g}   Total winnings: {winnings:+g}')

        if input('Play again? [y/n]: ').strip().lower() != 'y':
            break

if __name__ == '__main__':
    play()
