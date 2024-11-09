import re
import sys
from math import exp

def parse_arguments():
    args = sys.argv[1:]
    params = {"input1": "input1.txt", "output1": "output.txt", "input2": "operations.txt", "output2": None}
    for arg in args:
        key, _, value = arg.partition("=")
        if key in params:
            params[key] = value.strip()
    return params

def write_error(message):
    with open("error.txt", 'w', encoding="utf-8") as file:
        file.write(message)

def load_graph(filename):
    pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
    graph = {}
    in_degrees = {}
    out_degrees = {}
    unique_edges = set()
    order_check = {}
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read().replace("\n", "")
        matches = re.findall(pattern, content)
        if len(matches) == 0:
            return f"Ошибка: неверные данные во входном файле", None, None, None
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

def load_operations(filename):
    operations = {}
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read().strip()
        matches = re.findall(r'(\d+)\s*:\s*([\d+*exp]+)', content)
        for vertex, operation in matches:
            operations[int(vertex)] = operation
    return operations

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

def evaluate_expression(graph, operations, in_degrees, out_degrees, params):
    sinks = [node for node in in_degrees if node not in out_degrees]
    if not sinks:
        return "Ошибка: граф не имеет стоковой вершины.", None

    def evaluate(vertex):
        children = sorted(graph.get(vertex, []), key=lambda x: x[1])
        children_values  = [evaluate(child) for child, _ in children]
        operation = operations.get(vertex)
        
        if operation in ('+', '*', "exp") and not children_values :
            write_error(f"Ошибка: операция '{operation}' для вершины {vertex} требует аргументов, но дочерние вершины отсутствуют.")
            sys.exit()

        if operation is None:
            write_error(f"Операция для вершины {vertex} не найдена.")
            sys.exit()

        if operation == "+":
            return sum(children_values )
        elif operation == "*":
            result = 1
            for val in children_values :
                result *= val
            return result
        elif operation == "exp":
            try:
                return exp(children_values [0]) if children_values else 1
            except OverflowError:
                with open(params["output1"], "w", encoding="utf-8") as outfile:
                    outfile.write("Inf")
                sys.exit()
        else:
            try:
                return float(operation)
            except ValueError:
                write_error(f"Неподдерживаемая операция или константа для вершины {vertex}: {operation}")
                sys.exit()
    evaluated_sinks = [str(evaluate(sink)) for sink in sinks]
    return None, ", ".join(evaluated_sinks)

def main():
    params = parse_arguments()

    try:
        error, graph, in_degrees, out_degrees = load_graph(params["input1"])
        operations = load_operations(params["input2"])
        if error:
            write_error(error)
            return
    except FileNotFoundError as e:
        write_error(f"Ошибка: файл не найден: {str(e)}")
        return
    except ValueError as e:
        write_error(f"Ошибка в формате файла: {str(e)}")
        return

    if has_cycle(graph):
        write_error("Ошибка: граф содержит циклы.")
        return

    try:
        error, result = evaluate_expression(graph, operations, in_degrees, out_degrees, params)
    except ValueError as e:
        write_error(f"Ошибка при вычислении выражения: {str(e)}")
        return

    if error:
        write_error(error)
        return

    with open(params["output1"], "w", encoding="utf-8") as outfile:
        outfile.write(result)
    
    print(f"Результат успешно сохранён в {params['output1']}.")

if __name__ == "__main__":
    main()
