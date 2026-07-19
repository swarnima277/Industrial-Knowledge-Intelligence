from graph_manager import GraphManager

graph = GraphManager()

graph.create_equipment(
    "P500",
    "Hydraulic Pump",
    "Running"
)

graph.create_engineer(
    "E500",
    "Bhumika"
)

graph.assign_engineer(
    "P500",
    "E500"
)

graph.search_equipment(
    "P500"
)

graph.close()