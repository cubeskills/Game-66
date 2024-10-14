import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import game
import ai
import os

class SixtySixGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sixty-six")
        self.master.geometry("1000x800")  # Enlarged window size

        self.game = None
        self.player = game.Player("Player")
        self.ai_agent = ai.QLearningAgent("AI")

        # Dictionary for card images
        self.card_images = {}
        self.load_card_images()

        self.create_widgets()
        self.start_new_game()

    def load_card_images(self):
        # Load all card images into a dictionary
        image_folder = 'Images'  # Folder where the images are stored
        for filename in os.listdir(image_folder):
            if filename.endswith('.png'):
                card_name = filename[:-4]  # Remove the .png extension
                image_path = os.path.join(image_folder, filename)
                image = Image.open(image_path)
                # Use the new resampling mode LANCZOS instead of ANTIALIAS
                image = image.resize((100, 150), Image.Resampling.LANCZOS)
                self.card_images[card_name] = ImageTk.PhotoImage(image)

    def create_widgets(self):
        # Create frames
        self.top_frame = tk.Frame(self.master)
        self.top_frame.pack(pady=10)

        self.middle_frame = tk.Frame(self.master)
        self.middle_frame.pack(pady=10)

        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(pady=10)

        # Trump card
        self.trump_label = tk.Label(self.top_frame, text="Trump: ")
        self.trump_label.pack(side=tk.LEFT)

        # AI tricks
        self.ai_tricks_label = tk.Label(self.top_frame, text="AI Tricks: 0")
        self.ai_tricks_label.pack(side=tk.RIGHT)

        # Game field
        self.game_field_canvas = tk.Canvas(self.middle_frame, width=800, height=200)
        self.game_field_canvas.pack()

        # Player hand
        self.hand_label = tk.Label(self.bottom_frame, text="Your Hand:")
        self.hand_label.pack()

        self.hand_buttons = []

        # Start new game
        self.new_game_button = tk.Button(self.master, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(pady=5)

    def start_new_game(self):
        self.player.new_game()
        self.ai_agent.new_game()
        self.game = game.SixtySixGame(self.player, self.ai_agent)
        self.update_trump()
        self.update_hand()
        self.update_tricks()
        self.game_field_canvas.delete("all")
        self.master.update()

        # AI sometimes starts
        if self.game.current_starter == self.ai_agent:
            self.master.after(1000, self.ai_turn)

    def update_trump(self):
        trump_card = self.game.trump_card
        card_image = self.get_card_image(trump_card)
        if hasattr(self, 'trump_image_label'):
            self.trump_image_label.destroy()
        self.trump_image_label = tk.Label(self.top_frame, image=card_image)
        self.trump_image_label.image = card_image  # Save reference
        self.trump_image_label.pack(side=tk.LEFT)

    def get_card_image(self, card):
        # Convert the card object to the image name
        card_name = str(card).lower().replace(' ', '_')
        return self.card_images.get(card_name, None)

    def update_hand(self):
        # Remove old buttons
        for btn in self.hand_buttons:
            btn.destroy()
        self.hand_buttons = []

        # Create new buttons with card images
        for idx, card in enumerate(self.player.hand):
            card_image = self.get_card_image(card)
            btn = tk.Button(self.bottom_frame, image=card_image, command=lambda idx=idx: self.player_turn(idx))
            btn.image = card_image  # Save reference
            btn.pack(side=tk.LEFT, padx=5)
            self.hand_buttons.append(btn)

    def update_tricks(self):
        self.ai_tricks_label.config(text=f"AI Tricks: {len(self.ai_agent.tricks)}")

    def player_turn(self, index):
        if self.game.current_starter != self.player:
            messagebox.showinfo("Info", "Please wait for your turn.")
            return

        player_card = self.player.hand[index]
        self.player.play_card(player_card)
        self.update_hand()
        self.game_field_canvas.delete("all")

        # Display player's card
        player_card_image = self.get_card_image(player_card)
        self.game_field_canvas.create_image(200, 100, image=player_card_image)
        self.game_field_canvas.image1 = player_card_image  # Save reference

        # AI responds
        ai_card = self.ai_agent.choose_card(current_card=player_card)
        self.ai_agent.play_card(ai_card)

        # Display AI's card
        ai_card_image = self.get_card_image(ai_card)
        self.game_field_canvas.create_image(600, 100, image=ai_card_image)
        self.game_field_canvas.image2 = ai_card_image  # Save reference

        self.after_move(player_card, ai_card)

    def ai_turn(self):
        if self.game.current_starter != self.ai_agent:
            return

        # AI plays first
        ai_card = self.ai_agent.choose_card()
        self.ai_agent.play_card(ai_card)
        self.game_field_canvas.delete("all")

        # Display AI's card
        ai_card_image = self.get_card_image(ai_card)
        self.game_field_canvas.create_image(600, 100, image=ai_card_image)
        self.game_field_canvas.image2 = ai_card_image  # Save reference

        # Activate buttons
        for btn in self.hand_buttons:
            btn.config(state=tk.NORMAL)

    def after_move(self, player_card, ai_card):
        # Determine the winner of the trick
        winner = self.game.determine_trick_winner(player_card, ai_card)
        winner.add_trick([player_card, ai_card])
        self.update_tricks()

        # Winner draws a card first
        if self.game.deck.cards:
            winner.draw_cards(self.game.deck)
            loser = self.player if winner != self.player else self.ai_agent
            loser.draw_cards(self.game.deck)
            self.update_hand()

        # Next starter is the winner
        self.game.current_starter = winner

        # Check for game end
        if not self.player.hand or not self.ai_agent.hand:
            self.end_game()
            return

        # Next turn
        if self.game.current_starter == self.ai_agent:
            self.master.after(1000, self.ai_turn)

    def end_game(self):
        player_points = self.player.calculate_points()
        ai_points = self.ai_agent.calculate_points()

        if player_points >= 66:
            messagebox.showinfo("Game Over", f"You have won!\nYour Points: {player_points}\nAI Points: {ai_points}")
        elif ai_points >= 66:
            messagebox.showinfo("Game Over", f"The AI has won!\nYour Points: {player_points}\nAI Points: {ai_points}")
        else:
            messagebox.showinfo("Game Over", f"Draw.\nYour Points: {player_points}\nAI Points: {ai_points}")

        # Start new game
        self.start_new_game()

def main():
    root = tk.Tk()
    app = SixtySixGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

