# 🧠 MindCare - Mental Health Chatbot

<p align="center">
  <img src="https://img.shields.io/badge/Mental-Health-blue" alt="Mental Health">
  <img src="https://img.shields.io/badge/Python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/React-18+-61DAFB" alt="React">
  <img src="https://img.shields.io/badge/TailwindCSS-3.0-38B2AC" alt="Tailwind">
  <img src="https://img.shields.io/github/stars/Rogendo/Mental-health-Chatbot" alt="Stars">
  <img src="https://img.shields.io/github/forks/Rogendo/Mental-health-Chatbot" alt="Forks">
</p>

<p align="center">
  <img src="https://socialify.git.ci/Rogendo/Mental-health-Chatbot/image?language=1&owner=1&name=1&stargazers=1&theme=Light" alt="project-image">
</p>

## 📖 Description

MindCare is an AI-powered mental health chatbot designed to provide emotional support and assistance to individuals struggling with mental health issues. It uses advanced NLP techniques including:

- **Semantic Search** - Understands context and meaning, not just keywords
- **Sentiment Analysis** - Detects emotional tone in messages
- **Entity Recognition** - Identifies key topics and concerns
- **Negation Handling** - Properly understands phrases like "I am not okay"
- **Multilingual Support** - English ↔ Swahili translation

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Conversational AI** | Natural dialogue using deep learning intent classification |
| 🌍 **Multilingual** | Supports English and Swahili with automatic translation |
| 🧠 **NLP-Powered** | Sentence transformers for semantic understanding |
| 💬 **Sentiment Analysis** | Detects user mood and emotional state |
| 🎨 **Modern UI** | Beautiful React + Tailwind CSS interface |
| ⚡ **Fast** | Vite-powered frontend for instant hot reload |

---

## 📋 Prerequisites

Before installation, ensure you have the following installed:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | Latest | `pip --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | Latest | `git --version` |

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rogendo/Mental-health-Chatbot.git
cd Mental-health-Chatbot
```

### Step 2: Backend Setup (Flask + Python)

#### Create and activate virtual environment:

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Install Python dependencies:

```bash
pip install -r requirements.txt
```

#### Download spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

#### (Optional) Retrain the model:

```bash
python training.py
```

### Step 3: Frontend Setup (React + Vite)

```bash
cd frontend
npm install
```

---

## 🔧 Setup with LLM Integration (New Developers)

This project now includes **Ollama + Qwen LLM** for enhanced mental health responses. Here's what you need to know:

### System Requirements (Beyond Python/Node)

You'll need **Ollama** (the LLM service) running separately:

1. **Install Ollama**
   - Download from: https://ollama.com/
   - Follow the installer for your OS (Linux, macOS, Windows)
   - Verify installation: `ollama --version`

2. **Copy Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

3. **Pull the LLM Model** (one-time, ~8-10GB)
   ```bash
   ollama pull qwen2.5:14b-instruct
   # Verify: ollama list
   ```

### Initial Setup Summary

```bash
# 1. Clone and backend setup (as above)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Frontend setup
cd frontend
npm install
cd ..

# 3. Install Ollama (see above)

# 4. Copy environment file
cp .env.example .env
```

---

## 🏃 Running the Application

You need to run **both** the backend and frontend servers.

### Terminal 1: Start Backend Server

```bash
# From project root directory
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\activate   # Windows

python app.py
```

Backend runs at: `http://127.0.0.1:5000`

### Terminal 2: Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Access the Application

Open your browser and navigate to: **http://localhost:5173**

---

## 📁 Project Structure

```
Mental-health-Chatbot/
├── app.py                 # Flask backend with NLP processing
├── training.py            # Model training script
├── intents.json           # Intent patterns and responses
├── model.h5               # Trained Keras model
├── texts.pkl              # Vocabulary pickle file
├── labels.pkl             # Labels pickle file
├── requirements.txt       # Python dependencies
│
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Header.jsx
│   │   │   ├── ChatWidget.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   └── TypingIndicator.jsx
│   │   ├── App.jsx        # Main app component
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Tailwind styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── static/                # Legacy static files
├── templates/             # Legacy Flask templates
└── venv/                  # Virtual environment (not in git)
```

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **Keras/TensorFlow** - Deep learning model
- **Sentence Transformers** - Semantic similarity
- **spaCy** - NLP processing
- **TextBlob** - Sentiment analysis
- **MarianMT** - Translation (English ↔ Swahili)

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

---

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the root directory:

```env
FLASK_DEBUG=1
HF_TOKEN=your_huggingface_token  # For faster model downloads
USE_LLM=true
OLLAMA_MODEL=qwen2.5:14b-instruct
OLLAMA_CHAT_URL=http://localhost:11434/api/chat
OLLAMA_TAGS_URL=http://localhost:11434/api/tags
LLM_TIMEOUT_SECONDS=45
LLM_TEMPERATURE=0.5
LLM_TOP_P=0.9
RESPONSE_STYLE=balanced
```

### Ollama Setup (Open-Source LLM)

This project supports local LLM responses via [Ollama](https://ollama.com/), with automatic fallback to the existing NLP intent pipeline if Ollama is unavailable.

1. Install Ollama for your OS.
2. Pull a recommended model:

```bash
ollama pull qwen2.5:14b-instruct
```

3. Start Ollama service (if not already running).
4. Run the Flask app normally:

```bash
python app.py
```

Notes:
- `USE_LLM=true` enables LLM responses.
- If Ollama cannot be reached, the app falls back to the existing semantic/intent response engine.
- Crisis/self-harm phrases are handled by a safety-first response before LLM generation.

### Health Check Endpoint

You can verify backend + Ollama integration with:

```bash
curl http://127.0.0.1:5000/health
```

The `/health` response includes:
- Flask status (`flask.up`)
- Ollama service reachability (`llm.service_reachable`)
- Configured model availability (`llm.model_available`)
- Active style and sampling settings (`response_style`, `llm_temperature`, `llm_top_p`)

### Response Style Tuning

You can choose global style through `.env`:
- `RESPONSE_STYLE=concise`
- `RESPONSE_STYLE=balanced`
- `RESPONSE_STYLE=therapeutic`

You can also override style per request:

```text
/get?msg=I%20feel%20overwhelmed&style=therapeutic
```

The model sampling can be tuned using:
- `LLM_TEMPERATURE` (lower = more deterministic, higher = more creative)
- `LLM_TOP_P` (nucleus sampling)

### Vite Proxy Configuration

The frontend is configured to proxy API requests to the backend. See `frontend/vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

---

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the legacy HTML interface |
| `/get?msg=<message>` | GET | Get chatbot response |
| `/analyze?msg=<message>` | GET | Get NLP analysis (sentiment, entities) |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for semantic search
- [Hugging Face](https://huggingface.co/) for translation models
- [spaCy](https://spacy.io/) for NLP processing

---

<p align="center">Made with ❤️ for mental health awareness</p>


