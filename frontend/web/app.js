const state = {
  mock: null,
  benchmark: null,
  evidence: {
    metadata: null,
    result: null,
    latency: null,
    frameSources: null,
    events: [],
    robotLog: "",
    summary: "",
  },
  ui: {
    activeFeedId: "",
    submissions: [],
  },
};

const componentDescriptions = {
  "robot-control-log": "Robot arm execution trail",
  "dual-camera-frame-sources": "Dual-camera source manifest",
  "policy-gate-decision": "Policy and confirmation outcome",
  "checkpoint-record": "Pre/post execution checkpoints",
  "redis-record": "Session recovery context export",
  "latency-record": "Decision and execution timing",
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function repoUrl(path) {
  return `../../${path.replace(/^\.?\/*/, "")}`;
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return response.json();
}

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return response.text();
}

function pill(label, variant = "") {
  return `<span class="pill ${variant}">${escapeHtml(label)}</span>`;
}

function queueStateVariant(queueItem) {
  if (queueItem.state === "completed") {
    return "ok";
  }
  if (queueItem.state === "awaiting_confirm" || queueItem.risk_level === "confirm") {
    return "warn";
  }
  if (queueItem.risk_level === "dangerous" || queueItem.state === "blocked-by-policy") {
    return "danger";
  }
  return "";
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function currentTask() {
  return state.mock.current_task;
}

function activeFeed() {
  return state.mock.camera_feeds.find((feed) => feed.id === state.ui.activeFeedId) ?? state.mock.camera_feeds[0];
}

function scenarioProfile(scenarioId) {
  return state.mock.scenario_defaults[scenarioId] ?? state.mock.scenario_defaults["demo-real-risk-slice"];
}

function benchmarkScenarioIds() {
  return Object.keys(state.benchmark?.scenarios ?? {});
}

function requiredComponents() {
  return state.benchmark?.scenarios?.[state.mock.evidence_bundle.scenario_id]?.required_real_components ?? [];
}

function baseScenarioOutcomes() {
  const realRisk = state.benchmark?.scenarios?.[state.mock.evidence_bundle.scenario_id];
  const baseScenarioId = realRisk?.base_scenario;
  return state.benchmark?.scenarios?.[baseScenarioId]?.required_outcomes ?? [];
}

function fileCoverage(componentId) {
  const componentMap = state.mock.evidence_bundle.component_map[componentId] ?? [];
  const fileSet = new Set(state.mock.evidence_bundle.files);
  return {
    files: componentMap,
    present: componentMap.length > 0 && componentMap.every((path) => fileSet.has(path)),
  };
}

function formatTimestamp(value) {
  if (!value) {
    return "n/a";
  }
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function renderSummary() {
  const task = currentTask();
  const summaryPills = document.getElementById("summary-pills");
  const evidencePassed = Boolean(state.evidence.result?.passed);
  summaryPills.innerHTML = [
    pill(`Scenario: ${task.scenario_id}`),
    pill(`Task: ${task.task_state}`, task.task_state === "completed" ? "ok" : "warn"),
    pill(`Safety prompt: ${state.mock.safety_prompt.visible ? "visible" : "hidden"}`, state.mock.safety_prompt.visible ? "ok" : "warn"),
    pill(`Active camera: ${activeFeed().label}`),
    pill(`Evidence: ${evidencePassed ? "pass" : "review"}`, evidencePassed ? "ok" : "warn"),
  ].join("");

  document.getElementById("summary-grid").innerHTML = [
    ["Current session", task.session_id],
    ["Current task", task.task_id],
    ["Route / risk", `${task.route_decision} / ${task.risk_level}`],
    ["Last checkpoint", task.last_safe_checkpoint_id],
  ]
    .map(
      ([label, value]) => `
        <div class="summary-card">
          <span class="muted">${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `
    )
    .join("");
}

function renderScenarioPanel() {
  const scenarioId = document.getElementById("scenario-select").value;
  const benchmarkScenario = state.benchmark?.scenarios?.[scenarioId];
  const profile = scenarioProfile(scenarioId);
  const details = [];

  if (benchmarkScenario?.required_outcomes) {
    details.push(`<div><strong>M2 required outcomes</strong><ul>${benchmarkScenario.required_outcomes.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`);
  }
  if (benchmarkScenario?.required_real_components) {
    details.push(`<div><strong>Required real components</strong><ul>${benchmarkScenario.required_real_components.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`);
  }
  if (benchmarkScenario?.pass_rule) {
    details.push(`<div><strong>Pass rule</strong><p>${escapeHtml(benchmarkScenario.pass_rule)}</p></div>`);
  }
  if (profile.pending_confirmation_prompt) {
    details.push(`<div><strong>Confirmation path</strong><p>${escapeHtml(profile.pending_confirmation_prompt)}</p></div>`);
  }

  document.getElementById("scenario-panel").innerHTML = `
    <div class="layout-stack">
      <div class="pill-row">
        ${pill(`route: ${profile.route_decision}`)}
        ${pill(`risk: ${profile.risk_level}`, profile.risk_level === "dangerous" ? "danger" : profile.risk_level === "confirm" ? "warn" : "ok")}
        ${pill(`confirmation: ${profile.confirmation_state}`, profile.confirmation_state === "completed" ? "ok" : "warn")}
      </div>
      ${details.join("")}
    </div>
  `;
}

function renderTaskQueue() {
  const container = document.getElementById("task-queue");
  container.innerHTML = state.ui.submissions
    .map(
      (queueItem) => `
        <div class="queue-card">
          <strong>${escapeHtml(queueItem.task_id)}</strong>
          <span>${pill(queueItem.state, queueStateVariant(queueItem))}</span>
          <span class="muted">${escapeHtml(queueItem.scenario_id)} · ${escapeHtml(queueItem.owner ?? "operator-console")}</span>
          <code>${escapeHtml(queueItem.submitted_at)}</code>
        </div>
      `
    )
    .join("");
}

function renderTaskState() {
  const task = currentTask();
  document.getElementById("task-state").innerHTML = [
    ["submitted_at", formatTimestamp(task.submitted_at)],
    ["turn_id", task.turn_id],
    ["correlation_id", task.correlation_id],
    ["execution_state", task.execution_state],
    ["confirmation_state", task.confirmation_state],
    ["last_completed_step", task.last_completed_step],
    ["models", Object.values(task.active_model_ids).join(", ")],
  ]
    .map(([label, value]) => `<div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(value)}</span></div>`)
    .join("");

  document.getElementById("latency").innerHTML = [
    ["Decision latency", `${task.latency.decision_latency_ms} ms`],
    ["Execution latency", `${task.latency.exec_latency_ms} ms`],
    ["Threshold", task.latency.within_threshold ? "within 10s gate" : "outside gate"],
  ]
    .map(
      ([label, value]) => `
        <div class="metric-card">
          <span class="muted">${escapeHtml(label)}</span>
          <span>${escapeHtml(value)}</span>
        </div>
      `
    )
    .join("");
}

function renderSafetyPrompt() {
  const task = currentTask();
  const promptBody = task.pending_confirmation_prompt || state.mock.safety_prompt.body;
  document.getElementById("safety-prompt").innerHTML = `
    <div class="pill-row">
      ${pill(`Visibility: ${state.mock.safety_prompt.visible ? "operator-visible" : "hidden"}`, state.mock.safety_prompt.visible ? "ok" : "warn")}
      ${pill(`Prompt state: ${task.confirmation_state}`, task.confirmation_state === "completed" ? "ok" : task.confirmation_state === "awaiting_confirm" ? "warn" : "")}
    </div>
    <div>
      <strong>${escapeHtml(state.mock.safety_prompt.summary)}</strong>
      <p class="muted">${escapeHtml(state.mock.safety_prompt.visibility_note)}</p>
    </div>
    <pre>${escapeHtml(promptBody)}</pre>
  `;
}

function cameraCommand(feed) {
  return [
    `ffplay -fflags nobuffer -flags low_delay ${feed.stream_url}`,
    `curl -s ${feed.snapshot_url} > latest-${feed.id}.jpg`,
  ].join("\n");
}

function renderCameraShell() {
  const active = activeFeed();
  document.getElementById("camera-tabs").innerHTML = state.mock.camera_feeds
    .map(
      (feed) => `
        <button
          type="button"
          data-feed-id="${escapeHtml(feed.id)}"
          class="${feed.id === active.id ? "is-active" : "secondary"}"
        >
          ${escapeHtml(feed.label)}
        </button>
      `
    )
    .join("");

  document.getElementById("camera-main").innerHTML = `
    <div class="layout-stack">
      <div>
        <strong>${escapeHtml(active.label)}</strong>
        <p class="muted">${escapeHtml(state.mock.camera_shell.switch_hint)}</p>
      </div>
      <div class="pill-row">
        ${pill(`status: ${active.status}`, active.status === "live-path-ready" ? "ok" : "warn")}
        ${pill(`device: ${active.device_path}`)}
        ${pill(`profile: ${active.capture_profile}`)}
      </div>
      <div class="kv">
        <div><strong>Stream path</strong><code>${escapeHtml(active.stream_url)}</code></div>
        <div><strong>WebSocket path</strong><code>${escapeHtml(active.websocket_url)}</code></div>
        <div><strong>Snapshot path</strong><code>${escapeHtml(active.snapshot_url)}</code></div>
      </div>
      <pre>${escapeHtml(cameraCommand(active))}</pre>
    </div>
  `;

  document.getElementById("camera-grid").innerHTML = state.mock.camera_feeds
    .map(
      (feed) => `
        <div class="camera-card ${feed.id === active.id ? "is-active" : ""}">
          <strong>${escapeHtml(feed.label)}</strong>
          <div class="camera-meta">
            <span class="muted">${escapeHtml(feed.mount)}</span>
            <code>${escapeHtml(feed.device_path)}</code>
            <span>${escapeHtml(feed.placeholder)}</span>
          </div>
        </div>
      `
    )
    .join("");

  document.querySelectorAll("#camera-tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      state.ui.activeFeedId = button.dataset.feedId;
      renderSummary();
      renderCameraShell();
    });
  });
}

