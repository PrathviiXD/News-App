# server.py
import os
import re
from typing import List, Dict, Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 🔑 PUT YOUR NEWSAPI KEY HERE OR IN ENV
NEWSAPI_KEY = os.getenv("6380c266596d4658ad908220fe4f4026") or "6380c266596d4658ad908220fe4f4026"

if not NEWSAPI_KEY or NEWSAPI_KEY == "6380c266596d4658ad908220fe4f4026":
    raise RuntimeError("Set 6380c266596d4658ad908220fe4f4026 env var or replace 6380c266596d4658ad908220fe4f4026 with your NewsAPI key.")

app = FastAPI(title="BiasRadar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentIntensityAnalyzer()

SUBJECTIVE_WORDS = {
    "think", "believe", "feel", "should", "must", "maybe", "probably", "personally",
    "seems", "appears", "opinion", "suggest", "claim", "argue", "i", "we", "you"
}

EMOTION_LEXICON = {
    "fear": {
        "fear", "afraid", "scared", "terror", "panic", "threat", "worry", "worried",
        "concern", "concerned", "anxiety", "anxious", "risk"
    },
    "anger": {
        "angry", "rage", "furious", "outrage", "hate", "hateful", "attack", "blame",
        "corrupt", "corruption", "fraud", "scam"
    },
    "joy": {
        "happy", "joy", "joyful", "celebrate", "win", "victory", "success", "growth",
        "optimistic", "hope", "hopeful", "progress"
    }
}

SOURCE_BIAS: Dict[str, str] = {
    "fox-news": "right",
    "breitbart-news": "right",
    "the-hindu": "center-left",
    "the-times-of-india": "center",
    "bbc-news": "center",
    "cnn": "center-left",
    "al-jazeera-english": "center-left",
    "reuters": "center",
    "associated-press": "center",
    "default": "unknown",
}


class AnalyzeRequest(BaseModel):
    topic: str
    language: str = "en"
    page_size: int = 40  # 5–100


class SourceResult(BaseModel):
    id: str
    name: str
    political_lean: str
    article_count: int
    avg_sentiment: float
    avg_subjectivity: float
    dominant_emotion: str
    emotion_intensity: float


class AnalyzeResponse(BaseModel):
    topic: str
    language: str
    sources: List[SourceResult]


def subjectivity_score(text: str) -> float:
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in SUBJECTIVE_WORDS)
    return hits / len(tokens)


def emotion_label(text: str) -> str:
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return "neutral"

    counts = {k: 0 for k in EMOTION_LEXICON.keys()}
    for t in tokens:
        for emo, words in EMOTION_LEXICON.items():
            if t in words:
                counts[emo] += 1

    total = sum(counts.values())
    if total == 0:
        return "neutral"
    return max(counts, key=counts.get)


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_news(req: AnalyzeRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    page_size = min(max(req.page_size, 5), 100)

    params = {
        "q": topic,
        "language": req.language,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": NEWSAPI_KEY,
    }

    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=15)
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Failed to reach NewsAPI")

    if resp.status_code != 200:
        detail = f"NewsAPI error: HTTP {resp.status_code}"
        try:
            j = resp.json()
            if "message" in j:
                detail = f"NewsAPI error: {j['message']}"
        except Exception:
            pass
        raise HTTPException(status_code=resp.status_code, detail=detail)

    data = resp.json()
    if data.get("status") != "ok":
        raise HTTPException(status_code=502, detail=f"NewsAPI error: {data.get('message', 'unknown error')}")

    articles = data.get("articles", [])
    if not articles:
        return AnalyzeResponse(topic=topic, language=req.language, sources=[])

    per_source: Dict[str, Dict[str, Any]] = {}

    for art in articles:
        src = art.get("source") or {}
        source_id = src.get("id") or src.get("name") or "unknown"
        source_name = src.get("name") or source_id

        title = art.get("title") or ""
        desc = art.get("description") or ""
        content = art.get("content") or ""
        text = f"{title}. {desc}. {content}".strip()

        if not text:
            continue

        sent_scores = analyzer.polarity_scores(text)
        sentiment = sent_scores.get("compound", 0.0)  # -1..1
        subj = subjectivity_score(text)
        emo = emotion_label(text)

        if source_id not in per_source:
            per_source[source_id] = {
                "name": source_name,
                "sentiments": [],
                "subjectivities": [],
                "emotion_counts": {"fear": 0, "anger": 0, "joy": 0, "neutral": 0},
            }

        ps = per_source[source_id]
        ps["sentiments"].append(sentiment)
        ps["subjectivities"].append(subj)
        ps["emotion_counts"][emo] = ps["emotion_counts"].get(emo, 0) + 1

    results: List[SourceResult] = []

    for source_id, stats in per_source.items():
        sentiments = stats["sentiments"]
        subjectivities = stats["subjectivities"]
        emo_counts = stats["emotion_counts"]

        if not sentiments:
            continue

        article_count = len(sentiments)
        avg_sent = sum(sentiments) / article_count
        avg_subj = sum(subjectivities) / article_count if subjectivities else 0.0

        dominant_emo = max(emo_counts, key=emo_counts.get)
        non_neutral = article_count - emo_counts.get("neutral", 0)
        emotion_intensity = non_neutral / article_count if article_count else 0.0

        political_lean = SOURCE_BIAS.get(source_id, SOURCE_BIAS["default"])

        results.append(
            SourceResult(
                id=source_id,
                name=stats["name"],
                political_lean=political_lean,
                article_count=article_count,
                avg_sentiment=avg_sent,
                avg_subjectivity=avg_subj,
                dominant_emotion=dominant_emo,
                emotion_intensity=emotion_intensity,
            )
        )

    results.sort(key=lambda r: r.article_count, reverse=True)

    return AnalyzeResponse(topic=topic, language=req.language, sources=results)
