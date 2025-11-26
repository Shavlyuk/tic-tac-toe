console.log('🎮 game.js loaded!');

const API_BASE = window.location.origin + '/api/v1';

let currentGameId = null;
let playerName = null;
let pollInterval = null;
let myPlayerSymbol = null; // 'X' или 'O' - фиксируется при создании/присоединении

// Элементы DOM
const setupScreen = document.getElementById('setupScreen');
const gameScreen = document.getElementById('gameScreen');
const gameBoard = document.getElementById('gameBoard');
const gameStatus = document.getElementById('gameStatus');
const gameIdElement = document.getElementById('gameId');
const playerXElement = document.getElementById('playerX');
const playerOElement = document.getElementById('playerO');

/**
 * Создает новую игру
 */
async function createGame() {
    playerName = document.getElementById('playerName').value.trim();

    if (!playerName) {
        alert('Пожалуйста, введите ваше имя');
        return;
    }

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
            throw new Error('Ошибка при создании игры');
        }

        const game = await response.json();
        console.log('✅ Game created:', game);

        currentGameId = game.id;
        myPlayerSymbol = 'X';

        initializeGame(game);
        startPolling();

    } catch (error) {
        console.error('Error creating game:', error);
        alert('Ошибка при создании игры: ' + error.message);
    }
}

/**
 * Присоединяется к существующей игре
 */
async function joinGame() {
    playerName = document.getElementById('playerName').value.trim();
    const gameId = document.getElementById('gameIdInput').value.trim();

    if (!playerName || !gameId) {
        alert('Пожалуйста, введите имя и ID игры');
        return;
    }

    try {
        console.log('🔗 Joining game:', gameId);
        const gameResponse = await fetch(`${API_BASE}/games/${gameId}`);
        if (!gameResponse.ok) {
            throw new Error('Игра не найдена');
        }

        const joinResponse = await fetch(`${API_BASE}/games/${gameId}/join`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ player_name: playerName })
        });

        if (!joinResponse.ok) {
            throw new Error('Не удалось присоединиться к игре');
        }

        const game = await gameResponse.json();
        console.log('✅ Joined game:', game);

        currentGameId = gameId;
        myPlayerSymbol = 'O'; // Присоединившийся всегда O

        initializeGame(game);
        startPolling();

    } catch (error) {
        console.error('Error joining game:', error);
        alert(error.message);
    }
}

/**
 * Проверяет, мой ли сейчас ход
 */
function isMyTurn(game) {
    return game.current_player === myPlayerSymbol;
}

/**
 * Получает символ текущего игрока из состояния игры
 */
function getCurrentPlayerSymbol(game) {
    return game.current_player;
}

/**
 * Инициализирует игровой экран
 */
function initializeGame(game) {
    console.log('🎮 Initializing game screen');
    setupScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');

    gameIdElement.textContent = currentGameId;
    updateGameState(game);
    createBoard();
}

/**
 * Создает игровую доску
 */
function createBoard() {
    console.log('🏗️ Creating game board');
    gameBoard.innerHTML = '';

    for (let row = 0; row < 3; row++) {
        for (let col = 0; col < 3; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell disabled'; // Изначально все клетки заблокированы
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.style.pointerEvents = 'none'; // Изначально блокируем
            cell.title = 'Игра не начата';

            cell.addEventListener('click', () => makeMove(row, col));

            gameBoard.appendChild(cell);
        }
    }
    console.log('✅ Board created with', gameBoard.children.length, 'cells');
}

/**
 * Обновляет отображение доски
 */
function updateBoard(board) {
    console.log('🔄 Updating board with:', board);

    const cells = document.querySelectorAll('.cell');
    console.log('📋 Found', cells.length, 'cells to update');

    cells.forEach((cell, index) => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const value = board[row][col];

        // Очищаем клетку
        cell.textContent = value || '';
        cell.className = 'cell';

        // Добавляем классы для X и O
        if (value === 'X') {
            cell.classList.add('x');
            console.log(`🎯 Cell [${row},${col}] set to X`);
        } else if (value === 'O') {
            cell.classList.add('o');
            console.log(`🎯 Cell [${row},${col}] set to O`);
        } else {
            console.log(`🎯 Cell [${row},${col}] is empty`);
        }
    });

    console.log('✅ Board update completed');
}

