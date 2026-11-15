import numpy as np
import pickle
import matplotlib
import matplotlib.pyplot as plt
from constants import *
from blackjack import enviroment, showdown

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
                    hand_value, next_key = enviroment(p_key, d_key, action, choose_action)     # Compute Action within Enviroment
                    reward, d_value = showdown(hand_value, d_key, action, p_key == 9)  # Execute Dealer Action and Return Reward
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
            hand_value, next_key = enviroment(p_key, d_key, action, choose_action)     # Compute Action within Enviroment
            reward, d_value = showdown(hand_value, d_key, action, p_key == 9)  # Execute Dealer Action and Return Reward
            
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

    if p_key == 9:                                                      # Blackjack (A10) always stands
        return 0

    sorted_actions = np.argsort(QTABLE[p_key, d_key,:max_idx])
    idx = -2 if np.random.randint(0,3) == 0 else -1
    
    return sorted_actions[idx]
    
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
