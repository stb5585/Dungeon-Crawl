
def test_game_starts():
    from src.ui_curses.game import Game
    from src.ui_curses import game

    assert game.USE_ENHANCED_COMBAT is True
    assert callable(Game)
    assert hasattr(Game, "main_menu")
    assert hasattr(Game, "run")
    assert hasattr(Game, "navigate")
