#!/usr/bin/env python3
# post_simulator.py - Расширенная версия с поддержкой секции INPUT

import sys
import re

def parse_input_file(filename):
    """Разбор входного файла с поддержкой секции INPUT"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Ошибка: Файл '{filename}' не найден.")
    
    # Инициализация компонентов
    A = set()
    X = set()
    A1 = set()
    R = []
    INPUT = {}
    
    # Разбор каждой секции с помощью regex
    sections = {
        'A': r'A\s*=\s*\{([^}]*)\}',
        'X': r'X\s*=\s*\{([^}]*)\}', 
        'A1': r'A1\s*=\s*\{([^}]*)\}',
        'R': r'R\s*=\s*\{([^}]*)\}',
        'INPUT': r'INPUT\s*=\s*\{([^}]*)\}'
    }
    
    for section, pattern in sections.items():
        match = re.search(pattern, content)
        if match:
            items = [item.strip() for item in match.group(1).split(',') if item.strip()]
            if section == 'A':
                A = set(items)
            elif section == 'X':
                X = set(items)
            elif section == 'A1':
                A1 = set(items)
            elif section == 'R':
                for rule_str in items:
                    if '->' in rule_str:
                        lhs, rhs = [part.strip() for part in rule_str.split('->', 1)]
                        R.append((lhs, rhs))
            elif section == 'INPUT':
                for pair in items:
                    if '=' in pair:
                        var, value = [part.strip() for part in pair.split('=', 1)]
                        INPUT[var] = value
    
    return A, X, A1, R, INPUT

def substitute_variables(string, variables):
    """Подстановка значений вместо переменных"""
    result = string
    for var, value in variables.items():
        result = result.replace(var, value)
    return result

def validate_string(s, A, X):
    """Проверка, что все символы строки входят в алфавит"""
    for char in s:
        if char not in A:
            return False, f"Символ '{char}' не входит в алфавит A"
    return True, ""

def apply_rule(current_string, rule, A, X):
    """Попытка применить правило к текущей строке"""
    lhs, rhs = rule
    
    # Попробовать применить правило в каждой позиции строки
    for i in range(len(current_string)):
        substitutions = {}
        lhs_index = 0
        current_index = i
        match = True
        
        while lhs_index < len(lhs) and current_index < len(current_string):
            if lhs[lhs_index] in X:
                # Переменная – захватить всё до следующей константы
                var = lhs[lhs_index]
                start = current_index
                
                # Найти следующую константу в lhs
                next_const = None
                for j in range(lhs_index + 1, len(lhs)):
                    if lhs[j] not in X:
                        next_const = lhs[j]
                        break
                    
                if next_const:
                    idx = current_string.find(next_const, current_index)
                    if idx == -1:
                        match = False
                        break
                    value = current_string[start:idx]
                    current_index = idx
                else:
                    # Переменная до конца строки
                    value = current_string[start:]
                    current_index = len(current_string)

                substitutions[var] = value
                lhs_index += 1
            else:
                # Константа – должна совпадать точно
                if current_index >= len(current_string) or current_string[current_index] != lhs[lhs_index]:
                    match = False
                    break
                current_index += 1
                lhs_index += 1
        
        # Проверка на полное совпадение
        if match and lhs_index == len(lhs):
            # Подставить значения переменных в правую часть
            new_part = rhs
            for var, value in substitutions.items():
                new_part = new_part.replace(var, value)
            
            # Проверка результата
            valid, error = validate_string(new_part, A, X)
            if not valid:
                raise ValueError(f"Ошибка применения правила: {error}")
            
            # Построить новую строку
            new_string = current_string[:i] + new_part + current_string[current_index:]
            return new_string, substitutions
    
    return current_string, None  # Если правило не применимо

def main():
    if len(sys.argv) != 2:
        print("Использование: python post_simulator.py <входной_файл>")
        return

    try:
        # Разбор входного файла
        A, X, A1, R, INPUT = parse_input_file(sys.argv[1])

        # --- Проверки ---
        if not A1:
            print("Ошибка: не найдены аксиомы")
            return
        axiom_template = next(iter(A1))

        # Проверка, что аксиома содержит только символы алфавита или переменные
        for ch in axiom_template:
            if ch not in A and ch not in X:
                print(f"Ошибка: символ '{ch}' в аксиоме не входит в алфавит A или множество переменных X")
                return

        # Проверка, что все переменные во входных данных объявлены в X
        for var in INPUT.keys():
            if var not in X:
                print(f"Ошибка: переменная '{var}' в INPUT не входит в множество X")
                return

        # Подстановка переменных из INPUT
        current_string = substitute_variables(axiom_template, INPUT) if INPUT else axiom_template

        step = 0
        max_steps = 1000
        output_filename = "output.txt"
        final_result = ""  # Последний найденный результат между /…=

        with open(output_filename, "w", encoding='utf-8') as output_file:
            output_file.write(f"Начальная строка: {current_string}\n\n")

            while step < max_steps:
                rule_applied = False

                for rule in R:
                    try:
                        new_string, substitutions = apply_rule(current_string, rule, A, X)
                    except ValueError as e:
                        # Ошибка применения правила
                        print(f"Ошибка: {e}")
                        output_file.write(f"Ошибка: {e}\n")
                        return

                    if substitutions is not None:
                        # Обновить результат, если есть шаблон /…=
                        match = re.search(r'/([1]+)=', new_string)
                        if match:
                            final_result = match.group(1)

                        # Записать шаг
                        output_file.write(f"Шаг {step + 1}:\n")
                        output_file.write(f"Исходная строка: {current_string}\n")
                        output_file.write(f"Применено правило: {rule[0]} -> {rule[1]}\n")
                        output_file.write(f"Результат: {new_string}\n\n")

                        current_string = new_string
                        rule_applied = True
                        step += 1
                        break

                if not rule_applied:
                    output_file.write("Вычисление завершено успешно. Правила больше не применимы.\n")
                    print("Вычисление завершено успешно.")
                    break
            else:
                output_file.write("Вычисление остановлено: достигнут максимум шагов.\n")
                print("Предупреждение: достигнут максимум шагов")

            output_file.write(f"Итоговый результат: {final_result}\n")

        print(f"Результаты вычислений записаны в {output_filename}")
        print(f"Окончательный результат: {final_result}")

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
