from pydantic import BaseModel
from typing import List, Optional

# TODO: КРИТИЧЕСКИ ВАЖНО - Добавить валидацию для защиты от SQL injection
# и некорректных данных. См. REVIEW.md секцию "TODO: Уязвимость SQL Injection"
class GameCreate(BaseModel):
    player_name: str  # TODO: Добавить Field(..., min_length=1, max_length=50)

class GameUpdate(BaseModel):
    player_o: Optional[str] = None
    is_active: Optional[bool] = None

class Move(BaseModel):
    player: str  # TODO: Добавить Field(..., pattern="^[XO]$")
    row: int  # TODO: Добавить Field(..., ge=0, le=2)
    col: int  # TODO: Добавить Field(..., ge=0, le=2)

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