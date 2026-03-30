from flask import Flask, render_template, request, jsonify
import pandas as pd

from services.data_utils import clean_df
from services.ai_utils import ai_choose_top_charts

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

    file = request.files["file"]
    df = (
        pd.read_csv(file)
        if file.filename.endswith(".csv")
        else pd.read_excel(file)
    )

    df.ffill(inplace=True)
    df = clean_df(df)
    df_global = df

    charts = ai_choose_top_charts(df)

    return jsonify(charts)


@app.route("/data")
def data():
    x = request.args["x"]
    y = request.args.get("y")
    agg = request.args.get("agg")

    df = df_global.copy()

    if agg == "count":
        dfg = df.groupby(x).size().reset_index(name="value")
        return jsonify({
            "labels": dfg[x].tolist(),
            "values": dfg["value"].tolist()
        })

    if agg == "average":
        dfg = df.groupby(x)[y].mean().reset_index()
        return jsonify({
            "labels": dfg[x].tolist(),
            "values": dfg[y].tolist()
        })

    if agg == "none":
        df = df[[x, y]].dropna()

        return jsonify({
            "points": [
                {"x": float(row[x]), "y": float(row[y])}
                for _, row in df.iterrows()
            ]
        })
    
    if agg == "average" and isinstance(y, list):
        result = []
        for col in y:
            result.append(float(df[col].mean()))

        return jsonify({
            "labels": y,
            "values": result
        })

    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True)
