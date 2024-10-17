"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import os

# Import your game logic
import game
import ai

class SixtySixGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sixty-Six Card Game")
        self.game = None
        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Top layout: Trump card and AI's hand
        top_layout = QHBoxLayout()
        self.trump_card_label = QLabel()
        top_layout.addWidget(QLabel("Trump Card:"))
        top_layout.addWidget(self.trump_card_label)
        self.ai_hand_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("AI's Hand:"))
        top_layout.addLayout(self.ai_hand_layout)

        # Middle layout: Played cards area
        middle_layout = QHBoxLayout()
        self.played_cards_layout = QHBoxLayout()
        middle_layout.addLayout(self.played_cards_layout)

        # Bottom layout: Player's hand and buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Your Hand:"))
        self.player_hand_layout = QHBoxLayout()
        bottom_layout.addLayout(self.player_hand_layout)
        # Add Close Deck button
        self.close_deck_button = QPushButton("Close Deck")
        self.close_deck_button.clicked.connect(self.close_deck)
        bottom_layout.addWidget(self.close_deck_button)

        # Assemble layouts
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def load_card_image(self, card):
        # card is an instance of Card
        filename = f"{card.value.lower()}_{card.suit}.gif"
        path = os.path.join('Images', filename)
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Failed to load image: {path}")
            # Optionally use a placeholder image
        return pixmap

    def start_new_game(self):
        # Initialize players
        self.player = game.Player("Player")
        self.ai_agent = ai.QLearningAgent("AI")
        self.ai_agent.epsilon = 0  # Deterministic AI for testing

        # Start the game session
        self.game = game.SixtySixGame(self.player, self.ai_agent)
        self.last_player_card = None
        self.last_ai_card = None
        self.game.current_starter = self.player
        self.game.phase = 1

        # Update GUI elements
        self.update_trump_card()
        self.update_ai_hand()
        self.update_player_hand()
        self.update_played_cards()
        self.close_deck_button.setEnabled(True)
        self.current_turn()

    def update_trump_card(self):
        pixmap = self.load_card_image(self.game.trump_card)
        self.trump_card_label.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))

    def update_ai_hand(self):
        # Clear existing cards
        for i in reversed(range(self.ai_hand_layout.count())):
            widget = self.ai_hand_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display card backs
        for _ in self.ai_agent.hand:
            card_back_label = QLabel()
            pixmap = QPixmap(os.path.join('Images', 'back.gif'))
            card_back_label.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))
            self.ai_hand_layout.addWidget(card_back_label)

    def update_player_hand(self):
        # Clear existing cards
        for i in reversed(range(self.player_hand_layout.count())):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display player's cards
        for index, card in enumerate(self.player.hand):
            card_button = QPushButton()
            pixmap = self.load_card_image(card)
            icon = QIcon(pixmap)
            card_button.setIcon(icon)
            card_button.setIconSize(pixmap.size())
            card_button.clicked.connect(lambda checked, idx=index: self.player_card_clicked(idx))
            self.player_hand_layout.addWidget(card_button)

    def update_played_cards(self, player_card=None, ai_card=None):
        # Clear existing cards
        for i in reversed(range(self.played_cards_layout.count())):
            widget = self.played_cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display played cards
        if player_card:
            player_label = QLabel("You played:")
            pixmap = self.load_card_image(player_card)
            player_card_label = QLabel()
            player_card_label.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))
            self.played_cards_layout.addWidget(player_label)
            self.played_cards_layout.addWidget(player_card_label)
        if ai_card:
            ai_label = QLabel("AI played:")
            pixmap = self.load_card_image(ai_card)
            ai_card_label = QLabel()
            ai_card_label.setPixmap(pixmap.scaled(80, 120, Qt.KeepAspectRatio))
            self.played_cards_layout.addWidget(ai_label)
            self.played_cards_layout.addWidget(ai_card_label)

    def close_deck(self):
        if not self.game.deck_closed:
            self.player.wants_to_close_deck = True
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.player.closed = True
            self.game.deck_closed = True
            self.close_deck_button.setEnabled(False)
            QMessageBox.information(self, "Deck Closed", "You have closed the deck. The game is now in phase 2.")

    def player_card_clicked(self, card_index):
        selected_card = self.player.hand[card_index]

        if self.game.current_starter == self.player:
            # Player is leading
            valid_cards = self.player.hand
            self.player.play_card(selected_card)
            self.last_player_card = selected_card

            # Update GUI
            self.update_player_hand()
            self.update_played_cards(player_card=selected_card)

            # Now AI responds
            self.ai_respond_turn(selected_card)
        else:
            # Player is responding to AI
            valid_cards = self.player.get_valid_cards(
                current_card=self.last_ai_card,
                phase=self.game.phase,
                trump=self.game.trump
            )
            if selected_card not in valid_cards:
                QMessageBox.warning(self, "Invalid Move", "You cannot play that card.")
                return
            self.player.play_card(selected_card)
            self.last_player_card = selected_card

            # Update GUI
            self.update_player_hand()
            self.update_played_cards(player_card=selected_card, ai_card=self.last_ai_card)

            # Determine trick winner
            winner = self.game.determine_trick_winner(self.last_ai_card, self.ai_agent, selected_card, self.player)
            winner.add_trick([self.last_ai_card, selected_card])
            QMessageBox.information(self, "Trick Result", f"{winner.name} wins the trick.")

            # Check for game end or continue
            if not self.player.hand:
                self.end_game()
                return
            else:
                # Draw new cards if deck isn't empty and phase is 1
                if self.game.deck.cards and self.game.phase != 2:
                    winner.draw_cards(self.game.deck)
                    loser = self.player if winner != self.player else self.ai_agent
                    loser.draw_cards(self.game.deck)
                    # Update hands
                    self.update_player_hand()
                    self.update_ai_hand()
                # Set next starter
                self.game.current_starter = winner
                self.current_turn()

    def ai_respond_turn(self, player_card):
        # Check if AI wants to close the deck
        if not self.game.deck_closed and self.ai_agent.call_close_deck():
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.ai_agent.closed = True
            self.game.deck_closed = True
            QMessageBox.information(self, "Deck Closed", "The AI has closed the deck. The game is now in phase 2.")
            self.close_deck_button.setEnabled(False)

        ai_card = self.ai_agent.choose_card(
            current_card=player_card,
            phase=self.game.phase,
            trump=self.game.trump
        )
        if ai_card:
            self.ai_agent.play_card(ai_card)
            self.last_ai_card = ai_card
            self.update_ai_hand()
            self.update_played_cards(player_card=player_card, ai_card=ai_card)

            # Determine trick winner
            winner = self.game.determine_trick_winner(player_card, self.player, ai_card, self.ai_agent)
            winner.add_trick([player_card, ai_card])
            QMessageBox.information(self, "Trick Result", f"{winner.name} wins the trick.")

            # Check for game end or continue
            if not self.player.hand:
                self.end_game()
                return
            else:
                # Draw new cards if deck isn't empty and phase is 1
                if self.game.deck.cards and self.game.phase != 2:
                    winner.draw_cards(self.game.deck)
                    loser = self.player if winner != self.player else self.ai_agent
                    loser.draw_cards(self.game.deck)
                    # Update hands
                    self.update_player_hand()
                    self.update_ai_hand()
                # Set next starter
                self.game.current_starter = winner
                self.current_turn()
        else:
            # AI closed the deck
            pass

    def ai_play_turn(self):
        # Check if AI wants to close the deck
        if not self.game.deck_closed and self.ai_agent.call_close_deck():
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.ai_agent.closed = True
            self.game.deck_closed = True
            QMessageBox.information(self, "Deck Closed", "The AI has closed the deck. The game is now in phase 2.")
            self.close_deck_button.setEnabled(False)

        # AI plays first
        ai_card = self.ai_agent.choose_card(phase=self.game.phase, trump=self.game.trump)
        if ai_card:
            self.ai_agent.play_card(ai_card)
            self.last_ai_card = ai_card
            self.update_ai_hand()
            self.update_played_cards(ai_card=ai_card)
            # Now it's the player's turn to respond
            QMessageBox.information(self, "AI's Turn", f"The AI played: {ai_card}. Your turn to respond.")
        else:
            # AI closed the deck
            pass

    def current_turn(self):
        if self.game.current_starter == self.player:
            # Player plays first
            self.last_ai_card = None
            QMessageBox.information(self, "Your Turn", "It's your turn to play first.")
        else:
            # AI plays first
            self.ai_play_turn()

    def end_game(self):
        player_points = self.player.calculate_points()
        ai_points = self.ai_agent.calculate_points()
        result_message = f"Your Points: {player_points}\nAI Points: {ai_points}\n"

        if player_points >= 66:
            result_message += "You have won!"
        elif ai_points >= 66:
            result_message += "The AI has won!"
        else:
            result_message += "No one reached 66 points."

        QMessageBox.information(self, "Game Over", result_message)

        # Offer to play again
        reply = QMessageBox.question(self, 'New Game', 'Do you want to play again?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.start_new_game()
        else:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SixtySixGUI()
    window.show()
    sys.exit(app.exec_())
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

# Import your game logic
import game
import ai

class SixtySixGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sixty-Six Card Game")
        self.setMinimumSize(800, 600)  # Set a minimum window size
        self.game = None
        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Top layout: Trump card and AI's hand
        top_layout = QHBoxLayout()
        trump_layout = QVBoxLayout()
        trump_label = QLabel("Trump Card:")
        self.trump_card_label = QLabel()
        trump_layout.addWidget(trump_label)
        trump_layout.addWidget(self.trump_card_label)
        top_layout.addLayout(trump_layout)

        # AI Hand Layout with Scroll Area
        ai_hand_container = QVBoxLayout()
        ai_label = QLabel("AI's Hand:")
        ai_hand_container.addWidget(ai_label)
        self.ai_hand_layout = QGridLayout()
        ai_hand_widget = QWidget()
        ai_hand_widget.setLayout(self.ai_hand_layout)
        self.ai_hand_scroll_area = QScrollArea()
        self.ai_hand_scroll_area.setWidgetResizable(True)
        self.ai_hand_scroll_area.setWidget(ai_hand_widget)
        self.ai_hand_scroll_area.setFixedHeight(150)
        ai_hand_container.addWidget(self.ai_hand_scroll_area)
        top_layout.addLayout(ai_hand_container)

        # Middle layout: Played cards area
        middle_layout = QHBoxLayout()
        self.played_cards_layout = QHBoxLayout()
        middle_layout.addLayout(self.played_cards_layout)

        # Bottom layout: Player's hand and buttons
        bottom_layout = QHBoxLayout()
        player_hand_container = QVBoxLayout()
        player_label = QLabel("Your Hand:")
        player_hand_container.addWidget(player_label)
        self.player_hand_layout = QGridLayout()
        player_hand_widget = QWidget()
        player_hand_widget.setLayout(self.player_hand_layout)
        self.player_hand_scroll_area = QScrollArea()
        self.player_hand_scroll_area.setWidgetResizable(True)
        self.player_hand_scroll_area.setWidget(player_hand_widget)
        self.player_hand_scroll_area.setFixedHeight(200)
        player_hand_container.addWidget(self.player_hand_scroll_area)
        bottom_layout.addLayout(player_hand_container)

        # Add Close Deck button
        self.close_deck_button = QPushButton("Close Deck")
        self.close_deck_button.clicked.connect(self.close_deck)
        bottom_layout.addWidget(self.close_deck_button)

        # Assemble layouts
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def load_card_image(self, card):
        # card is an instance of Card
        filename = f"{card.value.lower()}_{card.suit}.gif"
        path = os.path.join('Images', filename)
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"Failed to load image: {path}")
            # Optionally use a placeholder image
            pixmap = QPixmap(os.path.join('Images', 'placeholder.gif'))
        pixmap = pixmap.scaled(80, 120, Qt.KeepAspectRatio)
        return pixmap

    def start_new_game(self):
        # Initialize players
        self.player = game.Player("Player")
        self.ai_agent = ai.QLearningAgent("AI")
        self.ai_agent.epsilon = 0  # Deterministic AI for testing

        # Start the game session
        self.game = game.SixtySixGame(self.player, self.ai_agent)
        self.last_player_card = None
        self.last_ai_card = None
        self.game.current_starter = self.player
        self.game.phase = 1

        # Update GUI elements
        self.update_trump_card()
        self.update_ai_hand()
        self.update_player_hand()
        self.update_played_cards()
        self.close_deck_button.setEnabled(True)
        self.current_turn()

    def update_trump_card(self):
        pixmap = self.load_card_image(self.game.trump_card)
        self.trump_card_label.setPixmap(pixmap)

    def update_ai_hand(self):
        # Clear existing cards
        for i in reversed(range(self.ai_hand_layout.count())):
            widget = self.ai_hand_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display card backs in a grid
        columns = 5  # Adjust the number of columns as needed
        for index, _ in enumerate(self.ai_agent.hand):
            row = index // columns
            col = index % columns
            card_back_label = QLabel()
            pixmap = QPixmap(os.path.join('Images', 'back.gif'))
            pixmap = pixmap.scaled(80, 120, Qt.KeepAspectRatio)
            card_back_label.setPixmap(pixmap)
            self.ai_hand_layout.addWidget(card_back_label, row, col)

    def update_player_hand(self):
        # Clear existing cards
        for i in reversed(range(self.player_hand_layout.count())):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display player's cards in a grid
        columns = 5  # Adjust as needed
        for index, card in enumerate(self.player.hand):
            row = index // columns
            col = index % columns
            card_button = QPushButton()
            pixmap = self.load_card_image(card)
            icon = QIcon(pixmap)
            card_button.setIcon(icon)
            card_button.setIconSize(pixmap.size())
            card_button.clicked.connect(lambda checked, idx=index: self.player_card_clicked(idx))
            self.player_hand_layout.addWidget(card_button, row, col)

    def update_played_cards(self, player_card=None, ai_card=None):
        # Clear existing cards
        for i in reversed(range(self.played_cards_layout.count())):
            widget = self.played_cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Display played cards
        if player_card:
            player_label = QLabel("You played:")
            pixmap = self.load_card_image(player_card)
            player_card_label = QLabel()
            player_card_label.setPixmap(pixmap)
            self.played_cards_layout.addWidget(player_label)
            self.played_cards_layout.addWidget(player_card_label)
        if ai_card:
            ai_label = QLabel("AI played:")
            pixmap = self.load_card_image(ai_card)
            ai_card_label = QLabel()
            ai_card_label.setPixmap(pixmap)
            self.played_cards_layout.addWidget(ai_label)
            self.played_cards_layout.addWidget(ai_card_label)

    def close_deck(self):
        if not self.game.deck_closed:
            self.player.wants_to_close_deck = True
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.player.closed = True
            self.game.deck_closed = True
            self.close_deck_button.setEnabled(False)
            QMessageBox.information(self, "Deck Closed", "You have closed the deck. The game is now in phase 2.")

    def player_card_clicked(self, card_index):
        selected_card = self.player.hand[card_index]

        if self.game.current_starter == self.player:
            # Player is leading
            self.player.play_card(selected_card)
            self.last_player_card = selected_card

            # Update GUI
            self.update_player_hand()
            self.update_played_cards(player_card=selected_card)

            # Now AI responds
            self.ai_respond_turn(selected_card)
        else:
            # Player is responding to AI
            valid_cards = self.player.get_valid_cards(
                current_card=self.last_ai_card,
                phase=self.game.phase,
                trump=self.game.trump
            )
            if selected_card not in valid_cards:
                QMessageBox.warning(self, "Invalid Move", "You cannot play that card.")
                return
            self.player.play_card(selected_card)
            self.last_player_card = selected_card

            # Update GUI
            self.update_player_hand()
            self.update_played_cards(player_card=selected_card, ai_card=self.last_ai_card)

            # Determine trick winner
            winner = self.game.determine_trick_winner(self.last_ai_card, self.ai_agent, selected_card, self.player)
            winner.add_trick([self.last_ai_card, selected_card])
            QMessageBox.information(self, "Trick Result", f"{winner.name} wins the trick.")

            # Check for game end or continue
            if not self.player.hand:
                self.end_game()
                return
            else:
                # Draw new cards if deck isn't empty and phase is 1
                if self.game.deck.cards and self.game.phase != 2:
                    winner.draw_cards(self.game.deck)
                    loser = self.player if winner != self.player else self.ai_agent
                    loser.draw_cards(self.game.deck)
                    # Update hands
                    self.update_player_hand()
                    self.update_ai_hand()
                # Set next starter
                self.game.current_starter = winner
                self.current_turn()

    def ai_respond_turn(self, player_card):
        # Check if AI wants to close the deck
        if not self.game.deck_closed and self.ai_agent.call_close_deck():
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.ai_agent.closed = True
            self.game.deck_closed = True
            QMessageBox.information(self, "Deck Closed", "The AI has closed the deck. The game is now in phase 2.")
            self.close_deck_button.setEnabled(False)

        ai_card = self.ai_agent.choose_card(
            current_card=player_card,
            phase=self.game.phase,
            trump=self.game.trump
        )
        if ai_card:
            self.ai_agent.play_card(ai_card)
            self.last_ai_card = ai_card
            self.update_ai_hand()
            self.update_played_cards(player_card=player_card, ai_card=ai_card)

            # Determine trick winner
            winner = self.game.determine_trick_winner(player_card, self.player, ai_card, self.ai_agent)
            winner.add_trick([player_card, ai_card])
            QMessageBox.information(self, "Trick Result", f"{winner.name} wins the trick.")

            # Check for game end or continue
            if not self.player.hand:
                self.end_game()
                return
            else:
                # Draw new cards if deck isn't empty and phase is 1
                if self.game.deck.cards and self.game.phase != 2:
                    winner.draw_cards(self.game.deck)
                    loser = self.player if winner != self.player else self.ai_agent
                    loser.draw_cards(self.game.deck)
                    # Update hands
                    self.update_player_hand()
                    self.update_ai_hand()
                # Set next starter
                self.game.current_starter = winner
                self.current_turn()
        else:
            # AI closed the deck
            pass

    def ai_play_turn(self):
        # Check if AI wants to close the deck
        if not self.game.deck_closed and self.ai_agent.call_close_deck():
            self.game.phase = 2
            self.game.deck.cards = []  # Remove remaining cards from the deck
            self.ai_agent.closed = True
            self.game.deck_closed = True
            QMessageBox.information(self, "Deck Closed", "The AI has closed the deck. The game is now in phase 2.")
            self.close_deck_button.setEnabled(False)

        # AI plays first
        ai_card = self.ai_agent.choose_card(phase=self.game.phase, trump=self.game.trump)
        if ai_card:
            self.ai_agent.play_card(ai_card)
            self.last_ai_card = ai_card
            self.update_ai_hand()
            self.update_played_cards(ai_card=ai_card)
            # Now it's the player's turn to respond
            QMessageBox.information(self, "AI's Turn", f"The AI played: {ai_card}. Your turn to respond.")
        else:
            # AI closed the deck
            pass

    def current_turn(self):
        if self.game.current_starter == self.player:
            # Player plays first
            self.last_ai_card = None
            QMessageBox.information(self, "Your Turn", "It's your turn to play first.")
        else:
            # AI plays first
            self.ai_play_turn()

    def end_game(self):
        player_points = self.player.calculate_points()
        ai_points = self.ai_agent.calculate_points()
        result_message = f"Your Points: {player_points}\nAI Points: {ai_points}\n"

        if player_points >= 66:
            result_message += "You have won!"
        elif ai_points >= 66:
            result_message += "The AI has won!"
        else:
            result_message += "No one reached 66 points."

        QMessageBox.information(self, "Game Over", result_message)

        # Offer to play again
        reply = QMessageBox.question(self, 'New Game', 'Do you want to play again?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.start_new_game()
        else:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SixtySixGUI()
    window.show()
    sys.exit(app.exec_())
