import json

from collections import defaultdict
from itertools import chain
from pathlib import Path

import requests

from flask import Flask, render_template, request, jsonify

DATA_PATH = Path("word_rankings.json")
DATA_URL = (
    "https://github.com/samj1912/song-lyrics/releases/download/Data/word_rankings.json"
)

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

ALL_WORDS = set(chain(*ranking_data.values()))
# Takes the max rank for all the value and multiplies it by 1.05 to get a
# slightly larger value for visualization
MAX_RANK = int(
    max(chain(*(ranking.values() for ranking in ranking_data.values()))) * 1.05
)


def get_rankings(word):
    """Returns a tuple containing the rank v/s year distribution.

    Args:
        word (str): The input word.

    Returns:
        Tuple[List[int], List[int]]: A tuple containing the list of
            rankings v/s the year. In case the word does not exist in
            the corpus at all, `MAX_RANK` is returned.

    """
    word = word.lower().strip()
    years = []
    rankings = []
    for year, year_rankings in ranking_data.items():
        if word in ALL_WORDS:
            ranking = year_rankings.get(word, len(year_rankings))
        else:
            ranking = MAX_RANK
        years.append(int(year))
        rankings.append(ranking)
    return (years, rankings)


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", max_rank=MAX_RANK)


@app.route("/values", methods=["GET", "POST"])
def get_values():
    values = request.values.getlist("values[]")
    final_data = defaultdict(dict)
    for word in values:
        for year, popularity in zip(*get_rankings(word)):
            final_data[year]["year"] = year
            final_data[year][word] = popularity
    return jsonify({"values": sorted(final_data.values(), key=lambda x: x["year"])})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
