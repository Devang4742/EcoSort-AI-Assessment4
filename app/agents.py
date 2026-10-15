from app.schemas import AgentMessage
from app.tools import lookup_recycling_rule

class ClassifierAgent:
    name = "classifier"
    def handle(self, message: AgentMessage) -> AgentMessage:
        if message.receiver != self.name or message.intent != "classify":
            raise ValueError("Classifier received unexpected message")
        item = message.content["item"]
        condition = message.content.get("condition", "unspecified")
        rule = lookup_recycling_rule(item=item,condition=condition)
        return AgentMessage(sender=self.name, receiver="validator", intent="review", content={"item":item,"condition":condition,"location_note":message.content.get("location_note",""),"rule":rule})

class ValidatorAgent:
    name = "validator"
    def handle(self, message: AgentMessage) -> AgentMessage:
        if message.receiver != self.name or message.intent != "review":
            raise ValueError("Validator received unexpected message")
        c=message.content; r=c["rule"]
        if not isinstance(r,dict) or not all(k in r for k in ("category","confidence","rule","warning")):
            raise ValueError("Malformed classification rule")
        if not isinstance(r["confidence"],(int,float)) or not 0<=r["confidence"]<=1:
            raise ValueError("Invalid confidence")
        category=r["category"]
        steps=[r["rule"], "Check official local council instructions before disposal."]
        if category in ("Special drop-off","E-waste"):
            steps.insert(0,"Keep this item out of ordinary mixed recycling.")
        if category=="Unknown":
            steps=["Do not assume this item is recyclable.","Consult an official council or waste-service guide."]
        warning=r["warning"]
        if c.get("location_note"):
            warning += " Location was provided as context only; no local council database was queried."
        return AgentMessage(sender=self.name,receiver="orchestrator",intent="approved",content={"category":category,"confidence":float(r["confidence"]),"reason":f"Deterministic rule matched for {c['item']}." if category!="Unknown" else "No supported rule matched the supplied item.","steps":steps,"warning":warning,"tool_rule":r["rule"]})
