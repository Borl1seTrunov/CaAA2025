from time import time
from collections import namedtuple
from pydantic.types import PositiveInt
from typing import Final
from typing import Callable
from typing import Any
from rich.console import Console
from random import seed
from random import randint
from PIL import Image 
from PIL import ImageDraw

RED_DEBUG_COLOR : Final[str] = "red"
BLUE_DEBUG_COLOR : Final[str] = "blue"
GREEN_DEBUG_COLOR : Final[str] = "green"
YELLOW_DEBUG_COLOR : Final[str] = "yellow"

PAVE_FILENAME : Final[str] = "result_pave.png"

Square = namedtuple('Square', ['x_coord', 'y_coord', 'side_size'])
SolveResult = namedtuple('SolveResult', ['squares', 'iterations'])



class BitBoard:
    def __init__(self, board_size : PositiveInt) -> None:
        self._board_size : PositiveInt = board_size
        self._rows : list[PositiveInt] = [0 for _ in range(board_size)] 



    @property
    def board_size(self) -> PositiveInt:
        return self._board_size
    


    @property
    def rows(self) -> list[PositiveInt]:
        return self._rows



    def is_paved(self) -> bool:
        pave_row : PositiveInt = (1 << self._board_size) - 1
        return all(row == pave_row for row in self._rows)



    def place_square(self, x_coord : PositiveInt, y_coord : PositiveInt, side_size : PositiveInt) -> None:
        bitmask : Final[PositiveInt] = ((1 << side_size) - 1) << (self._board_size - y_coord - side_size)
        for i in range(x_coord, x_coord + side_size):
            self._rows[i] |= bitmask



    def can_place_square(self, x_coord : PositiveInt, y_coord : PositiveInt, side_size : PositiveInt) -> bool:
        if x_coord + side_size > self._board_size or y_coord + side_size > self._board_size:
            return False
        bitmask : Final[PositiveInt] = ((1 << side_size) - 1) << (self._board_size - y_coord - side_size)
        for i in range(x_coord, x_coord + side_size):
            if (self._rows[i] & bitmask) != 0:
                return False
        return True



    def find_empty_place(self) -> tuple[int | PositiveInt]:
        for i in range(self._board_size):
            if self._rows[i] != (1 << self._board_size) - 1:
                for j in range(self._board_size):
                    if not (self._rows[i] & (1 << (self._board_size - j - 1))):
                        return (i, j)
        return (-1, -1)



def save_image(filename : str, side_size : PositiveInt, squares : list[Square], scale_coeff : PositiveInt = 50) -> None:
    image : Image = Image.new('RGB', (side_size * scale_coeff, side_size * scale_coeff), 'white')
    image_draw : ImageDraw = ImageDraw.Draw(image)
    
    seed(42)
    
    for square in squares:
        x_coord : PositiveInt = (square.x_coord - 1) * scale_coeff
        y_coord : PositiveInt = (square.y_coord - 1) * scale_coeff
        square_size : PositiveInt = square.side_size * scale_coeff
        color : tuple[PositiveInt] = (randint(0,255), randint(0,255), randint(0,255))

        image_draw.rectangle(
            [
                x_coord, y_coord, x_coord + square_size - 1, y_coord + square_size - 1
            ],
            fill = color,
            outline = 'black'
        )
    
    image.save(filename)



