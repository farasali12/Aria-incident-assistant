# ARIA – AI Incident Response Assistant

ARIA is a web-based tool I built to explore how AI can be applied to real cybersecurity workflows. Instead of just creating a chatbot, I wanted to build something closer to what a security analyst might actually use during an investigation.

The app combines incident triage, artifact analysis, and response planning into a simple interface.

---

## What it does

ARIA focuses on three main areas:

### Incident Chat
You can describe a suspicious event or possible attack, and the assistant will break it down into a structured response. It explains what might be happening, how serious it is, and what steps should be taken next.

### Quick Artifact Analysis
This feature allows you to quickly assess things like IP addresses, domains, hashes, or log entries. It provides a basic threat assessment, assigns a severity level, and suggests what to investigate next.

### Playbook Generator
Given an incident type (for example, ransomware or phishing), the app generates a step-by-step response plan covering detection, containment, eradication, and recovery.

---

## Preview

### Dashboard
![Dashboard/chat](screenshots/dashboard)

### Quick Artifact Analysis
![Analyzer](screenshots/analyzer.png)

### Incident Chat
![Playbook](screenshots/playbookGenerator.png)

---

## Tech Stack

- Python (Flask)
- JavaScript
- HTML / CSS
- OpenAI API
- python-dotenv

---

## How it works

The backend is built with Flask and exposes simple API routes for chat, analysis, and playbook generation. The frontend is built with HTML, CSS, and JavaScript and is designed to feel like a lightweight analyst dashboard.

AI responses are generated using the OpenAI API, with prompts structured to produce clear, step-by-step output rather than generic responses.

---

## Running it locally

Clone the repository:

```bash
git clone https://github.com/farasali12/Aria-incident-assistant.git
cd Aria-incident-assistant
