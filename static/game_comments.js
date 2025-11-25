console.log('🎮 game.js loaded!');

// TODO: КРИТИЧЕСКИ ВАЖНО - Убрать hardcoded URL
// При деплое приложение не будет работать
// См. REVIEW.md секцию "TODO: Безопасность - Hardcoded API URL"
// Рекомендация: const API_BASE = window.location.origin + '/api/v1';
const API_BASE = 'http://localhost:8000/api/v1';

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

// TODO: Добавить валидацию входных данных на стороне клиента
// См. REVIEW.md секцию "Добавьте валидацию на стороне клиента"
