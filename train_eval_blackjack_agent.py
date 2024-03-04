import numpy as np
import os
import sys
import time
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("blackjack")
import pepper_cmd
import blackjack_agent
import blackjack_env

if __name__ == "__main__":
    env = blackjack_env.BlackjackEnv()

    learning_rate = 0.01
    n_episodes = 2
    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2)  
    final_epsilon = 0.1
    agent = blackjack_agent.BlackjackAgent(
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
    agent.q_values = np.loadtxt("q_values.txt", dtype=np.float)

    scores = []
    for episode in range(16):
        obs,_ = env.reset()
        done = False
        score = 0

        while not done:
            action = agent.act(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)
            score += reward

            done = terminated or truncated
            obs = next_obs

        print "Eval Episode %d: Score = %f" %(episode+1, score)
        scores.append(score)
    print "Eval Avg Score = %f" %(sum(scores) / n_episodes)
