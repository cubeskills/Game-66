"""
- rauben mit 9
- decken 
- ohne nachziehen decken
- hochzeit
- phase 2 (bedienpflicht und keine hochzeiten und trumpf falls man nicht bedienen kann)
- spielbewertung
- letzter stich 10 punkte
- 65 - 65 unentschieden
"""
"""

Test Luca Kannst du mich sehen Paul???

"""

"""
ja kann ich

"""


import test
import random
import numpy as np

# Definition der Kartenfarben und -werte
FARBEN = ['Herz', 'Karo', 'Pik', 'Kreuz']
WERTE = ['Ass', '10', 'König', 'Dame', 'Bube', '9']
PUNKTZAHLEN = {'Ass': 11, '10': 10, 'König': 4, 'Dame': 3, 'Bube': 2, '9': 0}

# Karte-Klasse
class Karte:
    def __init__(self, farbe, wert):
        self.farbe = farbe
        self.wert = wert
        self.punkte = PUNKTZAHLEN[wert]

    def __repr__(self):
        return f"{self.wert} von {self.farbe}"

# Deck-Klasse
class Deck:
    def __init__(self):
        self.karten = [Karte(farbe, wert) for farbe in FARBEN for wert in WERTE]
        random.shuffle(self.karten)

    def ziehe_karte(self):
        if self.karten:
            return self.karten.pop()
        else:
            return None

# Spieler-Klasse
class Spieler:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.stiche = []
        self.punkte = 0

    def neues_spiel(self):
        self.hand = []
        self.stiche = []
        self.punkte = 0

    def ziehe_karten(self, deck, anzahl=1):
        for _ in range(anzahl):
            karte = deck.ziehe_karte()
            if karte:
                self.hand.append(karte)

    def spiele_karte(self, karte):
        self.hand.remove(karte)
        return karte

    def addiere_stich(self, karten):
        self.stiche.extend(karten)

    def berechne_punkte(self):
        self.punkte = sum(karte.punkte for karte in self.stiche)
        return self.punkte

    def __repr__(self):
        return f"{self.name} - Punkte: {self.punkte}"

# Sechsundsechzig-Spielklasse
class SechsundsechzigSpiel:
    def __init__(self, spieler1, spieler2):
        self.spieler1 = spieler1
        self.spieler2 = spieler2
        self.deck = Deck()
        self.trumpfkarte = self.deck.karten[1]  # Letzte Karte im Deck ist Trumpf
        self.trumpf = self.trumpfkarte.farbe
        self.offener_stapel = [self.trumpfkarte]
        self.aktueller_starter = self.spieler1  # Der erste Spieler beginnt

        # Beide Spieler ziehen 6 Karten
        self.spieler1.ziehe_karten(self.deck, 6)
        self.spieler2.ziehe_karten(self.deck, 6)

    def bestimme_gewinner_des_stichs(self, karte1, karte2):
        # Prüfe, ob eine der Karten Trumpf ist
        if karte1.farbe == self.trumpf and karte2.farbe != self.trumpf:
            return self.spieler1
        elif karte2.farbe == self.trumpf and karte1.farbe != self.trumpf:
            return self.spieler2
        # Wenn beide Karten gleiche Farbe haben
        elif karte1.farbe == karte2.farbe:
            # Vergleiche die Werte
            if WERTE.index(karte1.wert) < WERTE.index(karte2.wert):
                return self.spieler1
            else:
                return self.spieler2
        else:
            # Der Spieler, der angespielt hat, gewinnt
            return self.aktueller_starter

    def spiele_runde(self):
        while self.spieler1.hand and self.spieler2.hand:
            if self.aktueller_starter == self.spieler1:
                karte1 = self.spieler1.waehle_karte()
                self.spieler1.spiele_karte(karte1)

                karte2 = self.spieler2.waehle_karte(aktuelle_karte=karte1)
                self.spieler2.spiele_karte(karte2)
            else:
                karte2 = self.spieler2.waehle_karte()
                self.spieler2.spiele_karte(karte2)

                karte1 = self.spieler1.waehle_karte(aktuelle_karte=karte2)
                self.spieler1.spiele_karte(karte1)

            gewinner = self.bestimme_gewinner_des_stichs(karte1, karte2)
            gewinner.addiere_stich([karte1, karte2])

            # Gewinner zieht zuerst eine Karte
            if self.deck.karten:
                gewinner.ziehe_karten(self.deck)
                verlierer = self.spieler1 if gewinner != self.spieler1 else self.spieler2
                verlierer.ziehe_karten(self.deck)

            # Nächster Starter ist der Gewinner
            self.aktueller_starter = gewinner

    def spiel_beenden(self):
        punkte1 = self.spieler1.berechne_punkte()
        punkte2 = self.spieler2.berechne_punkte()
        if punkte1 >= 66:
            return self.spieler1
        elif punkte2 >= 66:
            return self.spieler2
        else:
            return None

