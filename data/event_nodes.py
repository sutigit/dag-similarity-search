from event_types import event_types

class EventNodes:
    def __init__(self):
        self.nodes = []
        
        self.create_nodes()
        
    def create_nodes(self):
        for event_id in event_types:
            et_name = event_types[event_id]
            self.nodes.append(et_name)
            
            
evn = EventNodes()
print(evn.nodes)