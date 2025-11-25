from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re


class GameCreate(BaseModel):
    player_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Player name (1-50 characters)"
    )

    @validator('player_name')
    def validate_player_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Player name cannot be empty or whitespace')
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-_]+$', v):
            raise ValueError('Player name contains invalid characters')
        return v


class GameUpdate(BaseModel):
    player_o: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None


class Move(BaseModel):
    player: str = Field(..., pattern="^[XO]$", description="Player symbol: X or O")
    row: int = Field(..., ge=0, le=2, description="Row number (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column number (0-2)")


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