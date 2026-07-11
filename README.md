# 🚑 Multi-Agent Emergency System

An AI-powered emergency assistance system that helps users during emergency situations by providing nearby hospitals, weather information, AI-generated first-aid advice, and voice interaction through a simple Streamlit interface.

---

## 📌 Features

- 🏥 Find nearby hospitals
- 📍 Detect user location
- 🌦 Get current weather information
- 🤖 AI-generated emergency first-aid advice using Groq LLM
- 🎤 Voice input support
- 💻 Simple and interactive Streamlit interface

---

## 🛠 Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI & APIs
- Groq API
- OpenStreetMap (Nominatim)
- OpenWeather API

### Libraries
- Streamlit
- Requests
- SpeechRecognition
- python-dotenv

---

## 📂 Project Structure

```
MULTI_AGENT_EMERGENCY_SYSTEM
│
├── agents/
│   ├── coordinator_agent.py
│   ├── hospital_agent.py
│   ├── llm_advice_agent.py
│   ├── location_agent.py
│   ├── voice_agent.py
│   └── weather_agent.py
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/harshithnayak07/MULTI_AGENT_EMERGENCY_SYSTEM.git
```

Move into the project folder

```bash
cd MULTI_AGENT_EMERGENCY_SYSTEM
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

---

## ▶ Run the Application

```bash
streamlit run app.py
```

---

## 🚀 How It Works

```
User
   │
   ▼
Streamlit Interface
   │
   ▼
Coordinator Agent
   │
   ├────────► Location Agent
   │
   ├────────► Hospital Agent
   │
   ├────────► Weather Agent
   │
   ├────────► Voice Agent
   │
   └────────► AI Advice Agent (Groq)
                    │
                    ▼
            Emergency Response
```

---