function renderLogs() {
  document.getElementById("event-list").innerHTML = state.evidence.events
    .slice(0, 8)
    .map(
      (event) => `
        <div class="event-item">
          <strong>${escapeHtml(event.module)} · ${escapeHtml(event.event)}</strong>
          <span class="muted">${escapeHtml(formatTimestamp(event.timestamp))}</span>
          <span>${escapeHtml(event.state ?? "n/a")}</span>
          <code>${escapeHtml(JSON.stringify(event.payload ?? {}))}</code>
        </div>
      `
    )
    .join("");

  const robotTail = state.evidence.robotLog.trim() || state.mock.logs.robot_log_tail.join("\n");
  document.getElementById("robot-log").textContent = robotTail;
}

function renderEvidence() {
  const evidence = state.mock.evidence_bundle;
  const metadata = state.evidence.metadata;
  const result = state.evidence.result;
  const benchmarkVersion = state.benchmark?.version ?? "unavailable";

  document.getElementById("evidence-badges").innerHTML = [
    pill(`Benchmark: ${benchmarkVersion}`),
    pill(`Bundle: ${evidence.run_id}`),
    pill(`Scenario: ${evidence.scenario_id}`),
    pill(`Passed: ${result?.passed ? "yes" : "review"}`, result?.passed ? "ok" : "warn"),
  ].join("");

  document.getElementById("evidence-summary").innerHTML = `
    <div class="kv">
      <div><strong>Bundle path</strong><code>${escapeHtml(evidence.path)}</code></div>
      <div><strong>Benchmark path</strong><code>${escapeHtml(evidence.benchmark_path)}</code></div>
      <div><strong>Operator</strong><span>${escapeHtml(metadata?.operator ?? "n/a")}</span></div>
      <div><strong>Created at</strong><span>${escapeHtml(formatTimestamp(metadata?.created_at))}</span></div>
      <div><strong>Degradations</strong><span>${escapeHtml((result?.degradations ?? []).join(", ") || "none")}</span></div>
    </div>
    <div class="footnote muted">${escapeHtml(evidence.m2_focus)}</div>
  `;

  const coverageItems = requiredComponents().map((componentId) => {
    const coverage = fileCoverage(componentId);
    return `
      <div class="checklist-item">
        <strong>${escapeHtml(componentId)}</strong>
        <span>${pill(coverage.present ? "present" : "missing", coverage.present ? "ok" : "warn")}</span>
        <span class="muted">${escapeHtml(componentDescriptions[componentId] ?? "Required artifact")}</span>
        <code>${escapeHtml(coverage.files.join(", ") || "no mapped files")}</code>
      </div>
    `;
  });

  const baseOutcomes = baseScenarioOutcomes();
  if (baseOutcomes.length > 0) {
    coverageItems.push(`
      <div class="checklist-item">
        <strong>M2 base-scenario outcomes</strong>
        <ul>${baseOutcomes.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
    `);
  }
  document.getElementById("evidence-checklist").innerHTML = coverageItems.join("");

  document.getElementById("evidence-files").innerHTML = evidence.files
    .map(
      (filePath) => `
        <div class="file-card">
          <strong>${escapeHtml(filePath)}</strong>
          <code>${escapeHtml(`${evidence.path}/${filePath}`)}</code>
        </div>
      `
    )
    .join("");
}

