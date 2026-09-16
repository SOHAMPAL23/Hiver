/**
 * Apple Support AI — Frontend Logic
 * Minimal, clean, all backend endpoints preserved.
 */

// ─────────────────────────────────────────────
// State
// ─────────────────────────────────────────────
let lastResult       = null;
let detailsOpen      = false;
let currentLlmConfig = null;

const INTENT_NAMES = {
  battery_power_charging:         '🔋 Battery & Power',
  software_update_os_bug:         '⚙️ OS Update',
  account_apple_id_icloud:        '🚨 Apple ID',
  hardware_physical_damage:       '📱 Hardware',
  connectivity_network_bluetooth: '📶 Connectivity',
  billing_subscriptions_appstore: '💳 Billing',
  device_performance_storage:     '⚡ Performance',
  general_feedback_complaint:     '💬 Feedback'
};

// ─────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initHealth();
  initLlmConfig();

  const textarea = document.getElementById('query');
  const charCount = document.getElementById('charCount');

  textarea.addEventListener('input', () => {
    charCount.innerText = `${textarea.value.length} chars`;
  });

  textarea.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      submitQuery();
    }
  });
});

// ─────────────────────────────────────────────
// Health Check
// ─────────────────────────────────────────────
async function initHealth() {
  const dot    = document.getElementById('statusDot');
  const text   = document.getElementById('statusText');
  const qaApi  = document.getElementById('qaApiStatus');
  const qaLat  = document.getElementById('qaApiLatency');

  const t = performance.now();
  try {
    const res = await fetch('/health');
    const ms  = Math.round(performance.now() - t);
    if (res.ok) {
      dot.className   = 'status-dot';
      text.innerText  = 'Online';
      if (qaApi) qaApi.innerText = 'Healthy';
      if (qaLat) qaLat.innerText = `${ms}ms · Port 8000`;
    } else throw new Error('not ok');
  } catch {
    dot.className  = 'status-dot offline';
    text.innerText = 'Offline';
  }
}

// ─────────────────────────────────────────────
// Submit query → /predict
// ─────────────────────────────────────────────
async function submitQuery() {
  const query = document.getElementById('query').value.trim();
  if (!query) { showToast('Enter an issue first.'); return; }

  const btn = document.getElementById('btnSubmit');
  btn.disabled   = true;
  btn.innerText  = 'Generating…';

  const t = performance.now();
  try {
    const res = await fetch('/predict', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: query })
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const data = await res.json();
    lastResult = { ...data, query, latency_ms: Math.round(performance.now() - t) };
    renderResults(data);
  } catch (err) {
    showToast(`Error: ${err.message}`);
    // Show error in output panel
    document.getElementById('outputEmpty').classList.add('hidden');
    const content = document.getElementById('outputContent');
    content.classList.remove('hidden');
    document.getElementById('resText').innerText = `⚠ ${err.message}\n\nMake sure the backend is running on port 8000.`;
  } finally {
    btn.disabled  = false;
    btn.innerText = 'Generate Resolution';
  }
}

