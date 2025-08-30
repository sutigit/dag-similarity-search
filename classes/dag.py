import networkx as nx
import matplotlib.pyplot as plt
from classes.node import Node

class DAG:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node):
        self.nodes[node.id] = node

    def add_edge(self, from_id, to_id):
        if from_id in self.nodes and to_id in self.nodes:
            self.edges.append((from_id, to_id))
        else:
            raise ValueError("Both nodes must be added before creating an edge.")

    def print_nodes(self):
        print("Nodes in DAG:")
        for node in self.nodes.values():
            print(f"ID: {node.id}, Label: {node.label}")

    def visualize(self):
        G = nx.DiGraph()
        for node in self.nodes.values():
            G.add_node(node.id, label=node.label)
        G.add_edges_from(self.edges)
        pos = nx.spring_layout(G)
        labels = {n: d['label'] for n, d in G.nodes(data=True)}
        nx.draw(G, pos, with_labels=True, labels=labels, arrows=True, node_color='lightblue', node_size=1000)
        plt.show()
