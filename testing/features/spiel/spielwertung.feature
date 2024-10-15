Feature: Login-Funktion auf einer Webseite

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 33 Punkte
    Given Spieler1 hat 66 Punkte und Spieler2 hat 33 Punkte
    When das Spiel beendet wird
    Then soll Spieler1 1 Satzpunkt erhalten

