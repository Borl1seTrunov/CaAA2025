from collections import deque
import sys
import graphviz
from typing import List, Tuple, Dict, Optional, Deque

DEBUG = True
VISUALIZE = True

input = sys.stdin.read().split()



def debug_print(message: str) -> None:
    if DEBUG:
        print(message)



class AhoNode:
    def __init__(self) -> None:
        self.trans: Dict[str, int] = {}
        self.fail: int = 0
        self.terminal: int = -1
        self.outputs: List[int] = []



def build_automaton(patterns: List[str]) -> List[AhoNode]:
    root = AhoNode()
    nodes: List[AhoNode] = [root]
    
    for idx, pattern in enumerate(patterns):
        debug_print(f"\nДобавление шаблона {idx + 1}: '{pattern}'")
        current_idx: int = 0
        for c in pattern:
            current_node: AhoNode = nodes[current_idx]
            if c not in current_node.trans:
                new_node = AhoNode()
                nodes.append(new_node)
                new_child_idx: int = len(nodes) - 1
                current_node.trans[c] = new_child_idx
                debug_print(f"  Создан переход из узла {current_idx} по '{c}' в узел {new_child_idx}")
            current_idx = current_node.trans[c]
        nodes[current_idx].outputs.append(idx + 1)
        debug_print(f"  Шаблон '{pattern}' добавлен в узел {current_idx}. Выходы: {nodes[current_idx].outputs}")
    
    debug_print("\nПостроение fail-ссылок:")
    queue: Deque[int] = deque()
    for c, child_idx in nodes[0].trans.items():
        queue.append(child_idx)
        nodes[child_idx].fail = 0
        nodes[child_idx].terminal = 0 if nodes[child_idx].outputs else -1
        debug_print(f"Инициализация дочернего узла {child_idx} корня: fail=0, terminal={nodes[child_idx].terminal}")
    
    while queue:
        current_idx: int = queue.popleft()
        current_node: AhoNode = nodes[current_idx]
        debug_print(f"\nОбработка узла {current_idx}")
        
        for c, child_idx in current_node.trans.items():
            debug_print(f"  Обработка дочернего узла {child_idx} по символу '{c}'")
            fail: int = current_node.fail
            while fail != 0 and c not in nodes[fail].trans:
                fail = nodes[fail].fail
                debug_print(f"    Переход по fail к узлу {fail}")
            
            nodes[child_idx].fail = nodes[fail].trans[c] if c in nodes[fail].trans else 0
            debug_print(f"    Установка fail для узла {child_idx} => {nodes[child_idx].fail}")
            
            if nodes[nodes[child_idx].fail].outputs:
                nodes[child_idx].terminal = nodes[child_idx].fail
            else:
                nodes[child_idx].terminal = nodes[nodes[child_idx].fail].terminal
            debug_print(f"    Установка terminal для узла {child_idx} => {nodes[child_idx].terminal}")
            
            queue.append(child_idx)
    
    debug_print("\nАвтомат построен:")
    for i, node in enumerate(nodes):
        debug_print(f"Узел {i}: переходы={node.trans}, fail={node.fail}, outputs={node.outputs}, terminal={node.terminal}")
    return nodes



def search(text: str, nodes: List[AhoNode], patterns: List[str]) -> List[Tuple[int, int]]:
    debug_print(f"\nПоиск в тексте '{text}':")
    current_idx: int = 0
    occurrences: List[Tuple[int, int]] = []
    for pos, c in enumerate(text, 1):
        debug_print(f"\nСимвол '{c}' (позиция {pos})")
        debug_print(f"  Текущий узел до обработки: {current_idx}")
        
        while current_idx != 0 and c not in nodes[current_idx].trans:
            prev: int = current_idx
            current_idx = nodes[current_idx].fail
            debug_print(f"  Переход по fail с {prev} на {current_idx}")
        
        if c in nodes[current_idx].trans:
            current_idx = nodes[current_idx].trans[c]
            debug_print(f"  Переход по символу '{c}' в узел {current_idx}")
        else:
            current_idx = 0
            debug_print(f"  Нет перехода по '{c}', возврат в корень")
        
        temp_idx: int = current_idx
        while temp_idx != 0:
            if nodes[temp_idx].outputs:
                for p_num in nodes[temp_idx].outputs:
                    start_pos: int = pos - len(patterns[p_num - 1]) + 1
                    occurrences.append((start_pos, p_num))
                    debug_print(f"  Найден шаблон {p_num} на позиции {start_pos}")
            temp_idx = nodes[temp_idx].terminal if nodes[temp_idx].terminal != -1 else 0
    
    return sorted(occurrences)



def read_input() -> Tuple[str, List[str]]:
    ptr: int = 0
    text: str = input[ptr]
    ptr += 1
    n: int = int(input[ptr])
    ptr += 1
    patterns: List[str] = [input[ptr + i] for i in range(n)]
    return text, patterns



def visualize_automaton(nodes: List[AhoNode], filename: str = 'automaton') -> None:
    dot = graphviz.Digraph(comment='Aho-Corasick Automaton', format='png')
    
    for i, node in enumerate(nodes):
        label: List[str] = [
            f'Узел {i}',
            f'Trans: {node.trans}',
            f'Fail: {node.fail}',
            f'Outputs: {node.outputs}'
        ]
        label_str: str = '\n'.join(label)
        dot.node(str(i), label=label_str)
        
        for c, target in node.trans.items():
            dot.edge(str(i), str(target), label=c, color='blue')
        
        if node.fail != i:
            dot.edge(str(i), str(node.fail), label='fail', color='red', style='dashed')
    
    dot.render(filename, view=True)



def process_data(text: str, patterns: List[str]) -> List[Tuple[int, int]]:
    nodes: List[AhoNode] = build_automaton(patterns)
    if VISUALIZE:
        visualize_automaton(nodes)
    return search(text, nodes, patterns)



def print_results(result: List[Tuple[int, int]]) -> None:
    for pos, p_num in result:
        print(pos, p_num)



def main() -> None:
    text, patterns = read_input()
    result = process_data(text, patterns)
    print_results(result)



if __name__ == "__main__":
    main()
