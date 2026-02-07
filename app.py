import os
import sys
import uuid

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    pass

try:
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
except ImportError as e:
    print("=" * 60)
    print("ERROR: Flask is not installed!")
    print("=" * 60)
    print("\nTo fix this, run:")
    print("  pip install flask flask-cors")
    print("\nOr install all dependencies:")
    print("  pip install -r requirements.txt")
    print("=" * 60)
    sys.exit(1)

from conversation import ConversationManager
from prompts import get_system_prompt, get_user_message, CONVERSATIONAL_SYSTEM_PROMPT
from llm_client import LLMClient
from feedback_analyzer import FeedbackAnalyzer
from storage import FeedbackStorage

app = Flask(__name__)
CORS(app)

storage = FeedbackStorage("feedback_data.csv")
analyzer = FeedbackAnalyzer()

provider = os.getenv("LLM_PROVIDER", "mock").lower()
try:
    llm_client = LLMClient(provider=provider)
    print(f"Web Server using LLM provider: {provider}")
except Exception as e:
    print(f"Warning: {e}, using mock provider")
    llm_client = LLMClient(provider="mock")

active_sessions = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/conversation/start', methods=['POST'])
def start_conversational_session():
    try:
        session_id = str(uuid.uuid4())
        
        conversation = ConversationManager()
        
        greeting = "Hello! I'm here to listen about your healthcare experience today. What would you like to share?"
        conversation.add_assistant_message(greeting)
        
        active_sessions[session_id] = conversation
        
        return jsonify({
            "success": True,
            "message": greeting,
            "is_active": True,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/conversation/message', methods=['POST'])
def send_message():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        if not session_id or session_id not in active_sessions:
            return jsonify({"success": False, "error": "Invalid or expired session"}), 400
        
        conversation = active_sessions[session_id]
        
        if user_message.lower() in ["end", "stop", "finish", "done"]:
             return end_conversational_session_internal(session_id)

        conversation.add_user_message(user_message)
        
        try:
            assistant_response = llm_client.chat(
                conversation.get_history(),
                CONVERSATIONAL_SYSTEM_PROMPT
            )
        except Exception as llm_error:
            print(f"LLM Error: {llm_error}")
            print("Falling back to mock provider for this response.")
            try:
                fallback_client = LLMClient(provider="mock")
                assistant_response = fallback_client.chat(
                    conversation.get_history(),
                    CONVERSATIONAL_SYSTEM_PROMPT
                )
                assistant_response += " [Note: System fallback engaged due to connection error]"
            except Exception as e:
                 assistant_response = f"System Error: {str(llm_error)}. Please check server logs."

        conversation.add_assistant_message(assistant_response)
        
        return jsonify({
            "success": True,
            "message": assistant_response,
            "is_active": True,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/conversation/end', methods=['POST'])
def end_conversational_session():
    try:
        data = request.json
        session_id = data.get('session_id')
        return end_conversational_session_internal(session_id)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def end_conversational_session_internal(session_id):
    if not session_id or session_id not in active_sessions:
        return jsonify({"success": False, "error": "Invalid session"}), 400
    
    conversation = active_sessions[session_id]
    
    closing_msg = "Thank you for your feedback. We are now analyzing your response."
    conversation.add_assistant_message(closing_msg)
    
    transcript = conversation.get_conversation_transcript()
    
    return jsonify({
        "success": True,
        "message": closing_msg,
        "transcript": transcript,
        "is_active": False,
        "should_analyze": True,
        "session_id": session_id
    })


@app.route('/api/conversation/analyze', methods=['POST'])
def analyze_conversational_feedback():
    try:
        data = request.json
        transcript = data.get('transcript', '')
        session_id = data.get('session_id')
        
        if not transcript and session_id and session_id in active_sessions:
            transcript = active_sessions[session_id].get_conversation_transcript()
        
        if not transcript:
            return jsonify({"success": False, "error": "No transcript provided"}), 400
        
        system_prompt = get_system_prompt()
        user_message = get_user_message(transcript)
        
        llm_response = llm_client.analyze_feedback(user_message, system_prompt)
        feedback = analyzer.process_llm_output(llm_response)
        
        storage.save_feedback(feedback)
        
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return jsonify({
            "success": True,
            "feedback": feedback,
            "display_text": analyzer.format_feedback_display(feedback)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/feedback-history', methods=['GET'])
def get_feedback_history():
    try:
        feedback_list = storage.load_all_feedback()
        return jsonify({
            "success": True,
            "feedback": feedback_list
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("HEALTHCARE FEEDBACK SERVER starting...")
    print(f"Provider: {provider}")
    print("http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
