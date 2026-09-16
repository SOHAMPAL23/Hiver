/**
 * AppleSupport AI Customer Support Agent & Verification Suite
 * Frontend Logic & Real-time Evaluation Runner
 */

// State Management
let allGoldenSamples = [];
let filteredGoldenSamples = [];
let lastInquiryResult = null;
let currentSelectedGolden = null;

const SCENARIOS = {
  battery_drain: "My iPhone 7 battery drops from 100% to 20% in two hours after updating to iOS 11",
  swollen_battery: "My battery is swollen and pushing the screen up, device is burning hot",
  hacked_account: "Someone hacked my Apple ID and changed my recovery email and password",
  broken_screen: "Dropped phone on concrete and front glass is shattered into pieces",
  airpods_audio: "AirPods keep dropping Bluetooth connection on my MacBook Pro",
  subscription_refund: "I was billed twice for an App Store subscription and need a refund",
  ambiguous_text: "phone broken thing help"
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  initHealthCheck();
  initLlmConfig();
  initComposer();
  loadGoldenDataset();
  
  // Set default initial scenario for instant exploration
  loadScenario('battery_drain');
});

// Tab Switching
function switchTab(tabName) {
  const btnConsole = document.getElementById("tabBtnConsole");
  const btnVerif = document.getElementById("tabBtnVerification");
  const panelConsole = document.getElementById("panelConsole");
  const panelVerif = document.getElementById("panelVerification");

  if (tabName === "console") {
    btnConsole.classList.add("active");
    btnConsole.setAttribute("aria-selected", "true");
    btnVerif.classList.remove("active");
    btnVerif.setAttribute("aria-selected", "false");
    panelConsole.classList.add("active");
    panelVerif.classList.remove("active");
  } else {
    btnVerif.classList.add("active");
    btnVerif.setAttribute("aria-selected", "true");
    btnConsole.classList.remove("active");
    btnConsole.setAttribute("aria-selected", "false");
    panelVerif.classList.add("active");
    panelConsole.classList.remove("active");
  }
}

// Health Check & Telemetry
async function initHealthCheck() {
  const startTime = performance.now();
  try {
    const res = await fetch("/health");
    const latency = Math.round(performance.now() - startTime);
    if (res.ok) {
      const data = await res.json();
      document.getElementById("systemHealthText").innerText = "Agent Ready & Grounded";
      document.getElementById("apiLatencyBadge").innerText = `${latency} ms`;
      document.getElementById("telServerStatus").innerText = `Online (${data.status.toUpperCase()})`;
      document.getElementById("telServerLatency").innerText = `Latency: ${latency}ms • Port 8000`;
    }
  } catch (err) {
    document.getElementById("systemHealthText").innerText = "Backend Offline";
    document.getElementById("systemHealthBadge").style.background = "rgba(255, 69, 58, 0.15)";
    document.getElementById("systemHealthBadge").style.color = "#ff453a";
    document.getElementById("apiLatencyBadge").innerText = "Timeout";
  }
}

// Composer Logic
function initComposer() {
  const textarea = document.getElementById("customerQuery");
  const charCount = document.getElementById("charCount");

  textarea.addEventListener("input", () => {
    charCount.innerText = `${textarea.value.length} chars`;
  });

  textarea.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      submitLiveInquiry();
    }
  });
}

function loadScenario(scenarioKey) {
  const text = SCENARIOS[scenarioKey];
  if (text) {
    const textarea = document.getElementById("customerQuery");
    textarea.value = text;
    document.getElementById("charCount").innerText = `${text.length} chars`;
    submitLiveInquiry();
  }
}

function clearComposer() {
  const textarea = document.getElementById("customerQuery");
  textarea.value = "";
  document.getElementById("charCount").innerText = "0 chars";
  textarea.focus();
}

// Live Inquiry Submission & Pipeline Rendering
async function submitLiveInquiry() {
  const query = document.getElementById("customerQuery").value.trim();
  if (!query) {
    showToast("Please enter a customer query or pick a scenario.");
    return;
  }

  const btn = document.getElementById("btnSubmitQuery");
  const btnLabel = document.getElementById("btnSubmitLabel");
  const btnIcon = document.getElementById("btnSubmitIcon");
  
  btn.disabled = true;
  btnLabel.innerText = "Generating Resolution...";
  btnIcon.innerText = "⏳";

  const startTime = performance.now();

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: query })
    });

    const latency = Math.round(performance.now() - startTime);
    document.getElementById("apiLatencyBadge").innerText = `${latency} ms`;

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    lastInquiryResult = data;
    lastInquiryResult.query = query;
    lastInquiryResult.latency_ms = latency;

    renderPipelineResults(data);
  } catch (err) {
    document.getElementById("draftReplyText").innerText = `Inference Error: ${err.message}. Please ensure backend is running.`;
    showToast(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btnLabel.innerText = "Generate Resolution";
    btnIcon.innerText = "✨";
  }
}

