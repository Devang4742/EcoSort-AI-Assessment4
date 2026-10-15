from fastapi.testclient import TestClient
from app.main import app
from app.orchestrator import Orchestrator
from app.schemas import WasteRequest,AgentMessage
from app.agents import ClassifierAgent,ValidatorAgent
import pytest
client=TestClient(app)

def test_home():assert client.get('/').status_code==200
def test_docs():assert client.get('/docs').status_code==200
def test_health():assert client.get('/health').json()['status']=='ok'
def test_classification():
 d=client.post('/api/agent/classify_waste',json={'item':'glass bottle'}).json()
 assert d['category']=='Recycling' and d['status']=='validated' and len(d['messages'])==3

def test_battery():assert client.post('/api/agent/classify_waste',json={'item':'lithium battery'}).json()['category']=='Special drop-off'
def test_unknown():assert client.post('/api/agent/classify_waste',json={'item':'broken ceramic mug'}).json()['category']=='Unknown'
def test_validation():assert client.post('/api/agent/classify_waste',json={'item':'x'}).status_code==422
def test_message_schema():
 with pytest.raises(Exception):AgentMessage(sender='bad',receiver='classifier',intent='classify',content={})
def test_wrong_receiver():
 with pytest.raises(ValueError):ClassifierAgent().handle(AgentMessage(sender='orchestrator',receiver='validator',intent='classify',content={'item':'paper'}))
def test_iteration_fallback():assert Orchestrator(max_iterations=1).run(WasteRequest(item='paper')).status=='fallback'
def test_timeout_fallback():
 import time
 e=Orchestrator(timeout_seconds=.001)
 e.agents['classifier'].handle=lambda msg:(time.sleep(.03),None)[1]
 assert e.run(WasteRequest(item='paper')).status=='fallback'
def test_invalid_route_fallback():
 e=Orchestrator();e.agents.pop('classifier')
 assert e.run(WasteRequest(item='paper')).status=='fallback'
def test_bad_output_fallback():
 e=Orchestrator();e.agents['classifier'].handle=lambda msg:'not a message'
 assert e.run(WasteRequest(item='paper')).status=='fallback'
def test_reset():
 e=Orchestrator();e.run(WasteRequest(item='paper'));e.reset();assert e.state()['runs']==0
