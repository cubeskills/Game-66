import random
import numpy as np
import game

# Q-Learning Agent
class QLearningAgent(game.Player):
    def __init__(self, name, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(name)
        self.q_table = {}  # {(state, action): value}
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.state_action_history = []

    def new_game(self):
        super().new_game()
        self.state_action_history = []

    def state_as_hash(self):
        # Simplified state representation
        hand_hash = tuple(sorted([f"{card.suit}-{card.value}" for card in self.hand]))
        return hand_hash

    def choose_card(self, current_card=None):
        state = self.state_as_hash()
        valid_cards = self.hand  # In a full implementation, only valid cards should be considered
        if np.random.rand() < self.epsilon:
            # Exploration
            action = random.choice(valid_cards)
        else:
            # Exploitation
            q_values = [self.q_table.get((state, card.value + card.suit), 0) for card in valid_cards]
            max_q = max(q_values)
            best_cards = [card for card, q in zip(valid_cards, q_values) if q == max_q]
            action = random.choice(best_cards)
        self.state_action_history.append((state, action))
        return action

    def play_card(self, card):
        super().play_card(card)

    def learn(self, reward):
        for state, action in reversed(self.state_action_history):
            old_q = self.q_table.get((state, action.value + action.suit), 0)
            new_q = old_q + self.alpha * (reward - old_q)
            self.q_table[(state, action.value + action.suit)] = new_q
            reward *= self.gamma  # Apply discount factor

# Training function
def train_ai(episodes):
    agent1 = QLearningAgent("Agent 1")
    agent2 = QLearningAgent("Agent 2")

    for episode in range(episodes):
        # Initialize agents for each episode
        agent1.new_game()
        agent2.new_game()

        session = game.SixtySixGame(agent1, agent2)
        session.play_round()

        winner = session.end_game()
        if winner == agent1:
            reward1 = 1
            reward2 = -1
        elif winner == agent2:
            reward1 = -1
            reward2 = 1
        else:
            reward1 = reward2 = 0

        # Update Q-values for both agents
        agent1.learn(reward1)
        agent2.learn(reward2)

        # Optionally: Reduce epsilon to decrease exploration
        agent1.epsilon = max(0.01, agent1.epsilon * 0.995)
        agent2.epsilon = max(0.01, agent2.epsilon * 0.995)

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}/{episodes} completed.")

    return agent1

# Function to play against the AI
def play_against_ai(ai_agent):
    player = game.Player("Player")
    ai_agent.name = "AI"
    ai_agent.new_game()

    session = game.SixtySixGame(player, ai_agent)

    while player.hand and ai_agent.hand:
        if session.current_starter == player:
            # Player plays first
            print(f"\nYour Hand: {player.hand}")
            print(f"Trump: {session.trump_card}")
            valid_input = False
            while not valid_input:
                try:
                    index = int(input("Choose a card to play (Index): "))
                    if 0 <= index < len(player.hand):
                        player_card = player.hand[index]
                        valid_input = True
                    else:
                        print("Invalid index. Please try again.")
                except ValueError:
                    print("Please enter a number.")
            player.play_card(player_card)

            # AI responds
            ai_card = ai_agent.choose_card(current_card=player_card)
            ai_agent.play_card(ai_card)
            print(f"The AI plays: {ai_card}")
        else:
            # AI plays first
            ai_card = ai_agent.choose_card()
            ai_agent.play_card(ai_card)
            print(f"\nThe AI plays: {ai_card}")

            # Player responds
            print(f"Your Hand: {player.hand}")
            print(f"Trump: {session.trump_card}")
            valid_input = False
            while not valid_input:
                try:
                    index = int(input("Choose a card to play (Index): "))
                    if 0 <= index < len(player.hand):
                        player_card = player.hand[index]
                        valid_input = True
                    else:
                        print("Invalid index. Please try again.")
                except ValueError:
                    print("Please enter a number.")
            player.play_card(player_card)

        # Determine the winner of the trick
        winner = session.determine_trick_winner(player_card, ai_card)
        winner.add_trick([player_card, ai_card])
        print(f"{winner.name} wins the trick.")

        player_points = player.calculate_points()
        ai_points = ai_agent.calculate_points()
        if player_points >= 66:
            print("You have won!")
            break
        elif ai_points >= 66:
            print("The AI has won!")
            break
        if session.deck.cards:
            winner.draw_cards(session.deck)
            loser = player if winner != player else ai_agent
            loser.draw_cards(session.deck)

        # Next starter is the winner
        session.current_starter = winner

    # End game and determine winner
    player_points = player.calculate_points()
    ai_points = ai_agent.calculate_points()
    print(f"\nYour Points: {player_points}")
    print(f"AI Points: {ai_points}")
    if player_points >= 66:
        print("You have won!")
    elif ai_points >= 66:
        print("The AI has won!")
    else:
        print("No one reached 66 points.")