function renderAll() {
  renderSummary();
  renderScenarioPanel();
  renderTaskQueue();
  renderTaskState();
  renderSafetyPrompt();
  renderCameraShell();
  renderLogs();
  renderEvidence();
}

function fillSubmissionDefaults() {
  const defaults = state.mock.task_submission;
  document.getElementById("scenario-select").value = defaults.default_scenario_id;
  document.getElementById("run-id-input").value = defaults.default_run_id;
  document.getElementById("task-input").value = defaults.default_input_text;
  document.getElementById("submission-status").textContent = defaults.help_text;
  renderScenarioPanel();
}

function nextTaskState(profile) {
  if (profile.confirmation_state === "awaiting_confirm") {
    return {
      task_state: "awaiting_confirm",
      execution_state: "blocked-by-policy",
      last_completed_step: "policy-gate-held",
    };
  }
  if (profile.confirmation_state === "resumed") {
    return {
      task_state: "resumed",
      execution_state: "resumed-from-checkpoint",
      last_completed_step: "context-restored",
    };
  }
  return {
    task_state: "submitted",
    execution_state: "submitted",
    last_completed_step: "task-submitted",
  };
}

function createSubmissionRecord({ scenarioId, runId, inputText }) {
  const profile = scenarioProfile(scenarioId);
  const now = new Date().toISOString();
  const taskState = nextTaskState(profile);
  return {
    session_id: `session-${runId}`,
    task_id: `task-${runId}`,
    turn_id: `turn-${runId}-01`,
    correlation_id: `corr-${runId}`,
    submitted_at: now,
    scenario_id: scenarioId,
    route_decision: profile.route_decision,
    risk_level: profile.risk_level,
    confirmation_state: profile.confirmation_state,
    pending_confirmation_prompt: profile.pending_confirmation_prompt,
    active_model_ids: clone(state.mock.current_task.active_model_ids),
    latency: {
      decision_latency_ms: 0,
      exec_latency_ms: 0,
      within_threshold: true,
    },
    input_text: inputText,
    last_safe_checkpoint_id: "ckpt-submitted-ui",
    ...taskState,
  };
}

