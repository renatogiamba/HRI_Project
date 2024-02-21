import sys
sys.path.append("blackjack")
import blackjack_env

if __name__ == "__main__":
    env = blackjack_env.BlackjackEnv()
    sum_hand, dealer_card, usable_ace = env.reset()
    print env.deck
    print env.player_hand
    print env.dealer_hand
    print sum_hand
    print dealer_card
    print usable_ace