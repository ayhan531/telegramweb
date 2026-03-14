import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { exec } from 'child_process';
import { promisify } from 'util';
import axios from 'axios';

import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { createServer } from 'http';
import { Server } from 'socket.io';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execAsync = promisify(exec);
import { 
    getFavorites, addFavorite, removeFavorite, isFavorite, 
    addAlarm, getAlarms, removeAlarm, getAllActiveAlarms, deactivateAlarm 
} from './db.js';
import { connectDB } from './db_mongo.js';

dotenv.config({ path: path.join(__dirname, '../.env') });

import crypto from 'crypto';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
    cors: { origin: "*", methods: ["GET", "POST"] }
});

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
const CACHE_DURATION = 15 * 1000; // 15 saniyeye düşürüldü (Daha anlık)

async function getCachedExec(command, cacheKey) {
    const now = Date.now();
    if (cache[cacheKey] && (now - cache[cacheKey].timestamp < CACHE_DURATION)) {
        return cache[cacheKey].data;
    }

    try {
        const { stdout, stderr } = await execAsync(command);

        if (stderr && !stdout) {
            console.error(`Script Stderr (${cacheKey}):`, stderr);
        }

        const trimmedStdout = stdout.trim();
        let data = null;

        // Try to parse the whole output first
        try {
            data = JSON.parse(trimmedStdout);
        } catch (e) {
            // If that fails, find JSON-like object in the output (e.g. { ... })
            // We look from the end to find the most likely JSON payload
            const lines = trimmedStdout.split('\n');
            let potentialJson = "";
            let openBraces = 0;
            let foundJson = false;

            for (let i = lines.length - 1; i >= 0; i--) {
                const line = lines[i];
                potentialJson = line + "\n" + potentialJson;
                if (line.includes('}')) openBraces++;
                if (line.includes('{')) openBraces--;

                if (openBraces === 0 && potentialJson.trim().startsWith('{')) {
                    try {
                        data = JSON.parse(potentialJson);
                        foundJson = true;
                        break;
                    } catch (err) {
                        // Not a valid JSON yet, keep looking
                    }
                }
            }

            if (!foundJson) {
                console.error(`Invalid JSON output from ${command}. Stdout:`, stdout);
                throw new Error("Output contains no valid JSON");
            }
        }

        cache[cacheKey] = { data, timestamp: now };
        return data;
    } catch (err) {
        console.error(`Exec Error (${cacheKey}):`, err.message);
        throw err;
    }
}

// Hisse Verisi Endpoint'i
app.get('/api/stock/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        const data = await getCachedExec(`python api/tv_api.py ${symbol}`, `stock_${symbol}`);
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
        const data = await getCachedExec(`python api/real_akd_api.py ${symbol}`, `akd_${symbol}`);
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
        const data = await getCachedExec(`python api/takas_api.py ${symbol}`, `takas_${symbol}`);
        res.json(data);
    } catch (error) {
        console.error('Takas API Hatası:', error);
        res.status(500).json({ error: 'Takas verisi çekilemedi' });
    }
});

// Geçmiş Veri (Grafik İçin) Endpoint'i
app.get('/api/history/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        // scanner_api.py veya tv_api.py üzerinden yfinance verisi çekilebilir
        const data = await getCachedExec(`python api/tv_api.py ${symbol} history`, `history_${symbol}`);
        res.json(data);
    } catch (error) {
        console.error('Geçmiş Veri API Hatası:', error);
        res.status(500).json({ error: 'Geçmiş veriler alınamadı' });
    }
});

// Bülten Verisi Endpoint'i
app.get('/api/bulten', async (req, res) => {
    try {
        const data = await getCachedExec('python api/bulten_api.py', 'bulten');
        res.json(data);
    } catch (error) {
        console.error('Bülten API Hatası:', error);
        res.status(500).json({ error: 'Bülten verisi çekilemedi' });
    }
});

// Fon Verisi Endpoint'i
app.get('/api/fon', async (req, res) => {
    try {
        const data = await getCachedExec('python api/fon_api.py', 'fon');
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
        const data = await getCachedExec(`python api/scanner_api.py ${category}`, `scan_${category}`);
        res.json(data);
    } catch (error) {
        console.error('Tarama API Hatası:', error);
        res.status(500).json({ error: 'Tarama verisi çekilemedi' });
    }
});

const MATRIKS_DATA_DIR = path.join(__dirname, '../data/matriks');
if (!fs.existsSync(MATRIKS_DATA_DIR)) {
    fs.mkdirSync(MATRIKS_DATA_DIR, { recursive: true });
}

