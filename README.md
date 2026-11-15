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

## Host the dashboard on GitHub Pages
The dashboard automatically switches to a standalone demo on GitHub Pages. It generates synthetic readings in the browser, saves the recent history in that browser's local storage, and does not need the Python backend. The chart library is loaded from a CDN, so visitors need an internet connection to load the chart.

To publish it from this repository:
1. Copy `frontend/index.html` to the repository root and name the copy `index.html` (keep the original in place for the local backend).
2. Push the change to GitHub.
3. In the repository, open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**, select your branch (usually `main`) and the `/(root)` folder, then click **Save**.
5. After GitHub finishes publishing, open the Pages URL shown on that settings page.

GitHub Pages' branch-based setup publishes from the repository root or a `/docs` folder, not the existing `/frontend` folder, which is why the copy is needed. The standalone demo's history is per-browser and is separate from the backend's SQLite database.

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
