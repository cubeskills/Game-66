from behave import given, when, then
from hamcrest import assert_that, equal_to
from game import Player
from game import Card


@given('Spieler1 spielt gegen Spieler2')
def step_impl(context):
        context.player1 = Player("Spieler 1")
        context.player2 = Player("Spieler 2")

#Spieler Punkte +22
@when('Spieler1 {s1_p} Punkte und Spieler2 {s2_p} Punkte hat')
def step_impl(context, s1_p, s2_p):
        context.player1.add_trick([Card('heart', 'ace'), Card('club', 'ace')])
        context.player2.add_trick([Card('heart', 'ace'), Card('club', 'ace')])
        context.player1.points = int(s1_p)
        context.player2.points = int(s2_p)
    
@when('Spieler1 {s1_cv} {s1_cc} spielt und Spieler2 {s2_cv} {s2_cc} spielt')
def step_impl(context, s1_cv, s1_cc, s2_cv, s2_cc):
     context.player1.add_trick([Card(s1_cc, s1_cv), Card(s2_cc, s2_cv)])
     context.player1.calculate_points()

@then('hat Spieler1 {s1_p} Punkte')
def step_impl(context, s1_p):
     assert_that(context.player1.points, equal_to(int(s1_p)))

@when('Spieler1 {s1_p} Punkte und Spieler2 0 Stiche hat')
def step_impl(context, s1_p):
    context.player1.points = int(s1_p)

@when('Spieler1 gedeckt hat')
def step_impl(context):
    context.player1.closed = True

@when('Spieler2 keinen Stich vor dem Decken hat')
def step_impl(context):
     context.player2.trick_before_closing = True

@then('sollte Spieler1 {punkte} Satzpunkt(e) gewinnen')
def step_impl(context, punkte):
    winner_points = Player.determine_set_points(context, context.player1, context.player2)
    context.player1.calculate_set_points(winner_points)
    assert_that(context.player1.set_points, equal_to(int(punkte)))

@then('sollte Spieler2 {punkte} Satzpunkt(e) gewinnen')
def step_impl(context, punkte):
    winner_points = Player.determine_set_points(context, context.player1, context.player2)
    context.player2.calculate_set_points(winner_points)
    assert_that(context.player2.set_points, equal_to(int(punkte)))

@then('gewinnt Spieler2 {punkte} Satzpunkt(e)')
def step_impl(context, punkte):
    winner_points = Player.determine_set_points(context, context.player2, context.player1)
    context.player2.calculate_set_points(winner_points)
    assert_that(context.player2.set_points, equal_to(int(punkte)))

