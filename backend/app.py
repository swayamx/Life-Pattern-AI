from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    hour INTEGER,
    usage INTEGER,
    mood INTEGER,
    productive INTEGER
)
""")
conn.commit()

# ---------------- MODEL ----------------
def train_model():
    cursor.execute("SELECT * FROM user_data")
    rows = cursor.fetchall()

    if len(rows) == 0:
        data = {
            "hour": [6,7,8,20,21,22],
            "usage": [10,15,20,80,90,95],
            "mood": [1,1,0,-1,-1,-1],
            "productive": [1,1,1,0,0,0]
        }
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(rows, columns=["hour","usage","mood","productive"])

    X = df[["hour","usage","mood"]]
    y = df["productive"]

    model = RandomForestClassifier()
    model.fit(X, y)
    return model

model = train_model()

# ---------------- ROUTES ----------------
@app.route("/predict", methods=["POST"])
def predict():
    global model

    data = request.json

    hour = int(data["hour"])
    usage = int(data["usage"])

    mood_map = {"happy":1,"neutral":0,"stressed":-1}
    mood = mood_map[data["mood"]]

    result = model.predict([[hour, usage, mood]])[0]

    # store data
    cursor.execute(
        "INSERT INTO user_data (hour, usage, mood, productive) VALUES (?, ?, ?, ?)",
        (hour, usage, mood, int(result))
    )
    conn.commit()

    # retrain model
    model = train_model()

    # AI logic
    focus_score = max(0, 100 - usage)

    if usage > 80 and hour > 20:
        burnout = "⚠️ Burnout Risk High"
    else:
        burnout = "✅ Normal"

    if result == 1:
        message = "You are PRODUCTIVE"
        suggestion = "Best time for deep work"
    else:
        message = "You are DISTRACTED"
        suggestion = "Reduce phone usage"

    return jsonify({
        "message": message,
        "suggestion": suggestion,
        "focus_score": focus_score,
        "burnout": burnout
    })

@app.route("/data", methods=["GET"])
def data():
    cursor.execute("SELECT * FROM user_data")
    return jsonify(cursor.fetchall())

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
