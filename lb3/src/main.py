from typing import List, Set, Tuple

DEBUG: bool = True

def classic_levenshtein_distance(s: str, t: str, w_ins: int, w_del: int, w_sub: int) -> Tuple[int, List[str]]:
    m: int = len(s)
    n: int = len(t)

    dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]
    ops: List[List[str]] = [[''] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i * w_del
        ops[i][0] = 'D' if i > 0 else ''
    for j in range(n + 1):
        dp[0][j] = j * w_ins
        ops[0][j] = 'I' if j > 0 else ''

    if DEBUG:
        print(f"Начальная таблица DP (классический алгоритм):")
        for row in dp:
            print(row)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i-1] == t[j-1]:
                dp[i][j] = dp[i-1][j-1]
                ops[i][j] = 'M'
                if DEBUG:
                    print(f"Совпадение на s[{i-1}]={s[i-1]}, t[{j-1}]={t[j-1]}: dp[{i}][{j}] = {dp[i][j]}, op=M")
            else:
                insert_cost: int = dp[i][j-1] + w_ins
                delete_cost: int = dp[i-1][j] + w_del
                substitute_cost: int = dp[i-1][j-1] + w_sub
                dp[i][j] = min(insert_cost, delete_cost, substitute_cost)

                if dp[i][j] == insert_cost:
                    ops[i][j] = 'I'
                elif dp[i][j] == delete_cost:
                    ops[i][j] = 'D'
                else:
                    ops[i][j] = 'R'

                if DEBUG:
                    print(f"Нет совпадения на s[{i-1}]={s[i-1]}, t[{j-1}]={t[j-1]}: "
                          f"Выбрана {ops[i][j]}, dp[{i}][{j}] = {dp[i][j]} "
                          f"(вставка={insert_cost}, удаление={delete_cost}, замена={substitute_cost})")

    if DEBUG:
        print("\nФинальная таблица DP (классический алгоритм):")
        for row in dp:
            print(row)
        print("\nФинальная таблица ops (классический алгоритм):")
        for row in ops:
            print(row)

    operations: List[str] = []
    i, j = m, n
    while i > 0 or j > 0:
        if ops[i][j] == 'M' or ops[i][j] == 'R':
            operations.append(ops[i][j])
            i -= 1
            j -= 1
        elif ops[i][j] == 'I':
            operations.append('I')
            j -= 1
        elif ops[i][j] == 'D':
            operations.append('D')
            i -= 1

    operations.reverse()
    return dp[m][n], operations

def restrict_operations(index: int, char: str, cursed_set: Set[int]) -> Tuple[bool, bool]:
    if index not in cursed_set:
        return True, True
    if char == 'U':
        return True, False
    return False, False