def scale_size(side_size : PositiveInt) -> tuple[PositiveInt]:
    for i in range(2, int(side_size**0.5) + 1):
        if side_size % i == 0:
            return (i, side_size // i)
    return (side_size, 1)



def upscale_solve(squares : list[Square], scale_coeff : PositiveInt) -> list[Square]:
    return [Square(
        x_coord = (square.x_coord - 1) * scale_coeff + 1,
        y_coord = (square.y_coord - 1) * scale_coeff + 1,
        side_size = square.side_size * scale_coeff
    ) for square in squares]



def solve(side_size : PositiveInt, debug_mode : bool) -> SolveResult:
    if side_size == 1:
        return SolveResult([Square(1, 1, 1)], 0)
    
    stack : list = []
    best_squares_comb : list[Square] = []
    min_count : PositiveInt | float = float('+inf')
    iteration_count : PositiveInt = 0
    
    start_pave_size : PositiveInt = (side_size + 1) // 2
    start_bit_board : BitBoard = BitBoard(side_size)
    start_bit_board.place_square(0, 0, start_pave_size)
    squares : list[Square] = [Square(1, 1, start_pave_size)]
    
    if debug_mode:
        Console().print(f"Поставлен квадрат размера {start_pave_size} в ({1}, {1})", style=YELLOW_DEBUG_COLOR)

    if remainder := side_size - start_pave_size:
        start_bit_board.place_square(0, start_pave_size, remainder)
        squares.append(Square(1, start_pave_size + 1, remainder))
        start_bit_board.place_square(start_pave_size, 0, remainder)
        squares.append(Square(start_pave_size + 1, 1, remainder))
        if debug_mode:
            Console().print(f"Поставлен квадрат размера {remainder} в ({1}, {start_pave_size + 1})", style=YELLOW_DEBUG_COLOR)
            Console().print(f"Поставлен квадрат размера {remainder} в ({start_pave_size + 1}, {1})", style=YELLOW_DEBUG_COLOR)
    
    stack.append((start_bit_board, squares))
    
    while stack:
        iteration_count += 1
        bit_board, current = stack.pop()
        if len(current) >= min_count:
            continue
        if bit_board.is_paved():
            if len(current) < min_count:
                min_count = len(current)
                best_squares_comb = current.copy()
                if debug_mode:
                    Console().print(f"Новая лучшая комбинация: {min_count} квадратов/квадрата", style=GREEN_DEBUG_COLOR)
                    for square in best_squares_comb:
                        Console().print(f"{square.x_coord} {square.y_coord} {square.side_size}", style=BLUE_DEBUG_COLOR)
            continue
        x_coord, y_coord = bit_board.find_empty_place()
        if x_coord == -1:
            continue
        if debug_mode:
            Console().print(f"Найдено свободное место: ({x_coord+1}, {y_coord+1})", style=BLUE_DEBUG_COLOR)

        max_size = min(side_size - x_coord, side_size - y_coord)
        for size in range(max_size, 0, -1):
            if not bit_board.can_place_square(x_coord, y_coord, size):
                if debug_mode:
                    Console().print(f"Невозможно поставить квадрат размера {size} в позицию ({x_coord+1}, {y_coord+1})", style=RED_DEBUG_COLOR)
                continue
            if debug_mode:
                Console().print(f"Поставлен квадрат размера {size} в ({x_coord+1}, {y_coord+1})", style=YELLOW_DEBUG_COLOR)
            
            new_grid : BitBoard = BitBoard(side_size)
            new_grid._rows = bit_board._rows.copy()
            new_grid.place_square(x_coord, y_coord, size)
            
            new_squares : list[Square] = current.copy()
            new_squares.append(Square(x_coord+1, y_coord+1, size))
            
            stack.append((new_grid, new_squares))
    
    return SolveResult(best_squares_comb, iteration_count)



def timebench(function : Callable) -> Callable:
    def wrapper(*args, **kwargs):
        time_start : PositiveInt = time()
        function_result : Any = function(*args, **kwargs)
        debug_mode : bool = kwargs.get("debug_mode")
        time_finish : PositiveInt = time()
        elapsed_time : PositiveInt = time_finish - time_start
        if debug_mode:
            Console().print(f"Итоговое время выполнения функции: {elapsed_time} ceк", style=GREEN_DEBUG_COLOR)
        return function_result , elapsed_time
    return wrapper



def solve_scaled(side_size : PositiveInt, debug_mode : bool) -> SolveResult:
    downscalled_side_size, scale_coeff = scale_size(side_size)
    if scale_coeff == 1:
        return solve(side_size, debug_mode)
    if debug_mode:
        Console().print(f"произведён upscaling результата относительно квадрата стороны {downscalled_side_size}", style=GREEN_DEBUG_COLOR)
    result : SolveResult = solve(downscalled_side_size, debug_mode)
    return SolveResult(upscale_solve(result.squares, scale_coeff), result.iterations)



def main() -> None:
    debug_mode : bool = bool(input("Режим отладки? "))
    N : PositiveInt = int(input("Введите размер стороны квадрата "))
    result : SolveResult = (solve_scaled(N, debug_mode)) if not debug_mode else (timebench(solve_scaled)(N, debug_mode = debug_mode))[0]
    Console().print(len(result.squares), style=BLUE_DEBUG_COLOR)
    for square in result.squares:
        Console().print(f"{square.x_coord} {square.y_coord} {square.side_size}", style=RED_DEBUG_COLOR)
    if debug_mode:
        Console().print(f"Итоговое количество операций для квадрата стороны {N} - {result.iterations}", style=GREEN_DEBUG_COLOR)
        save_image(PAVE_FILENAME ,N ,result.squares)



if __name__ == '__main__':
    main()