from classes.event_node import EventNode
from classes.event_graph import EventGraph

def generate_target_graphs():

    event_types = [
        {
            "event_type": "started_school",
            "event_attributes": {"age": 6, "time": "2005-09", "education_level": "primary"},
        },
        {
            "event_type": "finished_school",
            "event_attributes": {"age": 18, "time": "2017-05", "education_level": "highschool"},
        },
        {
            "event_type": "started_work",
            "event_attributes": {"age": 22, "time": "2019-06", "industry": "tech", "position": "junior", "company": "Acme Corp"},
        },
        {
            "event_type": "new_family_member",
            "event_attributes": {"age": 30, "time": "2022-01"},
        },
        {
            "event_type": "bought_house",
            "event_attributes": {"age": 28, "time": "2021-07"},
        },
        {
            "event_type": "got_married",
            "event_attributes": {"age": 29, "time": "2021-06"},
        },
        {
            "event_type": "got_divorced",
            "event_attributes": {"age": 35, "time": "2023-03"},
        },
        {
            "event_type": "had_child",
            "event_attributes": {"age": 30, "time": "2022-02"},
        },
        {
            "event_type": "moved_city",
            "event_attributes": {"age": 27, "time": "2020-10", "city": "Chiang Mai"},
        },
        {
            "event_type": "moved_country",
            "event_attributes": {"age": 33, "time": "2024-01", "country": "Australia"},
        },
        {
            "event_type": "graduated_highschool",
            "event_attributes": {"age": 18, "time": "2017-05"},
        },
        {
            "event_type": "graduated_university",
            "event_attributes": {"age": 22, "time": "2021-06"},
        },
    ]

    # create one EventNode per event type
    nodes = [EventNode(event_type=e['event_type'], event_attributes=e['event_attributes']) for e in event_types]

    # convenience variables (n0..n11) if you want quick access in the REPL/notebook
    for i, node in enumerate(nodes):
        globals()[f"n{i}"] = node

    # optional: map index -> node
    nodes_by_index = {i: node for i, node in enumerate(nodes)}

    g0 = EventGraph()
    g1 = EventGraph()
    g2 = EventGraph()
    g3 = EventGraph()
    g4 = EventGraph()
    g5 = EventGraph()
    g6 = EventGraph()

    edges_base = [
        (0, 1),   # started_school -> finished_school
        (1, 10),  # finished_school -> graduated_highschool
        (1, 11),  # finished_school -> graduated_university
        (10, 2),  # graduated_highschool -> started_work
        (11, 2),  # graduated_university -> started_work
        (2, 4),   # started_work -> bought_house
        (2, 5),   # started_work -> got_married
        (5, 7),   # got_married -> had_child
        (7, 3),   # had_child -> new_family_member
        (4, 8),   # bought_house -> moved_city
        (8, 9),   # moved_city -> moved_country
        (6, 3),   # got_divorced -> new_family_member (alternate family change)
    ]

    # build g0 exactly from the base edges
    for n in nodes_by_index.values():
        g0.add_node(n)
    for a, b in edges_base:
        g0.add_edge(nodes_by_index[a], nodes_by_index[b])

    # g1: base + one extra plausible edge
    for n in nodes_by_index.values():
        g1.add_node(n)
    extra_edges_g1 = [(2, 8)]  # started_work -> moved_city
    for a, b in edges_base + extra_edges_g1:
        g1.add_edge(nodes_by_index[a], nodes_by_index[b])

    # g2: base, but bought_house -> new_family_member instead of bought_house -> moved_city
    for n in nodes_by_index.values():
        g2.add_node(n)
    edges_g2 = [e for e in edges_base if e != (4, 8)]
    edges_g2.append((4, 3))  # bought_house -> new_family_member
    for a, b in edges_g2:
        g2.add_edge(nodes_by_index[a], nodes_by_index[b])

    # Additional target graphs with slightly more variation

    # g3: like g1 but also link got_married -> moved_city (extra plausible shortcut)
    g3 = EventGraph()
    for n in nodes_by_index.values():
        g3.add_node(n)
    extra_edges_g3 = extra_edges_g1 + [(5, 8)]  # started_work->moved_city, got_married->moved_city
    for a, b in edges_base + extra_edges_g3:
        g3.add_edge(nodes_by_index[a], nodes_by_index[b])

    # g4: reorder buying-house path: remove started_work->bought_house, make bought_house come after marriage
    g4 = EventGraph()
    for n in nodes_by_index.values():
        g4.add_node(n)
    edges_g4 = [e for e in edges_base if e != (2, 4)]  # drop started_work->bought_house
    edges_g4.append((5, 4))  # got_married -> bought_house
    for a, b in edges_g4:
        g4.add_edge(nodes_by_index[a], nodes_by_index[b])

    # g5: alternative city/house order: moved_city happens before bought_house (simulate relocating first)
    g5 = EventGraph()
    for n in nodes_by_index.values():
        g5.add_node(n)
    edges_g5 = [e for e in edges_base if e != (4, 8)]  # drop bought_house->moved_city
    edges_g5.append((8, 4))  # moved_city -> bought_house (different life path)
    for a, b in edges_g5:
        g5.add_edge(nodes_by_index[a], nodes_by_index[b])

    # g6: add a couple of extra long-range plausible edges to increase variation
    g6 = EventGraph()
    for n in nodes_by_index.values():
        g6.add_node(n)
    extra_edges_g6 = [(11, 8), (3, 9)]  # graduated_university->moved_city, new_family_member->moved_country
    for a, b in edges_base + extra_edges_g6:
        g6.add_edge(nodes_by_index[a], nodes_by_index[b])

    target_graphs = [g0, g1, g2, g3, g4, g5, g6]
    
    return target_graphs