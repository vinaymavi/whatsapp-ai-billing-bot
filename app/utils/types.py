from typing import Any, Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class LLMResponse(TypedDict, total=False):
    type: Literal["tool_calls", "message"]
    text: Optional[str]  # Present if type is "message"
    tool_calls: Optional[Any]  # Present if type is "tool_calls"


class VectorDBInvoiceData(BaseModel):
    invoice_id: str = Field(..., description="The unique identifier for the invoice")
    invoice_date: str = Field(..., description="The date of the invoice")
    customer_id: str = Field(..., description="The unique identifier for the customer")
    customer_name: str = Field(..., description="The name of the customer")
    customer_address: str = Field(..., description="The address of the customer")
    amount: float = Field(..., description="The total amount of the invoice")
    status: str = Field(..., description="The current status of the invoice")
    provider: str = Field(..., description="The provider of the invoice")
    summary: str = Field(..., description="A brief summary of the invoice combination of line items and other fields")