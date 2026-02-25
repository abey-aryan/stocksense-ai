# """
# StockSense AI — Analyzer Engine
# This is the AI brain. Uses rule-based NLP + FinBERT-style keyword analysis.
# When you fine-tune your model, replace the analyze() method with your model's inference.
# """

# import re
# from datetime import datetime
# from typing import List, Dict, Optional


# # ── Keyword Dictionaries ──────────────────────────────────────────────────────

# STRONG_BULLISH = [
#     "record profit", "beats estimate", "strong quarterly", "revenue surge",
#     "raises guidance", "dividend declared", "buyback", "major deal won",
#     "acquisition approved", "partnership signed", "regulatory approval",
#     "fda approved", "sebi approved", "ipo oversubscribed", "order wins",
#     "debt free", "promoter buying", "insider buying", "upgrade", "outperform",
#     "all time high", "52 week high", "strong demand", "expansion plan",
#     "new contract", "billion dollar", "exports rise", "market share gain",
#     "bullish", "rally", "surge", "soar", "jump", "skyrocket",
#     "etf inclusion", "index inclusion", "msci inclusion",
# ]

# MILD_BULLISH = [
#     "meets estimate", "in line with", "steady growth", "positive outlook",
#     "optimistic", "recovery", "improvement", "good results", "healthy",
#     "resilient", "consistent", "growing", "rising", "increase",
#     "profit rise", "revenue growth", "margin improvement",
# ]

# STRONG_BEARISH = [
#     "sebi notice", "sebi penalty", "sebi ban", "rbi action", "ed raid",
#     "cbi investigation", "fraud", "scam", "money laundering", "bribery",
#     "corruption", "arrest", "insider trading", "accounting irregularity",
#     "misappropriation", "default", "npa", "bankruptcy", "insolvency",
#     "debt crisis", "credit downgrade", "rating downgrade", "massive loss",
#     "profit warning", "revenue miss", "lowers guidance", "ceo resigned",
#     "cfo resigned", "promoter selling", "exit", "plant shutdown",
#     "hack", "data breach", "cyberattack", "ransomware",
#     "crash", "collapse", "plunge", "tank", "fall sharply",
#     "52 week low", "all time low",
# ]

# MILD_BEARISH = [
#     "misses estimate", "below expectation", "concern", "cautious",
#     "headwinds", "slowdown", "pressure", "challenging", "weak",
#     "below estimate", "margin squeeze", "cost rise", "inflation impact",
#     "competition", "market share loss", "decline", "drop", "fall",
# ]

# NEUTRAL_SIGNALS = [
#     "holds steady", "in line", "as expected", "board meeting",
#     "agm scheduled", "result date", "quarterly review", "analyst meet",
#     "conference", "presentation", "policy unchanged",
# ]

# # Event type classification
# EVENT_TYPES = {
#     "Regulatory Action": ["sebi", "rbi", "ed", "cbi", "notice", "penalty", "ban", "raid", "investigation"],
#     "Earnings Report": ["quarterly", "result", "profit", "revenue", "earnings", "q1", "q2", "q3", "q4", "fy"],
#     "Corporate Action": ["dividend", "buyback", "split", "bonus", "rights issue", "merger", "acquisition"],
#     "Management Change": ["ceo", "cfo", "cto", "md", "chairman", "resigned", "appointed", "new head"],
#     "Market Event": ["ipo", "listing", "delisting", "index", "inclusion", "exclusion"],
#     "Macro/Sector": ["rbi policy", "budget", "gdp", "inflation", "rate", "interest", "oil", "rupee"],
#     "Business Update": ["deal", "contract", "order", "partnership", "expansion", "plant", "launch"],
#     "Risk Event": ["fraud", "hack", "breach", "default", "insolvency", "lawsuit", "litigation"],
# }

# # Historical patterns for similar events
# HISTORICAL_PATTERNS = {
#     "Regulatory Action": {
#         "avg_impact": -4.2,
#         "recovery_days": 7,
#         "example": "SEBI notices have historically caused 3–8% corrections in large caps within 2–3 trading days.",
#     },
#     "Earnings Report": {
#         "avg_impact": 2.1,
#         "recovery_days": 2,
#         "example": "Strong earnings beats typically drive 2–5% gains in the session following the announcement.",
#     },
#     "Corporate Action": {
#         "avg_impact": 1.8,
#         "recovery_days": 1,
#         "example": "Dividend declarations and buybacks signal financial strength, typically adding 1–3%.",
#     },
#     "Management Change": {
#         "avg_impact": -1.5,
#         "recovery_days": 5,
#         "example": "Unexpected CEO exits create short-term uncertainty, typically 1–4% downside before stabilization.",
#     },
#     "Risk Event": {
#         "avg_impact": -6.8,
#         "recovery_days": 14,
#         "example": "Fraud allegations or data breaches cause sharp corrections, often 5–15% in the near term.",
#     },
#     "Business Update": {
#         "avg_impact": 1.2,
#         "recovery_days": 2,
#         "example": "New contract wins typically boost sentiment by 1–3%, especially in IT and infra sectors.",
#     },
#     "Macro/Sector": {
#         "avg_impact": 0.5,
#         "recovery_days": 3,
#         "example": "Macro events affect the broad market; sector-specific impact depends on direct exposure.",
#     },
#     "Market Event": {
#         "avg_impact": 3.5,
#         "recovery_days": 1,
#         "example": "Index inclusions drive strong institutional buying, often 3–8% over 5 trading days.",
#     },
# }


