import random

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
        self.satzpunkte = 0 
        self.stich_vor_decken = False
        self.gedeckt = False

    def neues_spiel(self):
        self.hand = []
        self.stiche = []
        self.punkte = 0
        self.stich_vor_decken = False
        self.gedeckt = False

    #Neuer Satz erstellen
    def neuer_satz(self):
        self.neues_spiel()
        self.satzpunkte = 0

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




    #bestimmen der Satzpunkte
    def bestimme_satzpunkte(self, gewinner, verlierer):
        """Bestimme die Spielpunkte nach den Spielregeln von '66'"""
        if gewinner.gedeckt:  # Wenn gedeckt wurde
            if gewinner.kartenpunkte >= 66:
                if verlierer.kartenpunkte >= 33:
                    return 1 # 1 Spielpunkt für den Gewinner
                elif len(verlierer.stiche) == 0:
                    return 3  # 3 Spielpunkte, weil Gegner keinen Stich (Schwarz) gemacht hat
                else:
                    return 2  # 2 Spielpunkte, weil Gegner Schneider ist (unter 33 Punkte)
            else:
                if len(verlierer.stiche) == 0 and verlierer.stich_vor_decken == True:
                    return 3  # Verlierer gewinnt 3 Spielpunkte, da Gewinner nicht 66 Punkte erreicht hat und Verlierer keine Stiche gemacht hat
                else:
                    return 2  # Verlierer gewinnt 2 Spielpunkte, da Gewinner nicht 66 Punkte erreicht hat
        else:  # Wenn nicht gedeckt wurde
            if gewinner.kartenpunkte >= 66:
                if verlierer.kartenpunkte >= 33:
                    return 1  # 1 Spielpunkt für den Gewinner
                elif len(verlierer.stiche) == 0:
                    return 3  # 3 Spielpunkte, weil Gegner Schwarz ist
                else:
                    return 2  # 2 Spielpunkte, weil Gegner Schneider ist (unter 33 Punkte)
        #Bei unentschieden beide 65 zu 65
        return 0    
        
    def berechne_satzpunkte(self, wert=0):
        self.satzpunkte += wert
        return self.satzpunkte

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

    #Bestimmung der Satzpunkte methode hinzufügen
    def spiel_beenden(self):
        punkte1 = self.spieler1.berechne_punkte()
        punkte2 = self.spieler2.berechne_punkte()
        #Bestimme Gewinner
        #Spieler 1 erreicht zuerst 66 Punkte
        if punkte1 >= 66:
            self.spieler1.berechne_satzpunkte(self.bestimme_satzpunkte(self.spieler1, self.spieler2))
            return self.spieler1
        #Spieler 2 erreicht zuerst 66 Punkte
        elif punkte2 >= 66:
            self.spieler2.berechne_satzpunkte(self.bestimme_satzpunkte(self.spieler2, self.spieler1))
            return self.spieler2
        #Spieler haben keine Karten mehr auf der Hand
        elif(len(self.spieler1.hand) == 0):
            #Spieler1 deckt und hat keine 66 Punkte --> Spieler2 gewinnt
            if(self.spieler1.decken == True):
                self.spieler2.berechne_satzpunkte(self.bestimme_satzpunkte(self.spieler1, self.spieler2))
                return self.spieler2
            #Spieler2 deckt und hat keine 66 Punkte --> Spieler1 gewinnt
            elif(self.spieler2.decken == True):
                self.spieler1.berechne_satzpunkte(self.bestimme_satzpunkte(self.spieler2, self.spieler1))
                return self.spieler1
        else:
            return None
        
    def satz_beenden(self):
        satzpunkte1 = self.spieler1.satzpunkte()
        satzpunkte2 = self.spieler2.satzpunkte()
        if satzpunkte1 >= 7:
            return self.spieler1
        elif satzpunkte2 >= 7:
            return self.spieler2
        else:
            return None
        
    
