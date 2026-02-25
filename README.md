# 📈 StockSense AI
### Indian Market & Crypto News Intelligence Engine

> AI-powered stock analysis that reads news and tells you what it means for your investments.

---

## 🚀 Run It Tonight — Step by Step

### Prerequisites (install these first)
```bash
# Python 3.10+
python --version

# Node.js (for future React build, optional tonight)
node --version
```

---

## ⚡ Option A: Just the Frontend (Works Right Now, No Setup)

1. Open `frontend/index.html` directly in your browser
2. That's it. The app runs in DEMO MODE with simulated data.
3. Every feature works — search, charts, AI analysis, market mood.

---

## 🔥 Option B: Full App with Live Data (Backend + Frontend)

### Step 1 — Install Python packages
```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Start the backend
```bash
uvicorn main:app --reload --port 8000
```
You'll see: `INFO: Uvicorn running on http://127.0.0.1:8000`

### Step 3 — Open the frontend
Open `frontend/index.html` in your browser.
The demo mode banner will disappear and you'll see live data.

### Step 4 — Test the API directly (optional)
```
http://localhost:8000/api/stock/RELIANCE
http://localhost:8000/api/stock/TCS
http://localhost:8000/api/stock/BTC
http://localhost:8000/api/market/overview
```

---

## 🧠 Option C: Fine-Tune Your Own Model (Weekend Project)

### Step 1 — Build your dataset
```bash
cd models
pip install -r ../backend/requirements.txt
python build_dataset.py
# Creates data/labeled_news.csv with ~200+ labeled samples
```

### Step 2 — Fine-tune FinBERT
```bash
python finetune.py
# Takes 30–60 mins on CPU, 5–10 mins on GPU
# Model saved to models/stocksense-finbert/
```

### Step 3 — Use your fine-tuned model
In `backend/main.py`, change:
```python
from analyzer import StockAnalyzer        # rule-based (default)
# to:
from models.model_inference import StockAnalyzer  # your fine-tuned model
```

---

## 📁 Project Structure

```
stocksense/
├── backend/
│   ├── main.py          ← FastAPI server (all API endpoints)
│   ├── analyzer.py      ← AI brain (rule-based NLP engine)
│   └── requirements.txt
│
├── frontend/
│   └── index.html       ← Complete React dashboard (single file)
│
├── models/
│   ├── finetune.py      ← FinBERT fine-tuning script
│   ├── build_dataset.py ← Dataset builder from live news
│   └── model_inference.py ← Fine-tuned model inference
│
└── data/                ← Created by build_dataset.py
    ├── labeled_news.csv
    └── raw_news.json
```

---

## 🎯 Features

| Feature | Description |
|---|---|
| 📰 News Analysis | Every news item analyzed for sentiment, impact, event type |
| 🧠 AI Reasoning | Model explains WHY it made its prediction |
| 📊 Price Charts | 30-day price history with area charts |
| 🎯 Verdict | Overall AI verdict synthesizing all news signals |
| ⚠️ Risk Flags | Detects Regulatory Risk, Fraud Risk, Cyber Risk etc. |
| 📈 Market Mood | Fear & Greed gauge for overall market |
| 🔄 Live Ticker | Nifty50, Sensex, BTC prices scrolling live |
| 🇮🇳 Indian Focus | NSE/BSE stocks + Crypto in one place |

---

## 🏗️ Architecture

```
User types "RELIANCE"
    ↓
FastAPI backend
    ↓
yfinance → current price, 30d history
    ↓
RSS/yfinance news → latest headlines
    ↓
StockAnalyzer (analyzer.py)
    ↓ for each news item:
    • Keyword scoring (bullish/bearish)
    • Event type classification
    • Risk flag detection
    • Confidence calculation
    • Reasoning generation
    ↓
overall_verdict() → synthesizes all signals
    ↓
React Dashboard → charts, cards, gauge
```

---

## 📊 Supported Symbols

**NSE Stocks:** RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, WIPRO, ADANIENT, TATAMOTORS, SBIN, BAJFINANCE, HINDUNILVR, MARUTI, SUNPHARMA, ONGC, ITC (and any NSE symbol)

**Crypto:** BTC, ETH, BNB, SOL, ADA, XRP, DOGE, MATIC

---

## 🔮 Upgrade Path (for portfolio / demo day)

1. **Better Model** → Fine-tune Mistral-7B-Instruct on your dataset for richer reasoning
2. **More Data** → Add Screener.in, NSE announcements, SEBI circulars
3. **Push Alerts** → Email/Telegram alert when HIGH impact bearish news detected
4. **Portfolio Mode** → Track multiple stocks, aggregate risk score
5. **Backtesting** → Test how well past signals predicted price movements

---

## ⚠️ Disclaimer

StockSense AI is an **educational tool only**. It does not constitute financial advice. All AI predictions are probabilistic estimates. Past patterns do not guarantee future performance. Always consult a **SEBI-registered financial advisor** before making investment decisions.

---

## 🏆 Portfolio / Hackathon Highlights

- ✅ **Real fine-tuning** — not just prompting an existing model
- ✅ **Domain-specific** — Indian market focus, not generic
- ✅ **Decision intelligence** — reasoning chain, not just sentiment score
- ✅ **Full stack** — working backend + beautiful frontend
- ✅ **Production-ready patterns** — proper error handling, fallbacks
- ✅ **Upgrade path** — clear roadmap from MVP to production

---

*Built with FastAPI · FinBERT · yfinance · React · Recharts*
