# 🎮 Tic-Tac-Toe Game API

Простая игра в крестики-нолики с FastAPI.

## 🚀 Технологии

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite
- **Frontend**: JavaScript, HTML5, CSS3
- **Tools**: Uvicorn, Pytest

## 📦 Установка и запуск

### 1. Клонирование и настройка
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd tic-tac-toe-game

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```
# Запуск приложения
# Способ 1: С autoreload (для разработки)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Способ 2: Через Python модуль
python -m src.main

# Открытие в браузере

Приложение:     http://localhost:8000
Документация:   http://localhost:8000/docs
Health check:   http://localhost:8000/api/v1/health

# API Endpoints
# 1. Создать новую игру
```bash
POST /api/v1/games
Content-Type: application/json

{
  "player_name": "Алиса"
}

```
# 2. Получить список всех игр
```bash
GET /api/v1/games
```

# 3. Получить игру по ID
```bash
GET /api/v1/games/{game_id}
```
# 4. Обновить игру
```bash
PUT /api/v1/games/{game_id}
Content-Type: application/json

{
  "player_o": "Боб",
  "is_active": true
}
```
# 5. Удалить игру
```bash
DELETE /api/v1/games/{game_id}
```

# 6. Проверка здоровья API
```bash
GET /api/v1/health
```

# 🎮 Использование веб-интерфейса
Откройте http://localhost:8000

Создайте игру: Введите имя → "Создать игру"

Скопируйте ID игры из появившегося поля

Присоединитесь к игре: Откройте новую вкладку → введите имя и ID → "Присоединиться"

Играйте: Кликайте на клетки по очереди

