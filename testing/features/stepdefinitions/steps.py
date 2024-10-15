from behave import given, when, then
from hamcrest import assert_that, equal_to

# Simulierter Benutzer und Login-Funktion
logged_in = False

@given('Spieler1 hat {s1_p} Punkte und Spieler2 hat {s2_p} Punkte')
def step_impl(context, s1_p, s2_p):
    context.spieler1 = context.Spieler("Spieler 1")
    context.spieler2 = context.Spieler("Spieler 2")
    context.spieler1.kartenpunkte = int(s1_p)
    context.spieler2.kartenpunkte = int(s2_p)

@when('Spieler1 deckt')
def step_impl(context):
    context.spieler1.decken()

@then('sollte Spieler1 {punkte} Spielpunkt(e) gewinnen')
def step_impl(context, punkte):
    gewinner_punkte = context.bestimme_satzpunkte(context.spieler1, context.spieler2)
    context.spieler1.berechne_satzpunkte(gewinner_punkte)
    assert_that(context.spieler1.spielpunkte, equal_to(int(punkte)))

@when('Spieler1 sagt "Aus"')
def step_impl(context):
    context.spieler1.aus_sagen()