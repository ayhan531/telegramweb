import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
dotenv.config({ path: '../.env' });

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.API_PORT || 3000;

// Hisse Verisi Endpoint'i
app.get('/api/stock/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        // Python script'ini çağırarak veri al (veya doğrudan kütüphaneleri kullan)
        // Şimdilik örnek veri döndürelim, daha sonra gerçek entegrasyon yapılacak
        res.json({
            symbol,
            price: 284.50,
            change: 1.25,
            name: "TURK HAVA YOLLARI",
            currency: "TRY"
        });
    } catch (error) {
        res.status(500).json({ error: 'Veri çekilemedi' });
    }
});

// AKD Verisi Endpoint'i
app.get('/api/akd/:symbol', async (req, res) => {
    const { symbol } = req.params;
    try {
        res.json({
            symbol,
            buyers: [
                { kurum: "YATIRIM FINANSMAN", lot: "1.250.000" },
                { kurum: "AK YATIRIM", lot: "850.000" }
            ],
            sellers: [
                { kurum: "BOFA", lot: "1.400.000" },
                { kurum: "ZIRAAT YATIRIM", lot: "900.000" }
            ]
        });
    } catch (error) {
        res.status(500).json({ error: 'AKD verisi çekilemedi' });
    }
});

app.listen(PORT, () => {
    console.log(`API Sunucusu http://localhost:${PORT} adresinde çalışıyor`);
});
