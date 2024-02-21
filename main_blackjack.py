import sys
sys.path.append("blackjack")
import blackjack_env

if __name__ == "__main__":
    env = blackjack_env.BlackjackEnv()
    (sum_hand, dealer_card, usable_ace), _ = env.reset()
    print env.deck
    print env.player_hand
    print env.dealer_hand
    print sum_hand
    print dealer_card
    print usable_ace
    print "---------------------------"
    (sum_hand, dealer_card, usable_ace), reward, terminated, _, _ = env.step(0)
    print env.deck
    print env.player_hand
    print env.dealer_hand
    print sum_hand
    print dealer_card
    print usable_ace
    print reward
    print terminated
