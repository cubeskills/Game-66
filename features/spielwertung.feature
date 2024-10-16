Feature: Spielbewertung

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 33 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 33 Punkte hat
    Then sollte Spieler1 1 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 32 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 33 Punkte hat
    Then sollte Spieler1 2 Satzpunkt(e) gewinnen

   