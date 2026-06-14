// Chatbot state and elements
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const chatError = document.getElementById("chatError");
const chatLoading = document.getElementById("chatLoading");
const chatResults = document.getElementById("chatResults");
const chatSimilar = document.getElementById("chatSimilar");
const chatStatus = document.getElementById("chatStatus");

let conversationHistory = [];

// Auto-resize textarea
function autoResizeTextarea() {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
}

chatInput.addEventListener("input", autoResizeTextarea);

// Handle Enter key to send message
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Format timestamp
function getTimeString() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Add message to chat
function addMessage(text, isUser = false) {
  const message = document.createElement("div");
  message.className = `message ${isUser ? "user-message" : "bot-message"}`;

  const avatar = isUser ? "👤" : "🤖";

  message.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      <p>${escapeHtml(text)}</p>
    </div>
  `;

  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add HTML message (for structured responses)
function addStructuredMessage(content, isUser = false) {
  const message = document.createElement("div");
  message.className = `message ${isUser ? "user-message" : "bot-message"}`;

  const avatar = isUser ? "👤" : "🤖";

  message.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      ${content}
    </div>
  `;

  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML special characters
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

// Display results from analysis
function displayResults(analysis, similar) {
  let resultsHtml = '<div class="results-content">';

  if (analysis.summary) {
    resultsHtml += `
      <div class="analysis-section">
        <h3><span class="section-icon">📋</span>Summary</h3>
        <p>${escapeHtml(analysis.summary)}</p>
      </div>
    `;
  }

  if (analysis.root_causes && analysis.root_causes.length > 0) {
    resultsHtml += `
      <div class="analysis-section">
        <h3><span class="section-icon">🔍</span>Likely Root Causes</h3>
        <ul>
          ${analysis.root_causes.map((cause) => `<li>${escapeHtml(cause)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  if (analysis.recommended_actions && analysis.recommended_actions.length > 0) {
    resultsHtml += `
      <div class="analysis-section">
        <h3><span class="section-icon">✅</span>Recommended Actions</h3>
        <ul>
          ${analysis.recommended_actions.map((action) => `<li>${escapeHtml(action)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  if (analysis.risk_level) {
    const riskClass = `risk-${analysis.risk_level.toLowerCase()}`;
    resultsHtml += `
      <div class="analysis-section">
        <h3><span class="section-icon">⚠️</span>Risk Assessment</h3>
        <span class="risk-badge ${riskClass}">Risk Level: ${escapeHtml(analysis.risk_level)}</span>
      </div>
    `;
  }

  if (analysis.confidence) {
    resultsHtml += `
      <div class="analysis-section">
        <h3><span class="section-icon">🎯</span>Confidence</h3>
        <p>${escapeHtml(analysis.confidence)}</p>
      </div>
    `;
  }

  resultsHtml += "</div>";
  chatResults.innerHTML = resultsHtml;

  // Display similar incidents
  if (similar && similar.length > 0) {
    chatSimilar.innerHTML = similar
      .map(
        (incident, index) => `
      <article class="similar-card">
        <h3>Match ${index + 1}</h3>
        <p><strong>Incident:</strong> ${escapeHtml(incident.incident_number || incident.incident_id || incident.id || "N/A")}</p>
        <p>${escapeHtml(incident.description)}</p>
        <div class="meta">
          <span><strong>Root cause:</strong> ${escapeHtml(incident.root_cause || "Unknown")}</span>
          <span><strong>Resolution:</strong> ${escapeHtml(incident.resolution || "N/A")}</span>
          <span><strong>Score:</strong> ${incident.score ? (incident.score * 100).toFixed(0) + "%" : "n/a"}</span>
        </div>
      </article>
    `
      )
      .join("");
  } else {
    chatSimilar.innerHTML = `<p class="placeholder">No similar incidents found.</p>`;
  }
}

// Show error
function showChatError(message) {
  chatError.innerText = message;
  chatError.classList.remove("hidden");
  setTimeout(() => {
    chatError.classList.add("hidden");
  }, 5000);
}

// Show/hide loading
function setLoading(isLoading) {
  if (isLoading) {
    chatLoading.classList.remove("hidden");
  } else {
    chatLoading.classList.add("hidden");
  }
}

// Update status badge
function updateStatus(text, isAnalyzing = false) {
  chatStatus.innerText = text;
  if (isAnalyzing) {
    chatStatus.style.animation = "pulse 1s infinite";
  } else {
    chatStatus.style.animation = "none";
  }
}

// Send message function
async function sendMessage() {
  const userText = chatInput.value.trim();

  if (!userText) {
    return;
  }

  // Add user message to chat
  addMessage(userText, true);
  conversationHistory.push({ role: "user", content: userText });

  // Clear input
  chatInput.value = "";
  autoResizeTextarea();

  // Show loading
  setLoading(true);
  updateStatus("Analyzing...", true);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userText,
        history: conversationHistory,
        use_internet_sources: true
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to get response");
    }

    const data = await response.json();
    setLoading(false);

    // Add assistant response
    if (data.reply) {
      addMessage(data.reply, false);
      conversationHistory.push({ role: "assistant", content: data.reply });
    }

    // Display analysis results if available
    if (data.analysis) {
      displayResults(data.analysis, data.similar_incidents);
      updateStatus("Analysis Complete");
    } else {
      updateStatus("Ready");
    }
  } catch (err) {
    setLoading(false);
    updateStatus("Error");
    showChatError(err.message || "An error occurred while processing your request.");
    console.error("Chat error:", err);
  }
}

// Handle send button click
sendBtn.addEventListener("click", sendMessage);

// Initial greeting is already in HTML
updateStatus("Ready");
