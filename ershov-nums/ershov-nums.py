import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

_uniqie_counter = 1

class Node:
    def __init__(self, value, left=None, right=None):
        global _uniqie_counter
        self._uniqie_num = _uniqie_counter 
        _uniqie_counter += 1

        self.value = value

        self.left = left
        self.right = right
        self.ershov_number = None

# Вычисление чисел Ершова
def calculate_ershov(node):
    if node.left is None and node.right is None:
        node.ershov_number = 1
        return 1

    left_number = calculate_ershov(node.left) if node.left else 0
    right_number = calculate_ershov(node.right) if node.right else 0

    if left_number == right_number:
        node.ershov_number = left_number + 1
    else:
        node.ershov_number = max(left_number, right_number)
    
    return node.ershov_number

# Генерация кода с исправлением регистра для хранения результата
def generate_code(node, base_register):
    print(f'GOING TO GEN NODE {node.value} WITH base_num={base_register}')

    if node.left is None and node.right is None:
        return [f"LD R{base_register}, {node.value}"] # base + k - 1, but k = 1 for leaves

    instructions = []
    
    # Обработка одинаковых чисел Ершова
    if node.left.ershov_number == node.right.ershov_number:
        # gen right node
        instructions += generate_code(node.right, base_register + 1)
        
        #gen left node
        instructions += generate_code(node.left, base_register)
        
        # merge
        instructions.append(f"{node.value.upper()} R{base_register + node.ershov_number - 1}, R{base_register + node.ershov_number - 2}, R{base_register + node.ershov_number - 1}")
        
    else:
        if node.left.ershov_number > node.right.ershov_number:
            left_ersh = node.left.ershov_number
            right_ersh = node.right.ershov_number

            #gen left node
            instructions += generate_code(node.left, base_register)
           
            # gen right node
            instructions += generate_code(node.right, base_register)

            # merge
            instructions.append(f"{node.value.upper()} R{base_register + left_ersh - 1}, R{base_register + left_ersh - 1}, R{base_register  + right_ersh - 1}")
        else:
            left_ersh = node.left.ershov_number
            right_ersh = node.right.ershov_number

            # gen right node
            instructions += generate_code(node.right, base_register)

            #gen left node
            instructions += generate_code(node.left, base_register)

            # merge
            instructions.append(f"{node.value.upper()} R{base_register + right_ersh - 1}, R{base_register + left_ersh - 1}, R{base_register  + right_ersh - 1}")    
    return instructions

# Построение графа дерева
def build_graph(node, graph=None, parent=None):
    
    if graph is None:
        graph = nx.DiGraph()
    
    graph.add_node(node._uniqie_num, label=f'{node.value} ({node.ershov_number})')
    
    if parent:
        graph.add_edge(parent._uniqie_num, node._uniqie_num)
    
    if node.left:
        build_graph(node.left, graph, node)
    if node.right:
        build_graph(node.right, graph, node)
    
    return graph

# Визуализация дерева с числами Ершова
def draw_tree(graph):
    pos = graphviz_layout(graph, prog="dot")  # Используем 'dot' для отображения в виде дерева
    labels = nx.get_node_attributes(graph, 'label')

    # pos = nx.spring_layout(graph)
    labels = nx.get_node_attributes(graph, 'label')
    
    plt.figure(figsize=(8, 6))
    nx.draw(graph, pos, with_labels=True, labels=labels, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=False)
    plt.show()

if __name__ == "__main__":
    # RSP НЕ РАБОТАЕТ!!!11!!!!11!!!

    # Пример дерева для выражения (a - b) + e * (c + d) - 1
    a = Node('a')
    b = Node('b')
    c = Node('c')
    d = Node('d')
    e = Node('e')
    one = Node('1')

    sub_a_b = Node("SUB", a, b)
    sum_c_d = Node("SUM", c, d)
    sub_1 = Node("SUB", sum_c_d, one)
    mul_e = Node("MUL", e, sub_1)
    root = Node('SUM', sub_a_b, mul_e)

    # Вычисление чисел Ершова
    calculate_ershov(root)

    # Генерация кода
    instructions = generate_code(root, 4)

    # Печать инструкций
    for instr in instructions:
        print(instr)

    # Визуализация дерева с числами Ершова
    graph = build_graph(root)
    draw_tree(graph)
