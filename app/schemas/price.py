from pydantic import BaseModel, Field
from datetime import datetime

class PriceRecord(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(..., gt=0)
