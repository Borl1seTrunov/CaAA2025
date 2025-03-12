from laba import *
import matplotlib.pyplot as plt
from pandas import DataFrame
from matplotlib.table import Table

PATH_TO_IMG : Final[str] = "assets/"
PATH_TO_IMG_SQUARES : Final[str] = "assets/Squares/"



def get_primes(range_primes : PositiveInt = 32) -> list[PositiveInt]:
    nums = [i for i in range(1, range_primes + 1)]
    idx : PositiveInt = 1
    prime : PositiveInt = 2
    while prime**2 <= range_primes and idx < len(nums):
        nums = list(filter(lambda x: (x % prime != 0) or x == prime, nums))
        idx += 1
        prime = 2 if idx >= len(nums) else nums[idx]
    return nums[1:]



def bench_time_and_iterrations(side_size : PositiveInt, debug_mode : bool = False, save_mode : bool = False) -> None:
    debug_mode : bool = False

    prime_nums : list[PositiveInt] = get_primes(side_size)
    
    x_data : list[PositiveInt] = prime_nums
    solve_data : list[list[SolveResult, PositiveInt]] = [timebench(solve_scaled)(n, debug_mode=debug_mode) for n in prime_nums]
    itterration_data : list[PositiveInt] = [data[0].iterations for data in solve_data]
    time_data : list[PositiveInt] = [data[1] for data in solve_data]
    
    data_table : dict = {
        "Сторона квадрата" : [n for n in prime_nums],
        "Количество итераций" : [iterration for iterration in itterration_data],
        "Время замощения" : [time for time in time_data]
    }

    df : DataFrame = DataFrame(data_table)

    if save_mode:
        for square_data in zip(solve_data, prime_nums):
            square_pave : list[Square] = square_data[0][0].squares
            square_side_size : PositiveInt = square_data[1]
            save_image(f"{PATH_TO_IMG_SQUARES}Square_pave_{square_side_size}.png", square_side_size, square_pave)

    fig, (axs_iter, axs_time, axs_table) = plt.subplots(3, figsize=(10,13))

    axs_iter.plot(x_data, itterration_data)
    axs_iter.plot(x_data, itterration_data, "bo")
    axs_iter.set(xlabel = "Сторона квадрата", ylabel = "Количество операций")

    axs_time.plot(x_data, time_data)
    axs_time.plot(x_data, time_data, "bo")
    axs_time.set(xlabel = "Сторона квадрата", ylabel = "Время затраченное на решение")

    table = axs_table.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        colColours=['#f3f4f6']*df.shape[1]
    )

    axs_table.axis('off')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    fig.suptitle("Графики зависимостей")
    plt.savefig(f"{PATH_TO_IMG}/graphs.png")
    plt.close()
    


def main() -> None:
    bench_time_and_iterrations(side_size = 10, debug_mode = False, save_mode = True)



if __name__ == "__main__":
    main()