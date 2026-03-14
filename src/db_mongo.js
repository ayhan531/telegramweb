import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '../.env') });

const MONGODB_URI = process.env.MONGODB_URI;

const userSchema = new mongoose.Schema({
  telegramId: { type: String, unique: true, required: true },
  username: String,
  firstName: String,
  createdAt: { type: Date, default: Date.now }
});

const favoriteSchema = new mongoose.Schema({
  userId: String,
  symbol: String,
  createdAt: { type: Date, default: Date.now }
});

const alarmSchema = new mongoose.Schema({
  userId: String,
  symbol: String,
  targetPrice: Number,
  condition: { type: String, enum: ['ABOVE', 'BELOW'] },
  createdAt: { type: Date, default: Date.now },
  isActive: { type: Boolean, default: true }
});

export const User = mongoose.model('User', userSchema);
export const Favorite = mongoose.model('Favorite', favoriteSchema);
export const Alarm = mongoose.model('Alarm', alarmSchema);

export const connectDB = async () => {
  if (!MONGODB_URI) {
    console.log('[DB] MongoDB URI not found. Staying on SQLite (Professional Hybrid Mode).');
    return false;
  }
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('[DB] MongoDB connected successfuly (Cloud Mode).');
    return true;
  } catch (err) {
    console.error('[DB] MongoDB connection error:', err);
    return false;
  }
};
