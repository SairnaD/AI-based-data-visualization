from flask import Flask, render_template, request, jsonify
import pandas as pd
import openpyxl 
import xlrd
import io
import lxml
from services.data_utils import clean_df
from services.ai_utils import ai_choose_top_charts, generate_chart_insight
import numpy as np

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

df_global = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global df_global

    if "file" not in request.files:
        return jsonify({"error": "Nav augšupielādēts fails"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nav izvēlēts fails"}), 400

    allowed_extensions = [".csv", ".xlsx", ".xls"]
    filename = file.filename.lower()

    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return jsonify({
            "error": "❌ Nepareizs faila formāts. Atļauti tikai CSV vai Excel faili (.csv, .xlsx, .xls)"
        }), 400

    try:
        content = file.read()

        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))

        else:
            try:
                df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
            except:
                try:
                    df = pd.read_excel(io.BytesIO(content), engine="xlrd")
                except:
                    df = pd.read_html(content)[0]

    except Exception as e:
        print("File read error:", e)
        return jsonify({
            "error": f"❌ Neizdevās nolasīt failu: {str(e)}"
        }), 400
    
    df.ffill(inplace=True)
    df_cleaned = clean_df(df)

    if df_cleaned.shape[1] < 2:
        print("⚠️ Cleaned df too small, using original")
    else:
        df = df_cleaned
    df_global = df

    charts = ai_choose_top_charts(df)

    return jsonify(charts)


@app.route("/data")
def data():
    global df_global

    if df_global is None:
        return jsonify({"error": "❌ Data not loaded (server restarted)"}), 400

    df = df_global.copy()

    x = request.args["x"]
    y = request.args.get("y")
    agg = request.args.get("agg")

    if y == "__count__":

        dfg = df.groupby(x).size().reset_index(name="value")

        return jsonify({
            "labels": dfg[x].astype(str).tolist(),
            "values": dfg["value"].tolist()
        })

    if x == "categories":
        if y and "," in y:
            y = y.split(",")

        result = []
        for col in y:
            if col in df:
                result.append(float(df[col].mean()))

        return jsonify({
            "labels": y,
            "values": result
        })

    if agg == "count":
        dfg = df.groupby(x).size().reset_index(name="value")
        return jsonify({
            "labels": dfg[x].astype(str).tolist(),
            "values": dfg["value"].tolist()
        })

    if agg == "average":
        if not pd.api.types.is_numeric_dtype(df[y]):
            dfg = df.groupby(x)[y].count().reset_index(name="value")
        else:
            dfg = df.groupby(x)[y].mean().reset_index(name="value")

        return jsonify({
            "labels": dfg[x].astype(str).tolist(),
            "values": dfg["value"].tolist()
        })

    if agg == "none":
        df = df[[x, y]].dropna()

        MAX_POINTS = 1000

        if len(df) > MAX_POINTS:
            df = df.sample(n=MAX_POINTS, random_state=42)

        return jsonify({
            "points": [
                {"x": float(row[x]), "y": float(row[y])}
                for _, row in df.iterrows()
            ]
        })

    return jsonify({})


@app.route("/insight")
def insight():
    global df_global

    if df_global is None:
        return jsonify({"insight": "Nav datu"}), 400

    df = df_global.copy()

    x = request.args.get("x")
    y = request.args.get("y")
    agg = request.args.get("agg")

    try:
        if y == "__count__" or agg == "count":
            dfg = df.groupby(x).size().reset_index(name="value")

            labels = dfg[x].astype(str).tolist()
            values = dfg["value"].tolist()

        elif agg == "none" and y in df.columns:
            df_clean = df[[x, y]].dropna()

            if len(df_clean) < 2:
                return jsonify({"insight": "Nepietiek datu analīzei"})

            corr = df_clean[x].corr(df_clean[y]) if df_clean[x].dtype != "O" else 0

            labels = ["correlation"]
            values = [round(corr, 3) if corr == corr else 0]

        elif agg == "average" and y in df.columns:
            dfg = df.groupby(x)[y].mean().reset_index(name="value")

            labels = dfg[x].astype(str).tolist()
            values = dfg["value"].tolist()

        else:
            return jsonify({"insight": "Nav derīgu datu analīzei"})

        insight = generate_chart_insight("chart", labels, values)

        return jsonify({"insight": insight})

    except Exception as e:
        print("INSIGHT ERROR:", e)
        return jsonify({"insight": "AI kļūda"}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
