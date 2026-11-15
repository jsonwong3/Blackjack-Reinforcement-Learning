import numpy as np
import pickle
import matplotlib
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from .constants import *
from .game import enviroment, showdown

QTABLE_PATH = Path(__file__).resolve().parent.parent / 'models' / 'QTable_new.pkl'
COUNTS_PATH = QTABLE_PATH.with_name('QCounts_new.pkl')                  # Times each (hand, dealer, action) was updated

if QTABLE_PATH.exists() and COUNTS_PATH.exists():
    QTABLE = pickle.load(open(QTABLE_PATH, 'rb'))
    COUNTS = pickle.load(open(COUNTS_PATH, 'rb'))
else:                                                                   # No counts: saved table predates the fixed update rule
    QTABLE = np.zeros((len(HANDS), 10, 3))
    COUNTS = np.zeros((len(HANDS), 10, 3))

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
                    steps = [(p_key, action)]                                   # Every (state, action) taken this hand
                    hand_value, next_key = enviroment(p_key, d_key, action, recorder(steps))     # Compute Action within Enviroment
                    reward, d_value = showdown(hand_value, d_key, action, p_key == 9)  # Execute Dealer Action and Return Reward
                    update_agent(steps, d_key, reward)                          # Update Q-Table with Reward
                    
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
    however it has an epsilon chance of disregarding the Q-table and
    trying any allowed action. Epsilon shrinks the more often the
    hand has been seen, down to MIN_EPSILON
    
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

    q = QTABLE[p_key, d_key,:max_idx]
    epsilon = max(MIN_EPSILON, EPSILON_DECAY / (EPSILON_DECAY + COUNTS[p_key, d_key].sum()))

    if np.random.rand() < epsilon:                                      # Explore: any allowed action
        return np.random.randint(0, max_idx)

    return np.random.choice(np.flatnonzero(q == q.max()))               # Best action, ties broken randomly

def recorder(steps):
    '''
    Wrap choose_action so every action taken after a hit is appended to steps
    '''
    def choose(p_key, d_key, max_idx=3):
        action = choose_action(p_key, d_key, max_idx)
        steps.append((p_key, action))
        return action
    return choose

def update_agent(steps, d_key, reward):
    '''
    Update the agents Q-Table after given a reward

    Inputs:
    ------------------------------------------------------------
    steps: list of (int, int)
        Every (hand index, action) the agent took this hand, in order

    d_key: int
        Index of the dealers hand in reference to the Q-Table

    reward: int
       Reward which the agent receives
    '''

    # Non-final steps: no reward yet, bootstrap from the next state (stand/hit only)
    for (p_key, action), (next_key, _) in zip(steps, steps[1:]):
        tmprl_diff_target = DISCOUNT_FACOTR * max(QTABLE[next_key, d_key,:2])
        tmprl_diff = tmprl_diff_target - QTABLE[p_key,d_key,action]
        COUNTS[p_key,d_key,action] += 1
        QTABLE[p_key,d_key,action] += tmprl_diff / COUNTS[p_key,d_key,action]     # Learning rate 1/N

    # Final step: the hand is over, so the target is just the reward
    p_key, action = steps[-1]
    tmprl_diff = reward - QTABLE[p_key,d_key,action]
    COUNTS[p_key,d_key,action] += 1
    QTABLE[p_key,d_key,action] += tmprl_diff / COUNTS[p_key,d_key,action]         # Learning rate 1/N

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
    
    pickle.dump(QTABLE, open(QTABLE_PATH, 'wb'))
    pickle.dump(COUNTS, open(COUNTS_PATH, 'wb'))

def main():
    parser = argparse.ArgumentParser(description='Train the blackjack Q-learning agent')
    parser.add_argument('--fresh', action='store_true', help='ignore the saved Q-table and start from zeros')
    parser.add_argument('--seed', type=int, help='random seed, for a repeatable run')
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)
    if args.fresh:
        QTABLE[:] = 0
        COUNTS[:] = 0
    print('Continuing from the saved Q-table' if COUNTS.any() else 'Starting from a fresh Q-table')

    run_simulation(DEFINITE, 10000)
    show_QTable()
    save_QTable()

if __name__ == '__main__':
    main()
