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
    def __init__(self, natural=True, sab=False):
        self.natural = natural
        self.sab = sab
        self.deck = self.reset_deck()
        self.player_hand = []
        self.dealer_hand = []
    
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
        return collections.deque(deck)
    
    def draw_card(self):
        card = self.deck.popleft()
        return card
    
    def usable_ace(self, hand):
        aces = list(filter(lambda card: card.type == "A", hand))
        sum_hand = sum(map(lambda card: card.value, hand))
        
        return int(len(aces) > 0 and sum_hand + 10 <= 21)
    
    def sum_hand(self, hand):
        sum_hand = sum(map(lambda card: card.value, hand))

        return sum_hand + 10 if self.usable_ace(hand) else sum_hand
    
    def reset(self):
        self.deck = self.reset_deck()
        self.player_hand.append(self.draw_card())
        self.player_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())

        return (
            self.sum_hand(self.player_hand),
            self.dealer_hand[0].value,
            self.usable_ace(self.player_hand)
        )
    
    def step(self, action):
        if action == 0:
            pass
        elif action == 1:
            pass
        else:
            reward = 0.