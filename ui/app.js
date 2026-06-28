const state = {
  threadId: null,
  lastIntent: "launch_review",
};

const els = {
  form: document.querySelector("#chatForm"),
  input: document.querySelector("#messageInput"),
  messages: document.querySelector("#messages"),
  region: document.querySelector("#region"),
  apiUrl: document.querySelector("#apiUrl"),
  apiStatus: document.querySelector("#apiStatus"),
  sendButton: document.querySelector("#sendButton"),
  threadLabel: document.querySelector("#threadLabel"),
  newThread: document.querySelector("#newThread"),
  promptChips: document.querySelectorAll(".prompt-chip"),
  intentTag: document.querySelector("#intentTag"),
  verdictLabel: document.querySelector("#verdictLabel"),
  priceBand: document.querySelector("#priceBand"),
  bestAngle: document.querySelector("#bestAngle"),
  demandBar: document.querySelector("#demandBar"),
  supplyBar: document.querySelector("#supplyBar"),
  fitBar: document.querySelector("#fitBar"),
  demandScore: document.querySelector("#demandScore"),
  supplyScore: document.querySelector("#supplyScore"),
  fitScore: document.querySelector("#fitScore"),
};

function classifyIntent(message) {
  const text = message.toLowerCase();
  if (["price", "pricing", "cost", "budget", "cheap", "expensive"].some((token) => text.includes(token))) {
    return "pricing_question";
  }
  if (["review", "complaint", "pain point", "gap", "problem"].some((token) => text.includes(token))) {
    return "review_gap";
  }
  if (["what about", "compare", "how about", "instead", "similar", "us market"].some((token) => text.includes(token))) {
    return "follow_up";
  }
  return "launch_review";
}

function mockChat(message, region) {
  const intent = classifyIntent(message);
  const isPricing = intent === "pricing_question";
  const isGap = intent === "review_gap";
  const regionName = region === "IN" ? "India" : region === "US" ? "the United States" : region;
  const verdict = isPricing || isGap ? "Niche" : "Niche";
  const price = region === "IN" ? "₹700-₹1,500" : "$18-$34";
  const angle = isGap ? "Leak-proof lid and better carry strap" : "Durability + giftability";

  return {
    thread_id: state.threadId || `ui-${Date.now()}`,
    region,
    intent,
    verdict: [
      `Verdict: ${verdict}`,
      `Demand: rising interest in ${regionName}, strongest around insulated, travel, and gifting searches.`,
      `Price band: ${price}.`,
      `Positioning: ${angle}.`,
      `Review gaps: leaks, poor lid seal, weak straps.`,
    ].join("\n"),
    research_summary: isPricing
      ? `Pricing branch used current supply assumptions for ${regionName}.`
      : `Demand and supply signals were blended for ${regionName}.`,
  };
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "user" ? "F" : "L";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const meta = document.createElement("p");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "Founder" : "LaunchLens";

  const body = document.createElement("p");
  body.innerHTML = escapeHtml(text).replace(/\n/g, "<br />");

  bubble.append(meta, body);
  article.append(avatar, bubble);
  els.messages.append(article);
  els.messages.scrollTop = els.messages.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (char) => {
    const entities = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return entities[char];
  });
}

function setLoading(isLoading) {
  els.sendButton.disabled = isLoading;
  els.sendButton.lastChild.textContent = isLoading ? "Thinking" : "Send";
}

function updateScores(intent) {
  const scores = {
    pricing_question: [6.8, 7.7, 7.2],
    review_gap: [7.1, 6.2, 7.5],
    follow_up: [7.6, 6.6, 7.0],
    launch_review: [7.4, 6.8, 7.1],
  }[intent] || [7.1, 6.8, 7.0];

  const [demand, supply, fit] = scores;
  els.demandScore.textContent = demand.toFixed(1);
  els.supplyScore.textContent = supply.toFixed(1);
  els.fitScore.textContent = fit.toFixed(1);
  els.demandBar.style.width = `${demand * 10}%`;
  els.supplyBar.style.width = `${supply * 10}%`;
  els.fitBar.style.width = `${fit * 10}%`;
}

function updateSummary(result) {
  const verdictLine = result.verdict.split("\n").find((line) => line.toLowerCase().startsWith("verdict:"));
  const priceLine = result.verdict.split("\n").find((line) => line.toLowerCase().startsWith("price band:"));
  const positioningLine = result.verdict.split("\n").find((line) => line.toLowerCase().startsWith("positioning:"));

  els.intentTag.textContent = result.intent || "launch_review";
  els.verdictLabel.textContent = verdictLine ? verdictLine.replace("Verdict:", "").trim() : "Niche";
  els.priceBand.textContent = priceLine ? priceLine.replace("Price band:", "").replace(".", "").trim() : "Market dependent";
  els.bestAngle.textContent = positioningLine ? positioningLine.replace("Positioning:", "").replace(".", "").trim() : "Focused differentiation";
  updateScores(result.intent);

  state.threadId = result.thread_id || state.threadId;
  state.lastIntent = result.intent || state.lastIntent;
  els.threadLabel.textContent = `Thread: ${state.threadId}`;
}

async function callApi(message, region) {
  const response = await fetch(els.apiUrl.value, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      region,
      thread_id: state.threadId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

async function handleSubmit(event) {
  event.preventDefault();
  const message = els.input.value.trim();
  if (!message) return;

  const region = els.region.value;
  addMessage("user", message);
  els.input.value = "";
  setLoading(true);

  try {
    const result = await callApi(message, region);
    els.apiStatus.textContent = "API connected";
    addMessage("assistant", result.verdict || "No verdict returned.");
    updateSummary(result);
  } catch (error) {
    const result = mockChat(message, region);
    els.apiStatus.textContent = "Mock mode";
    addMessage("assistant", `${result.verdict}\n\n${result.research_summary}`);
    updateSummary(result);
  } finally {
    setLoading(false);
  }
}

els.form.addEventListener("submit", handleSubmit);

els.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    els.form.requestSubmit();
  }
});

els.promptChips.forEach((chip) => {
  chip.addEventListener("click", () => {
    els.input.value = chip.textContent.trim();
    els.input.focus();
  });
});

els.newThread.addEventListener("click", () => {
  state.threadId = null;
  els.threadLabel.textContent = "Thread: new";
  addMessage("assistant", "New thread started. Send the next product idea when ready.");
});

updateScores(state.lastIntent);
