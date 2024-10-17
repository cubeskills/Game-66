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
        self.wants_to_close_deck = False  # Initialize as False

    def new_game(self):
        super().new_game()
        self.state_action_history = []
        self.wants_to_close_deck = False

    def state_as_hash(self):
        hand_hash = tuple(sorted([f"{card.suit}-{card.value}" for card in self.hand]))
        phase = 'closed' if self.closed else 'open'
        return (hand_hash, phase)

    def action_to_key(self, action):
        if action == 'close_deck':
            return 'close_deck'
        else:
            return action.value + action.suit

    def choose_action(self, valid_cards, state, include_close_deck=True):
        possible_actions = valid_cards.copy()  # Make a copy to prevent modifying valid_cards
        if include_close_deck and not self.closed:
            possible_actions.append('close_deck')  # Add 'close_deck' as a possible action

        if np.random.rand() < self.epsilon:
            # Exploration
            action = random.choice(possible_actions)
        else:
            # Exploitation
            q_values = [self.q_table.get((state, self.action_to_key(a)), 0) for a in possible_actions]
            max_q = max(q_values)
            best_actions = [a for a, q in zip(possible_actions, q_values) if q == max_q]
            action = random.choice(best_actions)
        return action

    def choose_card(self, current_card=None, phase=None, trump=None):
        state = self.state_as_hash()
        valid_cards = self.get_valid_cards(current_card, phase, trump)
        action = self.choose_action(valid_cards, state)
        
        if action == 'close_deck':
            self.wants_to_close_deck = True
            self.state_action_history.append((state, 'close_deck'))
            # Now choose a card to play, without including 'close_deck'
            action = self.choose_action(valid_cards, state, include_close_deck=False)
            self.state_action_history.append((state, self.action_to_key(action)))
            return action
        else:
            self.state_action_history.append((state, self.action_to_key(action)))
            return action

    def play_card(self, card):
        if card in self.hand:
            super().play_card(card)

    def call_close_deck(self):
        return self.wants_to_close_deck and not self.closed

    def learn(self, reward):
        for state, action in reversed(self.state_action_history):
            key = (state, action)
            old_q = self.q_table.get(key, 0)
            new_q = old_q + self.alpha * (reward - old_q)
            self.q_table[key] = new_q
            # Adjust reward if the action was 'close_deck'
            if action == 'close_deck':
                if reward > 0:
                    reward += 0.5  # Bonus reward for successful closing
                else:
                    reward -= 0.5  # Penalty for unsuccessful closing
            reward *= self.gamma  # Apply discount factor

    # Override get_valid_cards from Player class
    def get_valid_cards(self, current_card=None, phase=1, trump=None):
        return super().get_valid_cards(current_card, phase, trump)

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
            if agent1.closed:
                reward1 = 2  # Bonus for winning after closing the deck
            else:
                reward1 = 1
            reward2 = -1
        elif winner == agent2:
            if agent2.closed:
                reward2 = 2
            else:
                reward2 = 1
            reward1 = -1
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
            if not session.deck_closed and player.call_close_deck():
                session.phase = 2
                session.deck.cards = []
                player.closed = True
                session.deck_closed = True
                print("You have closed the deck.")

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
            if not session.deck_closed and ai_agent.call_close_deck():
                session.phase = 2
                session.deck.cards = []
                ai_agent.closed = True
                session.deck_closed = True
                print("The AI has closed the deck.")

            ai_card = ai_agent.choose_card(current_card=player_card, phase=session.phase, trump=session.trump)
            ai_agent.play_card(ai_card)
            print(f"The AI plays: {ai_card}")

            # Determine the winner of the trick
            winner = session.determine_trick_winner(player_card, player, ai_card, ai_agent)
        else:
            # AI plays first
            if not session.deck_closed and ai_agent.call_close_deck():
                session.phase = 2
                session.deck.cards = []
                ai_agent.closed = True
                session.deck_closed = True
                print("The AI has closed the deck.")

            ai_card = ai_agent.choose_card(phase=session.phase, trump=session.trump)
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
                        # Check if the card is valid
                        valid_cards = player.get_valid_cards(current_card=ai_card, phase=session.phase, trump=session.trump)
                        if player_card not in valid_cards:
                            print("Invalid card. You must follow suit if possible.")
                            continue
                        valid_input = True
                    else:
                        print("Invalid index. Please try again.")
                except ValueError:
                    print("Please enter a number.")
            player.play_card(player_card)

            # Determine the winner of the trick
            winner = session.determine_trick_winner(ai_card, ai_agent, player_card, player)

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
        if session.deck.cards and session.phase != 2:
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
