# EcoSort AI – COIT12204 Assessment 4

Two specialised agents: Classifier (deterministic recycling rule function) and Validator (checks schema and constructs safe guidance). The orchestrator passes validated Pydantic messages, enforces a step limit and per-agent timeout, logs messages, and returns a safe fallback. No external AI API key is required; this version deliberately uses deterministic agent logic for reproducibility. It does **not** make live Gemini calls.

## Windows setup
1. Install Python 3.11 or 3.12 and enable **Add Python to PATH**.
2. Open a terminal in this folder.
3. `py -m venv .venv`
4. `.venv\Scripts\activate`
5. `python -m pip install -r requirements.txt`
6. `python run.py`
7. Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs

## Tests
`python -m pytest -v`

## Evidence for report and video
Classify glass bottle, lithium battery, and ceramic mug; open `/api/agent/state` and `logs/ecosort.log`. Demonstrate failure by running the tests for timeout and iteration limit. Capture genuine screenshots after running locally. Show messages and final output in a 3–5 minute screen recording.

## Architecture
Browser → FastAPI → Orchestrator → ClassifierAgent → ValidatorAgent → Orchestrator → JSON result. Messages have message_id, sender, receiver, intent, content and constraints. The orchestrator records received/sent messages and the trace ID.

## Limitations
Rule coverage is small and is not authoritative local council policy. State is in-memory and resets on restart. The timeout stops waiting but cannot forcibly terminate a running Python thread. Confidence values are fixed rule scores, not measured probabilities.

## Academic integrity
Use this project as a working starting point, understand the code, run the tests, capture your own evidence and accurately disclose AI assistance.