/**
 * Выполняет ход
 */
async function makeMove(row, col) {
    console.log('=== 🎯 MAKE MOVE STARTED ===');
    console.log('📝 Current game ID:', currentGameId);
    console.log('👤 My player symbol:', myPlayerSymbol);
    console.log('📍 Move coordinates:', row, col);

    if (!currentGameId || !myPlayerSymbol) {
        alert('Ошибка: Игра не инициализирована');
        return;
    }

    // Получаем актуальное состояние игры для проверки
    try {
        const currentStateResponse = await fetch(`${API_BASE}/games/${currentGameId}`);
        if (!currentStateResponse.ok) {
            alert('Не удалось получить состояние игры');
            return;
        }

        const currentGame = await currentStateResponse.json();

        // Проверяем, может ли игрок ходить сейчас
        if (!isMyTurn(currentGame)) {
            console.log('❌ Not your turn! Current player:', currentGame.current_player);
            alert('Сейчас не ваш ход! Ждите своей очереди.');
            return;
        }

        const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
        if (cell && cell.textContent !== '') {
            console.log('❌ Cell already occupied');
            alert('Эта клетка уже занята!');
            return;
        }

        console.log('📡 Sending move request...');
        const response = await fetch(`${API_BASE}/games/${currentGameId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player: myPlayerSymbol, // Всегда используем фиксированный символ игрока
                row: row,
                col: col
            })
        });

        console.log('📨 Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('❌ Server error:', errorData);

            if (errorData.detail === 'Not your turn') {
                alert('Сейчас не ваш ход! Ждите своей очереди.');
            } else {
                alert(`Ошибка: ${errorData.detail || 'Неизвестная ошибка'}`);
            }
            return;
        }

        const game = await response.json();
        console.log('✅ Move successful! New game state:', game);

        // Обновляем состояние игры
        updateGameState(game);

    } catch (error) {
        console.error('❌ Network error:', error);
        alert('Ошибка сети: ' + error.message);
    }
}

/**
 * Обновляет все состояние игры
 */
function updateGameState(game) {
    console.log('🎮 UPDATING GAME STATE:', game);
    console.log('👤 My player symbol:', myPlayerSymbol);
    console.log('🔄 Current game player:', game.current_player);
    console.log('✅ Is my turn?:', isMyTurn(game));

    updateBoard(game.board);
    updatePlayersInfo(game.players, game.current_player);
    updateGameStatus(game);
    updateBoardInteractivity(game);
}

/**
 * Обновляет информацию об игроках
 */
function updatePlayersInfo(players, currentPlayerTurn) {
    console.log('👥 Updating players info:', players);

    const isMyTurn = currentPlayerTurn === myPlayerSymbol;

    playerXElement.textContent = `X: ${players.X || 'Ожидание...'}`;
    playerOElement.textContent = `O: ${players.O || 'Ожидание...'}`;

    // Сбрасываем все классы
    playerXElement.classList.remove('current', 'active', 'inactive');
    playerOElement.classList.remove('current', 'active', 'inactive');

    if (currentPlayerTurn === 'X') {
        playerXElement.classList.add('current');
        if (isMyTurn && myPlayerSymbol === 'X') {
            playerXElement.classList.add('your-turn');
        } else {
            playerXElement.classList.add('waiting-turn');
        }
    } else if (currentPlayerTurn === 'O') {
        playerOElement.classList.add('current');
        if (isMyTurn && myPlayerSymbol === 'O') {
            playerOElement.classList.add('your-turn');
        } else {
            playerOElement.classList.add('waiting-turn');
        }
    }
}

/**
 * Обновляет статус игры
 */
function updateGameStatus(game) {
    console.log('📊 Updating game status');

    if (game.winner) {
        const winnerName = game.players[game.winner];
        gameStatus.innerHTML = `<div class="winner">🎉 Победитель: ${winnerName} (${game.winner})!</div>`;
        console.log('🏆 Winner:', winnerName);
    } else if (game.is_draw) {
        gameStatus.innerHTML = `<div class="winner">🤝 Ничья!</div>`;
        console.log('🤝 Game is draw');
    } else {
        const currentPlayerName = game.players[game.current_player];
        gameStatus.textContent = `Сейчас ходит: ${currentPlayerName} (${game.current_player})`;
        console.log('🔄 Current turn:', currentPlayerName);
    }
}

/**
 * Запускает опрос сервера для обновления состояния
 */
function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        console.log('🔄 Cleared previous polling interval');
    }

    console.log('🚀 Starting polling every 2 seconds');
    pollInterval = setInterval(async () => {
        if (!currentGameId) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/games/${currentGameId}`);
            if (response.ok) {
                const game = await response.json();
                console.log('📡 Polled game state:', game);
                updateGameState(game);
            }
        } catch (error) {
            console.error('❌ Polling error:', error);
        }
    }, 2000);
}

