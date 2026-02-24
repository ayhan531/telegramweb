import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure data directory exists
const dataDir = path.join(__dirname, '../data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const db = new Database(path.join(dataDir, 'database.sqlite'));

// Veritabanı tablolarını oluştur
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id TEXT UNIQUE,
    username TEXT,
    first_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    symbol TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, symbol)
  );

  CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    symbol TEXT,
    target_price REAL,
    condition TEXT, -- 'ABOVE' or 'BELOW'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
  );
`);

export const getFavorites = (telegramId) => {
  return db.prepare('SELECT symbol FROM favorites WHERE user_id = ?').all(telegramId).map(r => r.symbol);
};

export const addFavorite = (telegramId, symbol) => {
  try {
    return db.prepare('INSERT INTO favorites (user_id, symbol) VALUES (?, ?)').run(telegramId, symbol.toUpperCase());
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') return { status: 'exists' };
    throw err;
  }
};

export const removeFavorite = (telegramId, symbol) => {
  return db.prepare('DELETE FROM favorites WHERE user_id = ? AND symbol = ?').run(telegramId, symbol.toUpperCase());
};

export const isFavorite = (telegramId, symbol) => {
  const row = db.prepare('SELECT 1 FROM favorites WHERE user_id = ? AND symbol = ?').get(telegramId, symbol.toUpperCase());
  return !!row;
};

// Alarm Functions
export const addAlarm = (userId, symbol, targetPrice, condition) => {
  return db.prepare('INSERT INTO alarms (user_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)')
    .run(userId, symbol.toUpperCase(), targetPrice, condition);
};

export const getAlarms = (userId) => {
  return db.prepare('SELECT * FROM alarms WHERE user_id = ? AND is_active = 1').all(userId);
};

export const removeAlarm = (alarmId, userId) => {
  return db.prepare('DELETE FROM alarms WHERE id = ? AND user_id = ?').run(alarmId, userId);
};

export const getAllActiveAlarms = () => {
  return db.prepare('SELECT * FROM alarms WHERE is_active = 1').all();
};

export const deactivateAlarm = (alarmId) => {
  return db.prepare('UPDATE alarms SET is_active = 0 WHERE id = ?').run(alarmId);
};

export default db;