// Matriks Köprü (Bridge) AKD Veri Alma Endpoint'i
app.post('/api/push-matriks-akd/:symbol', (req, res) => {
    const { symbol } = req.params;
    const { token, data } = req.body;
    if (token !== process.env.MATRIKS_BRIDGE_TOKEN) {
        return res.status(403).json({ error: 'Bridge Token Geçersiz' });
    }
    try {
        const filePath = path.join(MATRIKS_DATA_DIR, `${symbol.toUpperCase()}_akd.json`);
        fs.writeFileSync(filePath, JSON.stringify({ timestamp: Date.now(), data }));
        console.log(`[BRIDGE] ${symbol} AKD verisi güncellendi.`);
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: 'Dosya yazılamadı' });
    }
});

// Matriks Köprü (Bridge) Derinlik (Order Book) Veri Alma Endpoint'i
app.post('/api/push-matriks-derinlik/:symbol', (req, res) => {
    const { symbol } = req.params;
    const { token, data } = req.body;
    if (token !== process.env.MATRIKS_BRIDGE_TOKEN) {
        return res.status(403).json({ error: 'Bridge Token Geçersiz' });
    }
    try {
        const filePath = path.join(MATRIKS_DATA_DIR, `${symbol.toUpperCase()}_derinlik.json`);
        fs.writeFileSync(filePath, JSON.stringify({ timestamp: Date.now(), data }));
        console.log(`[BRIDGE] ${symbol} Derinlik verisi güncellendi.`);
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ error: 'Dosya yazılamadı' });
    }
});

// Derinlik (Order Book) Verisi Endpoint'i
app.get('/api/derinlik/:symbol', async (req, res) => {
    const { symbol } = req.params;
    
    // 1. Önce Matriks Bridge (Cache) kontrol et
    const filePath = path.join(MATRIKS_DATA_DIR, `${symbol.toUpperCase()}_derinlik.json`);
    if (fs.existsSync(filePath)) {
        try {
            const raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            const ageMs = Date.now() - raw.timestamp;
            // Eğer veri 1 dakikadan yeniyse kullan
            if (ageMs < 60000) {
                return res.json({ ...raw.data, age_seconds: Math.round(ageMs / 1000), source: "Matriks Bridge" });
            }
        } catch (e) {}
    }

    // 2. Cache yoksa veya eskiyse Matriks REST API üzerinden çekmeyi dene
    try {
        const data = await getCachedExec(`python3 src/api/matriks_api.py ${symbol} orderbook`, `depth_${symbol}`);
        if (data && !data.error) {
            return res.json(data);
        }
    } catch (error) {}

    // 3. Hiçbiri yoksa hata ver
    res.status(404).json({ error: 'Derinlik verisi bulunamadı' });
});

// Önbelleğe alınmış Derinlik verisini okuma endpoint'i (Legacy support)
app.get('/api/derinlik-cache/:symbol', (req, res) => {
    const { symbol } = req.params;
    const filePath = path.join(MATRIKS_DATA_DIR, `${symbol.toUpperCase()}_derinlik.json`);
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Henüz derinlik verisi yok' });
    }
    try {
        const raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const ageMs = Date.now() - raw.timestamp;
        res.json({ ...raw.data, age_seconds: Math.round(ageMs / 1000) });
    } catch {
        res.status(500).json({ error: 'Dosya okunamadı' });
    }
});

// Önbelleğe alınmış AKD verisini okuma endpoint'i
app.get('/api/akd-cache/:symbol', (req, res) => {
    const { symbol } = req.params;
    const filePath = path.join(MATRIKS_DATA_DIR, `${symbol.toUpperCase()}_akd.json`);
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Henüz AKD verisi yok' });
    }
    try {
        const raw = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const ageMs = Date.now() - raw.timestamp;
        res.json({ ...raw.data, age_seconds: Math.round(ageMs / 1000) });
    } catch {
        res.status(500).json({ error: 'Dosya okunamadı' });
    }
});

// --- Alarm Endpoint'leri ---

app.get('/api/alarms/:userId', (req, res) => {
    try {
        const alarms = getAlarms(req.params.userId);
        res.json(alarms);
    } catch (error) {
        res.status(500).json({ error: 'Alarmlar alınamadı' });
    }
});

app.post('/api/alarms', (req, res) => {
    const { userId, symbol, targetPrice, condition } = req.body;
    const initData = req.headers['x-telegram-init-data'];
    if (!validateInitData(initData)) return res.status(401).json({ error: 'Unauthorized' });
    try {
        addAlarm(userId, symbol, targetPrice, condition);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Alarm eklenemedi' });
    }
});

