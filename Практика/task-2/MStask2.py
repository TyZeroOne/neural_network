import sys
import re

def parse_arguments():
    args = sys.argv[1:]
    params = {"input1": "input1.txt", "output1": "output.txt", "input2": None, "output2": None}
    for arg in args:
        key, _, value = arg.partition("=")
        if key in params:
            params[key] = value.strip()
    return params

def write_error(exp):
    with open("error.txt", 'w', encoding="utf-8") as file:
        file.write(exp)

def validate_and_build_graph(file_content):
    pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
    graph = {}
    in_degrees = {}
    out_degrees = {}
    order_check = {}
    matches = re.findall(pattern, file_content.replace("\n", "").strip())
    if len(matches) == 0:
        return f"Ошибка: неверные данные во входном файле", None, None, None
    unique_edges = set()
    for match in matches:
        a, b, n = map(int, match)
        edge = (a, b)

        if edge in unique_edges:
            return f"Ошибка: повторяющаяся дуга между вершинами ({a}, {b})", None, None, None
        unique_edges.add(edge)

        if b not in order_check:
            order_check[b] = set()
        if n in order_check[b]:
            return f"Ошибка: повторяющийся номер дуги {n} для вершины {b}", None, None, None
        order_check[b].add(n)

        if b not in graph:
            graph[b] = []
        graph[b].append((a, n))

        in_degrees[b] = in_degrees.get(b, 0) + 1
        out_degrees[a] = out_degrees.get(a, 0) + 1

    for vertex, orders in order_check.items():
        if sorted(orders) != list(range(1, len(orders) + 1)):
            return f"Ошибка: у вершины {vertex} нарушена последовательность номеров дуг", None, None, None

    return None, graph, in_degrees, out_degrees

def has_cycle(graph):
    visited = set()
    stack = set()
    
    def dfs(vertex):
        if vertex in stack:
            return True
        if vertex in visited:
            return False

        visited.add(vertex)
        stack.add(vertex)
        for neighbor, _ in graph.get(vertex, []):
            if dfs(neighbor):
                return True
        stack.remove(vertex)
        return False
    for node in graph:
        if dfs(node):
            return True
    return False

def build_function_representation(graph, in_degrees, out_degrees):
    sinks = [node for node in in_degrees if node not in out_degrees]

    def build_expression(vertex):
        children = sorted(graph.get(vertex, []), key=lambda x: x[1])
        children_expr = ", ".join([f"{build_expression(child)}" for child, _ in children])
        return f"{vertex}({children_expr})" if children else f"{vertex}"
    return ", ".join(build_expression(sink) for sink in sinks)

def main():
    params = parse_arguments()
    
    try:
        with open(params["input1"], "r", encoding="utf-8") as infile:
            file_content = infile.read()
    except FileNotFoundError:
        write_error((f"Ошибка: входной файл {params['input1']} не найден."))
        return

    error, graph, in_degrees, out_degrees = validate_and_build_graph(file_content)
    if error:
        write_error(error)
        return

    if has_cycle(graph):
        write_error("Ошибка: граф содержит циклы.")
        return

    function_representation = build_function_representation(graph, in_degrees, out_degrees)

    with open(params["output1"], "w", encoding="utf-8") as outfile:
        outfile.write(function_representation)
    
    print(f"Функция успешно сохранена в {params['output1']}.")

if __name__ == "__main__":
    main()