class Node:
    def __init__(self, id: int, event_type: str) -> None:
        self.id = id
        self.event_type = event_type
        
    def __str__(self):
        return f'id: {self.id}, event_type: {self.event_type}'
