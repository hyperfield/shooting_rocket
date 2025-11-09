import json
import os

HIGHSCORES_FILE = "highscores.json"
MAX_ENTRIES = 5


def _default_scores():
    return [0] * MAX_ENTRIES


def load_high_scores():
    if not os.path.exists(HIGHSCORES_FILE):
        return _default_scores()

    try:
        with open(HIGHSCORES_FILE, "r", encoding="utf-8") as source:
            data = json.load(source)
    except (json.JSONDecodeError, OSError, ValueError):
        return _default_scores()

    if not isinstance(data, list):
        return _default_scores()

    scores = [int(max(0, score)) for score in data]
    scores.extend(_default_scores())
    return sorted(scores, reverse=True)[:MAX_ENTRIES]


def save_high_scores(scores):
    try:
        with open(HIGHSCORES_FILE, "w", encoding="utf-8") as destination:
            json.dump(scores, destination)
    except OSError:
        # Best effort persistence.
        pass


def register_score(score):
    scores = load_high_scores()
    scores.append(max(0, int(score)))
    scores = sorted(scores, reverse=True)[:MAX_ENTRIES]
    save_high_scores(scores)
    return scores
