from blackjack_env import BlackjackEnv
import numpy as np
import json
from collections import defaultdict
#from tqdm import tqdm

env = BlackjackEnv()

class BlackjackAgent:
    def __init__(
        self,
        learning_rate,
        initial_epsilon,
        epsilon_decay,
        final_epsilon,
        discount_factor = 0.95,
    ):
        
        #self.q_values = defaultdict(lambda: np.zeros(env.num_actions))
        self.q_values = np.zeros((708, env.num_actions))
        self.obs_keys = {}
        i = 0
        for player_sum in range(32):
            for dealer_card in range(11):
                for usable_ace in range(2):
                    self.obs_keys[(player_sum, dealer_card, usable_ace)] = i
                    i += 1

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs):
        if np.random.random() < self.epsilon:
            return env.sample_action()
        
        else:
            return int(np.argmax(self.q_values[self.obs_keys[obs]]))
            #return int(np.argmax(self.q_values[obs]))

    def act(self, obs):
        return int(np.argmax(self.q_values[self.obs_keys[obs]]))
        #return int(np.argmax(self.q_values[obs]))


    def update(
        self,
        obs,
        action,
        reward,
        terminated,
        next_obs,
    ):
        obs = self.obs_keys[obs]
        next_obs = self.obs_keys[next_obs]
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - epsilon_decay)


learning_rate = 0.01
n_episodes = 2
start_epsilon = 1.0
epsilon_decay = start_epsilon / (n_episodes / 2)  
final_epsilon = 0.1
'''
agent = BlackjackAgent(
    learning_rate=learning_rate,
    initial_epsilon=start_epsilon,
    epsilon_decay=epsilon_decay,
    final_epsilon=final_epsilon,
)

scores = []
for episode in range(n_episodes):
    obs,_ = env.reset()
    done = False
    score = 0

    while not done:
        action = agent.get_action(obs)
        next_obs, reward, terminated, truncated, info = env.step(action)
        score += reward
        agent.update(obs, action, reward, terminated, next_obs)

        done = terminated or truncated
        obs = next_obs

    agent.decay_epsilon()
    print "Train Episode %d: Score = %f" %(episode+1, score)
    scores.append(score)
print "Train Avg Score = %f" %(sum(scores) / n_episodes)
np.savetxt("q_values.txt", agent.q_values)
agent.q_values = np.loadtxt("q_values_5M.txt", dtype=np.float)

scores = []
for episode in range(16):
    obs,_ = env.reset()
    done = False
    score = 0

    while not done:
        action = agent.act(obs)
        next_obs, reward, terminated, truncated, info = env.step(action)
        score += reward
        #agent.update(obs, action, reward, terminated, next_obs)

        done = terminated or truncated
        obs = next_obs

    #agent.decay_epsilon()
    print "Eval Episode %d: Score = %f" %(episode+1, score)
    scores.append(score)
print "Eval Avg Score = %f" %(sum(scores) / n_episodes)

#obs = (17,8,0)
#action = agent.act(obs)
#print 'action:%s' %(action)

'''