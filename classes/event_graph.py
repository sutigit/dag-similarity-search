# ...existing code...
from typing import Dict, Tuple, List, Hashable
import networkx as nx
import matplotlib.pyplot as plt
from .node import Node

class EventGraph:
    def __init__(self):
        # node id can be str/int/whatever is hashable
        self.nodes: Dict[Hashable, Node] = {}
        # store edges as pairs of node ids
        self.edges: List[Tuple[Hashable, Hashable]] = []

    def add_node(self, node: Node):
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id!r} already exists")
        self.nodes[node.id] = node

    def add_edge(self, from_node: Node, to_node: Node):
        if from_node.id in self.nodes and to_node.id in self.nodes:
            self.edges.append((from_node.id, to_node.id))
        else:
            raise ValueError("Both nodes must be added before creating an edge.")


    def print_nodes(self):
        if not self.nodes:
            print("No nodes")
            return
        for nid, node in self.nodes.items():
            # Node has id: int and event_type: str
            print(f"{nid!r}: {node.event_type}")

    def visualize(self):
        G = nx.DiGraph()
        for node in self.nodes.values():
            # Node has id and event_type; use event_type as the label
            label = node.event_type if getattr(node, "event_type", None) is not None else str(node.id)
            G.add_node(node.id, label=label)
        G.add_edges_from(self.edges)
        pos = nx.spring_layout(G)
        labels = {n: d.get('label', str(n)) for n, d in G.nodes(data=True)}
        nx.draw(G, pos, with_labels=True, labels=labels, arrows=True, node_color='lightblue', node_size=1000)
        plt.show()