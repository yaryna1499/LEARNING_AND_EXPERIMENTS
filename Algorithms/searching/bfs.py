graph = {
    "A": ['S'],
    "B": ['C', 'D','S'],
    "C": ['B', 'J'],
    "D": ['B', 'G', 'S'],
    "E": ['G', 'S'],
    "F": ['G', 'H'],
    "G": ['D', 'E', 'F', 'H', 'J'],
    "H": ['F', 'G', 'I'],
    "I": ['H', 'J'],
    "J": ['C', 'G', 'I'],
    "S": ['A', 'B', 'D', 'E']
}

def order_bfs(graph, start_node):
    visited = set()
    queue = list()
    order = list()
    queue.append(start_node)
    visited.add(start_node)
    while queue:
        vertex = queue.pop(0)
        order.append(vertex)
        for node in graph[vertex]:
            if node not in visited:
                visited.add(node)
                queue.append(node)
    return order


simple_graph = {
    "A": ["B"],
    "B": ["A", "C", "D"],
    "C": ["B", "E"],
    "D": ["B", "F"],
    "E": ["C", "G"],
    "F": ["D", "H"],
    "G": ["E"],
    "H": ["F"]
}

print(order_bfs(simple_graph, "A"))