# class StockAnalyzer:
#     """
#     Rule-based financial news analyzer.
#     This simulates a fine-tuned LLM. Replace analyze() with your model's
#     inference call once you've fine-tuned FinBERT or Mistral on your dataset.
#     """

#     def analyze(self, news_item: Dict) -> Dict:
#         title = news_item.get("title", "").lower()
#         summary = news_item.get("summary", "").lower()
#         full_text = f"{title} {summary}"

#         # Score calculation
#         bullish_score = sum(2 for kw in STRONG_BULLISH if kw in full_text)
#         bullish_score += sum(1 for kw in MILD_BULLISH if kw in full_text)
#         bearish_score = sum(2 for kw in STRONG_BEARISH if kw in full_text)
#         bearish_score += sum(1 for kw in MILD_BEARISH if kw in full_text)

#         net_score = bullish_score - bearish_score

#         # Sentiment classification
#         if net_score >= 4:
#             sentiment = "STRONGLY BULLISH"
#             sentiment_score = min(0.95, 0.70 + net_score * 0.03)
#             direction = "UP"
#             color = "bullish"
#         elif net_score >= 1:
#             sentiment = "MILDLY BULLISH"
#             sentiment_score = 0.55 + net_score * 0.05
#             direction = "UP"
#             color = "bullish"
#         elif net_score <= -4:
#             sentiment = "STRONGLY BEARISH"
#             sentiment_score = min(0.95, 0.70 + abs(net_score) * 0.03)
#             direction = "DOWN"
#             color = "bearish"
#         elif net_score <= -1:
#             sentiment = "MILDLY BEARISH"
#             sentiment_score = 0.55 + abs(net_score) * 0.05
#             direction = "DOWN"
#             color = "bearish"
#         else:
#             sentiment = "NEUTRAL"
#             sentiment_score = 0.50
#             direction = "SIDEWAYS"
#             color = "neutral"

#         # Impact level
#         if abs(net_score) >= 4:
#             impact = "HIGH"
#         elif abs(net_score) >= 2:
#             impact = "MEDIUM"
#         else:
#             impact = "LOW"

#         # Event type detection
#         event_type = self._detect_event_type(full_text)

#         # Risk flags
#         risk_flags = self._extract_risk_flags(full_text)

#         # Time horizon
#         time_horizon = self._estimate_time_horizon(event_type, impact)

#         # Confidence
#         confidence = self._calculate_confidence(net_score, impact, risk_flags)

#         # Reasoning chain
#         reasoning = self._generate_reasoning(
#             news_item.get("title", ""), sentiment, event_type,
#             impact, risk_flags, net_score, confidence
#         )

#         # Historical context
#         historical = HISTORICAL_PATTERNS.get(event_type, {})

#         return {
#             **news_item,
#             "sentiment": sentiment,
#             "sentiment_score": round(sentiment_score, 2),
#             "direction": direction,
#             "color": color,
#             "impact": impact,
#             "event_type": event_type,
#             "risk_flags": risk_flags,
#             "time_horizon": time_horizon,
#             "confidence": confidence,
#             "reasoning": reasoning,
#             "historical_pattern": historical.get("example", ""),
#             "avg_historical_impact": historical.get("avg_impact", 0),
#             "analyzed_at": datetime.now().isoformat(),
#         }

#     def overall_verdict(self, analyzed_news: List[Dict], price_change_pct: float) -> Dict:
#         """Generate an overall AI verdict from all news + price action"""
#         if not analyzed_news:
#             return self._default_verdict(price_change_pct)

#         # Weight scores by impact
#         weight_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
#         total_weight = 0
#         weighted_score = 0

#         bullish_count = 0
#         bearish_count = 0
#         neutral_count = 0
#         high_impact_events = []

#         for item in analyzed_news:
#             w = weight_map.get(item.get("impact", "LOW"), 1)
#             direction = item.get("direction", "SIDEWAYS")
#             score = item.get("sentiment_score", 0.5)

