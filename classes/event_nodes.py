from typing import DefaultDict, List
from collections import defaultdict
from data.event_types import event_types
from .node import Node

class EventNodes:
    def __init__(self):
        self.nodes: DefaultDict[str, Node] = {}
        
        self.create_nodes()
            
    def print_nodes(self) -> None:
        if not self.nodes:
            return "No nodes"

        for _, node in self.nodes.items():
            print(node)

        
    def create_nodes(self):
        for et_id, et_name in event_types.items():
            node = Node(et_id, et_name)
            self.nodes[et_name] = node
            