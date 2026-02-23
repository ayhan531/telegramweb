import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { exec } from 'child_process';
import { promisify } from 'util';

import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execAsync = promisify(exec);
import { getFavorites, addFavorite, removeFavorite, isFavorite } from './db.js';
dotenv.config({ path: path.join(__dirname, '../.env') });

import crypto from 'crypto';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || process.env.API_PORT || 3000;
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

// Telegram initData doğrulama
function validateInitData(initData) {
    if (!BOT_TOKEN || !initData) return true; // Lokal testler için tolerans
    try {
        const urlParams = new URLSearchParams(initData);
        const hash = urlParams.get('hash');
        urlParams.delete('hash');

        const dataCheckString = Array.from(urlParams.entries())
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([key, value]) => `${key}=${value}`)
            .join('\n');

        const secretKey = crypto.createHmac('sha256', 'WebAppData').update(BOT_TOKEN).digest();
        const checkHash = crypto.createHmac('sha256', secretKey).update(dataCheckString).digest('hex');

        return checkHash === hash;
    } catch (e) {
        return false;
    }
}

// Basit önbellek (Cache) sistemi
const cache = {};
const CACHE_DURATION = 60 * 1000; // 60 saniye

async function getCachedExec(command, cacheKey) {
    const now = Date.now();
    if (cache[cacheKey] && (now - cache[cacheKey].timestamp < CACHE_DURATION)) {
        return cache[cacheKey].data;
    }
    const { stdout } = await execAsync(command);
    const data = JSON.parse(stdout);
    cache[cacheKey] = { data, timestamp: now };
    return data;
}

// Hisse Verisi Endpoint'i
app.get('/api/stock/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        const data = await getCachedExec(`python3 api/tv_api.py ${symbol}`, `stock_${symbol}`);
        res.json(data);
    } catch (error) {
        console.error('Stock API Hatası:', error);
        res.status(500).json({ error: 'Veri çekilemedi' });
    }
});

// AKD Verisi Endpoint'i
app.get('/api/akd/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        const data = await getCachedExec(`python3 api/real_akd_api.py ${symbol}`, `akd_${symbol}`);
        res.json(data);
    } catch (error) {
        console.error('AKD API Hatası:', error);
        res.status(500).json({ error: 'AKD verisi çekilemedi' });
    }
});

// Takas Verisi Endpoint'i
app.get('/api/takas/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        const data = await getCachedExec(`python3 api/takas_api.py ${symbol}`, `takas_${symbol}`);
        res.json(data);
    } catch (error) {
        console.error('Takas API Hatası:', error);
        res.status(500).json({ error: 'Takas verisi çekilemedi' });
    }
});

// Bülten Verisi Endpoint'i
app.get('/api/bulten', async (req, res) => {
    try {
        const data = await getCachedExec('python3 api/bulten_api.py', 'bulten');
        res.json(data);
    } catch (error) {
        console.error('Bülten API Hatası:', error);
        res.status(500).json({ error: 'Bülten verisi çekilemedi' });
    }
});

// Fon Verisi Endpoint'i
app.get('/api/fon', async (req, res) => {
    try {
        const data = await getCachedExec('python3 api/fon_api.py', 'fon');
        res.json(data);
    } catch (error) {
        console.error('Fon API Hatası:', error);
        res.status(500).json({ error: 'Fon verisi çekilemedi' });
    }
});

// Tarama Veri Endpoint'i
app.get('/api/scan/:category', async (req, res) => {
    const { category } = req.params;
    try {
        const data = await getCachedExec(`python3 api/scanner_api.py ${category}`, `scan_${category}`);
        res.json(data);
    } catch (error) {
        console.error('Tarama API Hatası:', error);
        res.status(500).json({ error: 'Tarama verisi çekilemedi' });
    }
});

// --- Favoriler Endpoint'leri ---

app.get('/api/favorites/:userId', (req, res) => {
    try {
        const favs = getFavorites(req.params.userId);
        res.json(favs.map(f => f.symbol));
    } catch (error) {
        res.status(500).json({ error: 'Favoriler alınamadı' });
    }
});

app.post('/api/favorites', (req, res) => {
    const { userId, symbol } = req.body;
    const initData = req.headers['x-telegram-init-data'];
    if (!validateInitData(initData)) return res.status(401).json({ error: 'Unauthorized' });

    try {
        addFavorite(userId, symbol);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Favori eklenemedi' });
    }
});

app.delete('/api/favorites', (req, res) => {
    const { userId, symbol } = req.body;
    const initData = req.headers['x-telegram-init-data'];
    if (!validateInitData(initData)) return res.status(401).json({ error: 'Unauthorized' });

    try {
        removeFavorite(userId, symbol);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Favori silinemedi' });
    }
});

app.get('/api/favorites/check/:userId/:symbol', (req, res) => {
    try {
        const status = isFavorite(req.params.userId, req.params.symbol);
        res.json({ isFavorite: status });
    } catch (error) {
        res.status(500).json({ error: 'Kontrol edilemedi' });
    }
});

// Serve Frontend
const distPath = path.join(__dirname, '../web-app/dist');

// Check if dist directory exists
if (!fs.existsSync(distPath)) {
    console.error(`UYARI: Frontend build klasörü bulunamadı: ${distPath}`);
    console.error('Lütfen "npm run build" komutunu çalıştırdığınızdan emin olun.');
}

app.use(express.static(distPath));

// Catch-all middleware to handle React Router and ensure index.html is served for all non-API routes
app.use((req, res, next) => {
    // If it's an API request that didn't match above, return 404
    if (req.path.startsWith('/api')) {
        return res.status(404).json({ error: 'API endpoint not found' });
    }

    // Don't serve index.html for missing assets (files with extensions)
    if (req.path.includes('.') && !req.path.endsWith('.html')) {
        return res.status(404).send('Asset not found');
    }

    // Otherwise serve the frontend
    res.sendFile(path.join(distPath, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`API Sunucusu http://localhost:${PORT} adresinde çalışıyor`);
});