// ─────────────────────────────────────────────
// Render results into the right panel
// ─────────────────────────────────────────────
function renderResults(data) {
  document.getElementById('outputEmpty').classList.add('hidden');
  document.getElementById('outputContent').classList.remove('hidden');

  // ── Policy badge ──
  const policyBadge = document.getElementById('policyBadge');
  if (data.decision === 'ESCALATE') {
    policyBadge.className = 'badge-policy badge-escalate';
    policyBadge.innerText = '▲ ESCALATE';
  } else {
    policyBadge.className = 'badge-policy badge-auto';
    policyBadge.innerText = '● AUTO-HANDLED';
  }

  // ── Intent badge ──
  document.getElementById('intentBadge').innerText =
    INTENT_NAMES[data.intent] || data.intent;

  // ── Model label ──
  const modelLabel = document.getElementById('modelLabel');
  if (modelLabel) {
    modelLabel.innerText = data.generation_model || '⚡ Engine';
  }

  // ── Resolution text ──
  document.getElementById('resText').innerText = data.reply;

  // ── Confidence bar ──
  const pct  = (data.intent_confidence * 100).toFixed(1);
  const fill = document.getElementById('confFill');
  fill.style.width = `${pct}%`;
  fill.className = 'conf-fill'
    + (data.intent_confidence > 0.70 ? ''
     : data.intent_confidence > 0.50 ? ' med' : ' low');
  document.getElementById('confVal').innerText = `${pct}%`;

  // ── Policy reason ──
  document.getElementById('policyReason').innerText =
    data.escalation_reason || 'High-confidence self-help diagnostic.';

  // ── Historical evidence ──
  const evList = document.getElementById('evidenceList');
  evList.innerHTML = '';
  if (data.evidence && data.evidence.length > 0) {
    data.evidence.slice(0, 3).forEach(ev => {
      const item = document.createElement('div');
      item.className = 'ev-item';
      item.innerHTML = `
        <div class="ev-match">${(ev.similarity * 100).toFixed(1)}% Match</div>
        <div class="ev-cust">"${escapeHtml(ev.customer_message)}"</div>
        <div class="ev-reply">@AppleSupport: "${escapeHtml(ev.historical_response)}"</div>
      `;
      evList.appendChild(item);
    });
  } else {
    evList.innerHTML = '<div style="font-size:12px;color:var(--text-3);">No historical matches found.</div>';
  }

  // Collapse details if previously open
  if (detailsOpen) closeDetails();
}

// ─────────────────────────────────────────────
// Technical details toggle
// ─────────────────────────────────────────────
function toggleDetails() {
  detailsOpen ? closeDetails() : openDetails();
}

function openDetails() {
  detailsOpen = true;
  document.getElementById('techDetails').classList.remove('hidden');
  document.getElementById('detailsToggle').classList.add('open');
  document.getElementById('detailsLabel').innerText = 'Hide Details';
}

function closeDetails() {
  detailsOpen = false;
  document.getElementById('techDetails').classList.add('hidden');
  document.getElementById('detailsToggle').classList.remove('open');
  document.getElementById('detailsLabel').innerText = 'Technical Details';
}

// ─────────────────────────────────────────────
// Copy resolution
// ─────────────────────────────────────────────
function copyResolution() {
  const text = document.getElementById('resText').innerText;
  if (!text) { showToast('Nothing to copy yet.'); return; }
  navigator.clipboard.writeText(text)
    .then(() => showToast('Copied to clipboard'))
    .catch(() => showToast('Copy failed'));
}

// ─────────────────────────────────────────────
// QA Panel
// ─────────────────────────────────────────────
function openQAPanel() {
  document.getElementById('qaPanel').classList.remove('hidden');
  initHealth(); // refresh stats
}

function closeQAPanel() {
  document.getElementById('qaPanel').classList.add('hidden');
}

