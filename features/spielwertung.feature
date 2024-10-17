Feature: Spielbewertung

  #Spieler gewinnt durch erreichen von mehr als 66 Punkten
  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 33 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 33 Punkte hat
    Then sollte Spieler1 1 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 32 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 32 Punkte hat
    Then sollte Spieler1 2 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 0 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 0 Punkte hat
    Then sollte Spieler1 2 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und Spieler 2 hat 0 Stiche
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 0 Stiche hat
    Then sollte Spieler1 3 Satzpunkt(e) gewinnen

  #Spieler1 gewinnt und hat gedeckt
  Scenario: Spieler 1 hat 66 Punkte und gedeckt und Spieler 2 hat 33 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 33 Punkte hat
    And Spieler1 gedeckt hat
    Then sollte Spieler1 1 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und gedeckt und Spieler 2 hat 32 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 32 Punkte hat
    And Spieler1 gedeckt hat
    Then sollte Spieler1 2 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und gedeckt und Spieler 2 hat 0 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 0 Punkte hat
    And Spieler1 gedeckt hat
    Then sollte Spieler1 2 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 66 Punkte und gedeckt und Spieler 2 hat 0 Stiche
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 66 Punkte und Spieler2 0 Stiche hat
    And Spieler1 gedeckt hat
    Then sollte Spieler1 3 Satzpunkt(e) gewinnen

  #Spieler1 hat gedeckt aber verloren
  Scenario: Spieler 1 hat 65 Punkte und gedeckt und Spieler 2 hat 0 Stiche
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 65 Punkte und Spieler2 0 Stiche hat
    And Spieler1 gedeckt hat
    And Spieler2 keinen Stich vor dem Decken hat
    Then sollte Spieler2 3 Satzpunkt(e) gewinnen
     
  Scenario: Spieler 1 hat 65 Punkte und gedeckt und Spieler 2 hat 1 Stiche
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 65 Punkte und Spieler2 12 Punkte hat
    And Spieler1 gedeckt hat
    And Spieler2 keinen Stich vor dem Decken hat
    Then sollte Spieler2 2 Satzpunkt(e) gewinnen

  Scenario: Spieler 1 hat 60 Punkte und gedeckt und Spieler 2 erreicht 66 Punkte und macht aus
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 60 Punkte und Spieler2 66 Punkte hat
    And Spieler1 gedeckt hat
    Then gewinnt Spieler2 2 Satzpunkt(e) 

  #Unentschieden beide Spieler haben 65 Punkte
  Scenario: Spieler 1 hat 65 Punkte und Spieler 2 erreicht 65 Punkte
    Given Spieler1 spielt gegen Spieler2
    When Spieler1 65 Punkte und Spieler2 65 Punkte hat
    Then sollte Spieler2 0 Satzpunkt(e) gewinnen
    Then sollte Spieler1 0 Satzpunkt(e) gewinnen