#             if direction == "UP":
#                 weighted_score += score * w
#                 bullish_count += 1
#             elif direction == "DOWN":
#                 weighted_score -= score * w
#                 bearish_count += 1
#             else:
#                 neutral_count += 1

#             total_weight += w

#             if item.get("impact") == "HIGH":
#                 high_impact_events.append({
#                     "title": item.get("title", ""),
#                     "direction": direction,
#                     "event_type": item.get("event_type", ""),
#                 })

#         # Net weighted sentiment
#         net = (weighted_score / total_weight) if total_weight > 0 else 0

#         # Incorporate price action
#         if price_change_pct > 2:
#             net += 0.1
#         elif price_change_pct < -2:
#             net -= 0.1

#         # Overall verdict
#         if net > 0.3:
#             verdict_label = "BULLISH"
#             verdict_emoji = "🟢"
#             short_term = "Upside likely in next 1–3 trading sessions"
#             risk_level = "LOW" if net > 0.5 else "MEDIUM"
#         elif net > 0.05:
#             verdict_label = "CAUTIOUSLY BULLISH"
#             verdict_emoji = "🟡"
#             short_term = "Mild upside possible; watch for reversals"
#             risk_level = "MEDIUM"
#         elif net < -0.3:
#             verdict_label = "BEARISH"
#             verdict_emoji = "🔴"
#             short_term = "Downside pressure expected in near term"
#             risk_level = "HIGH"
#         elif net < -0.05:
#             verdict_label = "CAUTIOUSLY BEARISH"
#             verdict_emoji = "🟡"
#             short_term = "Mild downside risk; monitor key levels"
#             risk_level = "MEDIUM"
#         else:
#             verdict_label = "NEUTRAL"
#             verdict_emoji = "⚪"
#             short_term = "No strong directional signal from recent news"
#             risk_level = "LOW"

#         # Summary reasoning
#         summary = self._build_verdict_summary(
#             analyzed_news, bullish_count, bearish_count,
#             neutral_count, high_impact_events, verdict_label,
#             price_change_pct
#         )

#         return {
#             "label": verdict_label,
#             "emoji": verdict_emoji,
#             "risk_level": risk_level,
#             "short_term_outlook": short_term,
#             "summary": summary,
#             "news_breakdown": {
#                 "bullish": bullish_count,
#                 "bearish": bearish_count,
#                 "neutral": neutral_count,
#             },
#             "high_impact_events": high_impact_events,
#             "confidence": min(95, int(abs(net) * 100 + 40)),
#             "net_sentiment_score": round(net, 3),
#         }

#     # ── Private helpers ────────────────────────────────────────────────────────

#     def _detect_event_type(self, text: str) -> str:
#         scores = {}
#         for event, keywords in EVENT_TYPES.items():
#             scores[event] = sum(1 for kw in keywords if kw in text)
#         best = max(scores, key=scores.get)
#         return best if scores[best] > 0 else "Business Update"

#     def _extract_risk_flags(self, text: str) -> List[str]:
#         flags = []
#         flag_map = {
#             "Regulatory Risk": ["sebi", "rbi", "notice", "penalty", "investigation", "ed", "cbi"],
#             "Fraud Risk": ["fraud", "scam", "money laundering", "bribery", "misappropriation"],
#             "Liquidity Risk": ["default", "npa", "debt", "insolvency", "bankruptcy"],
#             "Operational Risk": ["shutdown", "strike", "fire", "accident", "disruption"],
#             "Cyber Risk": ["hack", "breach", "ransomware", "cyberattack", "data leak"],
#             "Management Risk": ["ceo resign", "cfo resign", "promoter selling", "exit"],
#         }
#         for flag, keywords in flag_map.items():
#             if any(kw in text for kw in keywords):
#                 flags.append(flag)
#         return flags

#     def _estimate_time_horizon(self, event_type: str, impact: str) -> str:
#         horizons = {
#             "Regulatory Action": "3–7 trading days",
#             "Earnings Report": "1–2 trading days",
#             "Corporate Action": "1–3 trading days",
#             "Risk Event": "1–2 weeks",
#             "Management Change": "5–10 trading days",
#             "Macro/Sector": "1–5 trading days",
#             "Business Update": "1–3 trading days",
#             "Market Event": "1–5 trading days",
#         }
#         return horizons.get(event_type, "2–5 trading days")

#     def _calculate_confidence(self, net_score: int, impact: str, risk_flags: List) -> int:
#         base = 45
#         base += min(30, abs(net_score) * 5)
#         if impact == "HIGH":
#             base += 15
#         elif impact == "MEDIUM":
#             base += 8
#         if risk_flags:
#             base += 5
#         return min(92, base)

