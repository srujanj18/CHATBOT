from typing import TypedDict, List
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    messages: List[AnyMessage] 