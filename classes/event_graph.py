from __future__ import annotations
from typing import Dict, Set, Hashable, Protocol, List, Tuple
import networkx as nx
import matplotlib.pyplot as plt

class NodeLike(Protocol):
    event_type: str  # non-optional
    id: Hashable

class EventGraph:
    def __init__(self) -> None:
        self.nodes: Dict[Hashable, NodeLike] = {}
        self.adj_list: Dict[Hashable, Set[Hashable]] = {}

    # ---- core API ----
    def add_node(self, node: NodeLike) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id!r} already exists")
        self.nodes[node.id] = node
        self.adj_list[node.id] = set()
        
    def remove_node(self, node_id: Hashable) -> None:
        """Remove a node and all its incident edges by id."""
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id!r} not found")

        # remove outbound edges
        self.adj_list.pop(node_id, None)

        # remove inbound edges
        for nbrs in self.adj_list.values():
            nbrs.discard(node_id)

        # remove node record
        self.nodes.pop(node_id, None)

    def add_edge(self, from_node: NodeLike, to_node: NodeLike) -> None:
        u, v = from_node.id, to_node.id
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Both nodes must be added before creating an edge.")
        if u == v:
            raise ValueError("Self-loops are not allowed in a DAG.")
        if self._would_create_cycle(u, v):
            raise ValueError(f"Edge {u!r}->{v!r} would create a cycle.")
        self.adj_list[u].add(v)

    def remove_edge(self, from_id: Hashable, to_id: Hashable) -> None:
        if from_id in self.adj_list:
            self.adj_list[from_id].discard(to_id)

    def insert_between(self, u: Hashable, v: Hashable, new_node: NodeLike) -> None:
        if v not in self.adj_list.get(u, set()):
            raise ValueError(f"No edge {u!r}->{v!r} to split.")
        self.add_node(new_node)
        self.remove_edge(u, v)
        self.add_edge(self.nodes[u], new_node)
        self.add_edge(new_node, self.nodes[v])

    # ---- new convenience methods ----
    def to_edge_list(self, *, sort: bool = False) -> List[Tuple[Hashable, Hashable]]:
        """Return edges as (u,v) tuples. Optional deterministic sort."""
        edges: List[Tuple[Hashable, Hashable]] = []
        for u, nbrs in self.adj_list.items():
            for v in nbrs:
                edges.append((u, v))
        if sort:
            edges.sort(key=lambda e: (repr(e[0]), repr(e[1])))
        return edges

    def to_networkx(self) -> nx.DiGraph:
        """Build a NetworkX DiGraph with node attribute 'label'=event_type."""
        G = nx.DiGraph()
        for node in self.nodes.values():
            G.add_node(node.id, label=node.event_type)
        G.add_edges_from(self.to_edge_list())
        return G

    # ---- utils ----
    def successors(self, node_id: Hashable):
        return iter(self.adj_list.get(node_id, set()))

    def print_nodes(self) -> None:
        if not self.nodes:
            print("No nodes"); return
        for nid, node in self.nodes.items():
            print(f"{nid!r}: {node.event_type}")

    def visualize(self) -> None:
        G = self.to_networkx()
        pos = nx.spring_layout(G)
        labels = {n: d.get("label", str(n)) for n, d in G.nodes(data=True)}
        # shorten long labels
        labels = {n: (lbl if len(lbl) <= 18 else lbl[:15] + "...") for n, lbl in labels.items()}
        nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=400)
        nx.draw_networkx_edges(G, pos, arrows=True)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        plt.axis("off"); plt.tight_layout(); plt.show()
    


    # ---- internal ----
    def _would_create_cycle(self, u: Hashable, v: Hashable) -> bool:
        if u == v:
            return True
        seen: Set[Hashable] = set()
        stack = [v]
        while stack:
            x = stack.pop()
            if x == u:
                return True
            if x in seen:
                continue
            seen.add(x)
            stack.extend(self.adj_list.get(x, ()))
        return False
