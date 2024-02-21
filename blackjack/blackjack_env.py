import collections
import random

class Card():
    def __init__(self, type, suit, value):
        self.type = type
        self.suit = suit
        self.value = value
    
    def __str__(self):
        return "Card(" + self.type + " " + self.suit + ")"
    
    def __repr__(self):
        return "Card(" + self.type + " " + self.suit + ")"


class BlackjackEnv():
    def __init__(self):
        self.num_actions = 2
        self.deck, self.deck_values = self.reset_deck()
        self.player_hand = []
        self.player_hand_values = []
        self.dealer_hand = []
        self.dealer_hand_values = []
    
    def reset_deck(self):
        deck = [
            Card("A", "hearts", 1),
            Card("2", "hearts", 2),
            Card("3", "hearts", 3),
            Card("4", "hearts", 4),
            Card("5", "hearts", 5),
            Card("6", "hearts", 6),
            Card("7", "hearts", 7),
            Card("8", "hearts", 8),
            Card("9", "hearts", 9),
            Card("10", "hearts", 10),
            Card("J", "hearts", 10),
            Card("Q", "hearts", 10),
            Card("K", "hearts", 10),
            Card("A", "diamonds", 1),
            Card("2", "diamonds", 2),
            Card("3", "diamonds", 3),
            Card("4", "diamonds", 4),
            Card("5", "diamonds", 5),
            Card("6", "diamonds", 6),
            Card("7", "diamonds", 7),
            Card("8", "diamonds", 8),
            Card("9", "diamonds", 9),
            Card("10", "diamonds", 10),
            Card("J", "diamonds", 10),
            Card("Q", "diamonds", 10),
            Card("K", "diamonds", 10),
            Card("A", "clubs", 1),
            Card("2", "clubs", 2),
            Card("3", "clubs", 3),
            Card("4", "clubs", 4),
            Card("5", "clubs", 5),
            Card("6", "clubs", 6),
            Card("7", "clubs", 7),
            Card("8", "clubs", 8),
            Card("9", "clubs", 9),
            Card("10", "clubs", 10),
            Card("J", "clubs", 10),
            Card("Q", "clubs", 10),
            Card("K", "clubs", 10),
            Card("A", "spades", 1),
            Card("2", "spades", 2),
            Card("3", "spades", 3),
            Card("4", "spades", 4),
            Card("5", "spades", 5),
            Card("6", "spades", 6),
            Card("7", "spades", 7),
            Card("8", "spades", 8),
            Card("9", "spades", 9),
            Card("10", "spades", 10),
            Card("J", "spades", 10),
            Card("Q", "spades", 10),
            Card("K", "spades", 10)
        ]
        random.shuffle(deck)
        deck_values = map(lambda card: card.value, deck)
        return collections.deque(deck), collections.deque(deck_values)
    
    def draw_card(self):
        card = self.deck.popleft()
        card_value = self.deck_values.popleft()
        return card, card_value
    
    def usable_ace(self, hand):
        return int(1 in hand and sum(hand) + 10 <= 21)
    
    def sum_hand(self, hand):
        sum_hand = sum(hand)

        return sum_hand + 10 if self.usable_ace(hand) else sum_hand
    
    def is_blackjack(self, hand):
        return sorted(hand) == [1, 10]
    
    def is_bust(self, hand):
        return self.sum_hand(hand) > 21
    
    def score(self, hand, busted):
        return 0 if busted else self.sum_hand(hand)
    
    def get_observation(self):
        return (
            self.sum_hand(self.player_hand_values),
            self.dealer_hand_values[0],
            self.usable_ace(self.player_hand_values)
        )
    
    def sample_action(self):
        return random.randint(0, 1)
    
    def reset(self):
        self.deck,self.deck_values = self.reset_deck()

        card, card_value = self.draw_card()
        self.player_hand.append(card)
        self.player_hand_values.append(card_value)
        card, card_value = self.draw_card()
        self.player_hand.append(card)
        self.player_hand_values.append(card_value)
        card, card_value = self.draw_card()
        self.dealer_hand.append(card)
        self.dealer_hand_values.append(card_value)

        return self.get_observation(), {}
    
    def step(self, action):
        if action == 0:
            terminated = True
            while self.sum_hand(self.dealer_hand_values) < 17:
                card, card_value = self.draw_card()
                self.dealer_hand.append(card)
                self.dealer_hand_values.append(card_value)
            player_score = self.score(self.player_hand_values, False)
            dealer_score = self.score(
                self.dealer_hand_values, self.is_bust(self.dealer_hand_values)
            )
            reward = float(player_score > dealer_score) - float(player_score < dealer_score)
            if self.is_blackjack(self.player_hand_values) and\
                not self.is_blackjack(self.dealer_hand_values):
                reward = 1.5
        elif action == 1:
            card, card_value = self.draw_card()
            self.player_hand.append(card)
            self.player_hand_values.append(card_value)
            busted = self.is_bust(self.player_hand_values)
            terminated = busted
            reward = -1. if busted else 0.
        else:
            terminated = False
            reward = 0.
        
        return self.get_observation(), reward, terminated, False, {}
