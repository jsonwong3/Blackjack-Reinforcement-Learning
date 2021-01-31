import numpy as np
import pickle
import matplotlib
import matplotlib.pyplot as plt

# Simulate every dealt possibility once where each
# generation will play out each possibility once
def run_simulation(num=1):
    for i in range(0,num):
        # Deal dealers face up value
        for d_key in range(0, 10):
            # Deal players inital hand
            for p_key in range(0, hand_values.shape[1]):
                # Request agent for optimal action
                action = choose_action(p_key, d_key)
                
                # Send action into enviroment
                hand_value, next_key = enviroment(p_key, d_key, action)
                
                # Evaluate dealer action and return reward to agent
                reward, d_value = showdown(hand_value, d_key, action)
                
                # Update the agents Q-Table with the reward
                update_agent(p_key, next_key, d_key, action, reward)
                
                #print(f'Agent Hand: {hand_values[0, p_key]}, Action: {action}, Final Value: {hand_value}, Dealer Key: {d_key+2}, Reward: {reward}')
                                
# Agent has a 33% chance to disobey and attempt to
# learn a better strategy. Otherwise refer to its
# Q-Table for the most optimal decision.                
def choose_action(p_key, d_key, idx=3):
    if np.random.randint(0,3) == 0:
        action = np.random.randint(0,idx)
    else:
        action = np.argmax(QTable[p_key,d_key,:idx])
    return action
    
# Process agent action and calculate the agents new hand value.
# If the agent decides to hit, its following action (recursive)
# will be decided by referring to the optimal action of
# a 2 carded hand with the same value as the agents hand
def enviroment(p_key, d_key, action):
    cards = [2,3,4,5,6,7,8,9,10,11]
    probability = [1/13,1/13,1/13,1/13,1/13,1/13,1/13,1/13,4/13,1/13]
    
    p_value = int(hand_values[1, p_key])
    A_count = hand_values[0, p_key].count('A')
    
    final_value = p_value
    next_key = p_key
    
    if action != 0:
        # Initalize next card
        next_card = int(np.random.choice(cards, 1, probability))
        final_value = p_value + next_card
        
        # If an ace were to bust the agent if treated as an 11,
        # reduce it's value to a 1
        if (final_value > 21 and (A_count > 0 or next_card == 11)):
            final_value -= 10

        # Continue to find the next optimal action using the new key assigned
        if (action == 1 and final_value < 21):
            # Find a key which matches the new hand value.
            # Only included keys with an ace if the additional card
            # was an ace.
            if next_card == 11:
                next_key = np.where(hand_values[1,:] == str(final_value))[0][0]
            else:
                next_key = np.where(hand_values[1,9:] == str(final_value))[0][0] + 9
                    
            next_action = choose_action(next_key, d_key, 2)
                
            final_value, dump_key = enviroment(next_key, d_key, next_action)             

    return final_value, next_key
 
# Execute the dealers turn and return the appropriate reward
def showdown(p_value, d_key, action):
    cards = [2,3,4,5,6,7,8,9,10,11]
    probability = [1/13,1/13,1/13,1/13,1/13,1/13,1/13,1/13,4/13,1/13]
    
    d_value = d_key + 2
    A_count = int(d_key == 9)
    
    multiplier = max(1, action)
    
    # Draw the dealer cards until they bust or are at once at 17
    while(d_value < 17):
        # Initalize next card
        next_card = np.random.choice(cards, 1, probability)
        d_value += next_card
        
        if next_card == 11:
            A_count += 1
            
        # If an ace were to bust the dealer if treated as an 11,
        # reduce it's value to a 1
        if (d_value > 21 and A_count > 0):
            d_value -= 10
            A_count -= 1
            
    if p_value > 21:
        reward = -10 * multiplier
    elif d_value > 21:
        reward = 10 * multiplier
    elif p_value > d_value:
        reward = 10 * multiplier
    elif p_value < d_value:
        reward = -10 * multiplier
    else:
        reward = 0
    
    return reward, d_value

# Update agents Q Table value after given an reward
def update_agent(p_key, next_key, d_key, action, reward):
    learning_rate = 0.4
    discount_factor = 0.9
    
    tmprl_diff_target = reward + discount_factor * max(QTable[next_key, d_key,:2])
    tmprl_diff = tmprl_diff_target - QTable[p_key,d_key,action]
    
    QTable[p_key,d_key,action] += learning_rate * tmprl_diff

# Display the agents most optimal action for each scenerio
def show_QTable():
    plt.rcParams["figure.figsize"] = (5,10)
    best_decision = np.zeros((hand_values.shape[1],10))

    for i in range(0,hand_values.shape[1]):
        for j in range(0,10):
            best_decision[i,j] = np.argmax(QTable[i,j,:])
    
    dlr_key = ['2','3','4','5','6','7','8','9','10','A']
    plr_key = np.ndarray.tolist(hand_values[0,:])
    
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
            text = ax.text(j, i, action_word[best_decision[i, j]],
                           ha="center", va="center", color="w")
    
    ax.set_title("Agents Decision Matrix")
    plt.show()

def save_QTable():
    pickle.dump(QTable, open('QTable_new.pkl', 'wb'))

def optimal_wager(table, min_w=10, max_w=1000):
    wager_table = np.zeros((27,10))
    
    for i in range(0, table.shape[0]):
        for j in range(0, table.shape[1]):
            wager_table[i,j] = np.sum(table[i,j,:])
            
    return wager_table

if __name__ == "__main__":
    QTable = pickle.load(open('QTable_new.pkl', 'rb'))
    hand_values = np.loadtxt('Blackjack_Hands.txt', dtype=str)
    
    run_simulation(750)
    show_QTable()
    save_QTable()