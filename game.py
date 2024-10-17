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
        self.special_points = 0
        self.set_points = 0
        self.trick_before_closing = False
        self.closed = False
        self.wants_to_close_deck = False  # New attribute

    def new_game(self):
        self.hand = []
        self.tricks = []
        self.points = 0
        self.special_points = 0
        self.trick_before_closing = False
        self.closed = False
        self.wants_to_close_deck = False

    # Start a new set
    def new_set(self):
        self.new_game()
        self.set_points = 0

    def draw_cards(self, deck, count=1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return card

    def add_trick(self, cards):
        self.tricks.extend(cards)
        self.check_for_last_trick()

    def check_for_last_trick(self):
        if len(self.hand) == 0:
            self.special_points += 10

    def calculate_points(self):
        self.points = sum(card.points for card in self.tricks) + self.special_points
        return self.points
    
    # Determine set points
    def determine_set_points(self, winner, loser):
        """Determine the game points according to the rules of 'Sixty-Six'"""
        if winner.closed:  # If the deck is closed
            if winner.points >= 66:
                if loser.points >= 33:
                    return 1  # 1 game point for the winner
                elif len(loser.tricks) == 0:
                    return 3  # 3 game points because the opponent made no tricks (Black)
                else:
                    return 2  # 2 game points because the opponent is Schneider (under 33 points)
            else:
                if len(loser.tricks) == 0 and loser.trick_before_closing:
                    return 3  # Loser gains 3 game points because the winner didn't reach 66 points and loser made no tricks
                else:
                    return 2  # Loser gains 2 game points because the winner didn't reach 66 points
        else:  # If the deck is not closed
            if winner.points >= 66:
                if loser.points >= 33 and not loser.closed:
                    return 1  # 1 game point for the winner
                elif len(loser.tricks) == 0:
                    return 3  # 3 game points because the opponent is Black
                else:
                    return 2  # 2 game points because the opponent is Schneider (under 33 points)
        # In case of a tie (both 65 to 65)
        return 0

    def calculate_set_points(self, value=0):
        self.set_points += value
        return self.set_points

    def call_close_deck(self):
        return self.wants_to_close_deck and not self.closed

    def get_valid_cards(self, current_card=None, phase=1, trump=None):
        if phase == 1 or current_card is None:
            return self.hand
        else:
            valid_cards = [card for card in self.hand if card.suit == current_card.suit]
            if not valid_cards:
                valid_cards = [card for card in self.hand if card.suit == trump]
                if not valid_cards:
                    valid_cards = self.hand
            return valid_cards

    def __repr__(self):
        return f"{self.name} - Points: {self.points}"

# SixtySixGame class
class SixtySixGame:
    def __init__(self, player1, player2):
        self.player1 = player1  # Assuming player1 is the human player
        self.player2 = player2  # Assuming player2 is the AI
        self.deck = Deck()
        self.trump_card = self.deck.cards[0]  # First card in the deck is trump
        self.trump = self.trump_card.suit
        self.open_pile = [self.trump_card]
        self.current_starter = self.player1  # The first player starts
        self.phase = 1
        self.deck_closed = False
        # Both players draw 6 cards
        self.player1.draw_cards(self.deck, 6)
        self.player2.draw_cards(self.deck, 6)

    def determine_trick_winner(self, lead_card, lead_player, follow_card, follow_player):
        # Check if either card is trump
        if lead_card.suit == self.trump and follow_card.suit != self.trump:
            return lead_player
        elif follow_card.suit == self.trump and lead_card.suit != self.trump:
            return follow_player
        # If both cards have the same suit
        elif lead_card.suit == follow_card.suit:
            # Compare the values
            if VALUES.index(lead_card.value) < VALUES.index(follow_card.value):
                return lead_player
            else:
                return follow_player
        else:
            # The player who led wins
            return lead_player

    def play_round(self):
        while self.player1.hand and self.player2.hand:
            if self.current_starter == self.player1:
                if not self.deck_closed and self.player1.call_close_deck():
                    self.phase = 2
                    self.deck.cards = []
                    self.player1.closed = True
                    self.deck_closed = True
                card1 = self.player1.choose_card(phase=self.phase, trump=self.trump)
                if card1:
                    self.player1.play_card(card1)
                else:
                    # Player1 closed the deck
                    pass

                if not self.deck_closed and self.player2.call_close_deck():
                    self.phase = 2
                    self.deck.cards = []
                    self.player2.closed = True
                    self.deck_closed = True
                card2 = self.player2.choose_card(current_card=card1, phase=self.phase, trump=self.trump)
                if card2:
                    self.player2.play_card(card2)
                else:
                    # Player2 closed the deck
                    pass

                if card1 and card2:
                    winner = self.determine_trick_winner(card1, self.player1, card2, self.player2)
                    winner.add_trick([card1, card2])

                    # Winner draws a card first if deck is not empty and phase is 1
                    if self.deck.cards and self.phase != 2:
                        winner.draw_cards(self.deck)
                        loser = self.player1 if winner != self.player1 else self.player2
                        loser.draw_cards(self.deck)

                    # Next starter is the winner
                    self.current_starter = winner
            else:
                if not self.deck_closed and self.player2.call_close_deck():
                    self.phase = 2
                    self.deck.cards = []
                    self.player2.closed = True
                    self.deck_closed = True
                card2 = self.player2.choose_card(phase=self.phase, trump=self.trump)
                if card2:
                    self.player2.play_card(card2)
                else:
                    # Player2 closed the deck
                    pass

                if not self.deck_closed and self.player1.call_close_deck():
                    self.phase = 2
                    self.deck.cards = []
                    self.player1.closed = True
                    self.deck_closed = True
                card1 = self.player1.choose_card(current_card=card2, phase=self.phase, trump=self.trump)
                if card1:
                    self.player1.play_card(card1)
                else:
                    # Player1 closed the deck
                    pass

                if card1 and card2:
                    winner = self.determine_trick_winner(card2, self.player2, card1, self.player1)
                    winner.add_trick([card2, card1])

                    # Winner draws a card first if deck is not empty and phase is 1
                    if self.deck.cards and self.phase != 2:
                        winner.draw_cards(self.deck)
                        loser = self.player1 if winner != self.player1 else self.player2
                        loser.draw_cards(self.deck)

                    # Next starter is the winner
                    self.current_starter = winner

    # End game method
    def end_game(self):
        points1 = self.player1.calculate_points()
        points2 = self.player2.calculate_points()
        # Determine winner
        if points1 >= 66:
            set_points = self.player1.determine_set_points(self.player1, self.player2)
            self.player1.calculate_set_points(set_points)
            return self.player1
        elif points2 >= 66:
            set_points = self.player2.determine_set_points(self.player2, self.player1)
            self.player2.calculate_set_points(set_points)
            return self.player2
        elif len(self.player1.hand) == 0:
            # Player1 closed and didn't reach 66 points -> Player2 wins
            if self.player1.closed:
                set_points = self.player1.determine_set_points(self.player2, self.player1)
                self.player2.calculate_set_points(set_points)
                return self.player2
            # Player2 closed and didn't reach 66 points -> Player1 wins
            elif self.player2.closed:
                set_points = self.player2.determine_set_points(self.player1, self.player2)
                self.player1.calculate_set_points(set_points)
                return self.player1
        else:
            return None

    def end_set(self):
        set_points1 = self.player1.set_points
        set_points2 = self.player2.set_points
        if set_points1 >= 7:
            return self.player1
        elif set_points2 >= 7:
            return self.player2
        else:
            return None