def cursed_levenshtein_distance(s: str, t: str, cursed_indices: List[int], w_ins: int, w_del: int, w_sub: int) -> Tuple[int, List[str]]:
    m: int = len(s)
    n: int = len(t)
    cursed_set: Set[int] = set(cursed_indices)

    dp: List[List[float]] = [[float('inf')] * (n + 1) for _ in range(m + 1)]
    ops: List[List[str]] = [[''] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        if i == 0 or restrict_operations(i-1, s[i-1], cursed_set)[0]:
            dp[i][0] = i * w_del
            ops[i][0] = 'D' if i > 0 else ''

    for j in range(n + 1):
        dp[0][j] = j * w_ins
        ops[0][j] = 'I' if j > 0 else ''

    if DEBUG:
        print(f"\nНачальная таблица DP (проклятый алгоритм):")
        for row in dp:
            print([x if x != float('inf') else 'inf' for x in row])
        print(f"Проклятые индексы: {cursed_indices}")

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i-1] == t[j-1]:
                dp[i][j] = dp[i-1][j-1]
                ops[i][j] = 'M'
                if DEBUG:
                    print(f"Совпадение на s[{i-1}]={s[i-1]}, t[{j-1}]={t[j-1]}: dp[{i}][{j}] = {dp[i][j]}, op=M")
            else:
                can_delete, can_substitute = restrict_operations(i-1, s[i-1], cursed_set)
                insert_cost: float = dp[i][j-1] + w_ins
                delete_cost: float = dp[i-1][j] + w_del if can_delete else float('inf')
                substitute_cost: float = dp[i-1][j-1] + w_sub if can_substitute else float('inf')
                dp[i][j] = min(insert_cost, delete_cost, substitute_cost)

                if dp[i][j] == insert_cost:
                    ops[i][j] = 'I'
                elif dp[i][j] == delete_cost:
                    ops[i][j] = 'D'
                elif dp[i][j] == substitute_cost:
                    ops[i][j] = 'R'
                else:
                    ops[i][j] = 'X'

                if DEBUG:
                    print(f"Нет совпадения на s[{i-1}]={s[i-1]}, t[{j-1}]={t[j-1]}: "
                          f"Выбрана {ops[i][j]}, dp[{i}][{j}] = {dp[i][j]} "
                          f"(вставка={insert_cost}, удаление={delete_cost}, замена={substitute_cost})")

    if DEBUG:
        print("\nФинальная таблица DP (проклятый алгоритм):")
        for row in dp:
            print([x if x != float('inf') else 'inf' for x in row])
        print("\nФинальная таблица ops (проклятый алгоритм):")
        for row in ops:
            print(row)

    operations: List[str] = []
    i, j = m, n
    while i > 0 or j > 0:
        if ops[i][j] == 'M' or ops[i][j] == 'R':
            operations.append(ops[i][j])
            i -= 1
            j -= 1
        elif ops[i][j] == 'I':
            operations.append('I')
            j -= 1
        elif ops[i][j] == 'D':
            operations.append('D')
            i -= 1

    operations.reverse()
    return int(dp[m][n]), operations

def main() -> None:
    try:
        weights: List[str] = input("Введите цены операций (замена вставка удаление): ").strip().split()
        if len(weights) != 3:
            raise ValueError("Необходимо ввести ровно три числа")
        w_sub, w_ins, w_del = map(int, weights)

        if w_sub <= 0 or w_ins <= 0 or w_del <= 0:
            raise ValueError("Цены операций должны быть положительными числами")

        s: str = input("Введите исходную строку A: ").strip()
        t: str = input("Введите целевую строку B: ").strip()

        print(f"\nВычисление классического расстояния Левенштейна между '{s}' и '{t}' "
              f"с ценами (замена={w_sub}, вставка={w_ins}, удаление={w_del})")
        classic_distance, classic_ops = classic_levenshtein_distance(s, t, w_ins, w_del, w_sub)
        print(f"\nКлассическое расстояние Левенштейна: {classic_distance}")
        print("\nРедакционное последовательность (классический алгоритм):")
        print('\t'.join(classic_ops))
        print('\t'.join(s))
        print('\t'.join(t))

        cursed_input: str = input("\nВведите проклятые индексы (через пробел, начиная с 0, или пустую строку для пропуска): ").strip()
        cursed_indices: List[int] = [int(x) for x in cursed_input.split() if x.strip().isdigit()] if cursed_input else []

        print(f"\nВычисление расстояния Левенштейна между '{s}' и '{t}' "
              f"с проклятыми индексами {cursed_indices} и весами (замена={w_sub}, вставка={w_ins}, удаление={w_del})")
        cursed_distance, cursed_ops = cursed_levenshtein_distance(s, t, cursed_indices, w_ins, w_del, w_sub)
        print(f"\nРасстояние Левенштейна с проклятыми индексами: {cursed_distance}")
        print("\nРедакционное последовательность (проклятый алгоритм):")
        print('\t'.join(cursed_ops))
        print('\t'.join(s))
        print('\t'.join(t))

    except ValueError as e:
        print(f"Ошибка ввода: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()