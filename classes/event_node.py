import uuid

class EventNode:
    def __init__(self, event_type: str) -> None:
        self.id = uuid.uuid4().hex  # 32-char hex string
        self.event_type = event_type

    def __str__(self) -> str:
        return f'id: {self.id}, event_type: {self.event_type}'
