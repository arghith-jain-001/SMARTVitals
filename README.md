# SmartVitals AI — Astronaut Health Monitoring Prototype

A local, offline-first hackathon demonstrator with synthetic astronaut telemetry, a Scikit-learn Isolation Forest anomaly detector, FastAPI, SQLite, and a browser dashboard.

## Requirements
- [uv](https://docs.astral.sh/uv/)
- Internet connection for the first dependency installation only
- A modern browser

## Run on Windows
1. Extract the ZIP.
2. Open the extracted `SmartVitals-AI` folder in VS Code.
3. Double-click `SmartVitals.bat`. It installs uv if needed, creates `.venv`, installs dependencies, starts the server, waits until the API is ready, and opens the dashboard in your browser.

To run the setup manually, open Terminal in VS Code and use:

```powershell
uv venv --python 3.12
```

Install packages into that environment:

```powershell
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

Start the app:

```powershell
uv run --python .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.

## Demo controls
- **Test anomaly alert**: injects one unusual synthetic reading on the next update.
- **Simulate Earth link**: toggles the displayed connection state. Local monitoring continues either way.
- **Pause stream**: pauses generation of new readings.
- Data is stored in `data/astronaut_health.db`.

## Important limitations
This is a software prototype, not a medical device. All generated readings and stress values are synthetic. The Isolation Forest model is trained on synthetic baseline data and must not be interpreted as clinically validated. The temperature channel is simulated as core temperature; no real sensor is connected. The Earth-link control is a status simulation, not a real radio or network link. Do not use this prototype for real health decisions.

## Suggested next development steps
1. Replace or supplement synthetic data with a clearly documented public research dataset.
2. Evaluate the detector on held-out, labelled data and report precision, recall, false-alarm rate, and detection delay.
3. Add per-crew baselines and sensor-quality checks.
4. Add only reviewed, crew-approved medical reference protocols; keep the system as decision support.
5. Add a true communications-delay simulator and test offline recovery.
