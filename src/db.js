import Database from 'better-sqlite3';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const db = new Database(path.join(__dirname, 'database.sqlite'));

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
`);

export const getFavorites = (telegramId) => {
    return db.prepare('SELECT symbol FROM favorites WHERE user_id = ?').all(telegramId);
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

export default db;
