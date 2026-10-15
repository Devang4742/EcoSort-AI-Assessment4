from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

class WasteRequest(BaseModel):
    item: str = Field(min_length=2,max_length=120)
    condition: str = Field(default="unspecified",max_length=200)
    location_note: str = Field(default="",max_length=200)

class AgentMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: Literal["orchestrator","classifier","validator"]
    receiver: Literal["orchestrator","classifier","validator"]
    intent: Literal["classify","review","result","approved","rejected"]
    content: dict[str, Any]
    constraints: dict[str, Any] = Field(default_factory=lambda: {"format":"json"})

class WasteAdvice(BaseModel):
    category: str
    confidence: float = Field(ge=0,le=1)
    reason: str
    steps: list[str]
    warning: str
    tool_rule: str
    status: str
    trace_id: str
    messages: list[AgentMessage]