# Q-Learning-Agent
class QLearningAgent(Spieler):
    def __init__(self, name, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(name)
        self.q_tabelle = {}  # {(zustand, aktion): wert}
        self.alpha = alpha  # Lernrate
        self.gamma = gamma  # Diskontfaktor
        self.epsilon = epsilon  # Explorationsrate
        self.zustand_aktion_verlauf = []

    def neues_spiel(self):
        super().neues_spiel()
        self.zustand_aktion_verlauf = []

    def zustand_als_hash(self):
        # Vereinfachte Zustandsrepräsentation
        hand_hash = tuple(sorted([f"{karte.farbe}-{karte.wert}" for karte in self.hand]))
        return hand_hash

    def waehle_karte(self, aktuelle_karte=None):
        zustand = self.zustand_als_hash()
        gueltige_karten = self.hand  # In einer vollständigen Implementierung sollten nur gültige Karten berücksichtigt werden
        if np.random.rand() < self.epsilon:
            # Exploration
            aktion = random.choice(gueltige_karten)
        else:
            # Exploitation
            q_werte = [self.q_tabelle.get((zustand, karte.wert + karte.farbe), 0) for karte in gueltige_karten]
            max_q = max(q_werte)
            beste_karten = [karte for karte, q in zip(gueltige_karten, q_werte) if q == max_q]
            aktion = random.choice(beste_karten)
        self.zustand_aktion_verlauf.append((zustand, aktion))
        return aktion

    def lernen(self, belohnung):
        for zustand, aktion in reversed(self.zustand_aktion_verlauf):
            altes_q = self.q_tabelle.get((zustand, aktion.wert + aktion.farbe), 0)
            neues_q = altes_q + self.alpha * (belohnung - altes_q)
            self.q_tabelle[(zustand, aktion.wert + aktion.farbe)] = neues_q
            belohnung *= self.gamma  # Diskontfaktor anwenden

# Trainingsfunktion
def trainiere_ki(episoden):
    agent1 = QLearningAgent("Agent 1")
    agent2 = QLearningAgent("Agent 2")

    for episode in range(episoden):
        # Initialisiere die Agenten für jede Episode
        agent1.neues_spiel()
        agent2.neues_spiel()

        spiel = SechsundsechzigSpiel(agent1, agent2)
        spiel.spiele_runde()

        gewinner = spiel.spiel_beenden()
        if gewinner == agent1:
            belohnung1 = 1
            belohnung2 = -1
        elif gewinner == agent2:
            belohnung1 = -1
            belohnung2 = 1
        else:
            belohnung1 = belohnung2 = 0

        # Aktualisiere Q-Werte für beide Agenten
        agent1.lernen(belohnung1)
        agent2.lernen(belohnung2)

        # Optional: Reduziere epsilon, um die Exploration zu verringern
        agent1.epsilon = max(0.01, agent1.epsilon * 0.995)
        agent2.epsilon = max(0.01, agent2.epsilon * 0.995)

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}/{episoden} abgeschlossen.")

    return agent1

def simulate(ki_agent,idx = 0):
    mensch = Spieler("Spieler")
    ki_agent.name = "KI"
    ki_agent.neues_spiel()

    spiel = SechsundsechzigSpiel(ki_agent,mensch)

    while mensch.hand and ki_agent.hand:
        if spiel.aktueller_starter == mensch:
            # Mensch spielt zuerst
            gueltige_eingabe = False
            while not gueltige_eingabe:
                if idx == 0:
                    index = 0
                    mensch_karte = mensch.hand[index]
                    gueltige_eingabe = True
                else:
                    try:
                        index = int(input("Wähle eine Karte zum Spielen (Index): "))
                        if 0 <= index < len(mensch.hand):
                            mensch_karte = mensch.hand[index]
                            gueltige_eingabe = True
                    except ValueError:
                        pass
            mensch.spiele_karte(mensch_karte)

            # KI reagiert
            ki_karte = ki_agent.waehle_karte(aktuelle_karte=mensch_karte)
            ki_agent.spiele_karte(ki_karte)
        else:
            # KI spielt zuerst
            ki_karte = ki_agent.waehle_karte()
            ki_agent.spiele_karte(ki_karte)

            # Mensch reagiert
            gueltige_eingabe = False
            while not gueltige_eingabe:
                if idx == 0:
                    index = 0
                    mensch_karte = mensch.hand[index]
                    gueltige_eingabe = True
                else:
                    try:
                        index = int(input("Wähle eine Karte zum Spielen (Index): "))
                        if 0 <= index < len(mensch.hand):
                            mensch_karte = mensch.hand[index]
                            gueltige_eingabe = True
                    except ValueError:
                        pass
            mensch.spiele_karte(mensch_karte)

        # Bestimme den Gewinner des Stichs
        gewinner = spiel.bestimme_gewinner_des_stichs(mensch_karte, ki_karte)
        gewinner.addiere_stich([mensch_karte, ki_karte])

        mensch_punkte = mensch.berechne_punkte()
        ki_punkte = ki_agent.berechne_punkte()
        if mensch_punkte >= 66:
            return 1
        elif ki_punkte >= 66:
            return 0
        # Gewinner zieht zuerst eine Karte
        if spiel.deck.karten:
            gewinner.ziehe_karten(spiel.deck)
            verlierer = mensch if gewinner != mensch else ki_agent
            verlierer.ziehe_karten(spiel.deck)

        # Nächster Starter ist der Gewinner
        spiel.aktueller_starter = gewinner

    # Spiel beenden und Gewinner bestimmen
    mensch_punkte = mensch.berechne_punkte()
    ki_punkte = ki_agent.berechne_punkte()
    print(f"\nDeine Punkte: {mensch_punkte}")
    print(f"KI-Punkte: {ki_punkte}")
    if mensch_punkte >= 66:
        return 1
    elif ki_punkte >= 66:
        return 0
    else:
        return -1
