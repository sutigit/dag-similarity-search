from typing import List
from data.event_types import event_types
from .node import Node

class EventNodes:
    def __init__(self):
        self.nodes: List[Node] = []
        
        self.create_nodes()
        
    def create_nodes(self):
        for et_id, et_name in event_types.items():
            node = Node(et_id, et_name)
            self.nodes.append(node)
            