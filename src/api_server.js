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
const distPath = path.join(__dirname, '../web-app/dist');

// Check if dist directory exists
if (!fs.existsSync(distPath)) {
    console.error(`UYARI: Frontend build klasörü bulunamadı: ${distPath}`);
    console.error('Lütfen "npm run build" komutunu çalıştırdığınızdan emin olun.');
}

app.use(express.static(distPath));

// Wildcard to handle React Router and ensure index.html is served for all non-API routes
app.get('*', (req, res) => {
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
