options(warn=-1)

suppressMessages(library(tidyverse))
suppressMessages(library(parallel))
suppressMessages(library(foreach))
suppressMessages(library(doParallel))
suppressMessages(library(iterators))
suppressMessages(library(tcltk))

deckx2 = list("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2",
              "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")


# Sort cards in hand
strSort = function(x) {
    return(sapply(lapply(strsplit(x, NULL), sort), paste, collapse=""))
}

# Deal out starting hand
deal_hand = function(num) {
    return(sample(deckx2, num, replace=FALSE))
}

# Calculate hand value
hand_value = function(hand) {
    value = 0
    # Sum hand value excluding Aces
    for (i in hand) {
        if (i %in% c("9", "8", "7", "6", "5", "4", "3", "2")) {
            value = value + as.integer(i)
        } else if (i %in% c("K", "Q", "J", "T")) {
            value = value + 10
        }
    }
  # Add dynamic Ace value
  for (i in hand) {
      if(i == "A") {
          value = ifelse(value < 11,
                         value + 11,
                         value + 1)
      }
  }
  return(value)
}

#  Draw the dealer cards until they have 17 or more
dlr_action = function(dlr_hand) {
    new_dlr_hand = dlr_hand
    while(hand_value(new_dlr_hand) < 17) {
        new_dlr_hand = c(new_dlr_hand, sample(deckx2, 1))
    }
    return(new_dlr_hand)
}

# Deal out new instance 
new_instance = function(df) {
    plr_hand = deal_hand(2)
    dlr_hand = deal_hand(1)
    new_state = generate_state(plr_hand, dlr_hand, "1")
    
    # Add state into dataframe 
    if (nrow(df) == 0 || !any(df == new_state)) {
        new_entry = data.frame(state=new_state, stand=0, hit=0, double=0)
        df <<- bind_rows(df, new_entry)
    }
    return(new_state)
}

# Given a state and action, return thr new state
environment = function(state, action) {
    broken_down_state = decrypt_state(state)
    new_plr_hand = broken_down_state[[1]]
    new_dlr_hand = broken_down_state[[2]]
    new_game_state = broken_down_state[[3]]
    
    if (action == "stand") {
        # Queue dealers shuwdown new_dlr_hand
        new_dlr_hand = dlr_action(new_dlr_hand)
        new_game_state = "0"
    } else if (action == "hit") {
        new_plr_hand = c(new_plr_hand, sample(deckx2, 1))
        plr_val = hand_value(new_plr_hand)
        new_game_state = ifelse(plr_val > 21, "0", "1")
    } else if (action == "double") {
        new_plr_hand = c(new_plr_hand, sample(deckx2, 1))
        new_dlr_hand = dlr_action(new_dlr_hand)
        new_game_state = "0"
    }
    new_state = generate_state(new_plr_hand, new_dlr_hand, new_game_state)
    
    # Add new state into dataframe
	  if (!any(df == new_state)) {
	      new_entry = data.frame(state=new_state, stand=0, hit=0, double=0)
        df <<- bind_rows(df, new_entry)
    }
    return(new_state)
}

# Generate State string
generate_state = function(plr_hand, dlr_hand, game_state) {
    plr = strSort(str_c(plr_hand, collapse = ""))
    dlr = strSort(str_c(dlr_hand, collapse = ""))
    new_state = str_c(plr, dlr, game_state, sep="-")
    return(new_state)
}

# Decrypt State
decrypt_state = function(state) {
    object = str_split(state, "-")
    plr_hand = str_split(object[[1]][1], "")
    dlr_hand = str_split(object[[1]][2], "")
    is_showndown = object[[1]][3]
    return(c(plr_hand, dlr_hand, is_showndown))
}

# List possible actions
actions = list("stand", "hit")
first_actions = list("stand", "hit", "double")

# Decide the best action even past experiences and current state
agent = function(curr_state, df) {
    # Find best decision
    object = str_split(curr_state, "-")[[1]][1]
    hand_size = str_length(object)
    index = which(df==curr_state, arr.ind = TRUE)[1]
    if ((df[index,]$stand == df[index,]$hit) &
        (df[index,]$stand == df[index,]$double)) {
        best_action = ifelse(hand_size == 2,
                             sample(first_actions, 1),
                             sample(actions, 1))
    } else {
        chance = sample(c(1:10), 1)
        best_action = ifelse(chance == 10,
                             ifelse(hand_size == 2,
                                    sample(first_actions, 1),
                                    sample(actions, 1)),
                             ifelse(hand_size == 2,
                                    names(df)[apply(df[index, 2:4], 1, which.max)+1],
                                    names(df)[apply(df[index, 2:3], 1, which.max)+1]))
        
    }
    return(best_action)
}

