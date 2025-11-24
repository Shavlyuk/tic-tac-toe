from pydantic import BaseModel
from typing import List, Optional

class GameCreate(BaseModel):
    player_name: str

class GameUpdate(BaseModel):
    player_o: Optional[str] = None
    is_active: Optional[bool] = None

class Move(BaseModel):
    player: str
    row: int
    col: int

class GameState(BaseModel):
    id: str
    board: List[List[str]]
    current_player: str
    winner: Optional[str] = None
    is_draw: bool = False
    players: dict
    is_active: bool

    class Config:
        from_attributes = True

class GameList(BaseModel):
    games: List[GameState]
    total: int