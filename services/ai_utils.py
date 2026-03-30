import requests
import json
import numpy as np

from services.chart_logic import fallback_charts, calculate_confidence, generate_reason

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b-instruct-q4_K_M"

CHART_TYPES = [
    "Bar Chart",
    "Line Chart",
    "Area Chart",
    "Pie Chart",
    "Doughnut Chart",
    "Scatter Chart",
    "Radar Chart",
    "Polar Area Chart"
]


def safe_ai_call(prompt, timeout=12):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0.2}
            },
            timeout=timeout
        )
        return r.json().get("message", {}).get("content")
    except Exception as e:
        print("AI timeout / error:", e)
        return None


def ai_choose_top_charts(df):
    categorical = df.select_dtypes(exclude=np.number).columns.tolist()
    numeric = df.select_dtypes(include=np.number).columns.tolist()

    if not categorical and not numeric:
        return fallback_charts(df)

    sample_cols = (categorical + numeric)[:6]
    sample = df[sample_cols].head(10)

    prompt = f"""
You are a senior data visualization expert.

Supported chart types (Chart.js):
{CHART_TYPES}

Dataset sample:
{json.dumps(sample.to_dict(orient="records"), ensure_ascii=False)}

STRICT RULES:
- Propose EXACTLY 3 charts
- Each chart MUST have a DIFFERENT chart type
- Try to use DIFFERENT X and Y columns
- IGNORE non-informative columns
- Charts must be diverse and informative

Respond STRICTLY as valid JSON.
NO explanations. NO markdown.
"""

    text = safe_ai_call(prompt, timeout=12)

    if not text:
        return fallback_charts(df)

    try:
        if text.startswith("```"):
            text = text.strip("`").replace("json", "").strip()
        charts = json.loads(text)
    except Exception:
        return fallback_charts(df)

    final = []
    used_types = set()
    used_pairs = set()

    for c in charts:
        ct = c.get("chart")
        x = c.get("x")
        y = c.get("y")

        if ct not in CHART_TYPES:
            continue
        if ct in used_types:
            continue
        if (x, str(y)) in used_pairs:
            continue

        used_types.add(ct)
        used_pairs.add((x, str(y)))

        chart_type_lower = ct.lower().replace(" chart", "").strip()
        confidence = calculate_confidence(chart_type_lower, df, x, y)
        reason = generate_reason(chart_type_lower, df, x, y)

        final.append({
            "chart": ct,
            "x": x,
            "y": y,
            "confidence": confidence,
            "settings": {
                "aggregation": c.get("aggregation", "none"),
                "legend": False if ct in ["Bar Chart", "Scatter Chart"] else True,
                "smooth": ct in ["Line Chart", "Area Chart"],
                "sort": "desc" if ct in ["Bar Chart"] else None,
                "topN": 10 if ct in ["Bar Chart", "Pie Chart"] else None
            },
            "reason": reason
        })

        if len(final) == 3:
            break

    return final if final else fallback_charts(df)
