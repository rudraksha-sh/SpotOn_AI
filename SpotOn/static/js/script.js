// Hide loading initially
document.getElementById("summaryLoading").style.display = "none";
document.getElementById("biasLoading").style.display = "none";

let selectedMode = "neutral";

// Mode buttons
document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        selectedMode = btn.dataset.mode;
    });
});

// Analyze button click
document.getElementById("analyzeBtn").addEventListener("click", () => {
    const text = document.getElementById("newsInput").value.trim();
    if (!text) return;
    getSummary(selectedMode);
    getBias();
});

// Format bullets
function formatBullets(text, mode) {
    const lines = text.split(/[\.\n]+/).filter(Boolean);
    let emoji = "🌀";
    if (mode === "facts") emoji = "📌";
    else if (mode === "eli10") emoji = "👶";

    return "<ul>" + lines.map(l => `<li>${emoji} ${l.trim()}.</li>`).join("") + "</ul>";
}

// Fetch summary
async function getSummary(mode) {
    const text = document.getElementById("newsInput").value.trim();
    const summaryDiv = document.getElementById("summaryResult");
    const loadingDiv = document.getElementById("summaryLoading");

    summaryDiv.innerHTML = "";
    if (!text) return;
    loadingDiv.style.display = "block";

    try {
        const res = await fetch("/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, mode })
        });
        const data = await res.json();
        loadingDiv.style.display = "none";

        if (data.summary) {
            summaryDiv.className = `result ${mode}`;
            summaryDiv.innerHTML = formatBullets(data.summary, mode);
        } else {
            summaryDiv.innerHTML = data.error || "Could not generate summary.";
        }
    } catch (err) {
        loadingDiv.style.display = "none";
        summaryDiv.innerHTML = `Error: ${err.message}`;
    }
}

// Fetch bias
async function getBias() {
    const text = document.getElementById("newsInput").value.trim();
    const biasDiv = document.getElementById("biasResult");
    const loadingDiv = document.getElementById("biasLoading");

    biasDiv.innerHTML = "";
    if (!text) return;
    loadingDiv.style.display = "block";

    try {
        const res = await fetch("/bias", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        loadingDiv.style.display = "none";

        biasDiv.className = "result";
        biasDiv.innerHTML = "🧐 " + (data.bias || data.error || "Bias analysis could not be generated.");
    } catch (err) {
        loadingDiv.style.display = "none";
        biasDiv.innerHTML = `Error: ${err.message}`;
    }
}