#     def _generate_reasoning(self, title: str, sentiment: str, event_type: str,
#                              impact: str, risk_flags: List, net_score: int,
#                              confidence: int) -> str:
#         parts = []

#         # Event classification
#         parts.append(f"This is classified as a **{event_type}** event with **{impact} impact**.")

#         # Sentiment basis
#         if "BULLISH" in sentiment:
#             parts.append(
#                 "Positive signals detected: strong earnings language, business wins, "
#                 "or favorable corporate actions indicate near-term upside."
#             )
#         elif "BEARISH" in sentiment:
#             parts.append(
#                 "Negative signals detected: regulatory pressure, management risk, "
#                 "or earnings concerns suggest downside pressure."
#             )
#         else:
#             parts.append("No strong directional keywords detected; market may remain range-bound.")

#         # Risk flags
#         if risk_flags:
#             parts.append(f"⚠️ Risk flags identified: {', '.join(risk_flags)}.")

#         # Confidence qualifier
#         if confidence > 75:
#             parts.append(f"Confidence is high ({confidence}%) based on clear signal strength.")
#         elif confidence > 55:
#             parts.append(f"Moderate confidence ({confidence}%). Monitor for confirming price action.")
#         else:
#             parts.append(f"Low confidence ({confidence}%). News signal is ambiguous.")

#         return " ".join(parts)

#     def _build_verdict_summary(self, news: List, bull: int, bear: int,
#                                 neutral: int, high_impact: List,
#                                 verdict: str, price_chg: float) -> str:
#         total = len(news)
#         parts = []

#         parts.append(
#             f"Analyzed {total} recent news item{'s' if total != 1 else ''}. "
#             f"{bull} bullish, {bear} bearish, {neutral} neutral."
#         )

#         if high_impact:
#             titles = [e["title"][:60] for e in high_impact[:2]]
#             parts.append(f"High-impact events: {'; '.join(titles)}.")

#         if price_chg > 2:
#             parts.append(f"Price is up {abs(price_chg):.1f}% today, confirming positive sentiment.")
#         elif price_chg < -2:
#             parts.append(f"Price is down {abs(price_chg):.1f}% today, consistent with negative news flow.")

#         if verdict in ("BEARISH", "CAUTIOUSLY BEARISH"):
#             parts.append(
#                 "Exercise caution. Consider waiting for news resolution before adding positions."
#             )
#         elif verdict in ("BULLISH", "CAUTIOUSLY BULLISH"):
#             parts.append(
#                 "News flow appears favorable. Watch volume confirmation for stronger conviction."
#             )

#         parts.append(
#             "⚠️ This is an AI-generated analysis for educational purposes only. "
#             "Not financial advice. Consult a SEBI-registered advisor before investing."
#         )

#         return " ".join(parts)

#     def _default_verdict(self, price_change_pct: float) -> Dict:
#         if price_change_pct > 1:
#             label, risk = "CAUTIOUSLY BULLISH", "LOW"
#         elif price_change_pct < -1:
#             label, risk = "CAUTIOUSLY BEARISH", "MEDIUM"
#         else:
#             label, risk = "NEUTRAL", "LOW"

#         return {
#             "label": label,
#             "emoji": "🟡",
#             "risk_level": risk,
#             "short_term_outlook": "Insufficient news data for strong signal",
#             "summary": "No recent news available. Analysis based on price action only. ⚠️ Not financial advice.",
#             "news_breakdown": {"bullish": 0, "bearish": 0, "neutral": 0},
#             "high_impact_events": [],
#             "confidence": 30,
#             "net_sentiment_score": 0,
#         }
# # ── FASTAPI SERVER ────────────────────────────────────────────────────────────
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from transformers import pipeline
# import random
# import os

# app = FastAPI(title="StockSense AI Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 1. CALCULATE THE EXACT PATH TO YOUR MODEL
# # This goes UP from backend/, then DOWN into models/models/stocksense-finbert
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODEL_PATH = os.path.join(BASE_DIR, "models", "models", "stocksense-finbert")

# print(f"🧠 Loading custom FinBERT model from: {MODEL_PATH}...")
# try:
#     sentiment_analyzer = pipeline(
#         "text-classification", 
#         model=MODEL_PATH, 
#         tokenizer=MODEL_PATH
#     )
#     print("✅ Model loaded successfully!")
# except Exception as e:
#     print(f"❌ Error loading model: {e}")

# @app.get("/api/market/overview")
# def get_market_overview():
#     return {
#         "indices": {
#             "NIFTY50": {"price": 22450.50, "change_pct": 0.42, "direction": "up"},
#             "SENSEX": {"price": 73850.12, "change_pct": 0.38, "direction": "up"},
#         },
#         "mood_score": 62,
#         "mood_label": "Greed",
#     }

