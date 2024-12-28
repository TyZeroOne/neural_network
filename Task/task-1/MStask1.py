import sys
import re
import xml.etree.ElementTree as ET

def parse_arguments():
    args = sys.argv[1:]
    params = {"input1": "input.txt", "output1": "output.xml", "input2": None, "output2": None}
    for arg in args:
        key, _, value = arg.partition("=")
        if key in params:
            params[key] = value.strip()
    return params

def write_error(exp):
    with open("error.txt", 'w', encoding="utf-8") as file:
        file.write(exp)

def validate_and_parse_graph(file_content):
    graph = {"vertices": set(), "arcs": []}
    pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
    order_check = {}
    matches = re.findall(pattern, file_content.replace("\n", "").strip())
    if len(matches) == 0:
        return f"Ошибка: неверные данные во входном файле"
    unique_edges = set()
    for match in matches:
        a, b, n = map(int, match)
        graph["vertices"].add(a)
        graph["vertices"].add(b)
        arc = (a, b, n)
        edge = (a, b)
        graph["arcs"].append(arc)

        if edge in unique_edges:
            return f"Ошибка: повторяющаяся дуга между вершинами ({a}, {b})"
        unique_edges.add(edge)
        
        if b not in order_check:
            order_check[b] = set()
        if n in order_check[b]:
            return f"Ошибка: повторяющийся номер дуги {n} для вершины {b}"
        order_check[b].add(n)
    
    for vertex, orders in order_check.items():
        if sorted(orders) != list(range(1, len(orders) + 1)):
            return f"Ошибка: у вершины {vertex} нарушена последовательность номеров дуг"
    
    return graph

def build_xml(graph):
    root = ET.Element("graph")
    for vertex in sorted(graph["vertices"]):
        vertex_elem = ET.SubElement(root, "vertex")
        vertex_elem.text = f"v{vertex}"
    
    for arc in graph["arcs"]:
        arc_elem = ET.SubElement(root, "arc")
        from_elem = ET.SubElement(arc_elem, "from")
        from_elem.text = f"v{arc[0]}"
        to_elem = ET.SubElement(arc_elem, "to")
        to_elem.text = f"v{arc[1]}"
        order_elem = ET.SubElement(arc_elem, "order")
        order_elem.text = str(arc[2])
    
    return ET.ElementTree(root)

def main():
    params = parse_arguments()
    
    try:
        with open(params["input1"], "r", encoding="utf-8") as infile:
            file_content = infile.read()
    except FileNotFoundError:
        write_error((f"Ошибка: входной файл {params['input1']} не найден."))
        return
    
    graph = validate_and_parse_graph(file_content)
    if isinstance(graph, str): 
        write_error(graph)
        return
    
    tree = build_xml(graph)
    output_file = params["output1"]
    try:
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Граф успешно записан в файл {output_file}.")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

if __name__ == "__main__":
    main()