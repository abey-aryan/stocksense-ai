"""
StockSense AI — Backend API
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import yfinance as yf
import feedparser
import requests
import json
import re
from datetime import datetime, timedelta
from analyzer import StockAnalyzer
# from models.model_inference import StockAnalyzer

app = FastAPI(title="StockSense AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = StockAnalyzer()

# ── Indian Stock Tickers ──────────────────────────────────────────────────────
POPULAR_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "WIPRO": "WIPRO.NS",
    "ADANIENT": "ADANIENT.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "SBIN": "SBIN.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "ONGC": "ONGC.NS",
    "ITC": "ITC.NS",
}

CRYPTO_TICKERS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "BNB": "BNB-USD",
    "SOL": "SOL-USD",
    "ADA": "ADA-USD",
    "XRP": "XRP-USD",
    "DOGE": "DOGE-USD",
    "MATIC": "MATIC-USD",
}

NEWS_RSS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "https://feeds.feedburner.com/ndtvprofit-latest",
    "https://www.business-standard.com/rss/markets-106.rss",
]


@app.get("/")
def root():
    return {"status": "StockSense AI is running 🚀", "version": "1.0.0"}


@app.get("/api/stock/{symbol}")
def get_stock_analysis(symbol: str):
    """Main endpoint: fetch stock data + analyze latest news"""
    symbol = symbol.upper()

    # Resolve ticker
    ticker_symbol = POPULAR_STOCKS.get(symbol) or CRYPTO_TICKERS.get(symbol)
    if not ticker_symbol:
        # Try appending .NS for NSE
        ticker_symbol = f"{symbol}.NS"

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="30d")

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100

        # Price history for chart
        price_history = [
            {"date": str(idx.date()), "price": round(float(row["Close"]), 2), "volume": int(row["Volume"])}
            for idx, row in hist.iterrows()
        ]

        # Fetch and analyze news
        news_items = fetch_news_for_symbol(symbol, info.get("longName", symbol))
        analyzed_news = [analyzer.analyze(item) for item in news_items[:8]]

        # Overall verdict
        verdict = analyzer.overall_verdict(analyzed_news, price_change_pct)

        is_crypto = symbol in CRYPTO_TICKERS

        return {
            "symbol": symbol,
            "ticker": ticker_symbol,
            "name": info.get("longName") or info.get("shortName") or symbol,
            "sector": info.get("sector") or ("Cryptocurrency" if is_crypto else "Unknown"),
            "is_crypto": is_crypto,
            "current_price": round(float(current_price), 2),
            "currency": "USD" if is_crypto else "INR",
            "price_change": round(float(price_change), 2),
            "price_change_pct": round(float(price_change_pct), 2),
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "price_history": price_history,
            "news": analyzed_news,
            "verdict": verdict,
            "last_updated": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/overview")
def market_overview():
    """Nifty 50, Sensex, BTC snapshot + overall market mood"""
    indices = {
        "NIFTY50": "^NSEI",
        "SENSEX": "^BSESN",
        "NIFTYBANK": "^NSEBANK",
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
    }
    results = {}
    for name, sym in indices.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if not h.empty and len(h) >= 2:
                curr = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2])
                chg_pct = ((curr - prev) / prev) * 100
                results[name] = {
                    "price": round(curr, 2),
                    "change_pct": round(chg_pct, 2),
                    "direction": "up" if chg_pct >= 0 else "down",
                }
        except:
            results[name] = {"price": 0, "change_pct": 0, "direction": "neutral"}

    # Market mood score (0-100)
    changes = [v["change_pct"] for v in results.values() if v["change_pct"] != 0]
    avg_change = sum(changes) / len(changes) if changes else 0
    mood_score = min(100, max(0, int(50 + avg_change * 5)))
    mood_label = (
        "Extreme Fear" if mood_score < 20
        else "Fear" if mood_score < 40
        else "Neutral" if mood_score < 60
        else "Greed" if mood_score < 80
        else "Extreme Greed"
    )

    return {
        "indices": results,
        "mood_score": mood_score,
        "mood_label": mood_label,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/news/feed")
def get_news_feed():
    """Latest market news with AI analysis"""
    all_news = []
    for feed_url in NEWS_RSS_FEEDS[:2]:  # Limit for speed
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                item = {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:200],
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", "News"),
                }
                analyzed = analyzer.analyze(item)
                all_news.append(analyzed)
        except:
            pass

    # Sort by impact
    impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_news.sort(key=lambda x: impact_order.get(x.get("impact", "LOW"), 2))

    return {"news": all_news[:15], "timestamp": datetime.now().isoformat()}


@app.get("/api/watchlist")
def get_watchlist():
    """Quick snapshot of top Indian stocks"""
    watchlist = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ADANIENT", "WIPRO"]
    results = []
    for sym in watchlist:
        try:
            ticker = yf.Ticker(POPULAR_STOCKS[sym])
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                curr = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                chg_pct = ((curr - prev) / prev) * 100
                results.append({
                    "symbol": sym,
                    "price": round(curr, 2),
                    "change_pct": round(chg_pct, 2),
                    "direction": "up" if chg_pct >= 0 else "down",
                })
        except:
            pass
    return {"watchlist": results}

def fetch_news_for_symbol(symbol: str, company_name: str) -> list:
    """Fetch relevant news for a specific symbol, filtering out empty data"""
    news_items = []

    # Try yfinance news first
    try:
        ticker = yf.Ticker(
            POPULAR_STOCKS.get(symbol) or CRYPTO_TICKERS.get(symbol) or f"{symbol}.NS"
        )
        yf_news = ticker.news or []
        
        for item in yf_news:
            # yfinance changes its dictionary structure often. Let's catch all formats:
            title = item.get("title") or item.get("content", {}).get("title") or ""
            summary = item.get("summary") or item.get("content", {}).get("summary") or ""
            
            # ONLY add the news item if we successfully grabbed a real title
            if title.strip():
                news_items.append({
                    "title": title,
                    "summary": summary[:300],
                    "link": item.get("link", ""),
                    "published": "Recent",
                    "source": item.get("publisher", "Yahoo Finance"),
                })
                
            if len(news_items) >= 6:
                break
    except:
        pass

    # Fallback RSS (Will trigger if Yahoo Finance gives us blank data)
    if len(news_items) < 3:
        for feed_url in NEWS_RSS_FEEDS[:1]:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    title = entry.get("title", "")
                    if (symbol.lower() in title.lower() or
                            any(w.lower() in title.lower() for w in company_name.split()[:2])):
                        if title.strip():
                            news_items.append({
                                "title": title,
                                "summary": entry.get("summary", "")[:300],
                                "link": entry.get("link", ""),
                                "published": entry.get("published", ""),
                                "source": feed.feed.get("title", "News"),
                            })
            except:
                pass

    # If still empty, add general Indian market news from Economic Times
    if not news_items:
        try:
            feed = feedparser.parse(NEWS_RSS_FEEDS[0])
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                if title.strip():
                    news_items.append({
                        "title": title,
                        "summary": entry.get("summary", "")[:300],
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.get("title", "News"),
                    })
        except:
            pass

    return news_items[:8]
    


# def fetch_news_for_symbol(symbol: str, company_name: str) -> list:
#     """Fetch relevant news for a specific symbol"""
#     news_items = []

#     # Try yfinance news first
#     try:
#         ticker = yf.Ticker(
#             POPULAR_STOCKS.get(symbol) or CRYPTO_TICKERS.get(symbol) or f"{symbol}.NS"
#         )
#         yf_news = ticker.news or []
#         for item in yf_news[:6]:
#             news_items.append({
#                 "title": item.get("title", ""),
#                 "summary": item.get("summary", item.get("title", ""))[:300],
#                 "link": item.get("link", ""),
#                 "published": datetime.fromtimestamp(
#                     item.get("providerPublishTime", datetime.now().timestamp())
#                 ).strftime("%Y-%m-%d %H:%M"),
#                 "source": item.get("publisher", "Yahoo Finance"),
#             })
#     except:
#         pass

#     # Fallback RSS
#     if len(news_items) < 3:
#         for feed_url in NEWS_RSS_FEEDS[:1]:
#             try:
#                 feed = feedparser.parse(feed_url)
#                 for entry in feed.entries[:10]:
#                     title = entry.get("title", "")
#                     if (symbol.lower() in title.lower() or
#                             any(w.lower() in title.lower()
#                                 for w in company_name.split()[:2])):
#                         news_items.append({
#                             "title": title,
#                             "summary": entry.get("summary", "")[:300],
#                             "link": entry.get("link", ""),
#                             "published": entry.get("published", ""),
#                             "source": feed.feed.get("title", "News"),
#                         })
#             except:
#                 pass

#     # If still empty, add general market news
#     if not news_items:
#         try:
#             feed = feedparser.parse(NEWS_RSS_FEEDS[0])
#             for entry in feed.entries[:5]:
#                 news_items.append({
#                     "title": entry.get("title", ""),
#                     "summary": entry.get("summary", "")[:300],
#                     "link": entry.get("link", ""),
#                     "published": entry.get("published", ""),
#                     "source": feed.feed.get("title", "News"),
#                 })
#         except:
#             pass

#     return news_items
