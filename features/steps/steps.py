from behave import given, when, then
from hamcrest import assert_that, equal_to
from spiel import Spieler

# Simulierter Benutzer und Login-Funktion
logged_in = False


@given('Spieler1 spielt gegen Spieler2')
def step_impl(context):
        print("done")


@when('Spieler1 {s1_p} Punkte und Spieler2 {s2_p} Punkte hat')
def step_impl(context, s1_p, s2_p):
    context.spieler1 = Spieler("Spieler 1")
    context.spieler2 = Spieler("Spieler 2")
    context.spieler1.kartenpunkte = int(s1_p)
    context.spieler2.kartenpunkte = int(s2_p)

@when('Spieler1 deckt')
def step_impl(context):
    context.spieler1.decken = True

@then('sollte Spieler1 {punkte} Satzpunkt(e) gewinnen')
def step_impl(context, punkte):
    gewinner_punkte = Spieler.bestimme_satzpunkte(context, context.spieler1, context.spieler2)
    context.spieler1.berechne_satzpunkte(gewinner_punkte)
    assert_that(context.spieler1.satzpunkte, equal_to(int(punkte)))

