import numpy as np
from services.data_utils import numeric_score, categorical_score, correlation_score


def calculate_confidence(chart_type, df, col1, col2=None):

    confidence = 0.5

    # SCATTER
    if chart_type == "scatter" and col2:
        corr = correlation_score(df, col1, col2)
        confidence = min(1.0, 0.5 + corr)

    # BAR
    elif chart_type == "bar":
        unique_ratio = df[col1].nunique() / len(df[col1])
        confidence = min(1.0, 0.5 + (1 - unique_ratio))

    # PIE
    elif chart_type == "pie":
        unique_count = df[col1].nunique()
        balance = min(1.0, 10 / (unique_count + 1))
        confidence = 0.6 + 0.4 * balance

    # DOUGHNUT
    elif chart_type == "doughnut":
        unique_count = df[col1].nunique()
        balance = min(1.0, 8 / (unique_count + 1))
        confidence = 0.6 + 0.4 * balance

    # LINE
    elif chart_type == "line" and col2:
        corr = correlation_score(df, col1, col2)
        confidence = min(1.0, 0.5 + corr * 0.8)

    # AREA
    elif chart_type == "area" and col2:
        variance = df[col2].var()
        normalized_var = min(1.0, variance / (variance + 1))
        confidence = 0.5 + 0.5 * normalized_var

    # RADAR
    elif chart_type == "radar" and isinstance(col2, list):
        variances = [df[c].var() for c in col2 if c in df]
        if variances:
            avg_var = sum(variances) / len(variances)
            confidence = min(1.0, 0.5 + avg_var / (avg_var + 1))

    # POLAR
    elif chart_type == "polar area":
        unique_count = df[col1].nunique()
        confidence = min(1.0, 0.5 + (1 / (unique_count + 1)))

    return round(confidence, 2)


def generate_reason(chart_type, df, col1, col2=None):

    if chart_type == "scatter" and col2:
        corr = correlation_score(df, col1, col2)
        return f"• Izkliedes diagramma korelācijas dēļ (r = {round(corr,2)})"

    elif chart_type == "bar":
        return f"• Stabiņu diagramma kategoriju salīdzināšanai ({df[col1].nunique()} kategorijas)"

    elif chart_type == "pie":
        return f"• Sektoru diagramma proporciju attēlošanai ({df[col1].nunique()} kategorijas)"

    elif chart_type == "doughnut":
        return f"• Gredzenveida diagramma proporciju analīzei"

    elif chart_type == "line":
        return "• Līniju grafiks datu tendences analīzei"

    elif chart_type == "area":
        return "• Apgabala grafiks kumulatīvās dinamikas attēlošanai"

    elif chart_type == "radar":
        return "• Radara diagramma vairāku rādītāju salīdzināšanai"

    elif chart_type == "polar area":
        return "• Polārā diagramma kategoriju intensitātei"

    return "• Vizualizācija izvēlēta pēc statistiskās analīzes"


def fallback_charts(df):
    categorical = df.select_dtypes(exclude=np.number).columns.tolist()
    numeric = df.select_dtypes(include=np.number).columns.tolist()

    charts = []

    numeric_sorted = sorted(numeric, key=lambda c: numeric_score(df[c]), reverse=True)
    categorical_sorted = sorted(categorical, key=lambda c: categorical_score(df[c]), reverse=True)

    if categorical_sorted and numeric_sorted:
        x = categorical_sorted[0]
        y = numeric_sorted[0]

        confidence = calculate_confidence("bar", df, x, y)
        reason = generate_reason("bar", df, x, y)

        charts.append({
            "chart": "Bar Chart",
            "x": x,
            "y": y,
            "confidence": confidence,
            "settings": {
                "aggregation": "average",
                "sort": "desc",
                "topN": 10,
                "legend": False
            },
            "reason": reason
        })

    if len(numeric_sorted) >= 2:
        col1 = numeric_sorted[0]
        col2 = numeric_sorted[1]

        confidence = calculate_confidence("scatter", df, col1, col2)
        reason = generate_reason("scatter", df, col1, col2)

        charts.append({
            "chart": "Scatter Chart",
            "x": col1,
            "y": col2,
            "confidence": confidence,
            "settings": {
                "aggregation": "none",
                "legend": False
            },
            "reason": reason
        })

    if categorical_sorted:
        x = categorical_sorted[0]

        confidence = calculate_confidence("pie", df, x)
        reason = generate_reason("pie", df, x)

        charts.append({
            "chart": "Pie Chart",
            "x": x,
            "y": "__count__",
            "confidence": confidence,
            "settings": {
                "aggregation": "count",
                "legend": True,
                "topN": 8
            },
            "reason": reason
        })
    
        # RADAR
    if len(numeric_sorted) >= 3:
        radar_cols = numeric_sorted[:5]

        charts.append({
            "chart": "Radar Chart",
            "x": "categories",
            "y": radar_cols,
            "confidence": calculate_confidence("radar", df, None, radar_cols),
            "settings": {
                "aggregation": "average",
                "legend": True
            },
            "reason": generate_reason("radar", df, None, radar_cols)
        })

    # POLAR
    if categorical_sorted and numeric_sorted:
        charts.append({
            "chart": "Polar Area Chart",
            "x": categorical_sorted[0],
            "y": numeric_sorted[0],
            "confidence": calculate_confidence("polar area", df, categorical_sorted[0]),
            "settings": {
                "aggregation": "sum",
                "legend": True
            },
            "reason": generate_reason("polar area", df, categorical_sorted[0])
        })

    return charts[:3]
