import numpy as np
import pickle
import matplotlib
import matplotlib.pyplot as plt
from constants import *

def run_simulation(t, n=1000):
    '''
    Run simulations of the game blackjack being played,
    either by randomly choosing the state of the game or
    trying every state of the game once
    
    Inputs:
    ------------------------------------------------------------
    t: str
        Type of simulation we'd like to run
        
    n: int
        Number of trials we'd like to run
    '''
    
    if t == DEFINITE:
        for i in range(n):
            for d_key in range(10):                                             # Dealers Hand
                for p_key in range(len(HANDS)):                                 # Players Hand
                    action = choose_action(p_key, d_key)                        # Get Optimal Action
                    hand_value, next_key = enviroment(p_key, d_key, action)     # Compute Action within Enviroment
                    reward, d_value = showdown(hand_value, d_key, action)       # Execute Dealer Action and Return Reward
                    update_agent(p_key, next_key, d_key, action, reward)        # Update Q-Table with Reward
                    
                    #print(f'Agent Hand: {HANDS[p_key][0]}, '
                          #f'Inital Action: {action}, '
                          #f'Final Value: {hand_value}, '
                          #f'Dealer Card: {d_key+2}, '
                          #f'Dealer Value: {int(d_value)}, '
                          #f'Reward: {reward}')

    elif t == RANDOM:
        for i in range(0, n):
            d_key = np.random.randint(0, 10)
            p_key = np.random.randint(0, len(HANDS))
            
            action = choose_action(p_key, d_key)                        # Get Optimal Action
            hand_value, next_key = enviroment(p_key, d_key, action)     # Compute Action within Enviroment
            reward, d_value = showdown(hand_value, d_key, action)       # Execute Dealer Action and Return Reward            
            
            print(f'Agent Hand: {HANDS[p_key][0]}, '
                                  f'Inital Action: {action}, '
                                  f'Final Value: {hand_value}, '
                                  f'Dealer Card: {d_key+2}, '
                                  f'Dealer Value: {int(d_value)}, '
                                  f'Reward: {reward}')            
            
def choose_action(p_key, d_key, max_idx=3):
    '''
    Agent will refer to its Q-table for the most optimal action,
    however it has a 33% chance of disregarding the Q-table and
    attempt to learn a better optimal action
    
    Inputs:
    ------------------------------------------------------------
    p_key: int
        Index of the agents hand in reference to the Q-Table
        
    d_key: int
        Index of the dealers hand in reference to the Q-Table
    
    max_idx: int
        Indicate the actions the agents is allowed to take
    
    Output:
    ------------------------------------------------------------
    sorted_actions[idx]: int
        Index of the action the agent has choosen
    '''

    sorted_actions = np.argsort(QTABLE[p_key, d_key,:max_idx])
    idx = -2 if np.random.randint(0,3) == 0 else -1
    
    return sorted_actions[idx]
    

def enviroment(p_key, d_key, action):
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
    
    Output:
    ------------------------------------------------------------
    final_value: int
       Final value of the agents hand
    '''
    p_val = HANDS[p_key][1]
    A_count = HANDS[p_key][0].count('A')
    
    final_value, next_key = p_val, p_key

    if action != 0:
        # Draws additional card
        next_card = int(np.random.choice(CARDS, 1))
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
            final_value, dump_key = enviroment(next_key, d_key, next_action)             

    return final_value, next_key

def showdown(p_value, d_key, action):
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

    while d_value < 17:
        # Draws additional card
        next_card = int(np.random.choice(CARDS, 1))
        if next_card == 11:
            A_count += 1
        d_value += next_card
        
        # Reduce value of ace if required
        while d_value > 21 and A_count > 0:
            d_value -= 10
            A_count -= 1 

    # Evaluate the showdown and determine the reward
    if p_value > 21:
        bet = -bet
    elif p_value == d_value: 
        bet = 0
    elif p_value == 21:
        bet = bet * 1.5
    elif d_value > 21:
        pass
    elif p_value < d_value:
        bet = -bet
    elif p_value > d_value: 
        pass        

    return bet, d_value

def update_agent(p_key, next_key, d_key, action, reward):
    '''
    Update the agents Q-Table after given a reward
    
    Inputs:
    ------------------------------------------------------------
    p_key: int
        Index of the agents hand in reference to the Q-Table
    
    next_key: int
        Index of the agents hand after the first action in reference to the Q-Table
        
    d_key: int
        Index of the dealers hand in reference to the Q-Table
    
    action: int
        Index of the inital action the agent has choosen
        
    reward: int
       Reward which the agent receives
    '''
    
    tmprl_diff_target = reward + DISCOUNT_FACOTR * max(QTABLE[next_key, d_key,:2])
    tmprl_diff = tmprl_diff_target - QTABLE[p_key,d_key,action]
    QTABLE[p_key,d_key,action] += LEARNING_RATE * tmprl_diff


def show_QTable():
    '''
    Display the agents most optimal action for each scenerio
    '''
    
    plt.rcParams["figure.figsize"] = (5,10)
    best_decision = np.zeros((len(HANDS), 10))

    for i in range(len(HANDS)):
        for j in range(0,10):
            best_decision[i,j] = np.argmax(QTABLE[i,j,:])
    
    dlr_key = ['2','3','4','5','6','7','8','9','10','A']
    plr_key = [v[0] for i, v in enumerate(HANDS)]
    
    fig, ax = plt.subplots()
    im = ax.imshow(best_decision)
    
    ax.set_xticks(np.arange(len(dlr_key)))
    ax.set_yticks(np.arange(len(plr_key)))
    
    ax.set_xticklabels(dlr_key)
    ax.set_yticklabels(plr_key)
    
    plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
             rotation_mode="anchor")
    
    action_word = {0:'S', 1:'H', 2:'D'}
    
    for i in range(len(plr_key)):
        for j in range(len(dlr_key)):
            avg_return = str(np.round(np.average(QTABLE[i,j,:]), 1))
            text = ax.text(j, i, avg_return,
                           ha="center", va="center", color="black", fontsize="x-small")
    
    ax.set_title("Agents Decision Matrix")
    plt.show()

def save_QTable():
    '''
    Saves the Q-Table in pickel file
    '''
    
    pickle.dump(QTABLE, open('QTable_new.pkl', 'wb'))

run_simulation(DEFINITE, 10000)
show_QTable()
save_QTable()
