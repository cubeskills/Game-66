import random

# Definition of suits and values
SUITS = ['heart', 'diamond', 'spade', 'club']
VALUES = ['ace', '10', 'king', 'queen', 'jack', '9']
POINTS = {'ace': 11, '10': 10, 'king': 4, 'queen': 3, 'jack': 2, '9': 0}

# Card class
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.points = POINTS[value]

    def __repr__(self):
        return f"{self.value} of {self.suit}"

# Deck class
class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in SUITS for value in VALUES]
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        else:
            return None

# Player class
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.tricks = []
        self.points = 0

    def new_game(self):
        self.hand = []
        self.tricks = []
        self.points = 0

    def draw_cards(self, deck, count=1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)

    def play_card(self, card):
        self.hand.remove(card)
        return card

    def add_trick(self, cards):
        self.tricks.extend(cards)

    def calculate_points(self):
        self.points = sum(card.points for card in self.tricks)
        return self.points

    def __repr__(self):
        return f"{self.name} - Points: {self.points}"

# SixtySixGame class
class SixtySixGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.deck = Deck()
        self.trump_card = self.deck.cards[0]  # Last card in the deck is trump
        self.trump = self.trump_card.suit
        self.open_pile = [self.trump_card]
        self.current_starter = self.player1  # The first player starts

        # Both players draw 6 cards
        self.player1.draw_cards(self.deck, 6)
        self.player2.draw_cards(self.deck, 6)

    def determine_trick_winner(self, card1, card2):
        # Check if either card is trump
        if card1.suit == self.trump and card2.suit != self.trump:
            return self.player1
        elif card2.suit == self.trump and card1.suit != self.trump:
            return self.player2
        # If both cards have the same suit
        elif card1.suit == card2.suit:
            # Compare the values
            if VALUES.index(card1.value) < VALUES.index(card2.value):
                return self.player1
            else:
                return self.player2
        else:
            # The player who led wins
            return self.current_starter

    def play_round(self):
        while self.player1.hand and self.player2.hand:
            if self.current_starter == self.player1:
                card1 = self.player1.choose_card()
                self.player1.play_card(card1)

                card2 = self.player2.choose_card(current_card=card1)
                self.player2.play_card(card2)
            else:
                card2 = self.player2.choose_card()
                self.player2.play_card(card2)

                card1 = self.player1.choose_card(current_card=card2)
                self.player1.play_card(card1)

            winner = self.determine_trick_winner(card1, card2)
            winner.add_trick([card1, card2])

            # Winner draws a card first
            if self.deck.cards:
                winner.draw_cards(self.deck)
                loser = self.player1 if winner != self.player1 else self.player2
                loser.draw_cards(self.deck)

            # Next starter is the winner
            self.current_starter = winner

    def end_game(self):
        points1 = self.player1.calculate_points()
        points2 = self.player2.calculate_points()
        if points1 >= 66:
            return self.player1
        elif points2 >= 66:
            return self.player2
        else:
            return None
