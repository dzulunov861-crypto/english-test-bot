# Elementary English Test Bot

Telegram bot — 30 ta savol: zamonlar, prepositions, how many/much, reading.

## Fayllar
- `bot.py` — asosiy bot kodi
- `requirements.txt` — kerakli kutubxonalar
- `Procfile` — Railway/Render uchun ishga tushirish buyrug'i

## Railway'ga joylashtirish (bepul)

1. https://railway.app ga kiring, GitHub bilan ro'yxatdan o'ting
2. **New Project** → **Deploy from GitHub repo** bosing
3. Ushbu fayllarni GitHub repoga yuklang (yoki Railway'ning drag&drop'idan foydalaning)
4. Railway dashboard'da **Variables** bo'limiga o'ting
5. Quyidagi environment variable qo'shing:
   ```
   BOT_TOKEN = 7123456789:AAF...  ← BotFather dan olgan token
   ```
6. Deploy avtomatik boshlanadi — bir necha daqiqada bot ishlab ketadi

## Render'ga joylashtirish (bepul)

1. https://render.com ga kiring
2. **New** → **Background Worker** tanlang
3. GitHub repo ulang
4. **Environment Variables** ga `BOT_TOKEN` qo'shing
5. **Start Command**: `python bot.py`
6. Deploy bosing

## Lokal sinash (ixtiyoriy)

```bash
pip install -r requirements.txt
export BOT_TOKEN="your_token_here"
python bot.py
```
