const queryInput = document.getElementById('queryInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');
const avoidList = document.getElementById('avoidList');
const learnList = document.getElementById('learnList');
const summaryText = document.getElementById('summaryText');
const summaryCard = document.getElementById('summaryCard');

const loadingMessages = [
  "Scraping job boards & trend data...",
  "Analyzing skill demand signals...",
  "Consulting the AI advisor...",
  "Building your roadmap...",
];
let loadingInterval = null;

function cycleLoadingMessages() {
  let i = 0;
  const el = document.getElementById('loadingText');
  el.textContent = loadingMessages[0];
  loadingInterval = setInterval(() => {
    i = (i + 1) % loadingMessages.length;
    el.textContent = loadingMessages[i];
  }, 1800);
}

function stopLoadingMessages() {
  if (loadingInterval) {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }
}

function showLoading() {
  loading.style.display = 'flex';
  error.style.display = 'none';
  results.style.display = 'none';
  analyzeBtn.disabled = true;
  cycleLoadingMessages();
}

function hideLoading() {
  loading.style.display = 'none';
  analyzeBtn.disabled = false;
  stopLoadingMessages();
}

function showError(msg) {
  error.textContent = '⚠️ ' + msg;
  error.style.display = 'block';
  hideLoading();
}

function buildSkillCard(item, type) {
  const div = document.createElement('div');
  div.className = 'skill-card';

  const isAvoid = type === 'avoid';
  const badgeClass = isAvoid ? 'avoid-badge' : 'learn-badge';
  const badgeText = isAvoid ? 'Skip' : 'Focus';
  const icon = isAvoid ? '✕' : '✓';

  div.innerHTML = `
    <div class="skill-name">
      ${icon} ${escapeHtml(item.skill)}
      <span class="skill-badge ${badgeClass}">${badgeText}</span>
    </div>
    <div class="skill-reason">${escapeHtml(item.reason)}</div>
  `;
  return div;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str || '';
  return d.innerHTML;
}

function renderResults(data) {
  avoidList.innerHTML = '';
  learnList.innerHTML = '';

  const avoidItems = Array.isArray(data.avoid) ? data.avoid : [];
  const altItems = Array.isArray(data.alternatives) ? data.alternatives : [];

  if (avoidItems.length === 0 && altItems.length === 0) {
    showError('No results returned. Please try a different query.');
    return;
  }

  avoidItems.forEach(item => {
    avoidList.appendChild(buildSkillCard(item, 'avoid'));
  });

  altItems.forEach(item => {
    learnList.appendChild(buildSkillCard(item, 'learn'));
  });

  if (data.summary) {
    summaryText.textContent = data.summary;
    summaryCard.style.display = 'block';
  } else {
    summaryCard.style.display = 'none';
  }

  results.style.display = 'block';
  setTimeout(() => results.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

async function analyze() {
  const query = queryInput.value.trim();
  if (!query) {
    queryInput.focus();
    return;
  }

  showLoading();

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      let errMsg = `Server error (${response.status})`;
      try {
        const errData = await response.json();
        errMsg = errData.detail || errMsg;
      } catch (_) {}
      throw new Error(errMsg);
    }

    const data = await response.json();
    hideLoading();
    renderResults(data);
  } catch (err) {
    showError(err.message || 'An unexpected error occurred. Please try again.');
  }
}

// Event listeners
analyzeBtn.addEventListener('click', analyze);

queryInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') analyze();
});

// Example chips
document.querySelectorAll('.example-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    queryInput.value = chip.dataset.value;
    queryInput.focus();
    analyze();
  });
});