// Verification suite → /api/run_tests
async function runVerificationSuite() {
  const btn       = document.getElementById('btnRunTests');
  const progWrap  = document.getElementById('progWrap');
  const progFill  = document.getElementById('progFill');
  const progLabel = document.getElementById('progLabel');
  const tbody     = document.getElementById('testsTableBody');

  btn.disabled = true;
  progWrap.classList.remove('hidden');
  progWrap.style.display = 'flex';
  progFill.style.width   = '15%';
  progLabel.innerText    = 'Running acceptance tests…';
  tbody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align:center;color:var(--text-3);padding:24px;">
        Executing 6 test scenarios…
      </td>
    </tr>`;

  try {
    const res = await fetch('/api/run_tests', { method: 'POST' });
    progFill.style.width = '75%';
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    progFill.style.width = '100%';
    progLabel.innerText  = `${data.passed_tests} / ${data.total_tests} passed`;

    renderTestTable(data.results);

    if (data.all_passed) showToast(`All ${data.total_tests} tests passed ✓`);
    else                  showToast(`${data.failed_tests} test(s) failed`);
  } catch (err) {
    progLabel.innerText = `Error: ${err.message}`;
    showToast(`Test error: ${err.message}`);
  } finally {
    btn.disabled = false;
  }
}

function renderTestTable(results) {
  const tbody = document.getElementById('testsTableBody');
  tbody.innerHTML = '';
  results.forEach(t => {
    const tr     = document.createElement('tr');
    const actual = t.actual_action === 'ESCALATE'
      ? `<span class="badge-policy badge-escalate" style="font-size:10px;padding:2px 7px;">ESCALATE</span>`
      : `<span class="badge-policy badge-auto"    style="font-size:10px;padding:2px 7px;">AUTO</span>`;

    tr.innerHTML = `
      <td style="font-family:monospace;color:var(--blue);font-weight:600;font-size:11px;">${t.id}</td>
      <td>
        <strong style="color:var(--text);font-size:12px;display:block;">${escapeHtml(t.name)}</strong>
        <span style="font-size:11px;color:var(--text-3);">${escapeHtml(t.description)}</span>
      </td>
      <td style="font-size:11.5px;color:var(--text-2);">"${escapeHtml(t.query)}"</td>
      <td><code style="font-size:10px;background:var(--surface-2);padding:2px 6px;border-radius:4px;color:var(--text-2);">${t.expected_action}</code></td>
      <td>${actual}</td>
      <td style="font-size:11px;color:var(--text-3);font-family:monospace;">${t.latency_ms.toFixed(0)}ms</td>
      <td>${t.passed ? '<span class="pill-pass">✓ PASS</span>' : '<span class="pill-fail">✗ FAIL</span>'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ─────────────────────────────────────────────
// LLM Configuration Modal
// ─────────────────────────────────────────────
async function initLlmConfig() {
  try {
    const res = await fetch('/api/llm_config');
    if (res.ok) {
      currentLlmConfig = await res.json();
      updateEngineChip(currentLlmConfig);
    }
  } catch { /* silent */ }
}

function updateEngineChip(cfg) {
  const chip = document.getElementById('engineChip');
  if (!chip) return;
  if (cfg && cfg.use_llm && cfg.provider !== 'none') {
    chip.innerText = `🤖 ${cfg.model_name || cfg.provider.toUpperCase()}`;
  } else {
    chip.innerText = '⚡ Diagnostic Engine';
  }
}

// Compat alias used in old code references
function updateHeaderLlmBadge(cfg) { updateEngineChip(cfg); }

function openLlmModal() {
  document.getElementById('llmModal').classList.remove('hidden');
  if (currentLlmConfig) {
    document.getElementById('llmProviderSelect').value = currentLlmConfig.provider || 'none';
    document.getElementById('llmModelName').value      = currentLlmConfig.model_name || '';
    document.getElementById('llmBaseUrl').value        = currentLlmConfig.base_url   || '';
    const preview = document.getElementById('apiKeyPreviewNote');
    if (currentLlmConfig.provider === 'openai' && currentLlmConfig.openai_key_preview) {
      preview.innerText = `Current: ${currentLlmConfig.openai_key_preview}`;
    } else if (currentLlmConfig.provider === 'gemini' && currentLlmConfig.gemini_key_preview) {
      preview.innerText = `Current: ${currentLlmConfig.gemini_key_preview}`;
    } else {
      preview.innerText = '';
    }
  }
  onLlmProviderChange();
}

function closeLlmModal() {
  document.getElementById('llmModal').classList.add('hidden');
  const s = document.getElementById('llmTestStatus');
  s.classList.add('hidden');
  s.style.cssText = '';
}

function onLlmProviderChange() {
  const provider    = document.getElementById('llmProviderSelect').value;
  const groupApiKey = document.getElementById('groupApiKey');
  const groupBase   = document.getElementById('groupBaseUrl');
  const modelInp    = document.getElementById('llmModelName');
  const baseInp     = document.getElementById('llmBaseUrl');

  const showKey  = () => { groupApiKey.style.display = 'flex'; groupApiKey.style.flexDirection = 'column'; groupApiKey.style.gap = '6px'; };
  const hideKey  = () => { groupApiKey.style.display = 'none'; };
  const showBase = () => { groupBase.style.display = 'flex'; groupBase.style.flexDirection = 'column'; groupBase.style.gap = '6px'; };
  const hideBase = () => { groupBase.style.display = 'none'; };

  if (provider === 'none') {
    hideKey(); hideBase();
    modelInp.value = 'none';
  } else if (provider === 'openai') {
    showKey(); hideBase();
    if (!modelInp.value || ['none','llama3','gemini-1.5-flash'].includes(modelInp.value))
      modelInp.value = 'gpt-4o-mini';
  } else if (provider === 'gemini') {
    showKey(); hideBase();
    if (!modelInp.value || ['none','gpt-4o-mini','llama3'].includes(modelInp.value))
      modelInp.value = 'gemini-1.5-flash';
  } else if (provider === 'ollama') {
    hideKey(); showBase();
    if (!baseInp.value) baseInp.value = 'http://localhost:11434/v1';
    if (!modelInp.value || modelInp.value === 'none') modelInp.value = 'llama3';
  } else if (provider === 'groq') {
    showKey(); showBase();
    if (!baseInp.value) baseInp.value = 'https://api.groq.com/openai/v1';
    if (!modelInp.value || modelInp.value === 'none') modelInp.value = 'llama-3.1-8b-instant';
  } else {
    showKey(); showBase();
  }
}

async function testLlmConnection() {
  const statusDiv = document.getElementById('llmTestStatus');
  const btn       = document.getElementById('btnTestLlm');

  btn.disabled  = true;
  btn.innerText = 'Testing…';
  statusDiv.classList.remove('hidden');
  statusDiv.style.cssText = 'display:block;background:var(--surface-2);color:var(--text-2);border:1px solid var(--border);padding:10px 12px;border-radius:6px;font-size:12px;line-height:1.5;';
  statusDiv.innerText = 'Sending test ping…';

  try {
    const res  = await fetch('/api/test_llm', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      statusDiv.style.cssText += 'background:rgba(48,209,88,0.1);color:var(--green);border-color:rgba(48,209,88,0.25);';
      statusDiv.innerHTML = `<strong>✓ Connected</strong> (${data.latency_ms}ms)<br><span style="opacity:.8;font-size:11px;">"${escapeHtml(data.reply)}"</span>`;
      showToast('Connection verified!');
    } else {
      statusDiv.style.cssText += 'background:rgba(255,69,58,0.1);color:var(--red);border-color:rgba(255,69,58,0.25);';
      statusDiv.innerHTML = `<strong>✗ Failed:</strong> ${escapeHtml(data.error || 'Unknown error')}`;
    }
  } catch (err) {
    statusDiv.style.cssText += 'background:rgba(255,69,58,0.1);color:var(--red);border-color:rgba(255,69,58,0.25);';
    statusDiv.innerHTML = `<strong>✗ Error:</strong> ${escapeHtml(err.message)}`;
  } finally {
    btn.disabled  = false;
    btn.innerText = 'Test Connection';
  }
}

async function saveLlmSettings() {
  const provider  = document.getElementById('llmProviderSelect').value;
  const apiKey    = document.getElementById('llmApiKey').value.trim();
  const modelName = document.getElementById('llmModelName').value.trim();
  const baseUrl   = document.getElementById('llmBaseUrl').value.trim();

  try {
    const res = await fetch('/api/llm_config', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        provider,
        model_name: modelName || null,
        api_key:    apiKey    || null,
        base_url:   baseUrl   || null,
        use_llm:    provider !== 'none'
      })
    });
    if (res.ok) {
      const data = await res.json();
      currentLlmConfig = data.config;
      updateEngineChip(currentLlmConfig);
      closeLlmModal();
      showToast('Settings saved');
    } else {
      showToast('Failed to save settings');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

// ─────────────────────────────────────────────
// Toast notification
// ─────────────────────────────────────────────
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// ─────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────
function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#039;');
}