# Reward the agent according to its action
reward = function(state, new_state, df, action) {
    broken_down_state = decrypt_state(new_state)
    new_plr_hand = broken_down_state[[1]]
    new_dlr_hand = broken_down_state[[2]]
    new_status = broken_down_state[[3]]
    plr_val = hand_value(new_plr_hand)
    dlr_val = hand_value(new_dlr_hand)
  
    if (new_status == "1") {
        reward = 0
    } else {
        if (plr_val > 21) {
            reward = ifelse(action == "double", -100 ,-50)
            DEALER_WIN <<- DEALER_WIN + 1
        } else if (dlr_val > 21) {
            reward = ifelse(action == "double", 100 ,50)
            PLAYER_WIN <<- PLAYER_WIN + 1
        } else if (dlr_val == plr_val) {
            reward = 0
            TIE <<- TIE + 1
        } else if (dlr_val > plr_val) {
            reward = ifelse(action == "double", -100 ,-50)
            DEALER_WIN <<- DEALER_WIN + 1
        } else if (plr_val > dlr_val) {
            reward = ifelse(action == "double",
                            ifelse(plr_val == 21, 150, 100),
                            ifelse(plr_val == 21, 75, 50))
            PLAYER_WIN <<- PLAYER_WIN + 1
        }
    }
  
    # Find max reward of the next state
    index = which(df==state, arr.ind = TRUE)[1]
    new_index = which(df==new_state, arr.ind = TRUE)[1]
    max_reward = apply(df[new_index, 2:4], 1, max)
    
    if (action == "stand") {
        df[index,]$stand <<- (1-learning_rate)*(df[index,]$stand)+(learning_rate*(reward+discount*max_reward))
    } else if (action == "hit") {
        df[index,]$hit <<- (1-learning_rate)*(df[index,]$hit)+(learning_rate*(reward+discount*max_reward))
    } else {
        df[index,]$double <<- (1-learning_rate)*(df[index,]$double)+(learning_rate*(reward+discount*max_reward))
    }
}

# Constant Set Up
learning_rate = 0.1
discount = 0.9

decision_matrix = matrix(NA, nrow=91, ncol=13)
colnames(decision_matrix) = c("2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K" ,"A")
rownames(decision_matrix) = c("22", "23", "24", "25", "26", "27", "28", "29", "2A", "2J", "2K", "2Q", "2T",
                              "33", "34", "35", "36", "37", "38", "39", "3A", "3J", "3K", "3Q", "3T",
                              "44", "45", "46", "47", "48", "49", "4A", "4J", "4K", "4Q", "4T",
                              "55", "56", "57", "58", "59", "5A", "5J", "5K", "5Q", "5T",
                              "66", "67", "68", "69", "6A", "6J", "6K", "6Q", "6T",
                              "77", "78", "79", "7A", "7J", "7K", "7Q", "7T",
                              "88", "89", "8A", "8J", "8K", "8Q", "8T",
                              "99", "9A", "9J", "9K", "9Q", "9T",
                              "AA", "AJ", "AK", "AQ", "AT",
                              "JJ", "JQ", "JK", "JT",
                              "KK", "KQ", "KT",
                              "QQ","QT",
                              "TT")

numCores = detectCores()
registerDoParallel(numCores)

results =
  foreach(i=1:5, .packages = "tidyverse") %dopar% {
      PLAYER_WIN = 0
      DEALER_WIN = 0
      TIE = 0
	  # Replace Generation Here
      df = read.csv("C:/Users/jasonwong/Desktop/AgentQTable_Gen49_951W.csv", header=TRUE, sep=",")
      df = df %>% arrange(desc(str_sub(state, str_length(state), str_length(state))), str_length(state))
      for(i in (1:2500)) {
          curr_state = new_instance(df)
          curr_status = "1"
          while(curr_status != "0") {
              # print(str_c("Simulation ", as.character(i), " : ", curr_state))
              # Find best action
              best_action = agent(curr_state, df)
              # Send action to environment to calculate next state
              new_state = environment(curr_state, best_action)
              # # Reward agent based on action and next state
              reward(curr_state, new_state, df, best_action)
  
              # Update game variables
              new_status = decrypt_state(new_state)[[3]]
              curr_status = new_status
              curr_state = new_state
          }
      }
      return(c(PLAYER_WIN, df))
  }

for(i in 1:5) {
    best_index = 0
    if (results[[i]][[1]] > best_index) {
        best_index = i
    }
}

best_simulation = results[[best_index]]
stopImplicitCluster()

temp = as.data.frame(best_simulation)[,2:5] %>%
    filter(str_detect(str_sub(state, 1,3), "(.){2}-")) %>%
    filter(str_detect(str_sub(state, 3,5), "-(.){1}-")) %>%
    mutate(plr = str_sub(state, 1,2),
           dlr = str_sub(state, 4,4))

temp$action = toupper(str_sub(names(temp)[apply(temp[2:4], 1, which.max)+1],1,1))

for (i in 1:dim(temp)[1]) {
    instance = temp[i,]
    decision_matrix[instance$plr, instance$dlr] = instance$action
}
decision_frame = as.data.frame(decision_matrix)

# Replace Next Generation Here
write.csv(as.data.frame(best_simulation)[,2:5],
          str_c("C:/Users/jasonwong/Desktop/AgentQTable_Gen50_",
                best_simulation[[1]][[1]], "W.csv"),
          row.names = FALSE)
write.csv(decision_frame,
          str_c("C:/Users/jasonwong/Desktop/DecisionMatrix_Gen50_",
                best_simulation[[1]][[1]], "W.csv"))



