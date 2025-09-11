def iterative_multiply(x1, x2):
    """
    Итеративное умножение двух целых чисел (с помощью сложения).
    Обрабатывает отрицательные числа.
    """
    negative = False  # Флаг для определения знака результата

    # Случай, когда оба числа отрицательные -> результат положительный
    if x1 < 0 and x2 < 0:
        x1, x2 = -x1, -x2
    # Случай, когда только первое отрицательное -> результат отрицательный
    elif x1 < 0:
        x1 = -x1
        negative = True
    # Случай, когда только второе отрицательное -> результат отрицательный
    elif x2 < 0:
        x2 = -x2
        negative = True

    result = 0
    # Суммируем x1 ровно x2 раз
    for _ in range(x2):
        result += x1

    # Возвращаем с учётом знака
    return -result if negative else result


def recursive_multiply(x1, x2):
    """
    Рекурсивное умножение двух целых чисел.
    Основано на примитивной рекурсии: x1 * x2 = x1 + (x1 * (x2 - 1))
    Обрабатывает отрицательные числа.
    """

    # Базовый случай: умножение на ноль всегда даёт ноль
    if x1 == 0 or x2 == 0:
        return 0

    # Обработка отрицательных чисел
    if x1 < 0 and x2 < 0:       # (-a) * (-b) = a * b
        return recursive_multiply(-x1, -x2)
    elif x1 < 0:                # (-a) * b = -(a * b)
        return -recursive_multiply(-x1, x2)
    elif x2 < 0:                # a * (-b) = -(a * b)
        return -recursive_multiply(x1, -x2)

    # Рекурсивный шаг:
    # уменьшаем второй аргумент на 1 и прибавляем x1
    return x1 + recursive_multiply(x1, x2 - 1)


def main():
    print("=== Лабораторная работа №1: Рекурсивные функции ===")
    print("Задача: Умножение итеративным и рекурсивным способом")
    print("=" * 55)

    try:
        # Ввод данных от пользователя
        x1 = int(input("Введите первое число (x1): "))
        x2 = int(input("Введите второе число (x2): "))

        # Вычисление результатов
        iterative_result = iterative_multiply(x1, x2)
        recursive_result = recursive_multiply(x1, x2)

        # Вывод результатов
        print("\nРезультаты:")
        print(f"Итеративное умножение: {x1} * {x2} = {iterative_result}")
        print(f"Рекурсивное умножение: {x1} * {x2} = {recursive_result}")
        print(f"Встроенное умножение:  {x1} * {x2} = {x1 * x2}")

        # Проверка совпадения всех способов
        if iterative_result == recursive_result == x1 * x2:
            print("\n✓ Все методы дали одинаковый результат!")
        else:
            print("\n✗ Результаты не совпали!")

    except ValueError:
        print("Ошибка: нужно ввести целые числа!")


if __name__ == "__main__":
    main()
