# 🏥 Vital Sense AI

An AI-powered healthcare feedback system that uses conversational intelligence to collect, analyze, and understand patient experiences in real-time.

## 📋 Overview

Vital Sense AI functions as an empathetic virtual assistant that engages patients in natural conversations about their healthcare experiences. It automatically analyzes sentiment, extracts key issues, and generates satisfaction scores — helping healthcare providers improve their services.

### ✨ Key Features

- **🗣️ Real-Time Conversational AI** — Natural, empathetic dialogue with adaptive tone
- **🎤 Voice Support** — Speech-to-text input & text-to-speech output
- **📊 Smart Analysis** — Auto-generates satisfaction scores (1-5), summaries & key issues
- **🌐 Web & CLI Interfaces** — Modern web UI or command-line interaction
- **💾 Local Storage** — Anonymous feedback persisted to CSV

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.7+, Flask, Flask-CORS |
| **AI/LLM** | OpenAI GPT, Anthropic Claude |
| **Speech** | SpeechRecognition, PyAudio, pyttsx3 |
| **Frontend** | HTML, CSS, JavaScript |
| **Data** | CSV (local storage) |
| **Config** | python-dotenv |

---

## 🚀 Quick Start

```bash
# Clone & install
git clone https://github.com/your-username/Vital-Sense-AI.git
cd Vital-Sense-AI
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your OpenAI/Anthropic API key

# Run the web server
python app.py
```

Visit `http://localhost:5000` to start collecting feedback!

---

## 📁 Project Structure

```
├── app.py                 # Flask web server & API endpoints
├── conversation.py        # Conversation state management
├── llm_client.py          # Multi-provider LLM integration
├── feedback_analyzer.py   # Sentiment analysis & scoring
├── speech_input.py        # Voice recognition
├── speech_output.py       # Text-to-speech
├── prompts.py             # AI system prompts
├── storage.py             # CSV data persistence
├── static/                # Frontend assets (CSS, JS)
└── templates/             # HTML templates
```

---

## 📄 License

MIT License — feel free to use and modify!
