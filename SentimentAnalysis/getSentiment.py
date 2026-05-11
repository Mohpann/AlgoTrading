from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re, pandas as pd

# vader doesn't know finance slang, patching manually
_EXTRA = {
    "bullish": 3.0, "bearish": -3.0,
    "moon": 2.5, "mooning": 2.5,
    "dump": -2.5, "rugpull": -3.0,
    "pump": 1.5, "rekt": -3.0,
    "hodl": 1.0, "rally": 2.0,
    "crash": -3.0, "surge": 2.5, "plunge": -2.5,
    "call": 2.0, "calls": 2.0,
    "put": -2.0, "puts": -2.0,
    "short": -2.0, "long": 2.0,
    "ath": 2.0, "green": 1.5, "red": -1.5,
    "bear flag": -2.0, "bull flag": 2.0,
}

_ASPECT_KEYS = {
    "price":      ["price", "valuation", "worth", "cheap", "expensive"],
    "market":     ["market", "nasdaq", "sp500", "dow"],
    "revenue":    ["revenue", "earnings", "profit", "growth"],
    "management": ["ceo", "cfo", "management", "board"],
    "risk":       ["risk", "volatility", "hedge", "exposure"],
}

_TICKER = r"\$[A-Z]{1,6}"

_va = SentimentIntensityAnalyzer()
_va.lexicon.update(_EXTRA)


def _clean(text):
    t = re.sub(r"http\S+", "", text)
    t = re.sub(_TICKER, "TICKER", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    return t.strip()


def _noisy(text):
    low = text.lower()
    return text.count("!") > 6 or "discord" in low or "100x" in low


def _aspects(text):
    words = re.findall(r"\b\w+\b", text.lower())
    out = {}
    for aspect, kws in _ASPECT_KEYS.items():
        for i, w in enumerate(words):
            if w not in kws:
                continue
            chunk = " ".join(words[max(0, i-5):i+6])
            sc = _va.polarity_scores(chunk)["compound"]
            out[aspect] = {
                "label": "Positive" if sc >= 0.05 else ("Negative" if sc <= -0.05 else "Neutral"),
                "score": round(sc, 4),
                "matched_keyword": w,
            }
            break
    return out


def getSentiment(text):
    cleaned = _clean(text)
    sc = _va.polarity_scores(cleaned)
    c = sc["compound"]

    if cleaned.isupper():
        c *= 1.1

    if   c >= 0.05:  label = "Positive"
    elif c <= -0.05: label = "Negative"
    else:            label = "Neutral"

    if   c >  0.6:  strength = "strong_bullish"
    elif c >  0.2:  strength = "bullish"
    elif c < -0.6:  strength = "strong_bearish"
    elif c < -0.2:  strength = "bearish"
    else:            strength = "neutral"

    return {
        "label":      label,
        "score":      round(c, 4),
        "confidence": round(abs(c), 4),
        "strength":   strength,
        "tickers":    [t.replace("$", "") for t in re.findall(_TICKER, text)],
        "is_noisy":   _noisy(text),
        "aspects":    _aspects(cleaned),
    }


def test_on_massive_csv(csv_path, sample_size=20):
    print(f"Loading: {csv_path}")

    df = pd.read_csv(csv_path, usecols=["Sentence", "Sentiment"], on_bad_lines="skip").dropna()
    df = df[df["Sentence"].str.len() > 15]

    labeled = df[df["Sentiment"].str.lower().isin(["bullish", "bearish", "positive", "negative"])]
    print(f"Samples: {len(labeled)}")

    sample = labeled.sample(min(sample_size, len(labeled)))
    hits = 0

    for _, row in sample.iterrows():
        text   = str(row["Sentence"])
        actual = str(row["Sentiment"]).lower()

        gt = "Positive" if actual in ("bullish", "positive") else "Negative"
        res = getSentiment(text)

        if res["label"] == gt:
            hits += 1

        print(text[:90])
        print(f"  gt={gt}  pred={res['label']}  score={res['score']}  strength={res['strength']}")
        if res["tickers"]: print("  tickers:", res["tickers"])
        if res["aspects"]: print("  aspects:", res["aspects"])
        print("-" * 40)

    print(f"\naccuracy: {hits/sample_size:.2%}")


if __name__ == "__main__":
    demos = [
        "The market crashed today, terrible losses across all sectors.",
        "OMG you're a paralegal? Can you still walk?",
        "I love dogs! They're great",
        "Bitcoin is mooning again, hodl for dear life!",
        "Company faces rugpull allegations, stock dumps 40%.",
        "$SPY grabbed some 420 calls for Friday.",
        "Short side has a better risk/reward ratio going into next week.",
    ]

    for text in demos:
        r = getSentiment(text)
        print(f"\n{text}")
        print(f"  {r['label']} / {r['strength']}  score={r['score']}")
        if r["tickers"]: print("  tickers:", r["tickers"])
        if r["aspects"]:
            for k, v in r["aspects"].items():
                print(f"  {k}: {v['label']} ({v['score']})")

    # test_on_massive_csv("stocktwits_dataset.csv", sample_size=100)