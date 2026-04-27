import sys
import re

path = r'c:\Users\resha\OneDrive\Desktop\opshack\ReliefOps\frontend\index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# CSS Fixes
content = content.replace(
  '  .p-critical { background: var(--danger); box-shadow: 0 0 8px rgba(239,68,68,0.5); }',
  '  .p-critical { background: #ff4757; box-shadow: 0 0 8px rgba(255,71,87,0.5); }'
).replace(
  '  .p-high     { background: var(--warn); }',
  '  .p-high     { background: #ff6b35; }'
).replace(
  '  .p-medium   { background: #a3e635; }',
  '  .p-medium   { background: #ffd32a; }'
).replace(
  '  .p-low      { background: var(--muted); }',
  '  .p-low      { background: #2ed573; }'
).replace(
  '  .score-critical { background: var(--red-soft); color: var(--danger); }',
  '  .score-critical { background: rgba(255,71,87,0.12); color: #ff4757; }'
).replace(
  '  .score-high     { background: var(--amber-soft); color: var(--warn); }',
  '  .score-high     { background: rgba(255,107,53,0.12); color: #ff6b35; }'
).replace(
  '  .score-medium   { background: var(--green-soft); color: var(--accent); }',
  '  .score-medium   { background: rgba(255,211,42,0.12); color: #ffd32a; }'
).replace(
  '  .score-low      { background: var(--surface); color: var(--muted); border: 1px solid var(--border); }',
  '  .score-low      { background: rgba(46,213,115,0.12); color: #2ed573; }'
)

# Update form-row Location mapping
content = content.replace(
  """    <div class="form-row-2">
      <div class="form-row" style="margin:0">
        <label class="form-label">Latitude</label>
        <input class="form-input" id="f-lat" type="number" step="0.0001" value="12.9716" />
      </div>
      <div class="form-row" style="margin:0">
        <label class="form-label">Longitude</label>
        <input class="form-input" id="f-lon" type="number" step="0.0001" value="77.5946" />
      </div>
    </div>""",
  """    <div class="form-row" style="position: relative;">
      <label class="form-label">Location</label>
      <input class="form-input" id="location-search" placeholder="Search address..." autocomplete="off" />
      <div id="suggestions" style="position:absolute; top:calc(100% - 10px); left:0; right:0; background:var(--surface); z-index:1000; border:1px solid var(--border); border-radius:var(--radius); max-height:150px; overflow-y:auto; display:none;"></div>
      <div id="task-map" style="height: 250px; width: 100%; border-radius: 10px; margin-top: 8px;"></div>
      <div id="address-display" style="color: #22d3a0; font-family: var(--mono); font-size: 11px; margin-top: 8px; padding: 6px; background: var(--green-soft); border-radius: var(--radius);">📍 No location selected</div>
    </div>"""
)

