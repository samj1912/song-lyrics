import json

from collections import defaultdict
from pathlib import Path

import requests
import numpy as np

from flask import Flask, render_template, request, jsonify
from scipy.interpolate import make_interp_spline

DATA_PATH = Path("word_rankings.json")
DATA_URL = "https://github.com/samj1912/song-lyrics/releases/download/Data/word_rankings.json"

ranking_data = {}
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

if not DATA_PATH.exists():
    ranking_data = requests.get(DATA_URL).json()
    with DATA_PATH.open("w") as f:
        json.dump(ranking_data, f)
else:
    with DATA_PATH.open() as f:
        ranking_data = json.load(f)

def _get_rankings(word):
    word = word.lower().strip()
    years = []
    popularities = []
    for year, year_rankings in ranking_data.items():
        popularity = year_rankings.get(word, len(year_rankings))
        years.append(int(year))
        popularities.append(popularity)
    return (years, popularities)

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/values", methods=["GET", "POST"])
def get_values():
    values = request.values.getlist("values[]")
    final_data = defaultdict(dict)
    for word in values:
        for year, popularity in zip(*_get_rankings(word)):
            final_data[year]["year"] = year
            final_data[year][word] = popularity
    return jsonify({"values": sorted(final_data.values(), key=lambda x: x["year"])})

if __name__ == "__main__":
    app.run(host="0.0.0.0")
