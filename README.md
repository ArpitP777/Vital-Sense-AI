# Real-Time Healthcare Feedback AI

A conversational AI agent that collects patient feedback in real-time, functioning as an empathetic human listener.

## Features

*   **Real-Time Interaction**: Responds immediately to every user message.
*   **Empathetic Persona**: Adaptive tone that acknowledges frustration or satisfaction.
*   **Web & CLI Interfaces**: Chat via a modern web UI or the command line.
*   **Auto-Analysis**: Generates a satisfaction score (1-5), summary, and key issue list.
*   **CSV Storage**: Persists anonymous data locally.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file (see `.env.example`) to set your LLM provider.
    ```env
    # Options: mock, openai, anthropic
    LLM_PROVIDER=openai
    OPENAI_API_KEY=sk-your-key
    ```

## Usage

### Web Interface (Recommended)
Host the server locally and access the chat UI in your browser.
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000)

### CLI Mode
Run the conversation directly in your terminal.
```bash
python main.py
```

## Privacy & Ethics

*   **Anonymous Data**: This system collects general sentiment. Do not enter PII or PHI.
*   **Transparency**: The user is interacting with an AI Agent.
*   **Data Storage**: Feedback is stored in `feedback_data.csv`.