app.delete('/api/alarms/:alarmId', (req, res) => {
    const { userId } = req.body;
    const initData = req.headers['x-telegram-init-data'];
    if (!validateInitData(initData)) return res.status(401).json({ error: 'Unauthorized' });
    try {
        removeAlarm(req.params.alarmId, userId);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Alarm silinemedi' });
    }
});

// --- Favori Hisse Güncel Fiyat (Batch) ---
app.post('/api/stock/batch', async (req, res) => {
    const { symbols } = req.body;
    if (!symbols || !Array.isArray(symbols)) return res.status(400).json({ error: 'symbols array required' });
    try {
        const results = {};
        await Promise.all(symbols.map(async (sym) => {
            try {
                const { stdout } = await execAsync(`python api/tv_api.py ${sym}`);
                const lines = stdout.trim().split('\n');
                let data = null;
                for (let i = lines.length - 1; i >= 0; i--) {
                    try { data = JSON.parse(lines[i]); break; } catch { }
                }
                if (data) results[sym] = data;
            } catch { }
        }));
        res.json(results);
    } catch (error) {
        res.status(500).json({ error: 'Batch fiyat alınamadı' });
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

// ======================== BACKGROUND WORKERS ========================

// 1. Alarm & Price Worker (REAL-TIME)
async function alarmWorker() {
    try {
        const alarms = await getAllActiveAlarms();
        if (alarms.length === 0) return;

        // Group by symbol to reduce API calls
        const symbols = [...new Set(alarms.map(a => a.symbol))];
        
        for (const symbol of symbols) {
            try {
                // Get current price
                const command = `python api/tv_api.py ${symbol}`;
                const { stdout } = await execAsync(command);
                const priceData = JSON.parse(stdout.trim().split('\n').pop());
                const currentPrice = priceData.price;

                // Broadcast real-time price to all clients
                io.emit('price_update', { symbol, price: currentPrice, change: priceData.change });

                // Check alarms for this symbol
                const symbolAlarms = alarms.filter(a => a.symbol === symbol);
                for (const alarm of symbolAlarms) {
                    let triggered = false;
                    if (alarm.condition === 'ABOVE' && currentPrice >= alarm.target_price) triggered = true;
                    if (alarm.condition === 'BELOW' && currentPrice <= alarm.target_price) triggered = true;

                    if (triggered) {
                        console.log(`[ALARM] Triggered: ${symbol} at ${currentPrice} (${alarm.condition} ${alarm.target_price})`);
                        
                        // Send Telegram Notification
                        if (BOT_TOKEN) {
                            const message = `🔔 *ALARM TETİKLENDİ!*\n\n*Sembol:* ${symbol}\n*Fiyat:* ${currentPrice}\n*Hedef:* ${alarm.target_price}\n*Durum:* ${alarm.condition === 'ABOVE' ? 'Üzerine Çıktı' : 'Altına Düştü'}`;
                            const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
                            axios.post(url, {
                                chat_id: alarm.user_id,
                                text: message,
                                parse_mode: 'Markdown'
                            }).catch(e => console.error("Telegram error:", e.response?.data || e.message));
                        }

                        // Deactivate alarm
                        deactivateAlarm(alarm.id);
                    }
                }
            } catch (err) { /* ignore single symbol errors */ }
        }
    } catch (err) {
        console.error("Alarm Worker Error:", err);
    }
}

// 2. Signal & Scan Worker (ROBOT EYE)
async function signalWorker() {
    try {
        const command = `python api/signal_scanner.py`;
        const { stdout } = await execAsync(command);
        const signals = JSON.parse(stdout.trim().split('\n').pop());
        
        if (signals && signals.length > 0) {
            io.emit('market_signals', signals);
            console.log(`[SIGNAL] Broadcasted ${signals.length} market signals.`);
        }
    } catch (err) {
        console.error("Signal Worker Error:", err);
    }
}

// Register Socket.io connection
io.on('connection', (socket) => {
    console.log(`[SOCKET] User connected: ${socket.id}`);
    socket.on('disconnect', () => console.log(`[SOCKET] User disconnected`));
});

// Run Workers
setInterval(alarmWorker, 10000); // Check prices every 10s
setInterval(signalWorker, 60000); // Scan market every 1m

// Init DB & Start Server
connectDB().finally(() => {
    httpServer.listen(PORT, () => {
        console.log(`API Sunucusu http://localhost:${PORT} adresinde çalışıyor (WebSockets Aktif)`);
    });
});
