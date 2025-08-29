class Node:
    def __init__(self, id, label=None):
        self.id = id
        self.label = label if label else str(id)