function renderPipelineResults(data) {
  // Friendly Intent Mapping
  const friendlyNames = {
    battery_power_charging: "🔋 Battery & Power",
    software_update_os_bug: "⚙️ OS & Software Update",
    account_apple_id_icloud: "🚨 Apple ID & Security",
    hardware_physical_damage: "📱 Hardware Damage",
    connectivity_network_bluetooth: "📶 Wi-Fi & Network",
    billing_subscriptions_appstore: "💳 Billing & Subscriptions",
    device_performance_storage: "⚡ Storage & Performance",
    general_feedback_complaint: "💬 Customer Feedback"
  };

  // 1. Intent Badge & Confidence
  const intentBadge = document.getElementById("intentBadge");
  if (intentBadge) {
    intentBadge.style.display = "inline-flex";
    intentBadge.innerText = friendlyNames[data.intent] || data.intent;
  }
  
  const confPct = (data.intent_confidence * 100).toFixed(1);
  const confText = document.getElementById("intentConfidenceText");
  if (confText) confText.innerText = `${confPct}%`;
  
  const confBar = document.getElementById("intentConfidenceBar");
  if (confBar) {
    confBar.style.width = `${confPct}%`;
    if (data.intent_confidence > 0.70) {
      confBar.className = "bar-fill fill-green";
    } else if (data.intent_confidence > 0.50) {
      confBar.className = "bar-fill";
    } else {
      confBar.className = "bar-fill fill-red";
    }
  }

  // 2. Policy & Guardrails
  const policyBadge = document.getElementById("policyBadge");
  const policyDesc = document.getElementById("policyReasonDesc");

  if (policyBadge) {
    policyBadge.style.display = "inline-flex";
    if (data.decision === "ESCALATE") {
      policyBadge.className = "badge badge-escalate";
      policyBadge.innerText = "▲ ESCALATE TO GENIUS BAR";
    } else {
      policyBadge.className = "badge badge-auto";
      policyBadge.innerText = "● AUTO-HANDLED";
    }
  }

  if (policyDesc) {
    policyDesc.innerText = data.escalation_reason || "Routine high-confidence self-help diagnostic.";
  }

  // 3. Draft Reply & Model Attribution
  const replyBox = document.getElementById("draftReplyText");
  replyBox.innerText = data.reply;
  const replyCharCount = document.getElementById("replyCharCount");
  if (replyCharCount) replyCharCount.innerText = `${data.reply.length} chars`;

  const modelBadge = document.getElementById("replyModelBadge");
  if (modelBadge && data.generation_model) {
    modelBadge.innerText = data.generation_model;
    if (data.generation_model.includes("OPENAI") || data.generation_model.includes("GEMINI") || data.generation_model.includes("OLLAMA") || data.generation_model.includes("GROQ")) {
      modelBadge.style.background = "rgba(48, 209, 88, 0.15)";
      modelBadge.style.color = "var(--apple-green)";
      modelBadge.style.border = "1px solid var(--apple-green-border)";
    } else {
      modelBadge.style.background = "rgba(41, 151, 255, 0.12)";
      modelBadge.style.color = "var(--apple-blue)";
      modelBadge.style.border = "1px solid rgba(41, 151, 255, 0.25)";
    }
  }

  // 4. Stage 4: Historical Evidence
  const evContainer = document.getElementById("evidenceListContainer");
  evContainer.innerHTML = "";

  if (data.evidence && data.evidence.length > 0) {
    data.evidence.forEach((ev, idx) => {
      const simPct = (ev.similarity * 100).toFixed(1);
      const card = document.createElement("div");
      card.className = "evidence-card";
      card.innerHTML = `
        <div class="evidence-header">
          <span style="font-weight: 600; font-size: 12px; color: var(--text-muted);">Historical Resolution #${idx + 1}</span>
          <span class="ev-similarity-pill">${simPct}% Match</span>
        </div>
        <div class="ev-cust-msg">"${escapeHtml(ev.customer_message)}"</div>
        <div class="ev-brand-reply"><strong>@AppleSupport:</strong> "${escapeHtml(ev.historical_response)}"</div>
      `;
      evContainer.appendChild(card);
    });
  } else {
    evContainer.innerHTML = `<div style="font-size: 13px; color: var(--text-muted); padding: 12px 0;">No historical matches retrieved.</div>`;
  }
}

