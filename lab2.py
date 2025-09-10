class TuringMachine:
    def __init__(self, input_tape):
        self.tape = list(input_tape)
        self.head = 0
        self.state = 'q0'
        self.steps = 0
        
    def _get_current_symbol(self):
        if self.head < 0 or self.head >= len(self.tape):
            return '_'
        return self.tape[self.head]
    
    def _set_current_symbol(self, symbol):
        if self.head < 0:
            self.tape = [symbol] + ['_'] * (-self.head - 1) + self.tape
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape = self.tape + ['_'] * (self.head - len(self.tape)) + [symbol]
        else:
            self.tape[self.head] = symbol
    
    def _move(self, direction):
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        elif direction != 'S':
            raise ValueError(f"Неверное направление: {direction}")
    
    def _print_state(self):
        tape_str = ''.join(self.tape)
        head_pos = ' ' * self.head + '^'
        print(f"Шаг {self.steps:3d}: Состояние={self.state:2s} | Лента: {tape_str}")
        print(f"           {' ' * 12} {head_pos}")
    
    def run(self, max_steps=500, verbose=True):
        if verbose:
            print("Начальное состояние:")
            self._print_state()
            print("\n" + "="*50)

        # ИСПРАВЛЕННЫЕ ПРАВИЛА ПЕРЕХОДОВ
        transitions = {
            # Начальное состояние - найти первую 1 для пометки
            ('q0', '1'): ('X', 'R', 'q1'),
            ('q0', '*'): ('*', 'R', 'q9'),
            ('q9', '1'): ('y', 'R', 'q9'),
            ('q9', '='): ('=', 'S', 'halt'),

            # После пометки левой 1, перейти к правой части
            ('q1', '1'): ('1', 'R', 'q1'),
            ('q1', '*'): ('*', 'R', 'q2'),

            # Найти первую 1 в правой части для копирования
            ('q2', '1'): ('Y', 'R', 'q3'),
            ('q2', 'Y'): ('Y', 'R', 'q2'),
            ('q2', '='): ('=', 'L', 'q7'),

            # Перейти к концу ленты чтобы добавить новую 1
            ('q3', '1'): ('1', 'R', 'q3'),
            ('q3', '='): ('=', 'R', 'q4'),
            ('q4', '_'): ('1', 'L', 'q5'),
            ('q4', '1'): ('1', 'R', 'q4'),

            # Вернуться к правой части
            ('q5', '1'): ('1', 'L', 'q5'),
            ('q5', '='): ('=', 'L', 'q6'),
            ('q6', '1'): ('1', 'L', 'q6'),
            ('q6', 'Y'): ('Y', 'L', 'q6'),
            ('q6', '*'): ('*', 'R', 'q2'),

            # Все правые 1 обработаны, вернуться к левой части - СБРОСИТЬ Y обратно в 1
            ('q7', 'Y'): ('1', 'L', 'q7'),  # Сбросить Y в 1
            ('q7', '1'): ('1', 'L', 'q7'),
            ('q7', '*'): ('*', 'L', 'q8'),

            # Очистка - все левые 1 обработаны
            ('q8', '1'): ('1', 'L', 'q8'),
            ('q8', 'X'): ('X', 'R', 'q0'),  # ДОБАВЛЕНО: Очистить оставшиеся Y
            
        }

        while self.state != 'halt' and self.steps < max_steps:
            current_symbol = self._get_current_symbol()
            key = (self.state, current_symbol)

            if key not in transitions:
                if verbose:
                    print(f"\nНе определен переход для (состояние={self.state}, символ={current_symbol})")
                    print("Текущая лента:", ''.join(self.tape))
                break
            
            write_symbol, move_direction, next_state = transitions[key]

            self._set_current_symbol(write_symbol)
            self._move(move_direction)
            self.state = next_state
            self.steps += 1

            if verbose and self.steps <= 100:
                self._print_state()

        if verbose:
            print("\n" + "="*50)
            if self.state == 'halt':
                print("Вычисления завершены успешно!")
            else:
                print(f"Вычисления остановлены после {self.steps} шагов")

            result = ''.join([c for c in self.tape if c == '1'])
            print(f"Финальный результат: {len(result)} единиц -> {result}")

        return self.tape, self.state

def create_input_string(a, b):
    """Создать входную строку в формате '111*111=' для заданных чисел"""
    left_ones = '1' * a
    right_ones = '1' * b
    return f"{left_ones}*{right_ones}=______________"

def test_multiplication():
    """Протестировать машину Тьюринга для умножения"""
    test_cases = [
        (1, 1),  # 1 × 1 = 1
        (2, 1),  # 2 × 1 = 2
        (1, 2),  # 1 × 2 = 2
        (2, 2),  # 2 × 2 = 4
        (2, 3),  # 2 × 3 = 6
        (3, 2),  # 3 × 2 = 6
    ]
    
    print("Тестирование машины Тьюринга для умножения")
    print("=" * 40)
    
    for a, b in test_cases:
        input_str = create_input_string(a, b)
        expected = a * b
        
        print(f"\nТестирование {a} × {b} = {expected}")
        print(f"Вход: {input_str}")
        
        tm = TuringMachine(input_str)
        final_tape, final_state = tm.run(verbose=False, max_steps=500)
        
        result_ones = ''.join([c for c in final_tape if c == '1'])
        
        print(f"Ожидается: {expected} единиц")
        print(f"Получено:  {len(result_ones)} единиц")
        
        if len(result_ones) == expected:
            print("✓ УСПЕХ!")
        else:
            print("✗ НЕУДАЧА!")
            print(f"Финальная лента: {''.join(final_tape)}")
        
        print("-" * 40)

def debug_case(a, b):
    """Отладить конкретный случай с подробным выводом"""
    print(f"\nОТЛАДКА {a} × {b}:")
    print("=" * 30)
    
    input_str = create_input_string(a, b)
    expected = a * b
        
    print(f"Вход: {input_str}")
    print(f"Ожидается: {expected} единиц")
    
    tm = TuringMachine(input_str)
    final_tape, final_state = tm.run(verbose=True, max_steps=200)
    
    result_ones = ''.join([c for c in final_tape if c == '1'])
    
    print(f"\nОжидается: {expected} единиц, Получено: {len(result_ones)} единиц")
    if len(result_ones) == expected:
        print("✓ УСПЕХ!")
    else:
        print("✗ НЕУДАЧА!")
        print(f"Финальная лента: {''.join(final_tape)}")

if __name__ == "__main__":
    # Запустить комплексные тесты
    test_multiplication()
    
    # Отладить конкретные случаи которые не работают
    print("\n" + "="*60)
    print("ОТЛАДКА НЕУДАЧНЫХ СЛУЧАЕВ:")
    print("="*60)
    
    debug_case(2, 1)
    debug_case(2, 2)