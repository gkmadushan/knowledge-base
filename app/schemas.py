from datetime import time
from pydantic import BaseModel, Field
from typing import List, Optional

class CreateSchedule(BaseModel):
    id: Optional[str]
    frequency: str
    start: str
    terminate: str
    reference: str
    active: bool