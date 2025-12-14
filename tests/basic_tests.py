
def test_game_starts():
    import curses
    from game import Game

    curses.wrapper(Game)
    assert True  # If it runs without errors, the test passes
