from typing import Any, Dict, List, Literal, Optional, TypedDict


class LLMResponse(TypedDict, total=False):
    type: Literal["tool_calls", "message"]
    text: Optional[str]  # Present if type is "message"
    tool_calls: Optional[Any]  # Present if type is "tool_calls"