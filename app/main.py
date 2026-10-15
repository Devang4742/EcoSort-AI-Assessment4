import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.schemas import WasteRequest, WasteAdvice
from app.orchestrator import Orchestrator

BASE=Path(__file__).resolve().parent.parent
(BASE/"logs").mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",handlers=[logging.StreamHandler(),logging.FileHandler(BASE/"logs"/"ecosort.log",encoding="utf-8")])
app=FastAPI(title="EcoSort AI | Two-Agent Recycling Assistant",version="2.0.0",description="Classifier → Validator message routing with guardrails and logs")
app.mount("/static",StaticFiles(directory=BASE/"static"),name="static")
engine=Orchestrator()
@app.get("/",include_in_schema=False)
def homepage():return FileResponse(BASE/"static"/"index.html")
@app.get("/health",tags=["System"])
def health():return {"status":"ok","website":"/","docs":"/docs","mode":"deterministic two-agent"}
@app.post("/api/agent/classify_waste",response_model=WasteAdvice,tags=["Agent"])
def classify(request:WasteRequest):return engine.run(request)
@app.get("/api/agent/state",tags=["Agent"])
def state():return engine.state()
@app.post("/api/agent/reset_state",tags=["Agent"])
def reset():engine.reset();return {"status":"reset"}
