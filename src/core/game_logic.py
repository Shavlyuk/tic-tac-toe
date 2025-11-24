from typing import List, Optional


def create_empty_board() -> List[List[str]]:
    """Create an empty 3x3 board"""
    return [["" for _ in range(3)] for _ in range(3)]


def check_winner(board: List[List[str]]) -> Optional[str]:
    """Check if there's a winner on the board"""
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]

    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]

    return None


def is_board_full(board: List[List[str]]) -> bool:
    """Check if the board is completely filled"""
    for row in board:
        for cell in row:
            if cell == "":
                return False
    return True