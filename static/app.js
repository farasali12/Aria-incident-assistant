const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChatBtn");

const artifactType = document.getElementById("artifactType");
const artifactInput = document.getElementById("artifactInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const analysisOutput = document.getElementById("analysisOutput");

const playbookInput = document.getElementById("playbookInput");
const playbookBtn = document.getElementById("playbookBtn");
const playbookOutput = document.getElementById("playbookOutput");

const loadSampleBtn = document.getElementById("loadSampleBtn");
const clearChatBtn = document.getElementById("clearChatBtn");

const totalCount = document.getElementById("totalCount");
const p1Count = document.getElementById("p1Count");
const p2Count = document.getElementById("p2Count");
const p3Count = document.getElementById("p3Count");
const p4Count = document.getElementById("p4Count");
const incidentLogs = document.getElementById("incidentLogs");

tabButtons.forEach(button => {
    button.addEventListener("click", () => {
        tabButtons.forEach(btn => btn.classList.remove("active"));
        tabPanels.forEach(panel => panel.classList.remove("active"));

        button.classList.add("active");
        document.getElementById(button.dataset.tab).classList.add("active");
    });
});

function addMessage(role, text) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    wrapper.innerHTML = `
        <div class="message-label">${role === "user" ? "You" : "ARIA"}</div>
        <div class="message-body">${text}</div>
    `;

    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChat() {
    const message = chatInput.value.trim();

    if (!message) return;

    addMessage("user", message);
    chatInput.value = "";

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        if (data.error) {
            addMessage("assistant", `Error: ${data.error}`);
            return;
        }

        addMessage("assistant", data.reply);
        loadStats();
        loadLogs();
    } catch (error) {
        addMessage("assistant", `Request failed: ${error}`);
    }
}

async function runAnalysis() {
    const artifact = artifactInput.value.trim();
    const type = artifactType.value;

    if (!artifact) return;

    analysisOutput.textContent = "Analyzing artifact...";

    try {
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                artifact: artifact,
                type: type
            })
        });

        const data = await res.json();
        analysisOutput.textContent = data.analysis || data.error || "No response.";
    } catch (error) {
        analysisOutput.textContent = `Request failed: ${error}`;
    }
}

async function generatePlaybook() {
    const incidentType = playbookInput.value.trim();

    if (!incidentType) return;

    playbookOutput.textContent = "Generating playbook...";

    try {
        const res = await fetch("/api/playbook", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                incident_type: incidentType
            })
        });

        const data = await res.json();
        playbookOutput.textContent = data.playbook || data.error || "No response.";
    } catch (error) {
        playbookOutput.textContent = `Request failed: ${error}`;
    }
}

async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        totalCount.textContent = data.total ?? 0;
        p1Count.textContent = data.p1 ?? 0;
        p2Count.textContent = data.p2 ?? 0;
        p3Count.textContent = data.p3 ?? 0;
        p4Count.textContent = data.p4 ?? 0;
    } catch (error) {
        console.error("Failed to load stats", error);
    }
}

async function loadLogs() {
    try {
        const res = await fetch("/api/logs");
        const data = await res.json();

        if (!data.logs || data.logs.length === 0) {
            incidentLogs.innerHTML = '<p class="muted">No incidents logged yet.</p>';
            return;
        }

        incidentLogs.innerHTML = data.logs.slice().reverse().map(log => `
            <div class="log-item">
                <strong>${log.severity}</strong> • ${log.category}<br>
                <span>${log.user_query}</span>
            </div>
        `).join("");
    } catch (error) {
        console.error("Failed to load logs", error);
    }
}

async function clearConversation() {
    try {
        await fetch("/api/clear", { method: "POST" });
        chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-label">ARIA</div>
                <div class="message-body">
                    Conversation cleared. Describe a new incident when you're ready.
                </div>
            </div>
        `;
    } catch (error) {
        console.error("Failed to clear conversation", error);
    }
}

sendChatBtn.addEventListener("click", sendChat);
analyzeBtn.addEventListener("click", runAnalysis);
playbookBtn.addEventListener("click", generatePlaybook);
clearChatBtn.addEventListener("click", clearConversation);

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendChat();
    }
});

loadSampleBtn.addEventListener("click", () => {
    chatInput.value = "Multiple failed login attempts were detected from IP 203.0.113.55 against the admin account. Shortly after, a successful login occurred and sensitive payroll files were accessed without authorization. The activity happened outside normal business hours.";
});

loadStats();
loadLogs();