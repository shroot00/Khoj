const chatHistory = [];

function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return [...root.querySelectorAll(sel)]; }

// ---------- Tabs ----------
function showTab(name) {
  $all(".tab-btn").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  $all(".tab-panel").forEach(p => p.classList.toggle("active", p.id === name));
}

$all(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

$("#back-to-explore").addEventListener("click", () => showTab("explore"));

// ---------- API helper ----------
async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

// ---------- Explore Treks ----------
function riskBadge(level) {
  return `<span class="badge risk-${level}">${level} risk</span>`;
}

function trekCard(trek) {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <h3>${trek.name}</h3>
    <div class="meta">${trek.location} · ${trek.altitude}m · ${trek.duration} days</div>
    ${riskBadge(trek.riskLevel)}<span class="badge">${trek.difficulty}</span>
    ${trek.aiScore != null ? `<span class="badge">AI score: ${trek.aiScore}</span>` : ""}
  `;
  div.addEventListener("click", () => openTrekDetail(trek.id));
  return div;
}

async function loadTreks() {
  const treks = await api("/treks");
  const list = $("#trek-list");
  list.innerHTML = "";
  treks.forEach(t => list.appendChild(trekCard(t)));
}

async function openTrekDetail(id) {
  const data = await api(`/treks/${id}/plan`);
  const { trek, guides, lodging, safety_recs } = data;
  $("#trek-detail-content").innerHTML = `
    <h2>${trek.name}</h2>
    <div class="meta">${trek.location} · ${trek.altitude}m · ${trek.duration} days · ${trek.difficulty}</div>
    ${riskBadge(trek.riskLevel)}
    <p>Best season: ${trek.bestSeason}</p>
    <p>Estimated cost: $${trek.cost_min}–$${trek.cost_max}</p>
    <h3>Highlights</h3>
    <ul>${trek.highlights.map(h => `<li>${h}</li>`).join("")}</ul>
    <h3>Recommended gear</h3>
    <ul>${trek.gear.map(g => `<li>${g}</li>`).join("")}</ul>
    <h3>Guides</h3>
    <ul>${(guides || []).map(g => `<li>${g.name} — ★${g.rating} (${g.reviews} reviews) — $${g.price_per_day}/day</li>`).join("") || "<li>No guides listed</li>"}</ul>
    <h3>Lodging</h3>
    <ul>${(lodging || []).map(l => `<li>${l.type} — ${l.price_range}</li>`).join("") || "<li>No lodging listed</li>"}</ul>
    <h3>Safety recommendations</h3>
    <ul>${safety_recs.map(s => `<li>${s}</li>`).join("")}</ul>
  `;
  showTab("trek-detail");
}

// ---------- Recommendations ----------
$("#reco-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const profile = {
    experience: form.get("experience"),
    fitness: form.get("fitness"),
    budget: form.get("budget"),
    preferences: [],
  };
  const data = await api("/recommendations", { method: "POST", body: JSON.stringify(profile) });
  const results = $("#reco-results");
  results.innerHTML = "";
  data.recommendations.forEach(r => {
    const card = trekCard(r.trek);
    const reason = document.createElement("div");
    reason.className = "meta";
    reason.textContent = r.reason;
    card.appendChild(reason);
    results.appendChild(card);
  });
});

// ---------- Risk Check ----------
$("#risk-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const payload = {
    lat: parseFloat(form.get("lat")),
    lon: parseFloat(form.get("lon")),
    date: form.get("date") || null,
    elevation_m: form.get("elevation_m") ? parseFloat(form.get("elevation_m")) : null,
  };
  const data = await api("/risk/assess", { method: "POST", body: JSON.stringify(payload) });
  const r = data.risk;
  const bar = (label, pct) => `
    <div class="risk-bar-row">
      <span style="width:90px">${label}</span>
      <div class="risk-bar-track"><div class="risk-bar-fill" style="width:${pct}%"></div></div>
      <span>${pct}%</span>
    </div>`;
  $("#risk-result").innerHTML = `
    <div class="risk-card">
      <h3>${r.label} (${r.overall_pct}%)</h3>
      <p class="meta">${r.reason}</p>
      ${bar("Avalanche", r.avalanche_pct)}
      ${bar("Blizzard", r.blizzard_pct)}
      ${bar("Landslide", r.landslide_pct)}
    </div>
  `;
});

// ---------- Chat ----------
function appendChatMsg(role, text) {
  const win = $("#chat-window");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

$("#chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("#chat-input");
  const message = input.value.trim();
  if (!message) return;
  appendChatMsg("user", message);
  chatHistory.push({ type: "user", text: message });
  input.value = "";

  const data = await api("/chat", { method: "POST", body: JSON.stringify({ message, history: chatHistory }) });
  appendChatMsg("bot", data.reply);
  chatHistory.push({ type: "ai", text: data.reply });
  if (data.showPlan && data.selectedTrekId != null) {
    openTrekDetail(data.selectedTrekId);
  }
});

// ---------- Init ----------
(async function init() {
  try {
    await api("/");
    $("#api-status").textContent = `Connected to API: ${API_BASE}`;
  } catch (err) {
    $("#api-status").textContent = `Could not reach API at ${API_BASE}`;
  }
  loadTreks().catch(err => {
    $("#trek-list").textContent = "Failed to load treks — check API_BASE in config.js";
  });
})();
