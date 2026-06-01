import requests
import json
import numpy as np

from services.chart_logic import fallback_charts, calculate_confidence, generate_reason

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M"
MODEL_INSIGHT = "qwen3:4b-q4_K_M"

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


def safe_ai_call(prompt, system_prompt=None, timeout=90, use_json_format=True, model=None):
    try:
        print("\n🧠 [AI] Sending prompt to AI...")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "options": {"temperature": 0.2},
            "stream": False
        }

        if use_json_format:
            payload["format"] = "json"

        print("Using ", model)
        r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        return r.json().get("message", {}).get("content")

    except Exception as e:
        print("❌ [AI ERROR]:", e)
        return None


def build_column_summary(df, categorical, numeric):
    summary = {}

    for col in categorical[:3]:
        vc = df[col].value_counts()
        summary[col] = {
            "type": "categorical",
            "unique": int(df[col].nunique()),
            "top_values": vc.head(4).index.tolist(),
            "null_pct": round(df[col].isna().mean() * 100, 1)
        }

    for col in numeric[:4]:
        summary[col] = {
            "type": "numeric",
            "min": round(float(df[col].min()), 2),
            "max": round(float(df[col].max()), 2),
            "mean": round(float(df[col].mean()), 2),
            "std": round(float(df[col].std()), 2),
            "null_pct": round(df[col].isna().mean() * 100, 1)
        }

    return summary


def ai_choose_top_charts(df):
    print("\n🚀 === AI CHART SELECTION START ===")

    categorical = df.select_dtypes(exclude=np.number).columns.tolist()
    numeric = df.select_dtypes(include=np.number).columns.tolist()

    if not categorical and not numeric:
        print("⚠️ No matching columns → FALLBACK")
        return fallback_charts(df)

    column_summary = build_column_summary(df, categorical, numeric)

    system_prompt = (
        "You are a senior data visualization expert. "
        "You always respond with valid JSON only. "
        "No explanations, no markdown, no extra text."
    )

    prompt = f"""
Given this dataset column summary, propose the 3 most informative Chart.js visualizations.

Supported chart types: {CHART_TYPES}

Dataset column summary:
{json.dumps(column_summary, ensure_ascii=False, indent=2)}

Rules:
- Propose EXACTLY 3 charts
- y MUST contain exactly ONE column name
- Never return multiple columns in y
- Never separate columns with commas
- Rank from MOST to LEAST informative
- Prefer charts that reveal trends, distributions, or correlations
- Avoid redundant charts — different types preferred if they add value
- Use numeric columns for y when aggregation makes sense
- Use "__count__" as y when no numeric column fits (e.g. Pie, Bar by category)
- Ignore columns with high null_pct or low unique count if uninformative

Respond as a JSON object with a "charts" key containing an array of exactly 3 chart configuration objects.

The following JSON is ONLY an example of the expected structure and format.
Do NOT copy it literally, and do NOT use the same chart types or column names unless they are actually appropriate for the provided data.

Example:
[
  {{"chart": "Bar Chart",  "x": "category_column", "y": "numeric_column"}},
  {{"chart": "Line Chart", "x": "date_column",     "y": "numeric_column"}},
  {{"chart": "Pie Chart",  "x": "category_column", "y": "__count__"}}
]
"""

    text = safe_ai_call(prompt, system_prompt=system_prompt, timeout=90, use_json_format=True, model=MODEL_NAME)

    if not text:
        print("⚠️ AI didn't respond → FALLBACK")
        return fallback_charts(df)

    try:
        parsed = json.loads(text)
        print("✅ AI JSON parsed successfully")

        if isinstance(parsed, dict):
            charts = next((v for v in parsed.values() if isinstance(v, list)), None)
            if charts is None:
                charts = [parsed]
        elif isinstance(parsed, list):
            charts = parsed
        else:
            raise ValueError(f"Unexpected JSON shape: {type(parsed)}")

    except Exception as e:
        print("❌ JSON parse error → FALLBACK:", e)
        print("RAW:", text)
        return fallback_charts(df)
    
    final = []
    used_types = set()
    used_pairs = set()

    for c in charts:
        if not isinstance(c, dict):
            print("⚠️ Skip: not a dict:", c)
            continue

        ct = c.get("chart")
        x = c.get("x")
        y = c.get("y")

        if not x:
            continue

        if y is None:
            y = "__count__"

        if ct not in CHART_TYPES:
            print(f"⚠️ Skip: unknown chart type '{ct}'")
            continue

        if ct in used_types:
            continue

        if (x, str(y)) in used_pairs:
            continue

        used_types.add(ct)
        used_pairs.add((x, str(y)))

        chart_type_lower = ct.lower().replace(" chart", "").strip()

        confidence = 0.9 if x == "__count__" else float(calculate_confidence(chart_type_lower, df, x, y))
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
                "legend": ct not in ["Bar Chart", "Scatter Chart"],
                "smooth": ct in ["Line Chart", "Area Chart"],
                "sort": "desc" if ct == "Bar Chart" else None,
                "topN": 10 if ct in ["Bar Chart", "Pie Chart"] else None
            },
            "reason": reason
        })

        if len(final) == 3:
            break

    if not final:
        print("⚠️ AI returned no valid charts → FALLBACK")
        return fallback_charts(df)

    print("✅ Using AI results (not fallback)")
    return final


def generate_chart_insight(chart_type, labels, values):
    try:
        if not labels or not values:
            return "Nav pietiekami daudz datu interpretācijai."

        sample_size = min(len(labels), 10)
        labels_sample = labels[:sample_size]
        values_sample = values[:sample_size]

        labels_text = ", ".join(map(str, labels_sample))
        values_text = ", ".join(
            str(round(v, 2)) if isinstance(v, (int, float)) else str(v)
            for v in values_sample
        )

        system_prompt = (
            "/no_think "
            "You are a professional data analyst. "
            "You write short, clear data interpretations in Latvian. "
            "No markdown, no bullet points, no introductory phrases."
        )

        prompt = f"""
Write a SHORT interpretation of this chart data in Latvian.
Maximum 2 sentences. Mention the most important trend or pattern.

Chart type: {chart_type}
Labels: {labels_text}
Values: {values_text}
"""

        result = safe_ai_call(
            prompt,
            system_prompt=system_prompt,
            timeout=180,
            use_json_format=False,
            model=MODEL_INSIGHT
        )

        if not result:
            return "AI interpretācija nav pieejama."

        result = result.strip().replace("\n", " ")

        if len(result) > 220:
            result = result[:220] + "..."

        return result

    except Exception as e:
        print("Insight generation error:", e)
        return "AI interpretācija nav pieejama."