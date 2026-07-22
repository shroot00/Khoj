// Point this at your deployed FastAPI backend (Render URL), e.g.
// const API_BASE = "https://nsahackathon.onrender.com";
const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8123"
  : "https://REPLACE-WITH-YOUR-RENDER-URL.onrender.com";
