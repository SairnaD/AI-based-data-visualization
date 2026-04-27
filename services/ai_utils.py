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


def safe_ai_call(prompt, timeout=90):
    try:
        print("\n🧠 [AI] Sending prompt to an AI...")

        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0.2},
                "stream": False
            },
            timeout=timeout
        )
        return r.json().get("message", {}).get("content")
    except Exception as e:
        print("❌ [AI ERROR]:", e)
        print("AI timeout / error:", e)
        return None


def ai_choose_top_charts(df):
    print("\n🚀 === AI CHART SELECTION START ===")

    categorical = df.select_dtypes(exclude=np.number).columns.tolist()
    numeric = df.select_dtypes(include=np.number).columns.tolist()

    if not categorical and not numeric:
        print("⚠️ No matching collumns → FALLBACK")
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
- Use numeric columns ONLY for y when aggregation is mean/average
- If column is categorical (Yes/No), use count instead
- DO NOT return strings
- DO NOT explain anything
- DO NOT use markdown
- DO NOT wrap in ``` 

Available special values:
- "__count__" → number of rows per category
- For Pie/Bar charts you may use:
  y: "__count__"
  when no numeric column is available

Example:
[
  {{"chart": "Bar Chart", "x": "category", "y": "value"}},
  {{"chart": "Line Chart", "x": "date", "y": "sales"}},
  {{"chart": "Pie Chart", "x": "category", "y": "value"}}
]

Respond STRICTLY as valid JSON.
NO explanations. NO markdown.
"""

    text = safe_ai_call(prompt, timeout=90)

    if not text:
        print("⚠️ AI doesn't respond → FALLBACK")
        return fallback_charts(df)

    try:
        if text.startswith("```"):
            text = text.strip("`").replace("json", "").strip()
        charts = json.loads(text)
        print("✅ AI JSON parsed successfully")
    except Exception:
        print("❌ Parsing error JSON → FALLBACK")
        print("RAW:", text)
        return fallback_charts(df)

    final = []
    used_types = set()
    used_pairs = set()

    for c in charts:
        if not isinstance(c, dict):
            print("⚠️ Skip: not dict", c)
            continue

        ct = c.get("chart")
        x = c.get("x")
        y = c.get("y")

        if ct not in CHART_TYPES:
            print(f"⚠️ Skip: Unknown type {ct}")
            continue

        if ct in used_types:
            continue

        if (x, str(y)) in used_pairs:
            continue

        used_types.add(ct)
        used_pairs.add((x, str(y)))

        chart_type_lower = ct.lower().replace(" chart", "").strip()
        if x == "__count__":
            confidence = 0.9
        else:
            confidence = float(calculate_confidence(chart_type_lower, df, x, y))
        reason = generate_reason(chart_type_lower, df, x, y)

        agg = c.get("aggregation")

        if not agg:
            if ct == "Bar Chart":
                agg = "average"
            elif ct == "Pie Chart":
                agg = "count"
            elif ct == "Scatter Chart":
                agg = "none"
            elif ct == "Line Chart":
                agg = "average"
            else:
                agg = "none"

        final.append({
            "chart": ct,
            "x": x,
            "y": y,
            "confidence": confidence,
            "settings": {
                "aggregation": agg,
                "legend": False if ct in ["Bar Chart", "Scatter Chart"] else True,
                "smooth": ct in ["Line Chart", "Area Chart"],
                "sort": "desc" if ct in ["Bar Chart"] else None,
                "topN": 10 if ct in ["Bar Chart", "Pie Chart"] else None
            },
            "reason": reason
        })

        if len(final) == 3:
            break

    if len(final) == 0:
        print("⚠️ AI failed → fallback")
        return fallback_charts(df)


    print("Using AI (not fallback)")

    return final if final else fallback_charts(df)