# Add View Location Modal
content = content.replace(
  """<!-- Toast container -->
<div class="toast-container" id="toasts"></div>

<script>""",
  """<!-- View Location Modal -->
<div class="modal-overlay" id="view-location-modal">
  <div class="modal">
    <div class="modal-title">📍 Task Location</div>
    <div id="view-map" style="height: 300px; width: 100%; border-radius: 10px;"></div>
    <div id="view-address" style="color: var(--text); font-family: var(--mono); font-size: 12px; margin-top: 12px; margin-bottom: 20px; text-align: center;"></div>
    <div class="modal-footer">
      <button class="btn" onclick="document.getElementById('view-location-modal').classList.remove('open')">Close</button>
      <a class="btn btn-primary" id="google-maps-link" href="#" target="_blank">Open in Google Maps →</a>
    </div>
  </div>
</div>

<!-- Toast container -->
<div class="toast-container" id="toasts"></div>

<script>
// ── Geoapify Map Config ─────────────────────────────────
const GEOAPIFY_KEY = '545806cf8d194348b78434a772647fad';
let createMap = null;
let createMarker = null;
let viewMap = null;
let viewMarker = null;
let selectedTaskLat = 12.9716;
let selectedTaskLng = 77.5946;
let selectedTaskAddress = '';
let searchTimeout = null;

function initCreateMap() {
  if (!createMap) {
    createMap = L.map('task-map').setView([12.9716, 77.5946], 13);
    L.tileLayer(`https://maps.geoapify.com/v1/tile/dark-matter/{z}/{x}/{y}.png?apiKey=${GEOAPIFY_KEY}`, {
      attribution: '© Geoapify © OpenStreetMap',
      maxZoom: 20
    }).addTo(createMap);
    
    createMarker = L.marker([12.9716, 77.5946], {draggable: true}).addTo(createMap);
    
    createMap.on('click', (e) => {
      createMarker.setLatLng(e.latlng);
      geocodeReverse(e.latlng.lat, e.latlng.lng);
    });
    createMarker.on('dragend', () => {
      const pos = createMarker.getLatLng();
      geocodeReverse(pos.lat, pos.lng);
    });
  }
}

async function geocodeReverse(lat, lng) {
  selectedTaskLat = lat;
  selectedTaskLng = lng;
  try {
    const res = await fetch(`https://api.geoapify.com/v1/geocode/reverse?lat=${lat}&lon=${lng}&apiKey=${GEOAPIFY_KEY}`);
    const data = await res.json();
    if (data.features && data.features.length > 0) {
      selectedTaskAddress = data.features[0].properties.formatted;
      document.getElementById('address-display').innerHTML = `📍 ${selectedTaskAddress}`;
    } else {
      document.getElementById('address-display').innerHTML = `📍 ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
      selectedTaskAddress = '';
    }
  } catch (err) {
    console.error(err);
  }
}

document.getElementById('location-search').addEventListener('input', (e) => {
  const query = e.target.value;
  clearTimeout(searchTimeout);
  if (!query) {
    document.getElementById('suggestions').style.display = 'none';
    return;
  }
  searchTimeout = setTimeout(async () => {
    try {
      const res = await fetch(`https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(query)}&apiKey=${GEOAPIFY_KEY}&limit=5`);
      const data = await res.json();
      const sugDiv = document.getElementById('suggestions');
      sugDiv.innerHTML = '';
      if (data.features && data.features.length > 0) {
        data.features.forEach(f => {
          const div = document.createElement('div');
          div.style.padding = '8px 12px';
          div.style.cursor = 'pointer';
          div.style.borderBottom = '1px solid var(--border2)';
          div.style.fontSize = '12px';
          div.textContent = f.properties.formatted;
          div.onclick = () => {
            const lat = f.properties.lat;
            const lon = f.properties.lon;
            createMap.setView([lat, lon], 16);
            createMarker.setLatLng([lat, lon]);
            geocodeReverse(lat, lon);
            sugDiv.style.display = 'none';
            document.getElementById('location-search').value = f.properties.formatted;
          };
          sugDiv.appendChild(div);
        });
        sugDiv.style.display = 'block';
      } else {
        sugDiv.style.display = 'none';
      }
    } catch(err) {
      console.error(err);
    }
  }, 400);
});

function openViewLocationModal(lat, lng, address) {
  document.getElementById('view-location-modal').classList.add('open');
  document.getElementById('view-address').textContent = address || `Coordinates: ${lat}, ${lng}`;
  document.getElementById('google-maps-link').href = `https://www.google.com/maps?q=${lat},${lng}`;
  
  setTimeout(() => {
    if (!viewMap) {
      viewMap = L.map('view-map').setView([lat, lng], 15);
      L.tileLayer(`https://maps.geoapify.com/v1/tile/dark-matter/{z}/{x}/{y}.png?apiKey=${GEOAPIFY_KEY}`, {
        attribution: '© Geoapify © OpenStreetMap',
        maxZoom: 20
      }).addTo(viewMap);
      
      const redIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });
      viewMarker = L.marker([lat, lng], {icon: redIcon}).addTo(viewMap);
      viewMarker.bindPopup(`<b>${address || 'Location'}</b>`).openPopup();
    } else {
      viewMap.invalidateSize();
      viewMap.setView([lat, lng], 15);
      viewMarker.setLatLng([lat, lng]);
      viewMarker.setPopupContent(`<b>${address || 'Location'}</b>`).openPopup();
    }
  }, 350);
}"""
)

# openModal modification
content = content.replace(
  "function openModal() { document.getElementById('modal-overlay').classList.add('open'); }",
  """function openModal() {
  document.getElementById('modal-overlay').classList.add('open');
  setTimeout(() => {
    initCreateMap();
    if(createMap) createMap.invalidateSize();
  }, 350);
}"""
)

