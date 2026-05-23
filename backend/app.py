from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory session store
sessions = {}

# ── TEMPORARY MOCK (replace with Member 2's function later) ──
def generate_ai_response(history):
    return "## 🧭 Trip Plan\nThis is a mock itinerary for testing. Member 2 will replace this!"


# ── ROUTE 1: Plan a new trip ──────────────────────────────────
@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    data = request.get_json()

    destination = data.get('destination', '')
    duration    = data.get('duration', '')
    budget      = data.get('budget', '')
    session_id  = data.get('session_id', 'default')

    user_message = f"Plan a {duration} trip to {destination} with a maximum budget of {budget} INR."

    sessions[session_id] = [{"role": "user", "content": user_message}]

    ai_reply = generate_ai_response(sessions[session_id])

    sessions[session_id].append({"role": "assistant", "content": ai_reply})

    return jsonify({"itinerary": ai_reply})


# ── ROUTE 2: Modify an existing plan ─────────────────────────
@app.route('/api/modify-trip', methods=['POST'])
def modify_trip():
    data = request.get_json()

    session_id   = data.get('session_id', 'default')
    modification = data.get('modification_request', '')

    if session_id not in sessions:
        return jsonify({"error": "No active session. Please plan a trip first."}), 400

    sessions[session_id].append({"role": "user", "content": modification})

    ai_reply = generate_ai_response(sessions[session_id])

    sessions[session_id].append({"role": "assistant", "content": ai_reply})

    return jsonify({"itinerary": ai_reply})


# ── ROUTE 3: Approve the plan ─────────────────────────────────
@app.route('/api/approve-trip', methods=['POST'])
def approve_trip():
    data = request.get_json()
    session_id = data.get('session_id', 'default')

    sessions.pop(session_id, None)

    return jsonify({"message": "Trip approved! Have a safe journey 🎉"})


# ── ROUTE 4: Health check ─────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Server is running ✅"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)