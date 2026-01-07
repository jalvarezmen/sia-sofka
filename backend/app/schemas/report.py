"""Report schemas."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ReportRequest(BaseModel):
    """Schema for report generation request."""
    format: str = "json"  # pdf, html, json


class ReportResponse(BaseModel):
    """Schema for report response."""
    content: str | bytes
    filename: str
    content_type: str
    
    class Config:
        json_encoders = {
            bytes: lambda v: v.decode("latin-1") if isinstance(v, bytes) else v
        }


