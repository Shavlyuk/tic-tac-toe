from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.db.models import Game
from src.schemas.game_schemas import GameCreate, GameUpdate
from src.core.game_logic import create_empty_board
import uuid
from typing import List, Optional

def create_game(db: Session, game_data: GameCreate) -> Game:
    """Create a new game"""
    print("🔄 Creating game in database...")
    game_id = str(uuid.uuid4())
    db_game = Game(
        id=game_id,
        board=create_empty_board(),
        player_x=game_data.player_name,
        is_active=True
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    print(f"✅ Game created in DB: {db_game.id}")
    return db_game

def get_game(db: Session, game_id: str) -> Optional[Game]:
    """Get game by ID"""
    return db.query(Game).filter(Game.id == game_id).first()

def get_games(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Game]:
    """Get list of games with pagination"""
    query = db.query(Game)
    if active_only:
        query = query.filter(Game.is_active == True)
    return query.order_by(desc(Game.id)).offset(skip).limit(limit).all()

def update_game(db: Session, game_id: str, game_update: GameUpdate) -> Optional[Game]:
    """Update game properties"""
    db_game = get_game(db, game_id)
    if db_game:
        for field, value in game_update.dict(exclude_unset=True).items():
            setattr(db_game, field, value)
        db.commit()
        db.refresh(db_game)
    return db_game

def delete_game(db: Session, game_id: str) -> bool:
    """Delete game by ID"""
    db_game = get_game(db, game_id)
    if db_game:
        db.delete(db_game)
        db.commit()
        return True
    return False

def get_games_count(db: Session, active_only: bool = True) -> int:
    """Get total count of games"""
    query = db.query(Game)
    if active_only:
        query = query.filter(Game.is_active == True)
    return query.count()