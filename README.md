# RCA Gemini Agent

A small agent pipeline for root cause analysis using Gemini and incident similarity matching.

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install Node dependencies:

```bash
cd backend-node
npm install
```

3. Set your Gemini API key:

```bash
setx GEMINI_API_KEY "your_api_key"
```

## Run

1. Start the Python API:

```bash
python ai-engine/app.py
```

2. Start the Node server:

```bash
cd backend-node
npm start
```

3. Open `http://localhost:3000` in your browser.

## How it works

- Frontend calls the Node proxy at `http://localhost:3000/analyze`.
- Node forwards requests to the Python Flask service at `http://127.0.0.1:5000/analyze`.
- Python uses incident similarity from `ai-engine/similarity.py` and Gemini analysis from `ai-engine/gemini_rca.py`.
