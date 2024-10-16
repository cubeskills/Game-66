from behave import given, when, then
from hamcrest import assert_that, equal_to
from game import Player
from game import Card


@given('Spieler1 spielt gegen Spieler2')
def step_impl(context):
       context.player1 = Player("Spieler 1")
       context.player2 = Player("Spieler 2")


@when('Spieler1 {s1_p} Punkte und Spieler2 {s2_p} Punkte hat')
def step_impl(context, s1_p, s2_p):
    context.player2.add_trick([Card('heart', 'ace'), Card('club', 'ace')])
    context.player1.points = int(s1_p)
    context.player2.points = int(s2_p)

@when('Spieler1 deckt')
def step_impl(context):
    context.spieler1.closed = True

@then('sollte Spieler1 {punkte} Satzpunkt(e) gewinnen')
def step_impl(context, punkte):
    winner_points = Player.determine_set_points(context, context.player1, context.player2)
    context.player1.calculate_set_points(winner_points)
    assert_that(context.player1.set_points, equal_to(int(punkte)))

