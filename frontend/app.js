async function analyze() {
    const desc = document.getElementById("input").value;

    const res = await fetch("http://localhost:3000/analyze", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({description: desc})
    });

    const data = await res.json();

    let simHTML = "";
    data.similar_incidents.forEach(i => {
        simHTML += `
            <p>
            <b>${i.description}</b><br>
            Cause: ${i.root_cause}<br>
            Resolution: ${i.resolution}<br>
            Severity: ${i.severity}
            </p>
        `;
    });

    document.getElementById("similar").innerHTML = simHTML;
    document.getElementById("rca").innerText = data.rca;
}