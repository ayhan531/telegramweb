import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { exec } from 'child_process';
import { promisify } from 'util';

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execAsync = promisify(exec);
dotenv.config({ path: path.join(__dirname, '../.env') });

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || process.env.API_PORT || 3000;

// Hisse Verisi Endpoint'i
app.get('/api/stock/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        const { stdout } = await execAsync(`python3 api/tv_api.py ${symbol}`);
        const data = JSON.parse(stdout);
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
        const { stdout } = await execAsync(`python3 api/real_akd_api.py ${symbol}`);
        const data = JSON.parse(stdout);
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
        const { stdout } = await execAsync(`python3 api/takas_api.py ${symbol}`);
        const data = JSON.parse(stdout);
        res.json(data);
    } catch (error) {
        console.error('Takas API Hatası:', error);
        res.status(500).json({ error: 'Takas verisi çekilemedi' });
    }
});

// Serve Frontend
app.use(express.static(path.join(__dirname, '../web-app/dist')));

// Wildcard to handle React Router if used, otherwise serves index.html
app.get(/^(?!\/api).+/, (req, res) => {
    res.sendFile(path.join(__dirname, '../web-app/dist/index.html'));
});

app.listen(PORT, () => {
    console.log(`API Sunucusu http://localhost:${PORT} adresinde çalışıyor`);
});