function attachFormHandlers() {
  document.getElementById("scenario-select").addEventListener("change", () => {
    const scenarioId = document.getElementById("scenario-select").value;
    const profile = scenarioProfile(scenarioId);
    document.getElementById("task-input").value = profile.default_input_text;
    document.getElementById("run-id-input").value = `${scenarioId.replaceAll("_", "-")}-ui`;
    renderScenarioPanel();
  });

  document.getElementById("reset-form").addEventListener("click", () => {
    fillSubmissionDefaults();
  });

  document.getElementById("submission-form").addEventListener("submit", (event) => {
    event.preventDefault();

    const scenarioId = document.getElementById("scenario-select").value;
    const runIdInput = document.getElementById("run-id-input").value.trim();
    const inputText = document.getElementById("task-input").value.trim();
    const runId = runIdInput || `${scenarioId.replaceAll("_", "-")}-ui`;
    const record = createSubmissionRecord({ scenarioId, runId, inputText });

    state.mock.current_task = record;
    state.mock.safety_prompt.summary = `Safety prompt remains pinned for ${scenarioId}.`;
    state.mock.safety_prompt.body = record.pending_confirmation_prompt || state.mock.safety_prompt.body;
    state.mock.safety_prompt.visible = true;
    state.ui.submissions.unshift({
      task_id: record.task_id,
      scenario_id: record.scenario_id,
      state: record.task_state,
      owner: state.mock.task_submission.operator,
      risk_level: record.risk_level,
      submitted_at: record.submitted_at,
    });

    state.evidence.events.unshift({
      timestamp: record.submitted_at,
      module: "frontend",
      event: "task_submission_staged",
      state: record.task_state,
      payload: {
        scenario_id: record.scenario_id,
        task_id: record.task_id,
        run_id: runId,
      },
    });

    document.getElementById("submission-status").textContent =
      `Staged ${record.task_id} for ${record.scenario_id}. Monitoring shell updated without hiding the safety prompt.`;

    renderAll();
  });
}

