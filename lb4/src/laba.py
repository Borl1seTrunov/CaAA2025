from pydantic.types import PositiveInt as uint
from typing import Final
from rich.console import Console

RED_DEBUG_COLOR : Final[str] = "red"
BLUE_DEBUG_COLOR : Final[str] = "blue"
GREEN_DEBUG_COLOR : Final[str] = "green"
YELLOW_DEBUG_COLOR : Final[str] = "yellow"



class KMP:
    def __init__(self, text: str, pattern: str, debug_mode: bool = False) -> None:
        self._text: str = text
        self._pattern: str = pattern
        self._debug: bool = debug_mode
        self._longestPrefixSuffix = self._makeLongestPrefixSuffix()
        self._result: list[uint] = self._search() if KMP._validate_data(text, pattern) else [-1]



    @staticmethod
    def _validate_data(text : str, pattern : str) -> bool:
        if len(pattern) > len(text):
            return False
        if len(pattern) == 0 or len(text) == 0:
            return False
        return True



    @property
    def longestPrefixSuffix(self) -> list[uint]:
        return self._longestPrefixSuffix



    @property
    def pattern(self) -> str:
        return self._pattern



    @property
    def text(self) -> str:
        return self._text



    def _makeLongestPrefixSuffix(self) -> list[uint]:
        pattern : str = self._pattern
        text : str = self._text
        debug_mode : bool = self._debug
        if debug_mode and not KMP._validate_data(text, pattern):
            Console().print(f"\nДлина шаблона={len(pattern)} длина текста={len(text)}", style=BLUE_DEBUG_COLOR)
            Console().print(f"Выход из функции LPS=[]", style=RED_DEBUG_COLOR)
            return []
        current_length: uint = 0
        pattern_length: uint = len(pattern)
        longestPrefixSuffix = [0] * pattern_length
        i: uint = 1

        if debug_mode:
            Console().print("\n" + "="*50, style=BLUE_DEBUG_COLOR)
            Console().print(f"[LPS] Начало построения для шаблона: '{pattern}'", style=BLUE_DEBUG_COLOR)
            Console().print(f"[LPS] Длина шаблона: {pattern_length}", style=BLUE_DEBUG_COLOR)

        while i < pattern_length:
            if debug_mode:
                Console().print(f"\n[LPS] Шаг {i}:", style=BLUE_DEBUG_COLOR)
                Console().print(f"Сравнение pattern[{i}] = '{pattern[i]}' и pattern[{current_length}] = '{pattern[current_length]}'", style=BLUE_DEBUG_COLOR)

            if pattern[i] == pattern[current_length]:
                current_length += 1
                longestPrefixSuffix[i] = current_length
                i += 1
                if debug_mode:
                    Console().print(f"Совпадение! Новый LPS: {longestPrefixSuffix[:i]}", style=GREEN_DEBUG_COLOR)
            else:
                if current_length != 0:
                    if debug_mode:
                        Console().print(f"Несовпадение! Возврат к LPS[{current_length-1}] = {longestPrefixSuffix[current_length-1]}", style=RED_DEBUG_COLOR)
                    current_length = longestPrefixSuffix[current_length - 1]
                else:
                    if debug_mode:
                        Console().print("Несовпадение! Сброс счетчика", style=RED_DEBUG_COLOR)
                    longestPrefixSuffix[i] = 0
                    i += 1

        if debug_mode:
            Console().print("\n[LPS] Итоговый массив:")
            Console().print("Index:  " + " ".join(f"{i:2}" for i in range(pattern_length)), style=BLUE_DEBUG_COLOR)
            Console().print("Char :   " + " ".join(f"{c:2}" for c in pattern), style=BLUE_DEBUG_COLOR)
            Console().print("LPS  :  " + " ".join(f"{v:2}" for v in longestPrefixSuffix), style=BLUE_DEBUG_COLOR)
            Console().print("="*50 + "\n", style=BLUE_DEBUG_COLOR)

        return longestPrefixSuffix



    def _search(self) -> list[uint]:
        text : str = self._text
        pattern : str = self._pattern
        debug_mode : bool = self._debug
        text_length = len(text)
        pattern_length = len(pattern)
        result_search : list[int] = []
        lps : list[int] = self._longestPrefixSuffix
        i = j = 0
        total_checks : uint = 0
        skip_count : uint = 0

        if debug_mode:
            Console().print("\n" + "="*50, style=BLUE_DEBUG_COLOR)
            Console().print(f"[Поиск] Начало поиска '{pattern}' в тексте с длиной {text_length}", style=BLUE_DEBUG_COLOR)
            Console().print(f"[Поиск] LPS массив: {lps}", style=BLUE_DEBUG_COLOR)

        while i < text_length:
            total_checks += 1
            if debug_mode:
                visual_text = text[:i] + "[" + text[i] + "]" + text[i+1:]
                visual_pattern = " "*(i-j) + pattern[:j] + "[" + pattern[j] + "]" + pattern[j+1:] if j < pattern_length else ""
                Console().print(f"\n[Шаг {total_checks}] i={i}, j={j}", style=BLUE_DEBUG_COLOR)
                Console().print(f"Текст:  {visual_text}", style=BLUE_DEBUG_COLOR)
                Console().print(f"Шаблон: {visual_pattern}", style=BLUE_DEBUG_COLOR)

            if j < pattern_length and text[i] == pattern[j]:
                if debug_mode:
                    Console().print(f"Совпадение '{text[i]}' → увеличиваем оба указателя", style=GREEN_DEBUG_COLOR)
                
                i += 1
                j += 1

                if j == pattern_length:
                    pos : uint  = i - j
                    result_search.append(pos)
                    j = lps[j-1]
                    if debug_mode:
                        Console().print(f"\n!!! НАЙДЕНО СОВПАДЕНИЕ НА ПОЗИЦИИ {pos} !!!", style=GREEN_DEBUG_COLOR)
                        Console().print(f"Указатель j <- LPS[j - 1] j={j}", style=GREEN_DEBUG_COLOR)
            else:
                if j != 0:
                    skip_count += 1
                    new_j = lps[j-1]
                    if debug_mode:
                        Console().print(f"Несовпадение! j ← LPS[{j-1}] = {new_j}", style=RED_DEBUG_COLOR)
                    j = new_j
                else:
                    if debug_mode:
                        Console().print("Несовпадение! Увеличиваем i", style=RED_DEBUG_COLOR)
                    i += 1

        if debug_mode:
            Console().print("\nСтатистика:")
            Console().print(f"Всего проверок символов: {total_checks}", style=BLUE_DEBUG_COLOR)
            Console().print(f"Пропусков через LPS: {skip_count}", style=BLUE_DEBUG_COLOR)
            Console().print(f"Найдено совпадений: {len(result_search) if result_search else 0}", style=BLUE_DEBUG_COLOR)
            Console().print("="*50, style=BLUE_DEBUG_COLOR)

        return result_search if result_search else [-1]



    def __str__(self) -> str:
        return "Индексы вхождений шаблона в тексте: [" + ", ".join(map(str, self._result)) + "]" if self._result[0] != -1 else "Совпадений не найдено"



def main() -> None:
    pattern : str = input("Введите шаблон для поиска: ")
    text : str = input("Введите текст для поиска: ")
    debug : bool = input("Включить режим отладки? (y/n): ").lower() == 'y'
    
    kmp_result : KMP = KMP(text, pattern, debug)

    Console().print(f"\nРезультат:\n{kmp_result}", style=GREEN_DEBUG_COLOR)

    if debug:
        Console().print("\nLPS массив:", style=GREEN_DEBUG_COLOR)
        Console().print(kmp_result.longestPrefixSuffix, style=GREEN_DEBUG_COLOR)



if __name__ == "__main__":
    main()