// Copy & Export
function copyDraftReply() {
  const replyText = document.getElementById("draftReplyText").innerText;
  if (!replyText || replyText.startsWith("Enter an inquiry")) {
    showToast("No reply generated yet.");
    return;
  }
  navigator.clipboard.writeText(replyText).then(() => {
    showToast("Draft reply copied to clipboard!");
  }).catch(() => {
    showToast("Failed to copy to clipboard.");
  });
}

function exportDiagnosticJson() {
  if (!lastInquiryResult) {
    showToast("Please run an inquiry analysis first.");
    return;
  }
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastInquiryResult, null, 2));
  const dlAnchor = document.createElement("a");
  dlAnchor.setAttribute("href", dataStr);
  dlAnchor.setAttribute("download", `applesupport_trace_${Date.now()}.json`);
  dlAnchor.click();
  showToast("Diagnostic trace exported!");
}

// ==========================================================================
// Tab 2: Automated Verification Suite ("How We Know It's Working")
// ==========================================================================

async function runVerificationSuite() {
  const btn = document.getElementById("btnRunTests");
  const progressContainer = document.getElementById("testProgressContainer");
  const progressBar = document.getElementById("testProgressBar");
  const progressLabel = document.getElementById("testProgressLabel");
  const progressPercent = document.getElementById("testProgressPercent");
  const tableBody = document.getElementById("testsTableBody");

  btn.disabled = true;
  progressContainer.style.display = "block";
  progressBar.style.width = "20%";
  progressLabel.innerText = "Executing automated test suite against live model...";
  progressPercent.innerText = "20%";

  tableBody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 20px;">
        Running 6 acceptance tests: Safety Intercepts, Account Security, Hardware Guardrails, and KB Grounding...
      </td>
    </tr>
  `;

  try {
    const res = await fetch("/api/run_tests", { method: "POST" });
    progressBar.style.width = "80%";
    progressPercent.innerText = "80%";

    if (!res.ok) {
      throw new Error(`Verification runner returned HTTP ${res.status}`);
    }

    const testData = await res.json();
    progressBar.style.width = "100%";
    progressPercent.innerText = "100%";
    progressLabel.innerText = `All ${testData.total_tests} Tests Finished (${testData.passed_tests}/${testData.total_tests} Passed)`;

    renderTestResultsTable(testData.results);
    document.getElementById("testSummaryBadge").innerText = `${testData.passed_tests}/${testData.total_tests} Passed`;

    if (testData.all_passed) {
      showToast("🎉 All 6 Acceptance Tests Passed! System Verified 100% Operational.");
    } else {
      showToast(`⚠️ ${testData.failed_tests} test(s) failed. Check details in the table.`);
    }
  } catch (err) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--apple-red); padding: 20px;">
          Failed to execute verification suite: ${err.message}
        </td>
      </tr>
    `;
    showToast(`Test suite execution failed: ${err.message}`);
  } finally {
    btn.disabled = false;
  }
}

function renderTestResultsTable(results) {
  const tableBody = document.getElementById("testsTableBody");
  tableBody.innerHTML = "";

  results.forEach(t => {
    const tr = document.createElement("tr");
    const statusPill = t.passed 
      ? `<span class="test-status-pill test-pass">✓ PASS</span>`
      : `<span class="test-status-pill test-fail">✗ FAIL</span>`;

    const actualBadge = t.actual_action === "ESCALATE"
      ? `<span class="badge badge-escalate" style="font-size: 10px; padding: 2px 6px;">ESCALATE</span>`
      : `<span class="badge badge-auto" style="font-size: 10px; padding: 2px 6px;">AUTO-HANDLE</span>`;

    tr.innerHTML = `
      <td><strong style="font-family: monospace; color: var(--apple-blue);">${t.id}</strong></td>
      <td>
        <strong style="display: block; color: var(--text-primary);">${escapeHtml(t.name)}</strong>
        <span style="font-size: 11.5px; color: var(--text-muted);">${escapeHtml(t.description)}</span>
      </td>
      <td style="font-size: 12px; color: var(--text-secondary); max-width: 260px;">"${escapeHtml(t.query)}"</td>
      <td><code style="font-size: 11px; background: var(--bg-surface-elevated); padding: 2px 6px; border-radius: 4px;">${t.expected_action}</code></td>
      <td>${actualBadge}</td>
      <td style="font-family: monospace; font-size: 11.5px; color: var(--text-muted);">${t.latency_ms.toFixed(0)} ms</td>
      <td>${statusPill}</td>
    `;
    tableBody.appendChild(tr);
  });
}