# @app.get("/api/stock/{symbol}")
# def analyze_stock_endpoint(symbol: str):
#     symbol = symbol.upper()
    
#     # Fake headlines to test if the model actually reads them correctly
#     headlines = [
#         f"{symbol} announces massive record profits for Q3", 
#         f"SEBI launches fraud investigation into {symbol} executives",
#         f"{symbol} schedules standard board meeting for next Tuesday"
#     ]
    
#     analyzed_news = []
#     bull_count, bear_count, neut_count = 0, 0, 0
    
#     # 2. RUN HEADLINES THROUGH YOUR ML MODEL
#     for text in headlines:
#         result = sentiment_analyzer(text)[0]
#         ai_label = result['label'].lower() 
#         ai_confidence = result['score'] * 100
        
#         if ai_label == "bullish":
#             direction = "UP"
#             sentiment = "BULLISH"
#             bull_count += 1
#         elif ai_label == "bearish":
#             direction = "DOWN"
#             sentiment = "BEARISH"
#             bear_count += 1
#         else:
#             direction = "SIDEWAYS"
#             sentiment = "NEUTRAL"
#             neut_count += 1
            
#         analyzed_news.append({
#             "title": text,
#             "source": "Test Feed",
#             "published": "Just now",
#             "sentiment": sentiment,
#             "direction": direction,
#             "impact": "HIGH" if ai_confidence > 80 else "MEDIUM",
#             "confidence": int(ai_confidence),
#             "color": ai_label, 
#             "reasoning": f"Your custom FinBERT model predicted {ai_label.upper()} with {int(ai_confidence)}% certainty.",
#         })
        
#     total_sentiment = bull_count - bear_count
#     verdict_label = "BULLISH" if total_sentiment > 0 else "BEARISH" if total_sentiment < 0 else "NEUTRAL"

