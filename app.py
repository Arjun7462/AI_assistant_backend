from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import google.generativeai as genai
from dotenv import load_dotenv
import os, uuid
from werkzeug.utils import secure_filename
from voice_processor import transcribe_audio, text_to_speech
from mcp_handlers import send_email, send_message_via_whatsapp, search_drive, schedule_event

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

if not os.path.exists("temp"):
    os.makedirs("temp")

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
chat_sessions = {}

@app.route('/')
def index():
    return render_template("loading.html")

@app.route('/ui')
def ui():
    return render_template("ui.html")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get("message")
    chat_id = data.get("chat_id")

    if not msg:
        return jsonify({"success": False, "message": "Empty message"}), 400

    if chat_id and chat_id in chat_sessions:
        chat = chat_sessions[chat_id]
    else:
        chat = model.start_chat()
        chat_id = str(uuid.uuid4())
        chat_sessions[chat_id] = chat

    response = chat.send_message(msg)
    response_text = response.text.strip()

    # === Backend Intelligence: Handle Task Execution ===
    if "whatsapp" in msg.lower():
        phone = "+919999999999"  # Dummy for testing or replace with real input
        send_message_via_whatsapp(phone, response_text)
        response_text = f"✅ Message sent to Arjun on WhatsApp."

    elif "send email" in msg.lower():
        email_data = {
            "to": "arjun@example.com",
            "subject": "Message from AI",
            "body": response_text
        }
        send_email(email_data)
        response_text = "✅ Email sent to Arjun."

    elif "schedule meeting" in msg.lower() or "calendar" in msg.lower():
        event = {"title": "AI Scheduled Meeting", "time": "2025-04-21T11:00:00"}
        schedule_event(event)
        response_text = "✅ Meeting added to Calendar."

    elif "search drive" in msg.lower():
        results = search_drive("project")
        response_text = "✅ Found in Drive: " + str(results)

    return jsonify({"success": True, "text": response_text, "chat_id": chat_id})

@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files.get("file")
    chat_id = request.form.get("chat_id")

    if not file:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    path = os.path.join("temp", secure_filename(file.filename))
    file.save(path)

    try:
        genai_file = genai.upload_file(path)
        result = model.generate_content(["Summarize this file:", genai_file])
        return jsonify({"success": True, "summary": result.text, "chat_id": chat_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        os.remove(path)

@socketio.on("audio_data")
def audio(data):
    audio_id = str(uuid.uuid4())
    audio_path = f"temp/{audio_id}.wav"
    with open(audio_path, "wb") as f:
        f.write(data)

    text = transcribe_audio(audio_path)
    result = model.generate_content(text)
    response_text = result.text.strip()
    audio_response_path = text_to_speech(response_text)

    with open(audio_response_path, "rb") as f:
        audio_data = f.read()

    emit("ai_response", {"text": response_text, "audio": audio_data.decode('latin1')})
    os.remove(audio_path)
    os.remove(audio_response_path)

if __name__ == "__main__":
    socketio.run(app, port=5000, debug=True)