// ==========================================================================
// Golden Dataset Ground-Truth Explorer (200 Instances)
// ==========================================================================

async function loadGoldenDataset() {
  try {
    const res = await fetch("/api/golden_samples");
    if (res.ok) {
      allGoldenSamples = await res.json();
      filteredGoldenSamples = [...allGoldenSamples];
      populateGoldenSelect(filteredGoldenSamples);
      document.getElementById("goldenTotalCount").innerText = `${allGoldenSamples.length} Golden Samples Loaded`;
    }
  } catch (e) {
    console.error("Failed to load golden samples", e);
  }
}

function populateGoldenSelect(samples) {
  const sel = document.getElementById("goldenSelect");
  sel.innerHTML = `<option value="">-- Choose a Golden Test Sample (${samples.length} available) --</option>`;
  samples.forEach((s, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.innerText = `[${s.true_intent}] ${s.customer_text.substring(0, 65)}...`;
    sel.appendChild(opt);
  });
}

function filterGoldenSamples() {
  const intentFilter = document.getElementById("filterIntent").value;
  const diffFilter = document.getElementById("filterDifficulty").value;

  filteredGoldenSamples = allGoldenSamples.filter(s => {
    const matchIntent = intentFilter === "ALL" || s.true_intent === intentFilter;
    const matchDiff = diffFilter === "ALL" || s.difficulty === diffFilter;
    return matchIntent && matchDiff;
  });

  populateGoldenSelect(filteredGoldenSamples);
}

function loadRandomGoldenSample() {
  if (filteredGoldenSamples.length === 0) return;
  const randIdx = Math.floor(Math.random() * filteredGoldenSamples.length);
  const sel = document.getElementById("goldenSelect");
  sel.value = randIdx;
  onGoldenSelectChange();
}

async function onGoldenSelectChange() {
  const sel = document.getElementById("goldenSelect");
  const idx = sel.value;
  if (idx === "") {
    document.getElementById("goldenComparisonContainer").style.display = "none";
    return;
  }

  const sample = filteredGoldenSamples[idx];
  currentSelectedGolden = sample;

  // Render Ground Truth
  document.getElementById("gtIntent").innerText = sample.true_intent;
  document.getElementById("gtActionBadge").innerText = sample.true_action;
  document.getElementById("gtCustomerText").innerText = `"${sample.customer_text}"`;
  document.getElementById("gtBrandReply").innerText = `"${sample.historical_brand_reply}"`;
  document.getElementById("goldDifficultyBadge").innerText = sample.difficulty ? sample.difficulty.toUpperCase() : "NORMAL";

  // Show container with loading state for agent prediction
  const container = document.getElementById("goldenComparisonContainer");
  container.style.display = "block";
  document.getElementById("predGoldIntent").innerText = "Evaluating query with live model...";
  document.getElementById("predGoldReason").innerText = "...";
  document.getElementById("predGoldReply").innerText = "...";

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: sample.customer_text })
    });
    const pred = await res.json();

    document.getElementById("predGoldIntent").innerText = `${pred.intent} (${(pred.intent_confidence * 100).toFixed(1)}%)`;
    document.getElementById("predGoldActionBadge").innerText = pred.decision;
    document.getElementById("predGoldReason").innerText = pred.escalation_reason || "Routine Auto-Handle";
    document.getElementById("predGoldReply").innerText = `"${pred.reply}"`;

    const matchBadge = document.getElementById("evalMatchBadge");
    const isIntentMatch = pred.intent === sample.true_intent;
    const isActionMatch = (pred.decision.toLowerCase() === sample.true_action.toLowerCase());

    if (isIntentMatch && isActionMatch) {
      matchBadge.innerText = "✓ PERFECT MATCH (Intent & Action)";
      matchBadge.style.background = "var(--apple-green-bg)";
      matchBadge.style.color = "var(--apple-green)";
      matchBadge.style.border = "1px solid var(--apple-green-border)";
    } else if (isActionMatch) {
      matchBadge.innerText = "✓ ACTION MATCH (Policy Compliant)";
      matchBadge.style.background = "rgba(41, 151, 255, 0.15)";
      matchBadge.style.color = "var(--apple-blue)";
      matchBadge.style.border = "1px solid rgba(41, 151, 255, 0.3)";
    } else {
      matchBadge.innerText = "⚠ DISCREPANCY (Requires Review)";
      matchBadge.style.background = "rgba(255, 159, 10, 0.15)";
      matchBadge.style.color = "var(--apple-orange)";
      matchBadge.style.border = "1px solid rgba(255, 159, 10, 0.3)";
    }
  } catch (err) {
    document.getElementById("predGoldIntent").innerText = "Evaluation error: " + err.message;
  }
}

