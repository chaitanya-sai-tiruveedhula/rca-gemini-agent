const statusBadge = document.getElementById("statusBadge");
const errorElement = document.getElementById("error");
const similarElement = document.getElementById("similar");
const rcaElement = document.getElementById("rca");
const analyzeBtn = document.getElementById("analyzeBtn");

function setStatus(text) {
  statusBadge.innerText = text;
}

function showError(message) {
  errorElement.innerText = message;
  errorElement.classList.remove("hidden");
}

function clearError() {
  errorElement.innerText = "";
  errorElement.classList.add("hidden");
}

function clearForm() {
  document.getElementById("incident-id").value = "";
  document.getElementById("incident").value = "";
  rcaElement.innerHTML = `<p class="placeholder">Submit an incident to generate a structured LLM analysis, risk rating, and recommended actions.</p>`;
  similarElement.innerHTML = `<p class="placeholder">Matching incidents are displayed here to help identify repeat issues.</p>`;
  clearError();
  setStatus("Idle");
}

function renderSimilarIncidents(incidents) {
  if (!incidents || !incidents.length) {
    similarElement.innerHTML = `<p class="placeholder">No similar incidents found.</p>`;
    return;
  }

  similarElement.innerHTML = incidents.map((incident, index) => {
    const incidentNumber = incident.incident_number || incident.incident_id || incident.id || 'N/A';
    const source = incident.source || 'Local Database';
    const sourceIcon = {
      'GitHub': '🐙',
      'Stack Overflow': '📚',
      'CISA/NVD': '🔒',
      'Local Database': '💾'
    }[source] || '📌';
    
    // Build meta information based on source type
    let metaHtml = '';
    if (incident.root_cause) {
      metaHtml += `<span><strong>Root cause:</strong> ${incident.root_cause}</span>`;
    }
    if (incident.resolution) {
      metaHtml += `<span><strong>Resolution:</strong> ${incident.resolution}</span>`;
    }
    if (incident.score) {
      metaHtml += `<span><strong>Similarity:</strong> ${(incident.score * 100).toFixed(0)}%</span>`;
    } else if (incident.score === 0) {
      metaHtml += `<span><strong>Similarity:</strong> n/a</span>`;
    }
    
    // Add source-specific metadata
    if (incident.url) {
      metaHtml += `<span><strong>Link:</strong> <a href="${incident.url}" target="_blank">View</a></span>`;
    }
    if (incident.labels && incident.labels.length > 0) {
      metaHtml += `<span><strong>Tags:</strong> ${incident.labels.join(', ')}</span>`;
    }
    
    return `
      <article class="similar-card">
        <h3>Match ${index + 1} ${sourceIcon} <span style="font-size: 0.8rem; font-weight: normal;">${source}</span></h3>
        <p><strong>ID:</strong> ${incidentNumber}</p>
        <p>${incident.description || incident.title || 'No description available'}</p>
        <div class="meta">
          ${metaHtml}
        </div>
      </article>
    `;
  }).join("");
}

function renderRcaAnalysis(rca) {
  if (!rca || typeof rca !== 'object') {
    rcaElement.innerHTML = `<p class="placeholder">No RCA response returned.</p>`;
    return;
  }

  const incidentHeader = rca.incident_number || rca.incident_id ? `
      <div class="incident-number-banner">
        <span>Incident ID</span>
        <strong>${rca.incident_number || rca.incident_id || 'N/A'}</strong>
      </div>
    ` : '';

  const sections = [];

  if (rca.summary) {
    sections.push(`
      <div class="section">
        <h3>Summary</h3>
        <p>${rca.summary}</p>
      </div>
    `);
  }

  if (rca.root_causes && rca.root_causes.length) {
    sections.push(`
      <div class="section">
        <h3>Likely Root Causes</h3>
        <ul>${rca.root_causes.map(cause => `<li>${cause}</li>`).join('')}</ul>
      </div>
    `);
  }

  if (rca.recommended_actions && rca.recommended_actions.length) {
    sections.push(`
      <div class="section">
        <h3>Recommended Actions</h3>
        <ul>${rca.recommended_actions.map(step => `<li>${step}</li>`).join('')}</ul>
      </div>
    `);
  }

  const risk = rca.risk_level ? `<span class="pill-mini">Risk: ${rca.risk_level}</span>` : '';
  const confidence = rca.confidence ? `<span class="pill-mini">Confidence: ${rca.confidence}</span>` : '';

  rcaElement.innerHTML = `
    <div class="analysis-block">
      ${incidentHeader}
      ${risk || confidence ? `<div class="section"><p>${risk} ${confidence}</p></div>` : ''}
      ${sections.join('')}
      ${rca.analysis_text ? `<div class="section"><h3>Raw agent notes</h3><p>${rca.analysis_text}</p></div>` : ''}
    </div>
  `;
}

async function analyze() {
  clearError();
  const text = document.getElementById("incident").value.trim();
  const incidentId = document.getElementById("incident-id").value.trim();
  const useInternetSources = document.getElementById("useInternetSources").checked;

  if (!text && !incidentId) {
    showError("Please enter an incident description or incident ID.");
    return;
  }

  setStatus("Analyzing...");
  analyzeBtn.disabled = true;
  rcaElement.innerHTML = `<p class="placeholder">Analyzing incident... please wait.</p>`;
  similarElement.innerHTML = `<p class="placeholder">Finding matching incidents...</p>`;

  try {
    const payload = { 
      description: text,
      use_internet_sources: useInternetSources
    };
    if (incidentId) {
      payload.incident_id = incidentId;
    }
    const res = await fetch("/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || `Request failed with status ${res.status}`);
    }

    // Display data sources used
    if (data.data_sources_used && data.data_sources_used.length > 0) {
      document.getElementById("sourcesText").textContent = data.data_sources_used.join(", ");
      document.getElementById("sourcesUsed").classList.remove("hidden");
    }

    renderSimilarIncidents(data.similar_incidents || []);
    const analysis = data.rca_analysis || data.rca || {};
    if (data.incident_number) {
      analysis.incident_number = analysis.incident_number || data.incident_number;
    }
    renderRcaAnalysis(analysis);
    setStatus("Complete");
  } catch (err) {
    showError(`Unable to analyze incident: ${err.message}`);
    rcaElement.innerHTML = `<p class="placeholder">Analysis failed. See error message above.</p>`;
    similarElement.innerHTML = `<p class="placeholder">Unable to load similar incidents.</p>`;
    setStatus("Error");
  } finally {
    analyzeBtn.disabled = false;
  }
}
