from graph_manager import GraphManager

graph = GraphManager()

equipment = graph.get_equipment("P901")

print(equipment)

graph.close()