# Funktion zum Spielen gegen die KI
def spiele_gegen_ki(ki_agent):
    mensch = Spieler("Spieler")
    ki_agent.name = "KI"
    ki_agent.neues_spiel()

    spiel = SechsundsechzigSpiel(mensch, ki_agent)

    while mensch.hand and ki_agent.hand:
        if spiel.aktueller_starter == mensch:
            # Mensch spielt zuerst
            print(f"\nDeine Hand: {mensch.hand}")
            print(f"Trumpf: {spiel.trumpfkarte}")
            gueltige_eingabe = False
            while not gueltige_eingabe:
                try:
                    index = int(input("Wähle eine Karte zum Spielen (Index): "))
                    if 0 <= index < len(mensch.hand):
                        mensch_karte = mensch.hand[index]
                        gueltige_eingabe = True
                    else:
                        print("Ungültiger Index. Bitte erneut versuchen.")
                except ValueError:
                    print("Bitte eine Zahl eingeben.")
            mensch.spiele_karte(mensch_karte)

            # KI reagiert
            ki_karte = ki_agent.waehle_karte(aktuelle_karte=mensch_karte)
            ki_agent.spiele_karte(ki_karte)
            print(f"Die KI spielt: {ki_karte}")
        else:
            # KI spielt zuerst
            ki_karte = ki_agent.waehle_karte()
            ki_agent.spiele_karte(ki_karte)
            print(f"\nDie KI spielt: {ki_karte}")

            # Mensch reagiert
            print(f"Deine Hand: {mensch.hand}")
            print(f"Trumpf: {spiel.trumpfkarte}")
            gueltige_eingabe = False
            while not gueltige_eingabe:
                try:
                    index = int(input("Wähle eine Karte zum Spielen (Index): "))
                    if 0 <= index < len(mensch.hand):
                        mensch_karte = mensch.hand[index]
                        gueltige_eingabe = True
                    else:
                        print("Ungültiger Index. Bitte erneut versuchen.")
                except ValueError:
                    print("Bitte eine Zahl eingeben.")
            mensch.spiele_karte(mensch_karte)

        # Bestimme den Gewinner des Stichs
        gewinner = spiel.bestimme_gewinner_des_stichs(mensch_karte, ki_karte)
        gewinner.addiere_stich([mensch_karte, ki_karte])
        print(f"{gewinner.name} gewinnt den Stich.")

        mensch_punkte = mensch.berechne_punkte()
        ki_punkte = ki_agent.berechne_punkte()
        if mensch_punkte >= 66:
            print("Du hast gewonnen!")
            break
        elif ki_punkte >= 66:
            print("Die KI hat gewonnen!")
            break 
        if spiel.deck.karten:
            gewinner.ziehe_karten(spiel.deck)
            verlierer = mensch if gewinner != mensch else ki_agent
            verlierer.ziehe_karten(spiel.deck)

        # Nächster Starter ist der Gewinner
        spiel.aktueller_starter = gewinner

    # Spiel beenden und Gewinner bestimmen
    mensch_punkte = mensch.berechne_punkte()
    ki_punkte = ki_agent.berechne_punkte()
    print(f"\nDeine Punkte: {mensch_punkte}")
    print(f"KI-Punkte: {ki_punkte}")
    if mensch_punkte >= 66:
        print("Du hast gewonnen!")
    elif ki_punkte >= 66:
        print("Die KI hat gewonnen!")
    else:
        print("Keiner hat 66 Punkte erreicht.")

# Hauptprogramm
if __name__ == "__main__":
    """
    # Training der KI
    trainierter_agent = trainiere_ki(10000)

    # Gegen die trainierte KI spielen
    # spiele_gegen_ki(trainierter_agent)


    n_games = 10000
    drawn_games = 0
    ki_games = 0
    lost_games = 0
    for i in range(n_games):
        result = simulate(trainierter_agent)
        if result == -1:
            drawn_games += 1
        elif result == 0:
            ki_games += 1
        elif result == 1:
            lost_games += 1
    


    print()
    print()
    print(f"Ki won {ki_games} games")
    print(f"Ki draw {drawn_games} games")
    print(f"Ki lost {lost_games} games")

    import test

    """
    
    print_Hallo()
