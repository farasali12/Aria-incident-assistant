from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import json
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-prod")
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are ARIA (Automated Response & Incident Assistant), an elite AI cybersecurity incident response specialist built by Faras Ali.

You assist security teams in:
- identifying and triaging incidents
- mapping likely MITRE ATT&CK techniques
- recommending containment, investigation, eradication, and recovery steps
- providing calm, structured, actionable guidance

Rules:
1. Be precise and practical.
2. Use clear section headings.
3. Prefer concise, analyst-style answers.
4. If information is uncertain, say so clearly.
5. Do not invent evidence that was not provided.
"""

incident_logs = []


def get_conversation():
    if "conversation" not in session:
        session["conversation"] = []
    return session["conversation"]


def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def extract_text(response):
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    return str(response)


def build_conversation_input(conversation):
    items = []

    for msg in conversation:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        items.append({
            "role": role,
            "content": content
        })

    return items


def detect_severity(text):
    text_lower = text.lower()

    if any(word in text_lower for word in [
        "ransomware", "data breach", "critical", "zero-day",
        "nation-state", "active exploitation", "p1"
    ]):
        return "P1"
    if any(word in text_lower for word in [
        "malware", "intrusion", "compromised", "phishing",
        "lateral movement", "p2", "high"
    ]):
        return "P2"
    if any(word in text_lower for word in [
        "suspicious", "anomaly", "policy violation",
        "vulnerability", "p3", "medium"
    ]):
        return "P3"
    return "P4"


def detect_category(text):
    text_lower = text.lower()

    categories = {
        "Ransomware": ["ransomware", "encrypted files", "ransom"],
        "Phishing": ["phishing", "email", "credential", "spear"],
        "Malware": ["malware", "virus", "trojan", "backdoor", "rat"],
        "Intrusion": ["intrusion", "unauthorized access", "breach", "lateral"],
        "DDoS": ["ddos", "denial of service", "flood"],
        "Insider Threat": ["insider", "employee", "privilege abuse"],
        "Cloud": ["aws", "azure", "gcp", "s3", "cloud"],
        "Network": ["network", "firewall", "traffic", "packet"],
    }

    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category

    return "General"


def log_incident(user_message, assistant_reply):
    log_entry = {
        "id": len(incident_logs) + 1,
        "timestamp": datetime.now().isoformat(),
        "user_query": user_message[:100] + ("..." if len(user_message) > 100 else ""),
        "severity": detect_severity(user_message + " " + assistant_reply),
        "category": detect_category(user_message),
    }
    incident_logs.append(log_entry)
    return log_entry


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    conversation = get_conversation()
    conversation.append({"role": "user", "content": user_message})

    try:
        response = client.responses.create(
            model="gpt-5.4",
            instructions=SYSTEM_PROMPT,
            input=build_conversation_input(conversation)
        )

        assistant_reply = extract_text(response)

        conversation.append({"role": "assistant", "content": assistant_reply})
        session["conversation"] = conversation
        session.modified = True

        log_entry = log_incident(user_message, assistant_reply)

        return jsonify({
            "reply": assistant_reply,
            "log": log_entry
        })

    except Exception as e:
        return jsonify({"error": f"Chat request failed: {e}"}), 500


@app.route("/api/analyze", methods=["POST"])
def analyze_quick():
    data = request.get_json()
    artifact = data.get("artifact", "").strip()
    artifact_type = data.get("type", "unknown").strip()

    if not artifact:
        return jsonify({"error": "Artifact is required"}), 400

    prompt = f"""
Perform a rapid cybersecurity threat analysis on this {artifact_type}:

{artifact}

Respond with these sections:

Threat Assessment:
- State whether it is malicious, suspicious, or benign
- Brief justification

MITRE ATT&CK Mapping:
- Relevant tactic/technique if applicable

Severity:
- P1, P2, P3, or P4
- Explain why

Immediate Actions:
- Top 3 containment or validation steps

Investigation Leads:
- What should be checked next
"""

    try:
        response = client.responses.create(
            model="gpt-5.4",
            instructions=SYSTEM_PROMPT,
            input=prompt
        )

        return jsonify({"analysis": extract_text(response)})

    except Exception as e:
        return jsonify({"error": f"Analysis request failed: {e}"}), 500


@app.route("/api/playbook", methods=["POST"])
def get_playbook():
    data = request.get_json()
    incident_type = data.get("incident_type", "").strip()

    if not incident_type:
        return jsonify({"error": "Incident type is required"}), 400

    prompt = f"""
Generate a detailed incident response playbook for: {incident_type}

Use this exact structure:

## Playbook: {incident_type}
### Phase 1: Detection & Identification
### Phase 2: Containment
### Phase 3: Eradication
### Phase 4: Recovery
### Phase 5: Post-Incident Activity
### Key Metrics to Track
### Escalation Criteria
"""

    try:
        response = client.responses.create(
            model="gpt-5.4",
            instructions=SYSTEM_PROMPT,
            input=prompt
        )

        return jsonify({"playbook": extract_text(response)})

    except Exception as e:
        return jsonify({"error": f"Playbook request failed: {e}"}), 500


@app.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": incident_logs[-20:]})


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    session["conversation"] = []
    session.modified = True
    return jsonify({"status": "cleared"})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    total = len(incident_logs)

    if total == 0:
        return jsonify({
            "total": 0,
            "p1": 0,
            "p2": 0,
            "p3": 0,
            "p4": 0
        })

    counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}

    for log in incident_logs:
        severity = log.get("severity", "P4")
        counts[severity] = counts.get(severity, 0) + 1

    return jsonify({
        "total": total,
        "p1": counts["P1"],
        "p2": counts["P2"],
        "p3": counts["P3"],
        "p4": counts["P4"]
    })


if __name__ == "__main__":
    print("\n🛡️  ARIA — AI Incident Response Assistant")
    print("   Built by Faras Ali")
    print("   Running on http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)