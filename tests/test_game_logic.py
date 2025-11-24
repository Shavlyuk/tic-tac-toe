import pytest
from src.core.game_logic import check_winner, is_board_full, create_empty_board


def test_check_winner_rows():
    board = [
        ["X", "X", "X"],
        ["O", "O", ""],
        ["", "", ""]
    ]
    assert check_winner(board) == "X"


def test_check_winner_columns():
    board = [
        ["X", "O", ""],
        ["X", "O", ""],
        ["", "O", ""]
    ]
    assert check_winner(board) == "O"


def test_is_board_full():
    full_board = [
        ["X", "O", "X"],
        ["O", "X", "O"],
        ["X", "O", "X"]
    ]
    assert is_board_full(full_board) == True

    not_full_board = [
        ["X", "O", "X"],
        ["O", "X", "O"],
        ["X", "O", ""]
    ]
    assert is_board_full(not_full_board) == False