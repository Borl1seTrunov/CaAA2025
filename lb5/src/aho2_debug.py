import sys
from collections import deque
from typing import List, Tuple, Dict, Deque, Optional
import graphviz

DEBUG = True
VISUALIZE = True



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
    debug_print("\nНачало построения автомата...")
    root = AhoNode()
    nodes: List[AhoNode] = [root]
    
    for pid, pattern in enumerate(patterns):
        debug_print(f"\nДобавление шаблона {pid}: '{pattern}'")
        node = nodes[0]
        for c in pattern:
            if c not in node.trans:
                new_node = AhoNode()
                nodes.append(new_node)
                node.trans[c] = len(nodes) - 1
                debug_print(f"  Создан переход по '{c}' в новый узел {len(nodes)-1}")
            node = nodes[node.trans[c]]
        node.outputs.append(pid)
        debug_print(f"  Узел {len(nodes)-1} отмечен как терминал для шаблона {pid}")

    debug_print("\nПостроение fail-ссылок:")
    queue: Deque[int] = deque()
    for child in nodes[0].trans.values():
        queue.append(child)
        nodes[child].fail = 0
        nodes[child].terminal = 0 if nodes[child].outputs else -1
        debug_print(f"Инициализация узла {child}: fail=0, terminal={nodes[child].terminal}")

    while queue:
        current_idx: int = queue.popleft()
        current_node: AhoNode = nodes[current_idx]
        debug_print(f"\nОбработка узла {current_idx}")

        for c, child_idx in current_node.trans.items():
            debug_print(f"  Обработка дочернего узла {child_idx} (символ '{c}')")
            fail: int = current_node.fail
            while fail != 0 and c not in nodes[fail].trans:
                fail = nodes[fail].fail
                debug_print(f"    Переход по fail к узлу {fail}")

            nodes[child_idx].fail = nodes[fail].trans[c] if c in nodes[fail].trans else 0
            debug_print(f"    Установка fail для {child_idx} -> {nodes[child_idx].fail}")

            nodes[child_idx].terminal = nodes[nodes[child_idx].fail].terminal if not nodes[nodes[child_idx].fail].outputs else nodes[child_idx].fail
            debug_print(f"    Установка terminal для {child_idx} -> {nodes[child_idx].terminal}")
            
            queue.append(child_idx)

    debug_print("\nАвтомат успешно построен")
    return nodes



def visualize_automaton(nodes: List[AhoNode], filename: str = 'automaton') -> None:
    debug_print("\nГенерация визуализации автомата...")
    dot = graphviz.Digraph(comment='Aho-Corasick Automaton', format='png')
    
    for i, node in enumerate(nodes):
        label: List[str] = [
            f'Узел {i}',
            f'Переходы: {node.trans}',
            f'Fail: {node.fail}',
            f'Выходы: {node.outputs}',
            f'Terminal: {node.terminal}'
        ]
        dot.node(str(i), '\n'.join(label))
        
        for c, target in node.trans.items():
            dot.edge(str(i), str(target), label=c, color='blue')
        
        if node.fail != i and node.fail != 0:
            dot.edge(str(i), str(node.fail), label='fail', color='red', style='dashed')
    
    dot.render(filename, view=True)
    debug_print(f"Визуализация сохранена в {filename}.png")



def split_pattern(pattern: str, wildcard: str) -> List[Tuple[str, int]]:
    debug_print(f"\nРазбор шаблона '{pattern}' с wildcard '{wildcard}'")
    parts: List[Tuple[str, int]] = []
    current_part: List[str] = []
    part_start: Optional[int] = None
    
    for i, c in enumerate(pattern):
        if c != wildcard:
            if part_start is None:
                part_start = i
            current_part.append(c)
        else:
            if current_part:
                parts.append((''.join(current_part), part_start))
                debug_print(f"  Найден сегмент: '{''.join(current_part)}' на позиции {part_start}")
                current_part = []
                part_start = None
    
    if current_part:
        parts.append((''.join(current_part), part_start))
        debug_print(f"  Последний сегмент: '{''.join(current_part)}' на позиции {part_start}")
    
    debug_print(f"Всего сегментов: {len(parts)}")
    return parts



def find_occurrences(text: str, automaton: List[AhoNode], pattern_info: List[Tuple[str, int]], parts: List[Tuple[str, int]]) -> List[int]:
    debug_print(f"\nПоиск в тексте длиной {len(text)} символов...")
    current: AhoNode = automaton[0]
    occurrences: List[int] = []
    
    for pos, c in enumerate(text):
        while True:
            if c in current.trans:
                child_idx: int = current.trans[c]
                current = automaton[child_idx]
                debug_print(f"  Символ '{c}' на позиции {pos}: переход в узел {child_idx}")
                break
            elif current == automaton[0]:
                debug_print(f"  Символ '{c}' на позиции {pos}: остаемся в корне")
                break
            else:
                prev_fail: int = current.fail
                current = automaton[current.fail]
                debug_print(f"  Переход по fail из {prev_fail} в узел {current.fail}")
        
        temp: AhoNode = current
        while temp != automaton[0]:
            for pid in temp.outputs:
                pattern, start_in_pat = pattern_info[pid]
                start: int = pos - len(pattern) + 1 - start_in_pat
                if start >= 0:
                    debug_print(f"  Найдено совпадение сегмента {pid} ('{pattern}') на позиции {start}")
                    occurrences.append(start)
            temp = automaton[temp.terminal] if temp.terminal != -1 else automaton[0]
    
    debug_print(f"Всего предварительных совпадений: {len(occurrences)}")
    return occurrences



def process_results(occurrences: List[int], text: str, pattern_len: int, target_count: int) -> List[int]:
    max_start: int = len(text) - pattern_len
    if max_start < 0:
        return []
    
    counter: List[int] = [0] * (max_start + 1)
    for start in occurrences:
        if 0 <= start <= max_start:
            counter[start] += 1
    
    return [i + 1 for i in range(max_start + 1) if counter[i] == target_count]



def read_input() -> Tuple[str, str, str]:
    text: str = sys.stdin.readline().strip()
    pattern: str = sys.stdin.readline().strip()
    wildcard: str = sys.stdin.readline().strip()[0]
    return text, pattern, wildcard



def prepare_patterns(pattern: str, wildcard: str) -> Tuple[List[str], List[Tuple[str, int]]]:
    parts = split_pattern(pattern, wildcard)
    if not parts:
        return [], []
    return [p for p, _ in parts], [(p, pos) for p, pos in parts]



def execute_search(text: str, patterns: List[str], pattern_info: List[Tuple[str, int]], parts: List[Tuple[str, int]]) -> List[int]:
    automaton = build_automaton(patterns)
    if VISUALIZE:
        visualize_automaton(automaton)
    return find_occurrences(text, automaton, pattern_info, parts)



def print_results(results: List[int]) -> None:
    if results:
        print('\n'.join(map(str, sorted(results))))
    else:
        print("")



def main() -> None:
    text, pattern, wildcard = read_input()
    patterns, pattern_info = prepare_patterns(pattern, wildcard)
    
    if not patterns:
        print("")
        return
    
    occurrences = execute_search(text, patterns, pattern_info, split_pattern(pattern, wildcard))
    results = process_results(occurrences, text, len(pattern), len(patterns))
    print_results(results)



if __name__ == "__main__":
    main()
