from behave import given, when, then
from hamcrest import assert_that, equal_to

# Simulierter Benutzer und Login-Funktion
logged_in = False

@given('Spieler1 hat {s1_p} Punkte und Spieler2 hat {s2_p} Punkte')
def step_impl(context):
    

@when('der Benutzer "{username}" und "{password}" eingibt')
def step_impl(context, username, password):
    context.username = username
    context.password = password
    if context.username == "Benutzername" and context.password == "Passwort":
        context.logged_in = True
    else:
        context.logged_in = False

@then('sollte der Benutzer zur Startseite weitergeleitet werden')
def step_impl(context):
    assert_that(context.logged_in, equal_to(True))

@then('sollte der Benutzer eine Fehlermeldung sehen')
def step_impl(context):
    assert_that(context.logged_in, equal_to(False))