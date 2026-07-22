# Khoj — Smart Trek Planner

Khoj helps mountaineers and trekkers plan safe, informed expeditions: trek data, safety risk
assessments, guide/lodging recommendations, and a trek-planning chatbot.

## Structure

- `backend/` — FastAPI API (treks, recommendations, risk assessment, chat, places). See
  `backend/app/main.py` for routes.
- `frontend/` — static HTML/CSS/JS UI that calls the backend API.

## Running locally

Backend:
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000, docs at `/docs`.

Frontend:
```
cd frontend
python -m http.server 5500
```
Open http://127.0.0.1:5500 — it targets `http://127.0.0.1:8000` automatically when run
from localhost. Edit `frontend/config.js` to point at your deployed API URL for production.

## Deployment

- **Backend**: deploy `backend/` on Render (or similar) as a Python web service.
  `backend/Procfile` defines the start command. If deploying from this monorepo, set the
  service's root directory to `backend/`.
- **Frontend**: deploy `frontend/` as a static site (Render Static Site, GitHub Pages,
  Netlify, etc.), with root directory `frontend/`. Update `frontend/config.js` with the
  backend's live URL first.

## Notes

- `backend/chatbot.py` is a separate Streamlit chatbot prototype (not used by the deployed
  API). It reads its OpenAI key from the `OPENAI_API_KEY` environment variable — set that
  before running it, never hardcode a key in source.
- Data is stored in local SQLite files; on most free hosting tiers the filesystem is
  ephemeral, so assessment history won't persist across restarts unless you add a
  persistent disk or migrate to a hosted database.

## Team

- Shreeyut Karmacharya — Backend development
- Rehash Adhikari — Backend development
- Nasna Bajracharya — UI/UX, Front End Dev
- Medhavi Pandit — Product Owner
- Spriha Paudel — Program Manager
