import heapq
from typing import List, Tuple, Set
import math
import random
import os

def generate_matrix(N: int, min_weight: float = 1.0, max_weight: float = 100.0) -> List[List[float]]:
    """Генерация случайной матрицы весов"""
    print(f"\nОтладка: Генерация матрицы {N}x{N}")
    print(f"Веса: [{min_weight}, {max_weight}]")
    matrix = []
    edges_count = 0
    for i in range(N):
        row = []
        for j in range(N):
            if i == j:
                row.append(float('inf'))
                print(f"Отладка: M[{i}][{j}] = inf (диагональ)")
            else:
                weight = round(random.uniform(min_weight, max_weight), 2)
                row.append(weight)
                edges_count += 1
                print(f"Отладка: M[{i}][{j}] = {weight}")
        matrix.append(row)
    
    print(f"\nОтладка: Сгенерировано {edges_count} рёбер")
    return matrix

def save_matrix(matrix: List[List[float]], filename: str):
    """Сохранение матрицы в файл, преобразование inf в -1 только для диагональных элементов"""
    with open(filename, 'w') as f:
        f.write(f"{len(matrix)}\n")
        for i, row in enumerate(matrix):
            row_str = ' '.join(str(-1) if (j == i and math.isinf(x)) else str(x) 
                             for j, x in enumerate(row))
            f.write(row_str + '\n')

def read_matrix_from_file(filename: str) -> Tuple[int, List[List[float]]]:
    """Чтение матрицы из файла, преобразование -1 в inf только для диагональных элементов"""
    with open(filename, 'r') as f:
        N = int(f.readline())
        M = []
        for i in range(N):
            row = [float('inf') if (j == i and x == -1) else float(x) 
                  for j, x in enumerate(map(float, f.readline().split()))]
            M.append(row)
    return N, M

def read_input() -> Tuple[int, List[List[float]]]:
    """Чтение матрицы со стандартного ввода, преобразование -1 в inf только для диагональных элементов"""
    print("Введите размер матрицы:")
    N = int(input())
    print(f"Введите {N} строк по {N} чисел в каждой (-1 разрешён только на диагонали):")
    M = []
    for i in range(N):
        values = list(map(float, input().split()))
        row = [float('inf') if (j == i and x == -1) else float(x) 
               for j, x in enumerate(values)]
        print(f"Прочитана строка {i}: {row}")
        M.append(row)
    return N, M

def calculate_mst_weight(vertices: List[int], matrix: List[List[float]]) -> float:
    """Вычисление веса минимального остовного дерева для подмножества вершин"""
    N = len(vertices)
    if N <= 1:
        return 0
    
    # Алгоритм Прима для подграфа
    visited = {vertices[0]}
    edges = []
    total_weight = 0
    
    while len(visited) < N:
        min_edge = float('inf')
        next_vertex = None
        
        for v in visited:
            for u in vertices:
                if u not in visited and matrix[v][u] < min_edge:
                    min_edge = matrix[v][u]
                    next_vertex = u
        
        if next_vertex is None:
            return float('inf')
        
        visited.add(next_vertex)
        total_weight += min_edge
    
    return total_weight

def get_two_min_edges(vertices: List[int], matrix: List[List[float]]) -> float:
    """Получение полусуммы двух легчайших рёбер для подмножества вершин"""
    min_edges = []
    for i in vertices:
        for j in vertices:
            if i != j and not math.isinf(matrix[i][j]):
                min_edges.append(matrix[i][j])
    
    if len(min_edges) < 2:
        return float('inf')
    
    min_edges.sort()
    return (min_edges[0] + min_edges[1]) / 2

def calculate_antipriority(path: List[int], next_vertex: int, M: List[List[float]], N: int) -> float:
    """Вычисление антиприоритета для следующей вершины"""
    k = len(path)
    S = sum(M[path[i]][path[i+1]] for i in range(k-1)) if k > 1 else 0
    L = M[path[-1]][next_vertex]
    return (S/k + L/N) * (4*N/(3*N+k))