function transferGoldenToConsole() {
  if (!currentSelectedGolden) return;
  switchTab("console");
  const textarea = document.getElementById("customerQuery");
  textarea.value = currentSelectedGolden.customer_text;
  document.getElementById("charCount").innerText = `${currentSelectedGolden.customer_text.length} chars`;
  submitLiveInquiry();
}

// Utility: Toast Notification
function showToast(msg) {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toastMessage");
  toastMsg.innerText = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// Utility: HTML Escaping
function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================================================
// LLM Provider Configuration & Modal Logic
// ==========================================================================

let currentLlmConfig = null;

async function initLlmConfig() {
  try {
    const res = await fetch("/api/llm_config");
    if (res.ok) {
      currentLlmConfig = await res.json();
      updateHeaderLlmBadge(currentLlmConfig);
    }
  } catch (err) {
    console.warn("Failed to fetch initial LLM configuration", err);
  }
}

function updateHeaderLlmBadge(cfg) {
  const icon = document.getElementById("headerLlmIcon");
  const label = document.getElementById("headerLlmLabel");
  if (!icon || !label) return;

  if (cfg.use_llm && cfg.provider !== "none") {
    icon.innerText = "🤖";
    label.innerText = `LLM: ${cfg.model_name || cfg.provider.toUpperCase()}`;
    label.style.color = "var(--apple-green)";
  } else {
    icon.innerText = "⚡";
    label.innerText = "Diagnostic Engine";
    label.style.color = "var(--text-primary)";
  }
}

function openLlmModal() {
  const modal = document.getElementById("llmModal");
  modal.style.display = "flex";
  
  if (currentLlmConfig) {
    document.getElementById("llmProviderSelect").value = currentLlmConfig.provider || "none";
    document.getElementById("llmModelName").value = currentLlmConfig.model_name || "";
    document.getElementById("llmBaseUrl").value = currentLlmConfig.base_url || "";
    
    const preview = document.getElementById("apiKeyPreviewNote");
    if (currentLlmConfig.provider === "openai" && currentLlmConfig.openai_key_preview) {
      preview.innerText = `Current key: ${currentLlmConfig.openai_key_preview}`;
    } else if (currentLlmConfig.provider === "gemini" && currentLlmConfig.gemini_key_preview) {
      preview.innerText = `Current key: ${currentLlmConfig.gemini_key_preview}`;
    } else {
      preview.innerText = "";
    }
  }
  
  onLlmProviderChange();
}

function closeLlmModal() {
  document.getElementById("llmModal").style.display = "none";
  document.getElementById("llmTestStatus").style.display = "none";
}

function onLlmProviderChange() {
  const provider = document.getElementById("llmProviderSelect").value;
  const groupApiKey = document.getElementById("groupApiKey");
  const groupBaseUrl = document.getElementById("groupBaseUrl");
  const modelInput = document.getElementById("llmModelName");
  const baseUrlInput = document.getElementById("llmBaseUrl");

  if (provider === "none") {
    groupApiKey.style.display = "none";
    groupBaseUrl.style.display = "none";
    modelInput.placeholder = "Built-in Rule Engine";
    modelInput.value = "none";
  } else if (provider === "openai") {
    groupApiKey.style.display = "block";
    groupBaseUrl.style.display = "none";
    if (!modelInput.value || modelInput.value === "none" || modelInput.value === "gemini-1.5-flash" || modelInput.value === "llama3") {
      modelInput.value = "gpt-4o-mini";
    }
  } else if (provider === "gemini") {
    groupApiKey.style.display = "block";
    groupBaseUrl.style.display = "none";
    if (!modelInput.value || modelInput.value === "none" || modelInput.value === "gpt-4o-mini" || modelInput.value === "llama3") {
      modelInput.value = "gemini-1.5-flash";
    }
  } else if (provider === "ollama") {
    groupApiKey.style.display = "none";
    groupBaseUrl.style.display = "block";
    baseUrlInput.placeholder = "http://localhost:11434/v1";
    if (!baseUrlInput.value) baseUrlInput.value = "http://localhost:11434/v1";
    if (!modelInput.value || modelInput.value === "none" || modelInput.value.includes("gpt") || modelInput.value.includes("gemini")) {
      modelInput.value = "llama3";
    }
  } else if (provider === "groq") {
    groupApiKey.style.display = "block";
    groupBaseUrl.style.display = "block";
    baseUrlInput.placeholder = "https://api.groq.com/openai/v1";
    if (!baseUrlInput.value) baseUrlInput.value = "https://api.groq.com/openai/v1";
    if (!modelInput.value || modelInput.value === "none") {
      modelInput.value = "llama-3.1-8b-instant";
    }
  } else { // custom
    groupApiKey.style.display = "block";
    groupBaseUrl.style.display = "block";
  }
}

async function testLlmConnection() {
  const statusDiv = document.getElementById("llmTestStatus");
  const btn = document.getElementById("btnTestLlm");

  btn.disabled = true;
  btn.innerText = "⏳ Testing...";
  statusDiv.style.display = "block";
  statusDiv.style.background = "rgba(255, 255, 255, 0.05)";
  statusDiv.style.color = "var(--text-secondary)";
  statusDiv.style.border = "1px solid var(--border-subtle)";
  statusDiv.innerText = "Sending test ping to configured provider...";

  try {
    const res = await fetch("/api/test_llm", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      statusDiv.style.background = "rgba(48, 209, 88, 0.15)";
      statusDiv.style.color = "var(--apple-green)";
      statusDiv.style.border = "1px solid var(--apple-green-border)";
      statusDiv.innerHTML = `<strong>✓ Connection Successful!</strong> (${data.latency_ms}ms)<br/><span style="font-size: 11px; opacity: 0.9;">"${escapeHtml(data.reply)}"</span>`;
      showToast("LLM Connection Verified!");
    } else {
      statusDiv.style.background = "rgba(255, 69, 58, 0.15)";
      statusDiv.style.color = "var(--apple-red)";
      statusDiv.style.border = "1px solid rgba(255, 69, 58, 0.3)";
      statusDiv.innerHTML = `<strong>✗ Connection Failed:</strong> ${escapeHtml(data.error || "Unknown error")}`;
    }
  } catch (err) {
    statusDiv.style.background = "rgba(255, 69, 58, 0.15)";
    statusDiv.style.color = "var(--apple-red)";
    statusDiv.style.border = "1px solid rgba(255, 69, 58, 0.3)";
    statusDiv.innerHTML = `<strong>✗ Request Error:</strong> ${escapeHtml(err.message)}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>🔌</span> Test Connection`;
  }
}

async function saveLlmSettings() {
  const provider = document.getElementById("llmProviderSelect").value;
  const apiKey = document.getElementById("llmApiKey").value.trim();
  const modelName = document.getElementById("llmModelName").value.trim();
  const baseUrl = document.getElementById("llmBaseUrl").value.trim();

  const payload = {
    provider: provider,
    model_name: modelName || null,
    api_key: apiKey || null,
    base_url: baseUrl || null,
    use_llm: provider !== "none"
  };

  try {
    const res = await fetch("/api/llm_config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const respData = await res.json();
      currentLlmConfig = respData.config;
      updateHeaderLlmBadge(currentLlmConfig);
      closeLlmModal();
      showToast(`LLM Configuration Saved: ${currentLlmConfig.provider.toUpperCase()} (${currentLlmConfig.model_name})`);
    } else {
      showToast("Failed to save LLM configuration");
    }
  } catch (err) {
    showToast(`Error saving settings: ${err.message}`);
  }
}