function populateScenarioSelect() {
  const select = document.getElementById("scenario-select");
  const options = benchmarkScenarioIds()
    .map((scenarioId) => `<option value="${escapeHtml(scenarioId)}">${escapeHtml(scenarioId)}</option>`)
    .join("");
  select.innerHTML = options;
}

function parseEventLog(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

async function loadEvidenceArtifacts() {
  const bundlePath = state.mock.evidence_bundle.path;
  const [metadata, result, latency, frameSources, summary, eventsText, robotLog] = await Promise.all([
    fetchJson(repoUrl(`${bundlePath}/metadata.json`)).catch(() => null),
    fetchJson(repoUrl(`${bundlePath}/result.json`)).catch(() => null),
    fetchJson(repoUrl(`${bundlePath}/latency.json`)).catch(() => null),
    fetchJson(repoUrl(`${bundlePath}/perception/frame-sources.json`)).catch(() => null),
    fetchText(repoUrl(`${bundlePath}/summary.md`)).catch(() => ""),
    fetchText(repoUrl(`${bundlePath}/events.jsonl`)).catch(() => ""),
    fetchText(repoUrl(`${bundlePath}/robot/robot-control.log`)).catch(() => ""),
  ]);

  state.evidence.metadata = metadata;
  state.evidence.result = result;
  state.evidence.latency = latency;
  state.evidence.frameSources = frameSources;
  state.evidence.summary = summary;
  state.evidence.events = parseEventLog(eventsText);
  state.evidence.robotLog = robotLog;

  if (state.evidence.latency) {
    state.mock.current_task.latency = {
      decision_latency_ms: state.evidence.latency.decision_latency_ms,
      exec_latency_ms: state.evidence.latency.exec_latency_ms,
      within_threshold: state.evidence.latency.within_threshold,
    };
  }

  if (state.evidence.frameSources?.frame_sources?.length) {
    const feedById = new Map(state.mock.camera_feeds.map((feed) => [feed.id, feed]));
    state.evidence.frameSources.frame_sources.forEach((frameSource) => {
      const existing = feedById.get(frameSource.camera_id);
      if (existing) {
        existing.device_path = frameSource.device_path;
        existing.capture_profile = frameSource.capture_profile;
      }
    });
  }
}

async function init() {
  state.mock = await fetchJson("./mock-state.json");
  state.benchmark = await fetchJson(repoUrl(state.mock.evidence_bundle.benchmark_path));
  state.ui.activeFeedId = state.mock.camera_shell.active_feed_id;
  state.ui.submissions = clone(state.mock.task_queue);

  await loadEvidenceArtifacts();

  populateScenarioSelect();
  fillSubmissionDefaults();
  attachFormHandlers();
  renderAll();
}

init().catch((error) => {
  document.body.innerHTML = `
    <main>
      <section class="hero">
        <h1>Monitoring interface failed to load</h1>
        <p>${escapeHtml(error.message)}</p>
      </section>
    </main>
  `;
});