def mvag(N: int, M: List[List[float]], start: int = 0) -> Tuple[List[int], float]:
    """Метод ветвей и границ с последовательным ростом пути"""
    print(f"\nОтладка МВиГ: Запуск алгоритма для {N} вершин, старт из {start}")
    
    def lower_bound(path: List[int], unvisited: Set[int]) -> float:
        """Вычисление нижней границы"""
        remaining = list(unvisited)
        if not remaining:
            bound = M[path[-1]][start] if not math.isinf(M[path[-1]][start]) else float('inf')
            print(f"Отладка МВиГ: Нижняя граница для полного пути: {bound}")
            return bound
        
        bound1 = get_two_min_edges(remaining + [path[-1]], M)
        bound2 = calculate_mst_weight(remaining + [path[-1]], M)
        print(f"Отладка МВиГ: Границы для пути {path}:")
        print(f"    - По полусумме рёбер: {bound1}")
        print(f"    - По МОД: {bound2}")
        return max(bound1, bound2)
    
    best_path = []
    best_cost = float('inf')
    nodes_visited = 0
    paths = [(0, [start], set(range(N)) - {start})]
    
    while paths:
        nodes_visited += 1
        cost, path, unvisited = paths.pop(0)
        
        print(f"\nОтладка МВиГ: Исследуется путь {path}")
        print(f"Текущая стоимость: {cost}")
        print(f"Осталось вершин: {unvisited}")
        
        if len(path) == N:
            if not math.isinf(M[path[-1]][start]):
                total_cost = cost + M[path[-1]][start]
                print(f"Отладка МВиГ: Найден полный путь")
                print(f"Стоимость пути: {total_cost}")
                if total_cost < best_cost:
                    print(f"Отладка МВиГ: Обновление лучшего решения")
                    best_cost = total_cost
                    best_path = path.copy()
            continue
        
        current = path[-1]
        lb = cost + lower_bound(path, unvisited)
        
        if lb >= best_cost:
            print(f"Отладка МВиГ: Ветвь отсечена (оценка {lb} >= {best_cost})")
            continue
        
        next_vertices = []
        for next_vertex in unvisited:
            if not math.isinf(M[current][next_vertex]):
                antipriority = calculate_antipriority(path, next_vertex, M, N)
                next_vertices.append((antipriority, next_vertex))
        
        next_vertices.sort()
        
        for _, next_vertex in next_vertices:
            new_path = path + [next_vertex]
            new_cost = cost + M[current][next_vertex]
            new_unvisited = unvisited - {next_vertex}
            paths.append((new_cost, new_path, new_unvisited))
    
    print(f"\nОтладка МВиГ: Поиск завершён")
    print(f"Исследовано узлов: {nodes_visited}")
    print(f"Лучший путь: {best_path}")
    print(f"Лучшая стоимость: {best_cost}")
    return best_path, best_cost

