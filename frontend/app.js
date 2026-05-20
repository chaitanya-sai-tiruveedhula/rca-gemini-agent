async function analyze() {
  const text = document.getElementById("incident").value.trim();
  const errorElement = document.getElementById("error");
  const similarElement = document.getElementById("similar");
  const rcaElement = document.getElementById("rca");

  errorElement.innerText = "";
  similarElement.innerHTML = "";
  rcaElement.innerText = "Analyzing incident...";

  if (!text) {
    errorElement.innerText = "Please enter an incident description first.";
    rcaElement.innerText = "";
    return;
  }

  try {
    const res = await fetch("http://localhost:3000/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ description: text })
    });

    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }

    const data = await res.json();

    if (data.error) {
      throw new Error(data.error);
    }

    let simHTML = "";
    if (data.similar_incidents && data.similar_incidents.length) {
      data.similar_incidents.forEach(i => {
        simHTML += `
          <div class="incident-card">
            <p><strong>Incident #${i.incident_id}: ${i.description}</strong></p>
            <p>Cause: ${i.root_cause}</p>
            <p>Fix: ${i.resolution}</p>
            <p>Severity: ${i.severity}</p>
          </div>
        `;
      });
    } else {
      simHTML = "<p>No similar incidents found.</p>";
    }

    similarElement.innerHTML = simHTML;
    rcaElement.innerText = data.rca || "No RCA response returned.";
  } catch (err) {
    rcaElement.innerText = "";
    errorElement.innerText = `Unable to analyze incident: ${err.message}`;
  }
}
