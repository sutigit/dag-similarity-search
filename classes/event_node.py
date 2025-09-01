import uuid
from typing import Dict

class EventNode:
    def __init__(self, event_type: str, event_attributes: Dict[str, str] = {}) -> None:
        self.id = uuid.uuid4().hex  # 32-char hex string
        self.event_type = event_type
        self.event_attributes = event_attributes

    def __str__(self) -> str:
        return f'id: {self.id}, event_type: {self.event_type}'