def improved_avnn(N: int, M: List[List[float]], start: int = 0) -> Tuple[List[int], float]:
    """Улучшенный алгоритм поиска ближайшего соседа с антиприоритетом"""
    print(f"\nОтладка АВБГ: Запуск алгоритма для {N} вершин, старт из {start}")
    
    unvisited = set(range(N))
    path = [start]
    unvisited.remove(start)
    total_cost = 0
    
    print(f"Отладка АВБГ: Начальный путь = [{start}]")
    print(f"Отладка АВБГ: Непосещённые вершины = {unvisited}")
    
    while unvisited:
        curr = path[-1]
        print(f"\nОтладка АВБГ: Текущая вершина = {curr}")
        print("Отладка АВБГ: Поиск следующей вершины")
        
        best_next = None
        best_priority = float('inf')
        priorities = []
        
        for next_vertex in unvisited:
            if not math.isinf(M[curr][next_vertex]):
                k = len(path)
                S = sum(M[path[i]][path[i+1]] for i in range(k-1)) if k > 1 else 0
                L = M[curr][next_vertex]
                priority = (S/k + L/N) * (4*N/(3*N+k))
                priorities.append((next_vertex, priority, L))
                print(f"Отладка АВБГ: Вершина {next_vertex}:")
                print(f"    S = {S}, k = {k}, L = {L}")
                print(f"    Приоритет = {priority}")
                
                if priority < best_priority:
                    best_priority = priority
                    best_next = next_vertex
        
        if best_next is None:
            print("Отладка АВБГ: Нет доступных вершин, путь невозможен")
            return [], float('inf')
        
        print(f"Отладка АВБГ: Выбрана вершина {best_next} с приоритетом {best_priority}")
        path.append(best_next)
        edge_cost = M[curr][best_next]
        total_cost += edge_cost
        unvisited.remove(best_next)
        
        print(f"Отладка АВБГ: Добавлено ребро {curr}->{best_next} стоимостью {edge_cost}")
        print(f"Отладка АВБГ: Текущий путь = {path}")
        print(f"Отладка АВБГ: Текущая стоимость = {total_cost}")
    
    print("\nОтладка АВБГ: Попытка замкнуть цикл")
    if not math.isinf(M[path[-1]][start]):
        final_cost = M[path[-1]][start]
        total_cost += final_cost
        print(f"Отладка АВБГ: Цикл замкнут, добавлено ребро {path[-1]}->{start}")
        print(f"Отладка АВБГ: Финальная стоимость = {total_cost}")
        return path, total_cost
    
    print("Отладка АВБГ: Невозможно замкнуть цикл")
    return [], float('inf')

def main() -> None:
    """main =)"""
    while True:
        print("\nВыберите операцию:")
        print("1. Сгенерировать и сохранить новую матрицу")
        print("2. Загрузить матрицу из файла")
        print("3. Ввести матрицу вручную")
        print("4. Выход")
        
        choice = input("Введите ваш выбор (1-4): ")
        
        if choice == '1':
            print("\nОтладка: Выбрана генерация новой матрицы")
            size: int = int(input("Введите размер матрицы: "))
            filename: str = input("Введите имя файла для сохранения: ")
            
            print("\nОтладка: Начало генерации матрицы")
            matrix: List[List[float]] = generate_matrix(size)
            save_matrix(matrix, filename)
            print(f"Матрица сохранена в файл {filename}")
            N, M = size, matrix
        
        elif choice == '2':
            print("\nОтладка: Выбрана загрузка из файла")
            filename = input("Введите имя файла: ")
            try:
                N, M = read_matrix_from_file(filename)
                print("Матрица успешно загружена")
            except FileNotFoundError:
                print("Файл не найден!")
                continue
        
        elif choice == '3':
            print("\nОтладка: Выбран ручной ввод")
            N, M = read_input()
        
        elif choice == '4':
            print("\nЗавершение работы")
            break
        
        else:
            print("Неверный выбор!")
            continue
        
        print("\nВходная матрица:")
        for row in M:
            print('\t'.join("inf" if math.isinf(x) else f"{x:6.2f}" for x in row))
        
        print("\nВыберите алгоритм:")
        print("1. Метод ветвей и границ (МВиГ)")
        print("2. Улучшенный алгоритм ближайшего соседа")
        
        algo_choice = input("Введите ваш выбор (1-2): ")
        
        start_vertex = 0
        import time
        start_time = time.time()
        
        if algo_choice == '1':
            print("\nЗапуск метода ветвей и границ...")
            path, cost = mvag(N, M, start_vertex)
        else:
            print("\nЗапуск улучшенного алгоритма ближайшего соседа...")
            path, cost = improved_avnn(N, M, start_vertex)
        
        end_time = time.time()
        
        print("\nРезультат:")
        print(f"Путь: {' '.join(map(str, path))}")
        print(f"Стоимость: {cost:.2f}")
        print(f"Время выполнения: {end_time - start_time:.3f} секунд")

if __name__ == '__main__':
    main()