#     # 3. RETURN DATA TO REACT UI
#     return {
#         "symbol": symbol,
#         "ticker": f"{symbol}.NS",
#         "name": f"{symbol} Limited",
#         "sector": "Indian Equities",
#         "current_price": random.randint(500, 3000),
#         "price_change_pct": random.uniform(-2, 2),
#         "news": analyzed_news,
#         "verdict": {
#             "label": verdict_label,
#             "emoji": "📈" if verdict_label == "BULLISH" else "📉" if verdict_label == "BEARISH" else "🟡",
#             "risk_level": "MEDIUM",
#             "short_term_outlook": "Based on custom ML inference",
#             "summary": f"Your FinBERT model analyzed {len(headlines)} headlines.",
#             "news_breakdown": {"bullish": bull_count, "bearish": bear_count, "neutral": neut_count},
#             "confidence": 85,
#         },
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
"""
StockSense AI — Analyzer Engine
This is the AI brain. Uses rule-based NLP + FinBERT-style keyword analysis.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional

# ── Keyword Dictionaries ──────────────────────────────────────────────────────

STRONG_BULLISH = [
    "record profit", "beats estimate", "strong quarterly", "revenue surge",
    "raises guidance", "dividend declared", "buyback", "major deal won",
    "acquisition approved", "partnership signed", "regulatory approval",
    "fda approved", "sebi approved", "ipo oversubscribed", "order wins",
    "debt free", "promoter buying", "insider buying", "upgrade", "outperform",
    "all time high", "52 week high", "strong demand", "expansion plan",
    "new contract", "billion dollar", "exports rise", "market share gain",
    "bullish", "rally", "surge", "soar", "jump", "skyrocket",
    "etf inclusion", "index inclusion", "msci inclusion",
]

MILD_BULLISH = [
    "meets estimate", "in line with", "steady growth", "positive outlook",
    "optimistic", "recovery", "improvement", "good results", "healthy",
    "resilient", "consistent", "growing", "rising", "increase",
    "profit", "growth", "jump", "soar", "gain", "up", "higher", "positive",
    "beats", "surges", "expands", "dividend"
]

MILD_BEARISH = [
    "misses estimate", "below expectation", "concern", "cautious",
    "headwinds", "slowdown", "pressure", "challenging", "weak",
    "below estimate", "margin squeeze", "cost rise", "inflation impact",
    "competition", "market share loss", "decline", "drop", "fall",
    "loss", "slump", "down", "lower", "negative", "cuts", "misses",
    "warning", "debt", "crash", "investigation"
]

STRONG_BEARISH = [
    "sebi notice", "sebi penalty", "sebi ban", "rbi action", "ed raid",
    "cbi investigation", "fraud", "scam", "money laundering", "bribery",
    "corruption", "arrest", "insider trading", "accounting irregularity",
    "misappropriation", "default", "npa", "bankruptcy", "insolvency",
    "debt crisis", "credit downgrade", "rating downgrade", "massive loss",
    "profit warning", "revenue miss", "lowers guidance", "ceo resigned",
    "cfo resigned", "promoter selling", "exit", "plant shutdown",
    "hack", "data breach", "cyberattack", "ransomware",
    "crash", "collapse", "plunge", "tank", "fall sharply",
    "52 week low", "all time low",
]

# MILD_BEARISH = [
#     "misses estimate", "below expectation", "concern", "cautious",
#     "headwinds", "slowdown", "pressure", "challenging", "weak",
#     "below estimate", "margin squeeze", "cost rise", "inflation impact",
#     "competition", "market share loss", "decline", "drop", "fall",
# ]

NEUTRAL_SIGNALS = [
    "holds steady", "in line", "as expected", "board meeting",
    "agm scheduled", "result date", "quarterly review", "analyst meet",
    "conference", "presentation", "policy unchanged",
]

# Event type classification
EVENT_TYPES = {
    "Regulatory Action": ["sebi", "rbi", "ed", "cbi", "notice", "penalty", "ban", "raid", "investigation"],
    "Earnings Report": ["quarterly", "result", "profit", "revenue", "earnings", "q1", "q2", "q3", "q4", "fy"],
    "Corporate Action": ["dividend", "buyback", "split", "bonus", "rights issue", "merger", "acquisition"],
    "Management Change": ["ceo", "cfo", "cto", "md", "chairman", "resigned", "appointed", "new head"],
    "Market Event": ["ipo", "listing", "delisting", "index", "inclusion", "exclusion"],
    "Macro/Sector": ["rbi policy", "budget", "gdp", "inflation", "rate", "interest", "oil", "rupee"],
    "Business Update": ["deal", "contract", "order", "partnership", "expansion", "plant", "launch"],
    "Risk Event": ["fraud", "hack", "breach", "default", "insolvency", "lawsuit", "litigation"],
}

# Historical patterns for similar events
HISTORICAL_PATTERNS = {
    "Regulatory Action": {
        "avg_impact": -4.2,
        "recovery_days": 7,
        "example": "SEBI notices have historically caused 3–8% corrections in large caps within 2–3 trading days.",
    },
    "Earnings Report": {
        "avg_impact": 2.1,
        "recovery_days": 2,
        "example": "Strong earnings beats typically drive 2–5% gains in the session following the announcement.",
    },
    "Corporate Action": {
        "avg_impact": 1.8,
        "recovery_days": 1,
        "example": "Dividend declarations and buybacks signal financial strength, typically adding 1–3%.",
    },
    "Management Change": {
        "avg_impact": -1.5,
        "recovery_days": 5,
        "example": "Unexpected CEO exits create short-term uncertainty, typically 1–4% downside before stabilization.",
    },
    "Risk Event": {
        "avg_impact": -6.8,
        "recovery_days": 14,
        "example": "Fraud allegations or data breaches cause sharp corrections, often 5–15% in the near term.",
    },
    "Business Update": {
        "avg_impact": 1.2,
        "recovery_days": 2,
        "example": "New contract wins typically boost sentiment by 1–3%, especially in IT and infra sectors.",
    },
    "Macro/Sector": {
        "avg_impact": 0.5,
        "recovery_days": 3,
        "example": "Macro events affect the broad market; sector-specific impact depends on direct exposure.",
    },
    "Market Event": {
        "avg_impact": 3.5,
        "recovery_days": 1,
        "example": "Index inclusions drive strong institutional buying, often 3–8% over 5 trading days.",
    },
}

class StockAnalyzer:
    """
    Rule-based financial news analyzer.
    """

    def analyze(self, news_item: Dict) -> Dict:
        title = news_item.get("title", "").lower()
        summary = news_item.get("summary", "").lower()
        full_text = f"{title} {summary}"

        # Score calculation
        bullish_score = sum(2 for kw in STRONG_BULLISH if kw in full_text)
        bullish_score += sum(1 for kw in MILD_BULLISH if kw in full_text)
        bearish_score = sum(2 for kw in STRONG_BEARISH if kw in full_text)
        bearish_score += sum(1 for kw in MILD_BEARISH if kw in full_text)

        net_score = bullish_score - bearish_score

        # Sentiment classification
        if net_score >= 4:
            sentiment = "STRONGLY BULLISH"
            sentiment_score = min(0.95, 0.70 + net_score * 0.03)
            direction = "UP"
            color = "bullish"
        elif net_score >= 1:
            sentiment = "MILDLY BULLISH"
            sentiment_score = 0.55 + net_score * 0.05
            direction = "UP"
            color = "bullish"
        elif net_score <= -4:
            sentiment = "STRONGLY BEARISH"
            sentiment_score = min(0.95, 0.70 + abs(net_score) * 0.03)
            direction = "DOWN"
            color = "bearish"
        elif net_score <= -1:
            sentiment = "MILDLY BEARISH"
            sentiment_score = 0.55 + abs(net_score) * 0.05
            direction = "DOWN"
            color = "bearish"
        else:
            sentiment = "NEUTRAL"
            sentiment_score = 0.50
            direction = "SIDEWAYS"
            color = "neutral"

        # Impact level
        if abs(net_score) >= 4:
            impact = "HIGH"
        elif abs(net_score) >= 2:
            impact = "MEDIUM"
        else:
            impact = "LOW"

        # Event type detection
        event_type = self._detect_event_type(full_text)

        # Risk flags
        risk_flags = self._extract_risk_flags(full_text)

        # Time horizon
        time_horizon = self._estimate_time_horizon(event_type, impact)

        # Confidence
        confidence = self._calculate_confidence(net_score, impact, risk_flags)

        # Reasoning chain
        reasoning = self._generate_reasoning(
            news_item.get("title", ""), sentiment, event_type,
            impact, risk_flags, net_score, confidence
        )

        # Historical context
        historical = HISTORICAL_PATTERNS.get(event_type, {})

        return {
            **news_item,
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "direction": direction,
            "color": color,
            "impact": impact,
            "event_type": event_type,
            "risk_flags": risk_flags,
            "time_horizon": time_horizon,
            "confidence": confidence,
            "reasoning": reasoning,
            "historical_pattern": historical.get("example", ""),
            "avg_historical_impact": historical.get("avg_impact", 0),
            "analyzed_at": datetime.now().isoformat(),
        }

    def overall_verdict(self, analyzed_news: List[Dict], price_change_pct: float) -> Dict:
        if not analyzed_news:
            return self._default_verdict(price_change_pct)

        weight_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        total_weight = 0
        weighted_score = 0
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        high_impact_events = []

        for item in analyzed_news:
            w = weight_map.get(item.get("impact", "LOW"), 1)
            direction = item.get("direction", "SIDEWAYS")
            score = item.get("sentiment_score", 0.5)

            if direction == "UP":
                weighted_score += score * w
                bullish_count += 1
            elif direction == "DOWN":
                weighted_score -= score * w
                bearish_count += 1
            else:
                neutral_count += 1

            total_weight += w

            if item.get("impact") == "HIGH":
                high_impact_events.append({
                    "title": item.get("title", ""),
                    "direction": direction,
                    "event_type": item.get("event_type", ""),
                })

        net = (weighted_score / total_weight) if total_weight > 0 else 0

        if price_change_pct > 2:
            net += 0.1
        elif price_change_pct < -2:
            net -= 0.1

        if net > 0.3:
            verdict_label, verdict_emoji, short_term, risk_level = "BULLISH", "🟢", "Upside likely in next 1–3 trading sessions", ("LOW" if net > 0.5 else "MEDIUM")
        elif net > 0.05:
            verdict_label, verdict_emoji, short_term, risk_level = "CAUTIOUSLY BULLISH", "🟡", "Mild upside possible; watch for reversals", "MEDIUM"
        elif net < -0.3:
            verdict_label, verdict_emoji, short_term, risk_level = "BEARISH", "🔴", "Downside pressure expected in near term", "HIGH"
        elif net < -0.05:
            verdict_label, verdict_emoji, short_term, risk_level = "CAUTIOUSLY BEARISH", "🟡", "Mild downside risk; monitor key levels", "MEDIUM"
        else:
            verdict_label, verdict_emoji, short_term, risk_level = "NEUTRAL", "⚪", "No strong directional signal from recent news", "LOW"

        summary = self._build_verdict_summary(
            analyzed_news, bullish_count, bearish_count,
            neutral_count, high_impact_events, verdict_label, price_change_pct
        )

        return {
            "label": verdict_label,
            "emoji": verdict_emoji,
            "risk_level": risk_level,
            "short_term_outlook": short_term,
            "summary": summary,
            "news_breakdown": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": neutral_count,
            },
            "high_impact_events": high_impact_events,
            "confidence": min(95, int(abs(net) * 100 + 40)),
            "net_sentiment_score": round(net, 3),
        }

    def _detect_event_type(self, text: str) -> str:
        scores = {}
        for event, keywords in EVENT_TYPES.items():
            scores[event] = sum(1 for kw in keywords if kw in text)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "Business Update"

    def _extract_risk_flags(self, text: str) -> List[str]:
        flags = []
        flag_map = {
            "Regulatory Risk": ["sebi", "rbi", "notice", "penalty", "investigation", "ed", "cbi"],
            "Fraud Risk": ["fraud", "scam", "money laundering", "bribery", "misappropriation"],
            "Liquidity Risk": ["default", "npa", "debt", "insolvency", "bankruptcy"],
            "Operational Risk": ["shutdown", "strike", "fire", "accident", "disruption"],
            "Cyber Risk": ["hack", "breach", "ransomware", "cyberattack", "data leak"],
            "Management Risk": ["ceo resign", "cfo resign", "promoter selling", "exit"],
        }
        for flag, keywords in flag_map.items():
            if any(kw in text for kw in keywords):
                flags.append(flag)
        return flags

    def _estimate_time_horizon(self, event_type: str, impact: str) -> str:
        horizons = {
            "Regulatory Action": "3–7 trading days",
            "Earnings Report": "1–2 trading days",
            "Corporate Action": "1–3 trading days",
            "Risk Event": "1–2 weeks",
            "Management Change": "5–10 trading days",
            "Macro/Sector": "1–5 trading days",
            "Business Update": "1–3 trading days",
            "Market Event": "1–5 trading days",
        }
        return horizons.get(event_type, "2–5 trading days")

    def _calculate_confidence(self, net_score: int, impact: str, risk_flags: List) -> int:
        base = 45
        base += min(30, abs(net_score) * 5)
        if impact == "HIGH":
            base += 15
        elif impact == "MEDIUM":
            base += 8
        if risk_flags:
            base += 5
        return min(92, base)

    def _generate_reasoning(self, title: str, sentiment: str, event_type: str,
                             impact: str, risk_flags: List, net_score: int,
                             confidence: int) -> str:
        parts = []
        parts.append(f"This is classified as a **{event_type}** event with **{impact} impact**.")
        if "BULLISH" in sentiment:
            parts.append("Positive signals detected: strong earnings language, business wins, or favorable corporate actions indicate near-term upside.")
        elif "BEARISH" in sentiment:
            parts.append("Negative signals detected: regulatory pressure, management risk, or earnings concerns suggest downside pressure.")
        else:
            parts.append("No strong directional keywords detected; market may remain range-bound.")
        if risk_flags:
            parts.append(f"⚠️ Risk flags identified: {', '.join(risk_flags)}.")
        if confidence > 75:
            parts.append(f"Confidence is high ({confidence}%) based on clear signal strength.")
        elif confidence > 55:
            parts.append(f"Moderate confidence ({confidence}%). Monitor for confirming price action.")
        else:
            parts.append(f"Low confidence ({confidence}%). News signal is ambiguous.")
        return " ".join(parts)

    def _build_verdict_summary(self, news: List, bull: int, bear: int,
                                neutral: int, high_impact: List,
                                verdict: str, price_chg: float) -> str:
        total = len(news)
        parts = []
        parts.append(f"Analyzed {total} recent news item{'s' if total != 1 else ''}. {bull} bullish, {bear} bearish, {neutral} neutral.")
        if high_impact:
            titles = [e["title"][:60] for e in high_impact[:2]]
            parts.append(f"High-impact events: {'; '.join(titles)}.")
        if price_chg > 2:
            parts.append(f"Price is up {abs(price_chg):.1f}% today, confirming positive sentiment.")
        elif price_chg < -2:
            parts.append(f"Price is down {abs(price_chg):.1f}% today, consistent with negative news flow.")
        if verdict in ("BEARISH", "CAUTIOUSLY BEARISH"):
            parts.append("Exercise caution. Consider waiting for news resolution before adding positions.")
        elif verdict in ("BULLISH", "CAUTIOUSLY BULLISH"):
            parts.append("News flow appears favorable. Watch volume confirmation for stronger conviction.")
        parts.append("⚠️ This is an AI-generated analysis for educational purposes only. Not financial advice. Consult a SEBI-registered advisor before investing.")
        return " ".join(parts)

    def _default_verdict(self, price_change_pct: float) -> Dict:
        if price_change_pct > 1:
            label, risk = "CAUTIOUSLY BULLISH", "LOW"
        elif price_change_pct < -1:
            label, risk = "CAUTIOUSLY BEARISH", "MEDIUM"
        else:
            label, risk = "NEUTRAL", "LOW"
        return {
            "label": label,
            "emoji": "🟡",
            "risk_level": risk,
            "short_term_outlook": "Insufficient news data for strong signal",
            "summary": "No recent news available. Analysis based on price action only. ⚠️ Not financial advice.",
            "news_breakdown": {"bullish": 0, "bearish": 0, "neutral": 0},
            "high_impact_events": [],
            "confidence": 30,
            "net_sentiment_score": 0,
        }