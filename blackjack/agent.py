import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import argparse
from pathlib import Path
from .constants import *
from .game import enviroment, showdown

QTABLE_PATH = Path(__file__).resolve().parent.parent / 'models' / 'QTable_new.pkl'
COUNTS_PATH = QTABLE_PATH.with_name('QCounts_new.pkl')                  # Times each (hand, dealer, action) was updated
IMAGE_PATH = QTABLE_PATH.parent.parent / 'docs' / 'strategy.png'       # Strategy chart for the README

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

def show_QTable(save_path=None, show=True):
    '''
    Display the agents most optimal action for each scenerio,
    optionally saving the chart as an image
    '''

    best_decision = np.argmax(QTABLE, axis=2)
    best_decision[9, :] = 0                                             # Blackjack (A10) always stands

    dlr_key = ['2','3','4','5','6','7','8','9','10','A']
    plr_key = [v[0] for v in HANDS]
    action_word = {0:'S', 1:'H', 2:'D'}
    action_name = {0:'Stand', 1:'Hit', 2:'Double'}
    colors = ['#2a78d6', '#eb6834', '#1baf7a']                          # Stand, Hit, Double
    surface, ink, muted = '#fcfcfb', '#0b0b0b', '#52514e'

    fig, ax = plt.subplots(figsize=(5, 10.5), facecolor=surface)
    ax.set_facecolor(surface)
    ax.pcolormesh(best_decision, cmap=ListedColormap(colors), vmin=-0.5, vmax=2.5,
                  edgecolors=surface, linewidth=2)
    ax.axhline(10, color=surface, linewidth=8)                         # Gap between soft and hard hands
    ax.invert_yaxis()

    for i in range(len(plr_key)):
        for j in range(len(dlr_key)):
            ax.text(j + 0.5, i + 0.5, action_word[best_decision[i,j]],
                    ha="center", va="center", color=ink, fontsize=9, fontweight="bold")

    ax.set_xticks(np.arange(len(dlr_key)) + 0.5, dlr_key)
    ax.set_yticks(np.arange(len(plr_key)) + 0.5, plr_key)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('Dealer upcard', color=muted, labelpad=8)
    ax.set_ylabel('Player hand', color=muted)
    ax.tick_params(length=0, colors=ink)
    for spine in ax.spines.values():
        spine.set_visible(False)

    handles = [Patch(color=colors[a], label=f'{action_word[a]} = {action_name[a]}') for a in range(3)]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0), ncol=3,
              frameon=False, labelcolor=ink, handlelength=1, columnspacing=1.5)

    fig.suptitle("Agent's learned strategy", color=ink, fontsize=13, fontweight="bold")
    fig.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, facecolor=surface)
    if show:
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
    parser.add_argument('--plot-only', action='store_true', help='skip training, just chart the saved Q-table')
    args = parser.parse_args()

    if args.plot_only:
        if not COUNTS.any():
            print('No trained Q-table to plot, run training first')
            return
        show_QTable(IMAGE_PATH)
        print(f'Saved {IMAGE_PATH}')
        return

    if args.seed is not None:
        np.random.seed(args.seed)
    if args.fresh:
        QTABLE[:] = 0
        COUNTS[:] = 0
    print('Continuing from the saved Q-table' if COUNTS.any() else 'Starting from a fresh Q-table')

    run_simulation(DEFINITE, 10000)
    save_QTable()
    show_QTable(IMAGE_PATH)
    print(f'Saved {IMAGE_PATH}')

if __name__ == '__main__':
    main()
