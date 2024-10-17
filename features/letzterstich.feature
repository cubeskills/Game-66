Feature: Letzter Stich = 10 Punkte

    Scenario: Spieler1 gewinnt mit seiner letzten Handkarte den letzten Stich
        Given Spieler1 spielt gegen Spieler2
        When Spieler1 0 Punkte und Spieler2 0 Stiche hat
        And Spieler1 ace club spielt und Spieler2 10 club spielt
        Then hat Spieler1 31 Punkte
