from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
import sqlite3, random, math, time
import numpy as np
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "astronaut_health.db"
FRONTEND = ROOT / "frontend"
(ROOT / "data").mkdir(exist_ok=True)

app = FastAPI(title="SmartVitals AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

# Prototype model: trained on simulated baseline readings, not clinical data.
rng = np.random.default_rng(42)
normal = np.column_stack([
    rng.normal(72, 8, 1500),      # heart rate
    rng.normal(98, 1.0, 1500),    # SpO2
    rng.normal(36.8, 0.25, 1500), # temperature
    rng.normal(25, 10, 1500)      # simulated stress score
])
model = IsolationForest(n_estimators=120, contamination=0.035, random_state=42)
model.fit(normal)

state = {"simulation": True, "earth_connected": False, "force_event": False, "last": None}
crew = {"name": "ASTRONAUT 01", "mission": "MARS EXPEDITION // SIMULATION"}

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS vitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, heart_rate REAL,
        spo2 REAL, temperature REAL, stress REAL, anomaly INTEGER, score REAL,
        status TEXT, note TEXT
    )""")
    conn.commit()
    return conn

class Controls(BaseModel):
    simulation: bool | None = None
    earth_connected: bool | None = None
    force_event: bool | None = None

def make_reading():
    hr = random.gauss(72, 7)
    spo2 = random.gauss(98, 0.8)
    temp = random.gauss(36.8, 0.2)
    stress = max(0, min(100, random.gauss(25, 9)))
    if state["force_event"]:
        hr = random.gauss(118, 5)
        spo2 = random.gauss(91, 1.5)
        stress = random.gauss(78, 7)
        state["force_event"] = False
    vals = np.array([[hr, spo2, temp, stress]])
    pred = int(model.predict(vals)[0] == -1)
    score = float(model.decision_function(vals)[0])
    # Transparent safety layer: flag conspicuous simulated readings too.
    if hr > 110 or spo2 < 93 or temp > 38.0 or temp < 35.5:
        pred = 1
    status = "ALERT" if pred else "NOMINAL"
    note = "Unusual simulated pattern; review crew-approved medical guidance." if pred else "No anomaly detected by prototype model."
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": round(hr, 1), "spo2": round(spo2, 1),
        "temperature": round(temp, 2), "stress": round(stress, 1),
        "anomaly": pred, "score": round(score, 4), "status": status, "note": note
    }

@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")

@app.get("/api/status")
def get_status():
    return {"simulation": state["simulation"], "earth_connected": state["earth_connected"],
            "local_ai": True, "database": "online", "crew": crew}

@app.post("/api/controls")
def controls(payload: Controls):
    for key, value in payload.model_dump(exclude_none=True).items():
        state[key] = value
    return get_status()

@app.get("/api/vitals")
def get_vitals():
    if state["simulation"]:
        reading = make_reading()
        conn = db()
        conn.execute("""INSERT INTO vitals(timestamp,heart_rate,spo2,temperature,stress,anomaly,score,status,note)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                     (reading["timestamp"], reading["heart_rate"], reading["spo2"], reading["temperature"],
                      reading["stress"], reading["anomaly"], reading["score"], reading["status"], reading["note"]))
        conn.commit()
        conn.close()
        state["last"] = reading
        return reading
    return state["last"] or {"status": "WAITING", "note": "Simulation paused."}

@app.get("/api/history")
def history(limit: int = 40):
    conn = db()
    rows = conn.execute("SELECT * FROM vitals ORDER BY id DESC LIMIT ?", (min(limit, 100),)).fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

@app.get("/api/summary")
def summary():
    conn = db()
    total = conn.execute("SELECT COUNT(*) FROM vitals").fetchone()[0]
    alerts = conn.execute("SELECT COUNT(*) FROM vitals WHERE anomaly=1").fetchone()[0]
    conn.close()
    return {"readings": total, "alerts": alerts}

@app.post("/api/reset")
def reset():
    conn = db()
    conn.execute("DELETE FROM vitals")
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/test-alert")
def test_alert():
    state["force_event"] = True
    state["simulation"] = True
    return {"ok": True, "message": "A simulated unusual reading will be generated on the next update."}