# Parse Float map
content = content.replace(
  """  const lat    = parseFloat(document.getElementById('f-lat').value);
  const lon    = parseFloat(document.getElementById('f-lon').value);

  if (!title) { toast('Please enter a task title', 'error'); return; }

  const priority_score = Math.round((urgency/5*0.5 + Math.min(lives/100,1)*0.3 + 0.2) * 1000) / 1000;
  const newTask = {
    id: Date.now(),
    ngoId: currentNgoId,
    title, required_skill: skill, urgency, lives_at_risk: lives,
    latitude: lat, longitude: lon,
    status: 'pending', assigned_to: null, priority_score,
    invited_to: [], accepted_by: [], created_at: new Date().toLocaleString()
  };

  allTasks.push(newTask);
  const invited = autoAssignTask(newTask);""",
  """  const lat    = selectedTaskLat;
  const lon    = selectedTaskLng;

  if (!title) { toast('Please enter a task title', 'error'); return; }

  const newTask = {
    id: Date.now(),
    ngoId: currentNgoId,
    title, required_skill: skill, urgency, lives_at_risk: lives,
    latitude: lat, longitude: lon, address: selectedTaskAddress,
    status: 'pending', assigned_to: null, priority_score: 0, score_breakdown: '',
    invited_to: [], accepted_by: [], created_at: new Date().toLocaleString()
  };
  
  updatePriorityScore(newTask);
  allTasks.push(newTask);
  const invited = autoAssignTask(newTask);"""
)

# Task Detail map
content = content.replace(
  """function taskDetail(id) {
  const t = allTasks.find(x => x.id === id);
  if (t) toast(`Priority score: ${(t.priority_score*100).toFixed(0)} · Urgency ${t.urgency}/5 · ${t.lives_at_risk} lives at risk`, 'success');
}""",
  """function taskDetail(id) {
  const t = allTasks.find(x => x.id === id);
  if (t) toast(t.score_breakdown || `Priority score: ${t.priority_score.toFixed(0)}`, 'success');
}"""
)

# Render Task updates
content = re.sub(
  r'    <div class="task-card" style="animation-delay:\${i\*0\.04}s" onclick="taskDetail\(\${task\.id}\)">.*?<div class="status-tag s-\${task\.status}">\${task\.status\.replace\(\'_\',\' \'\)}</div>\s*</div>\s*</div>`;',
  """    const addressStr = task.address ? `<span>📍 ${task.address}</span>` : '';
    return `
    <div class="task-card" style="animation-delay:${i*0.04}s" onclick="taskDetail(${task.id})">
      <div class="priority-bar p-${pc}"></div>
      <div>
        <div class="task-title">${task.title}</div>
        <div class="task-meta">
          <span class="task-skill">${SKILL_EMOJI[task.required_skill] || '•'} ${task.required_skill.replace('_',' ')}</span>
          <span>Urgency ${task.urgency}/5</span>
          <span>⚠ ${task.lives_at_risk} lives</span>
          ${vol ? `<span>👤 ${vol.name}</span>` : ''}
          ${task.invite_message ? `<span>${task.invite_message}</span>` : ''}
          <span>Requests ${invitedCount}</span>
          <span>Accepted ${acceptedCount}</span>
          ${addressStr}
        </div>
      </div>
      <div class="task-right">
        <div class="score-badge score-${pc}" title="${task.score_breakdown || ''}">${(task.priority_score).toFixed(0)}</div>
        <div class="status-tag s-${task.status}">${task.status.replace('_',' ')}</div>
      </div>
    </div>`;""",
    content, flags=re.DOTALL
)

# updatePriorityScore
content = re.sub(
  r'function priorityClass\(score\) \{.*?return \'Low\';\n\}',
  """function priorityClass(score) {
  if (score >= 150) return 'critical';
  if (score >= 100) return 'high';
  if (score >= 50) return 'medium';
  return 'low';
}
function priorityLabel(score) {
  if (score >= 150) return 'Critical';
  if (score >= 100) return 'High';
  if (score >= 50) return 'Medium';
  return 'Low';
}

function updatePriorityScore(task) {
  let unassignedCount = allVolunteers.filter(v => v.available && v.skills.split(',').includes(task.required_skill)).length;
  let scarcityBonus = 0;
  if (unassignedCount < 2) scarcityBonus = 30;
  else if (unassignedCount >= 2 && unassignedCount <= 4) scarcityBonus = 15;
  
  let hoursUnassigned = 0;
  if (!task.assigned_to) {
    hoursUnassigned = (Date.now() - new Date(task.created_at).getTime()) / (1000 * 60 * 60);
  }
  
  const urgencyPts = task.urgency * 20;
  const livesPts = Math.min(task.lives_at_risk * 1.5, 150);
  const decayPts = Math.floor(hoursUnassigned * 2);
  
  task.priority_score = urgencyPts + livesPts + scarcityBonus - decayPts;
  task.score_breakdown = `Score: ${task.priority_score.toFixed(0)} | Urgency: ${urgencyPts} pts | Lives: ${livesPts} pts | Scarcity: +${scarcityBonus} | Decay: -${decayPts} pts`;
}""",
  content, flags=re.DOTALL
)


with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("done")
