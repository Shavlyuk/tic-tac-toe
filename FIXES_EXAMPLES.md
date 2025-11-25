# Примеры исправлений критических замечаний

Этот файл содержит готовые примеры кода для исправления критических замечаний из REVIEW.md

## 1. Создание config.py

```python
# src/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite:///./tictactoe.db"
    
    # Приложение
    app_title: str = "Tic-Tac-Toe API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Логирование
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 2. Создание .env файла

```bash
# .env
DATABASE_URL=sqlite:///./tictactoe.db
APP_TITLE=Tic-Tac-Toe API
APP_VERSION=1.0.0
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
LOG_LEVEL=INFO
```

## 3. Обновленный main.py

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.db.database import create_tables
from src.api.endpoints import router as api_router
from src.config import settings

# Настройка логирования
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Starting application...")
    create_tables()
    logger.info("Database tables created")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.app_title,
    description="A simple Tic-Tac-Toe game API with FastAPI and SQLite",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1", tags=["games"])
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. Обновленный database.py

```python
# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from src.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```

## 5. Обновленный game_schemas.py с валидацией

```python
# src/schemas/game_schemas.py
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
```

## 6. Обновленный endpoints.py с логированием

```python
# src/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

from src.db.database import get_db
from src.db.models import Game
from src.schemas.game_schemas import GameCreate, GameState, GameUpdate, Move, GameList
from src.crud import game_crud
from src.core.game_logic import check_winner, is_board_full

router = APIRouter()
logger = logging.getLogger(__name__)

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
    logger.info(f"Creating new game for player: {game_data.player_name}")
    try:
        db_game = game_crud.create_game(db, game_data)
        result = game_db_to_state(db_game)
        logger.info(f"Game created successfully: {result['id']}")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error creating game: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error creating game: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/games/{game_id}/move", response_model=GameState, summary="Make a move")
def make_move(game_id: str, move_data: Move, db: Session = Depends(get_db)):
    """Make a move in the game"""
    logger.info(f"Move request: game_id={game_id}, player={move_data.player}, row={move_data.row}, col={move_data.col}")

    db_game = game_crud.get_game(db, game_id)
    if not db_game:
        logger.warning(f"Game not found: {game_id}")
        raise HTTPException(status_code=404, detail="Game not found")

    # Проверка присоединения второго игрока
    if not db_game.player_o:
        logger.warning(f"Game {game_id}: waiting for second player")
        raise HTTPException(
            status_code=400, 
            detail="Waiting for second player to join"
        )

    # Game validation
    if db_game.winner or db_game.is_draw:
        logger.info(f"Game {game_id} is already over")
        raise HTTPException(status_code=400, detail="Game is over")

    if move_data.player != db_game.current_player:
        logger.warning(f"Wrong turn: expected {db_game.current_player}, got {move_data.player}")
        raise HTTPException(status_code=400, detail="Not your turn")

    if move_data.player == 'X' and not db_game.player_x:
        logger.error("Player X not registered")
        raise HTTPException(status_code=400, detail="Player X not registered")

    if move_data.player == 'O' and not db_game.player_o:
        logger.error("Player O not registered")
        raise HTTPException(status_code=400, detail="Player O not registered")

    if db_game.board[move_data.row][move_data.col] != "":
        logger.warning(f"Cell [{move_data.row}][{move_data.col}] already occupied")
        raise HTTPException(status_code=400, detail="Cell already occupied")

    # Make move
    new_board = [row.copy() for row in db_game.board]
    new_board[move_data.row][move_data.col] = move_data.player
    db_game.board = new_board

    winner = check_winner(db_game.board)
    if winner:
        logger.info(f"Game {game_id}: Winner found - {winner}")
        db_game.winner = winner
        db_game.is_active = False
    elif is_board_full(db_game.board):
        logger.info(f"Game {game_id}: Draw")
        db_game.is_draw = True
        db_game.is_active = False
    else:
        new_player = "O" if move_data.player == "X" else "X"
        logger.debug(f"Switching player: {move_data.player} -> {new_player}")
        db_game.current_player = new_player

    db.commit()
    db.refresh(db_game)
    
    return game_db_to_state(db_game)

@router.get("/health", summary="Health check")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database status"""
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }
```

## 7. Обновленный game.js