function updateBoardInteractivity(game) {
    const cells = document.querySelectorAll('.cell');
    const isMyTurnNow = isMyTurn(game);
    const gameIsActive = !game.winner && !game.is_draw;

    console.log(`🎮 Board interactivity: myTurn=${isMyTurnNow}, gameActive=${gameIsActive}`);

    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const isCellEmpty = game.board[row][col] === '';

        if (!gameIsActive) {
            // Игра завершена - блокируем все клетки
            cell.classList.add('disabled');
            cell.style.pointerEvents = 'none';
            cell.title = 'Игра завершена';
        } else if (!isMyTurnNow) {
            // Не наш ход - блокируем клетки
            cell.classList.add('disabled');
            cell.style.pointerEvents = 'none';
            cell.title = 'Ждите своего хода';
        } else if (!isCellEmpty) {
            // Наш ход, но клетка занята
            cell.classList.add('disabled');
            cell.style.pointerEvents = 'none';
            cell.title = 'Клетка занята';
        } else {
            // Наш ход и клетка свободна
            cell.classList.remove('disabled');
            cell.style.pointerEvents = 'auto';
            cell.title = `Кликните для хода ${myPlayerSymbol}`;
        }
    });

    // Обновляем статус с информацией о очереди
    updateTurnStatus(isMyTurnNow, game);
}

/**
 * Обновляет статус очереди хода
 */
function updateTurnStatus(isMyTurnNow, game) {
    const statusElement = document.getElementById('gameStatus');

    if (game.winner) {
        const winnerName = game.players[game.winner];
        const isWinnerMe = game.winner === myPlayerSymbol;
        if (isWinnerMe) {
            statusElement.innerHTML = `<div class="winner">🎉 Вы победили! (${game.winner})</div>`;
        } else {
            statusElement.innerHTML = `<div class="winner">🎉 Победитель: ${winnerName} (${game.winner})!</div>`;
        }
    } else if (game.is_draw) {
        statusElement.innerHTML = `<div class="winner">🤝 Ничья!</div>`;
    } else if (isMyTurnNow) {
        const currentPlayerName = game.players[game.current_player];
        statusElement.innerHTML = `<div class="your-turn">✅ Ваш ход! (${game.current_player})</div>`;
    } else {
        const currentPlayerName = game.players[game.current_player];
        statusElement.innerHTML = `<div class="waiting-turn">⏳ Ожидаем ход игрока: ${currentPlayerName} (${game.current_player})</div>`;
    }
}
/**
 * Сбрасывает игру и возвращает к начальному экрану
 */
function resetGame() {
    console.log('🔄 Resetting game');

    if (currentGameId) {
        fetch(`${API_BASE}/games/${currentGameId}`, { method: 'DELETE' })
            .catch(error => console.error('Error deleting game:', error));
    }

    currentGameId = null;
    myPlayerSymbol = null;
    playerName = null;

    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }

    gameScreen.classList.add('hidden');
    setupScreen.classList.remove('hidden');

    document.getElementById('playerName').value = '';
    document.getElementById('gameIdInput').value = '';
}

/**
 * Выход из игры
 */
function leaveGame() {
    resetGame();
}

// Очищаем ресурсы при закрытии страницы
window.addEventListener('beforeunload', () => {
    if (currentGameId) {
        navigator.sendBeacon(`${API_BASE}/games/${currentGameId}`);
    }
});