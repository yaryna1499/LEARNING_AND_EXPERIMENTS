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

def order_dfs(graph, start_node, visited=None):
    if visited is None:
        visited = set()

    order = list()
    if start_node not in order:
        order.append(start_node)
        visited.add(start_node)
        for node in graph[start_node]:
            if node not in visited:
                order.extend(order_dfs(graph, node, visited))
    return order

print(order_dfs(simple_graph, "A"))