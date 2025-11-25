from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from src.db.database import get_db
from src.db.models import Game
from src.schemas.game_schemas import GameCreate, GameState, GameUpdate, Move, GameList
from src.crud import game_crud
from src.core.game_logic import check_winner, is_board_full

router = APIRouter()


def game_db_to_state(game_db: Game) -> dict:
    """Конвертирует SQLAlchemy модель в словарь для Pydantic"""
    return {
        "id": game_db.id,
        "board": game_db.board,
        "current_player": game_db.current_player,
        "winner": game_db.winner,
        "is_draw": game_db.is_draw,
        "players": {"X": game_db.player_x, "O": game_db.player_o},
        "is_active": game_db.is_active
    }


@router.post("/games", response_model=GameState, summary="Create new game")
def create_game(game_data: GameCreate, db: Session = Depends(get_db)):
    """Create a new Tic-Tac-Toe game"""
    # TODO: Заменить print() на logging.logger
    # См. REVIEW.md секцию "TODO: Избыточное логирование print()"
    print("🎮 Creating new game for player:", game_data.player_name)
    try:
        db_game = game_crud.create_game(db, game_data)
        result = game_db_to_state(db_game)
        print("✅ Game created successfully:", result["id"])
        return result
    except Exception as e:
        # TODO: КРИТИЧЕСКИ ВАЖНО - Улучшить обработку ошибок
        # Общий except Exception скрывает реальные проблемы
        # См. REVIEW.md секцию "TODO: Отсутствие обработки ошибок базы данных"
        print("❌ Error creating game:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/games", response_model=GameList, summary="List all games")
def list_games(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        active_only: bool = Query(True, description="Show only active games"),
        db: Session = Depends(get_db)
):
    """Get list of all games with pagination"""
    games = game_crud.get_games(db, skip=skip, limit=limit, active_only=active_only)
    total = game_crud.get_games_count(db, active_only=active_only)

    game_states = [game_db_to_state(game) for game in games]
    return GameList(games=game_states, total=total)


@router.get("/games/{game_id}", response_model=GameState, summary="Get game by ID")
def get_game(game_id: str, db: Session = Depends(get_db)):
    """Get game details by ID"""
    db_game = game_crud.get_game(db, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_db_to_state(db_game)


@router.put("/games/{game_id}", response_model=GameState, summary="Update game")
def update_game(
        game_id: str,
        game_update: GameUpdate,
        db: Session = Depends(get_db)
):
    """Update game properties"""
    db_game = game_crud.update_game(db, game_id, game_update)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_db_to_state(db_game)


@router.delete("/games/{game_id}", summary="Delete game")
def delete_game(game_id: str, db: Session = Depends(get_db)):
    """Delete game by ID"""
    if not game_crud.delete_game(db, game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}


@router.post("/games/{game_id}/join", response_model=GameState, summary="Join existing game")
def join_game(game_id: str, player_data: GameCreate, db: Session = Depends(get_db)):
    """Join an existing game as second player"""
    db_game = game_crud.get_game(db, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    if db_game.player_o:
        raise HTTPException(status_code=400, detail="Game is full")

    db_game.player_o = player_data.player_name
    db.commit()
    db.refresh(db_game)

    return game_db_to_state(db_game)


@router.post("/games/{game_id}/move", response_model=GameState, summary="Make a move")
def make_move(game_id: str, move_data: Move, db: Session = Depends(get_db)):
    """Make a move in the game"""
    print(f"🎯 MOVE REQUEST: game_id={game_id}, player={move_data.player}, row={move_data.row}, col={move_data.col}")

    db_game = game_crud.get_game(db, game_id)
    if not db_game:
        print("❌ GAME NOT FOUND")
        raise HTTPException(status_code=404, detail="Game not found")
    
    # TODO: КРИТИЧЕСКИ ВАЖНО - Добавить проверку присоединения второго игрока
    # Сейчас игрок O может сделать ход до того как присоединится к игре
    # См. REVIEW.md секцию "TODO: Отсутствие валидации существования второго игрока"

    print(f"📊 GAME STATE - Player X: {db_game.player_x}, Player O: {db_game.player_o}")
    print(f"📊 GAME STATE - Current player: {db_game.current_player}, Requested player: {move_data.player}")

    # Game validation
    if db_game.winner or db_game.is_draw:
        print("❌ GAME IS OVER")
        raise HTTPException(status_code=400, detail="Game is over")

    # СТРОГАЯ проверка очереди
    if move_data.player != db_game.current_player:
        print(f"❌ WRONG TURN: expected {db_game.current_player}, got {move_data.player}")
        raise HTTPException(status_code=400, detail="Not your turn")

    # Проверяем, существует ли игрок с таким символом
    if move_data.player == 'X' and not db_game.player_x:
        print("❌ PLAYER X NOT REGISTERED")
        raise HTTPException(status_code=400, detail="Player X not registered")

    if move_data.player == 'O' and not db_game.player_o:
        print("❌ PLAYER O NOT REGISTERED")
        raise HTTPException(status_code=400, detail="Player O not registered")

    if not (0 <= move_data.row < 3 and 0 <= move_data.col < 3):
        print("❌ INVALID COORDINATES")
        raise HTTPException(status_code=400, detail="Invalid move coordinates")

    if db_game.board[move_data.row][move_data.col] != "":
        print("❌ CELL OCCUPIED")
        raise HTTPException(status_code=400, detail="Cell already occupied")

    new_board = [row.copy() for row in db_game.board]
    new_board[move_data.row][move_data.col] = move_data.player
    db_game.board = new_board

    print(f"🆕 AFTER MOVE - Board: {db_game.board}")

    winner = check_winner(db_game.board)
    if winner:
        print(f"🏆 WINNER FOUND: {winner}")
        db_game.winner = winner
        db_game.is_active = False
    elif is_board_full(db_game.board):
        print("🤝 GAME IS DRAW")
        db_game.is_draw = True
        db_game.is_active = False
    else:
        new_player = "O" if move_data.player == "X" else "X"
        print(f"🔄 SWITCHING PLAYER: {move_data.player} -> {new_player}")
        db_game.current_player = new_player

    db.commit()
    db.refresh(db_game)

    print(f"💾 CHANGES COMMITTED - New current player: {db_game.current_player}")

    result = game_db_to_state(db_game)
    return result

@router.get("/health", summary="Health check")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}