```javascript
// static/game.js
console.log('🎮 game.js loaded!');

// Используем относительный путь для работы на любом домене
const API_BASE = window.location.origin + '/api/v1';

let currentGameId = null;
let playerName = null;
let pollInterval = null;
let myPlayerSymbol = null;

// Элементы DOM
const setupScreen = document.getElementById('setupScreen');
const gameScreen = document.getElementById('gameScreen');
const gameBoard = document.getElementById('gameBoard');
const gameStatus = document.getElementById('gameStatus');
const gameIdElement = document.getElementById('gameId');
const playerXElement = document.getElementById('playerX');
const playerOElement = document.getElementById('playerO');

/**
 * Показывает уведомление пользователю
 */
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Валидация имени игрока
 */
function validatePlayerName(name) {
    const trimmed = name.trim();
    
    if (!trimmed) {
        showNotification('error', 'Пожалуйста, введите ваше имя');
        return false;
    }
    
    if (trimmed.length < 2) {
        showNotification('error', 'Имя должно содержать минимум 2 символа');
        return false;
    }
    
    if (trimmed.length > 50) {
        showNotification('error', 'Имя слишком длинное (максимум 50 символов)');
        return false;
    }
    
    if (!/^[a-zA-Zа-яА-ЯёЁ0-9\s\-_]+$/.test(trimmed)) {
        showNotification('error', 'Имя содержит недопустимые символы');
        return false;
    }
    
    return true;
}

/**
 * Создает новую игру
 */
async function createGame() {
    const nameInput = document.getElementById('playerName').value;
    
    if (!validatePlayerName(nameInput)) {
        return;
    }
    
    playerName = nameInput.trim();

    try {
        console.log('🚀 Creating game for player:', playerName);
        const response = await fetch(`${API_BASE}/games`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player_name: playerName })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при создании игры');
        }

        const game = await response.json();
        console.log('✅ Game created:', game);

        currentGameId = game.id;
        myPlayerSymbol = 'X';

        initializeGame(game);
        startPolling();
        showNotification('success', 'Игра создана! Отправьте ID второму игроку.');

    } catch (error) {
        console.error('Error creating game:', error);
        showNotification('error', error.message);
    }
}

// ... остальной код с аналогичными улучшениями
```

## 8. Создание requirements-dev.txt

```txt
# requirements-dev.txt
-r requirements.txt

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Code Quality
black==23.12.0
flake8==6.1.0
mypy==1.7.1
pylint==3.0.3

# Type stubs
types-setuptools==69.0.0

# Development
ipython==8.18.1
```

## 9. Создание Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8000

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////app/data/tictactoe.db

# Запускаем приложение
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 10. Создание docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:////app/data/tictactoe.db
      - DEBUG=False
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

## Инструкция по применению исправлений

### Шаг 1: Установка дополнительных зависимостей
```bash
pip install pydantic-settings
```

### Шаг 2: Создание файлов конфигурации
1. Создайте `src/config.py` с кодом из примера 1
2. Создайте `.env` файл из примера 2
3. Добавьте `.env` в `.gitignore`

### Шаг 3: Обновление существующих файлов
1. Замените код в `src/main.py`
2. Замените код в `src/db/database.py`
3. Замените код в `src/schemas/game_schemas.py`
4. Обновите `src/api/endpoints.py`
5. Исправьте `static/game.js`

### Шаг 4: Тестирование
```bash
# Запустите приложение
uvicorn src.main:app --reload

# В другом терминале запустите тесты
pytest tests/ -v
```

### Шаг 5: Проверка
1. Откройте http://localhost:8000/docs
2. Проверьте endpoint /health
3. Создайте новую игру через веб-интерфейс
4. Проверьте, что все работает корректно

## Полезные команды

```bash
# Форматирование кода
black src/ tests/

# Проверка линтером
flake8 src/ tests/

# Проверка типов
mypy src/

# Запуск тестов с покрытием
pytest tests/ --cov=src --cov-report=html

# Сборка Docker образа
docker build -t tic-tac-toe .

# Запуск через Docker Compose
docker-compose up -d
```

## Чек-лист исправлений

- [ ] Создан `src/config.py`
- [ ] Создан `.env` файл
- [ ] Обновлен `src/main.py` (lifespan + CORS)
- [ ] Обновлен `src/db/database.py`
- [ ] Добавлена валидация в `src/schemas/game_schemas.py`
- [ ] Заменен print() на logging в `src/api/endpoints.py`
- [ ] Исправлен hardcoded URL в `static/game.js`
- [ ] Добавлена валидация на клиенте
- [ ] Создан `requirements-dev.txt`
- [ ] Создан `Dockerfile`
- [ ] Обновлен `requirements.txt` (добавлен pydantic-settings)
- [ ] Добавлена проверка присоединения второго игрока
- [ ] Улучшен health check endpoint

После выполнения всех пунктов проект будет соответствовать современным стандартам разработки! 🚀
