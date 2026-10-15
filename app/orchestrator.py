import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from threading import RLock
from uuid import uuid4
from app.schemas import AgentMessage, WasteRequest, WasteAdvice
from app.agents import ClassifierAgent, ValidatorAgent

logger=logging.getLogger("ecosort")

class Orchestrator:
    def __init__(self, max_iterations=4, timeout_seconds=3):
        self.agents={"classifier":ClassifierAgent(),"validator":ValidatorAgent()}
        self.max_iterations=max_iterations
        self.timeout_seconds=timeout_seconds
        self.lock=RLock()
        self.history=[]
        self.runs=0
        self.errors=0

    def _dispatch(self,message):
        if message.receiver not in self.agents:
            raise ValueError(f"Invalid receiver: {message.receiver}")
        # Per-call executor with non-blocking shutdown: timeout is enforced at routing boundary.
        executor=ThreadPoolExecutor(max_workers=1)
        future=executor.submit(self.agents[message.receiver].handle,message)
        try:
            return future.result(timeout=self.timeout_seconds)
        except FutureTimeout as exc:
            future.cancel()
            raise TimeoutError("Agent response exceeded timeout") from exc
        finally:
            executor.shutdown(wait=False,cancel_futures=True)

    def _record(self,message,trace):
        logger.info("MESSAGE trace=%s sender=%s receiver=%s intent=%s payload=%s",trace,message.sender,message.receiver,message.intent,message.model_dump_json())
        with self.lock:
            self.history.append({"trace_id":trace,**message.model_dump()})
            self.history=self.history[-100:]

    def run(self,request:WasteRequest)->WasteAdvice:
        trace=str(uuid4()); messages=[]
        current=AgentMessage(sender="orchestrator",receiver="classifier",intent="classify",content=request.model_dump())
        try:
            for iteration in range(self.max_iterations):
                self._record(current,trace);messages.append(current)
                if current.receiver=="orchestrator":
                    if current.intent!="approved":raise ValueError("Unexpected terminal message")
                    with self.lock:self.runs+=1
                    return WasteAdvice(**current.content,status="validated",trace_id=trace,messages=messages)
                outgoing=self._dispatch(current)
                if outgoing.sender!=current.receiver:
                    raise ValueError("Message sender does not match invoked agent")
                current=AgentMessage.model_validate(outgoing.model_dump())
            raise RuntimeError("Maximum iteration limit reached")
        except Exception as exc:
            logger.exception("FALLBACK trace=%s error=%s",trace,exc)
            with self.lock:self.errors+=1;self.runs+=1
            return WasteAdvice(category="Unknown",confidence=0.0,reason="A processing or validation error occurred.",steps=["Check an official council or waste-service source."],warning="Automatic advice was unavailable; do not guess for hazardous waste.",tool_rule="Fallback: no verified classification available.",status="fallback",trace_id=trace,messages=messages)

    def state(self):
        with self.lock:return {"runs":self.runs,"errors":self.errors,"recent_messages":self.history[-30:]}
    def reset(self):
        with self.lock:self.runs=0;self.errors=0;self.history=[]
