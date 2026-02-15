from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import json

class ExtractionRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    accuracy: float = 0.0
    line_item_count: int = 0
    currency: str = "INR"
    units: str = "Cr"
    json_data: str  # Store the full financial data as JSON

    def get_data(self) -> Dict[str, Any]:
        return json.loads(self.json_data)

    @classmethod
    def from_data(cls, filename: str, data: Dict[str, Any]):
        items = data.get("items", [])
        avg_confidence = sum(item.get("confidence", 0) for item in items) / len(items) if items else 0
        
        return cls(
            filename=filename,
            accuracy=avg_confidence,
            line_item_count=len(items),
            currency=data.get("currency", "INR"),
            units=data.get("units", "Cr"),
            json_data=json.dumps(data)
        )
