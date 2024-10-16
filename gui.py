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

        # Bottom layout: Player's hand
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Your Hand:"))
        self.player_hand_layout = QHBoxLayout()
        bottom_layout.addLayout(self.player_hand_layout)

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

        # Update GUI elements
        self.update_trump_card()
        self.update_ai_hand()
        self.update_player_hand()
        self.update_played_cards()

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

    def player_card_clicked(self, card_index):
        # Player selects a card to play
        player_card = self.player.hand[card_index]
        self.player.play_card(player_card)

        # AI responds
        ai_card = self.ai_agent.choose_card(current_card=player_card)
        self.ai_agent.play_card(ai_card)

        # Update GUI
        self.update_player_hand()
        self.update_ai_hand()
        self.update_played_cards(player_card=player_card, ai_card=ai_card)

        # Determine trick winner
        winner = self.game.determine_trick_winner(player_card, ai_card)
        winner.add_trick([player_card, ai_card])
        QMessageBox.information(self, "Trick Result", f"{winner.name} wins the trick.")

        # Check for game end or continue
        if not self.player.hand:
            self.end_game()
        else:
            # Draw new cards if deck isn't empty
            if self.game.deck.cards:
                winner.draw_cards(self.game.deck)
                loser = self.player if winner != self.player else self.ai_agent
                loser.draw_cards(self.game.deck)
            # Update hands
            self.update_player_hand()
            self.update_ai_hand()
            # Set next starter
            self.game.current_starter = winner

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
