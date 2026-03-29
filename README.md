🚫 What NOT to Learn Engine

An AI-powered web app that helps users avoid wasting time on outdated or low-value skills by providing data-driven recommendations on what to skip and what to focus on instead.

Overview

This project analyzes real-time skill trends and combines them with AI reasoning to guide users in making smarter learning decisions. Instead of just telling you what to learn, it highlights what not to learn — which is where most people usually go wrong.

⚙️ How It Works
User enters a career goal or domain
The app fetches real-time trend data using external APIs
AI analyzes the data and returns:
Skills to avoid
Better alternatives
A strategic summary
🛠️ Tech Stack
Backend: Python + FastAPI
Frontend: HTML, CSS, JavaScript
APIs:
Bright Data (trend scraping)
Featherless AI (analysis engine)

🚀 Features
Real-time trend-based analysis
AI-generated career guidance
Clean and interactive UI
Structured output (avoid vs alternatives)
Fast and lightweight
🔑 API Keys Setup

This project requires API keys to work.

Open main.py and replace the placeholder values:

BRIGHTDATA_API_KEY = "your_brightdata_api_key"
FEATHERLESS_API_KEY = "your_featherless_api_key"
▶️ Run Locally
pip install -r requirements.txt
python main.py

Then open:

http://127.0.0.1:8000


💡 Idea

Most platforms tell you what to learn.
This project focuses on the opposite:

Knowing what to avoid is just as important as knowing what to pursue.