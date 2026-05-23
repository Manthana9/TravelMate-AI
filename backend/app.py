from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# ---------------------------------------------------
# Allow backend to access the agent folder
# ---------------------------------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# ---------------------------------------------------
# Load environment variables
# ---------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------
# Google ADK imports
# ---------------------------------------------------
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ---------------------------------------------------
# Import Member 2's Agent
# ---------------------------------------------------
from agent.agent import root_agent

# ---------------------------------------------------
# Flask setup
# ---------------------------------------------------
app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# ADK Session Memory
# ---------------------------------------------------
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="travelmate",
    session_service=session_service
)

# ---------------------------------------------------
# Generate AI Response Function
# ---------------------------------------------------
def generate_ai_response(session_id: str, user_message: str) -> str:

    try:
        # Create session
        session_service.create_session(
            app_name="travelmate",
            user_id="user1",
            session_id=session_id
        )

    except Exception:
        # Ignore if session already exists
        pass

    # Create user content
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)]
    )

    response_text = ""

    # Run the agent
    for event in runner.run(
        user_id="user1",
        session_id=session_id,
        new_message=content
    ):

        # Final AI response
        if event.is_final_response():

            if event.content and event.content.parts:

                for part in event.content.parts:

                    if hasattr(part, "text") and part.text:
                        response_text += part.text

    return response_text


# ---------------------------------------------------
# ROUTE 1 — Plan Trip
# ---------------------------------------------------
@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():

    try:

        data = request.get_json()

        destination = data.get('destination', '')
        duration = data.get('duration', '')
        budget = data.get('budget', '')
        session_id = data.get('session_id', 'default')

        # Build user prompt
        user_message = (
            f"Plan a {duration} trip to {destination} "
            f"with a budget of {budget} INR."
        )

        # Get AI response
        ai_reply = generate_ai_response(
            session_id,
            user_message
        )

        return jsonify({
            "success": True,
            "itinerary": ai_reply
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ---------------------------------------------------
# ROUTE 2 — Modify Existing Trip
# ---------------------------------------------------
@app.route('/api/modify-trip', methods=['POST'])
def modify_trip():

    try:

        data = request.get_json()

        session_id = data.get('session_id', 'default')
        modification_request = data.get(
            'modification_request',
            ''
        )

        ai_reply = generate_ai_response(
            session_id,
            modification_request
        )

        return jsonify({
            "success": True,
            "itinerary": ai_reply
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ---------------------------------------------------
# ROUTE 3 — Approve Trip
# ---------------------------------------------------
@app.route('/api/approve-trip', methods=['POST'])
def approve_trip():

    try:

        data = request.get_json()

        session_id = data.get('session_id', 'default')

        return jsonify({
            "success": True,
            "message": f"Trip approved successfully for session {session_id} 🎉"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ---------------------------------------------------
# ROUTE 4 — Health Check
# ---------------------------------------------------
@app.route('/health', methods=['GET'])
def health():

    return jsonify({
        "status": "Server is running ✅"
    })


# ---------------------------------------------------
# Run Flask App
# ---------------------------------------------------
if __name__ == '__main__':

    app.run(
        debug=True,
        port=5000,
        use_reloader=False
    )