import hashlib
from typing import Tuple, Hashable
from data.attribute_weights import attribute_weights
from classes.event_graph import EventGraph

def stable_hash(label: str):
    h = hashlib.blake2b(label.encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(h, "little")

def WL_neighborhood_label(graph: EventGraph, iterations: int = 3, inspect: bool = False):
    labels = {node: stable_hash(graph.nodes[node].event_type) for node in graph.nodes}
    history = [labels.copy()]
    
    for _ in range(iterations):
        new_core = {}
        for node in graph.nodes:
            nbrs = graph.adj_list.get(node, [])  # safe default
            neighbor_labels = [labels[nbr] for nbr in nbrs if nbr in labels]
            
            # deterministic sort even if labels later become non-strings
            neighbor_labels.sort(key=repr)

            signature = (labels[node], tuple(neighbor_labels))

            if inspect:
                # keep inspection output readable and still a string so next iter is safe
                new_label = signature
            else:
                new_label = stable_hash(repr(signature))
            
            new_core[node] = new_label
            
        labels = new_core
        history.append(labels.copy())
        
    return history  # list of dicts for it=0..h

def attributes_hash(graph: EventGraph, inspect: bool = False):
    attr_features = []
    
    for node in graph.nodes.values():
        for (attr_name, attr_value) in node.event_attributes.items():
            feat_key = (node.event_type, attr_name, attr_value)
            feat_hash = stable_hash(repr(feat_key))
            attr_features.append((feat_hash, attribute_weights[attr_name]))
    
    return attr_features
        

def graph_to_fingerprint(graph: EventGraph, D=1024):
    labels_h_stack = WL_neighborhood_label(graph)
    attr_features = attributes_hash(graph)
    
    fingerprint = [0.0] * D
    
    # structural contribution
    for labels in labels_h_stack:          # use 0..h
        for feat in labels.values():
            idx = feat % D
            fingerprint[idx] = 1.0       # or +=1 for counts
            
    # attribute contribution
    for (feat_hash, weight) in attr_features:
        idx = feat_hash % D
        fingerprint[idx] = weight
    
    return fingerprint