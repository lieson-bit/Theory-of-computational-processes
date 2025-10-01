import os

class MealyMachineGenerator:
    def __init__(self, n, m, k):
        self.n = n
        self.m = m 
        self.k = k
        self.states = ["Qstart", "SuffixX", "SuffixB", "Qfinal", "Qtrap"]  # УДАЛЕН SuffixA
        self.transitions = {}
        
    def generate_automaton(self):
        self._generate_all_states()
        self._generate_all_transitions()
        return self.transitions
    
    def _generate_all_states(self):
        # Генерация состояний для всех k групп
        for group in range(self.k):
            # Состояния X-группы: ReadingX_группа_i (i от 1 до n)
            for i in range(1, self.n + 1):
                state_name = f"ReadingX_{group}_{i}"
                self.states.append(state_name)
                
            # Состояния D-группы: ReadingD_группа_j (j от 1 до m)  
            for j in range(1, self.m + 1):
                state_name = f"ReadingD_{group}_{j}"
                self.states.append(state_name)
    
    def _generate_all_transitions(self):
        # Инициализация всех состояний переходами в ловушку
        for state in self.states:
            self.transitions[state] = {}
            for symbol in ['x', 'd', 'a', 'b']:
                self.transitions[state][symbol] = ("Qtrap", "0")
        
        # Переходы из начального состояния
        self.transitions["Qstart"] = {
            'x': ("ReadingX_0_1", "0"),
            'd': ("ReadingD_0_1", "0"),
            'a': ("Qtrap", "0"),
            'b': ("Qtrap", "0")
        }
        
        # Генерация переходов для всех групп
        for group in range(self.k):
            self._add_x_group_transitions(group)
            self._add_d_group_transitions(group)
            
        # ИСПРАВЛЕННЫЕ переходы суффикса - ФИКС!
        # После завершения ПОСЛЕДНЕЙ группы, мы читаем 'a' и переходим прямо в SuffixX
        # Затем SuffixX --x--> SuffixB (ожидаем 'x') 
        # Затем SuffixB --b--> Qfinal (ожидаем 'b', выход 1)
        
        self.transitions["SuffixX"] = {
            'x': ("SuffixB", "0"),  # После 'a', ожидаем 'x'
            'a': ("Qtrap", "0"),
            'd': ("Qtrap", "0"), 
            'b': ("Qtrap", "0")
        }
        self.transitions["SuffixB"] = {
            'b': ("Qfinal", "1"),   # После 'x', ожидаем 'b' для завершения
            'x': ("Qtrap", "0"),
            'a': ("Qtrap", "0"),
            'd': ("Qtrap", "0")
        }
        
    def _add_x_group_transitions(self, group):
        for i in range(1, self.n + 1):
            state_name = f"ReadingX_{group}_{i}"
            
            if i < self.n:
                # Продолжаем в той же x-группе - читаем следующий 'x'
                self.transitions[state_name]['x'] = (f"ReadingX_{group}_{i+1}", "0")
            else:
                # Завершили x-группу (получили n 'x')
                if group < self.k - 1:
                    # Нужно больше групп - можем начать либо x-группу, либо d-группу
                    self.transitions[state_name]['x'] = (f"ReadingX_{group+1}_1", "0")
                    self.transitions[state_name]['d'] = (f"ReadingD_{group+1}_1", "0")
                else:
                    # Завершили последнюю группу - теперь ожидаем 'a' для начала суффикса
                    # После чтения 'a', переходим прямо в SuffixX (ожидая 'x')
                    self.transitions[state_name]['a'] = ("SuffixX", "0")
        
    def _add_d_group_transitions(self, group):
        for j in range(1, self.m + 1):
            state_name = f"ReadingD_{group}_{j}"
            
            if j < self.m:
                # Продолжаем в той же d-группе - читаем следующий 'd'
                self.transitions[state_name]['d'] = (f"ReadingD_{group}_{j+1}", "0")
            else:
                # Завершили d-группу (получили m 'd')
                if group < self.k - 1:
                    # Нужно больше групп - можем начать либо x-группу, либо d-группу
                    self.transitions[state_name]['x'] = (f"ReadingX_{group+1}_1", "0")
                    self.transitions[state_name]['d'] = (f"ReadingD_{group+1}_1", "0")
                else:
                    # Завершили последнюю группу - теперь ожидаем 'a' для начала суффикса
                    # После чтения 'a', переходим прямо в SuffixX (ожидая 'x')
                    self.transitions[state_name]['a'] = ("SuffixX", "0")

def validate_word(word, automaton_matrix):
    """Проверяет, принимается ли слово автоматом"""
    current_state = "Qstart"
    output_sequence = []
    path = [current_state]
    transition_log = []
    
    print(f"\nПроверка слова: '{word}'")
    print(f"Ожидаемый паттерн: k групп из (n 'x' ИЛИ m 'd') затем 'a x b'")
    
    for i, char in enumerate(word):
        if char not in ['x', 'd', 'a', 'b']:
            print(f"Ошибка: Неверный символ '{char}' на позиции {i}")
            return False, output_sequence, path, transition_log
            
        if current_state not in automaton_matrix:
            print(f"Ошибка: Неизвестное состояние '{current_state}'")
            return False, output_sequence, path, transition_log
            
        if char not in automaton_matrix[current_state]:
            print(f"Ошибка: Нет перехода для '{char}' из состояния '{current_state}'")
            print(f"Доступные переходы из {current_state}: {list(automaton_matrix[current_state].keys())}")
            return False, output_sequence, path, transition_log
            
        next_state, output = automaton_matrix[current_state][char]
        transition_info = f"{current_state} --{char}--> {next_state}"
        print(f"Шаг {i+1}: {transition_info} (выход: {output})")
        
        transition_log.append(transition_info)
        output_sequence.append(output)
        current_state = next_state
        path.append(current_state)
    
    # Проверяем, закончили ли мы в конечном состоянии
    is_accepted = (current_state == "Qfinal")
    print(f"Финальное состояние: {current_state}, Принято: {is_accepted}")
    
    return is_accepted, output_sequence, path, transition_log

def main():
    # Получаем текущую директорию
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(current_dir, 'input.txt')
    
    print(f"Поиск входного файла по пути: {input_file_path}")
    
    # Проверяем существование файла
    if not os.path.exists(input_file_path):
        print("Входной файл не найден. Создание файла input.txt по умолчанию...")
        
        # Создаем файл по умолчанию
        with open(input_file_path, 'w', encoding='utf-8') as f:
            f.write("n=2 m=3 k=2\n")
            f.write("xxdddaxb\n")
        
        print("Создан файл input.txt по умолчанию с n=2, m=3, k=2 и тестовым словом 'xxdddaxb'")
    
    # Читаем параметры из файла
    test_word = None
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not lines:
                print("Входной файл пуст. Используются значения по умолчанию.")
                n, m, k = 2, 3, 1
            else:
                # Первая строка должна содержать параметры
                params_line = lines[0]
                params = dict(item.split('=') for item in params_line.split())
                n = int(params['n'])
                m = int(params['m']) 
                k = int(params['k'])
                
                # Вторая строка (если существует) должна содержать тестовое слово
                if len(lines) > 1:
                    test_word = lines[1].replace(" ", "")  # Удаляем пробелы из тестового слова
                    
        print(f"Успешно прочитаны параметры: n={n}, m={m}, k={k}")
        print(f"Паттерн: {k} групп из ({n} 'x' ИЛИ {m} 'd') затем 'a x b'")
        if test_word:
            print(f"Тестовое слово: '{test_word}'")
            print(f"Ожидаемая длина: {k} групп + 'a x b' = общая длина: {k * max(n, m) + 3}")
            print(f"Фактическая длина: {len(test_word)}")
        else:
            print("Тестовое слово не предоставлено в input.txt")
            
    except Exception as e:
        print(f"Ошибка чтения входного файла: {e}")
        print("Используются значения по умолчанию: n=2, m=3, k=1")
        n, m, k = 2, 3, 1
    
    # Генерируем автомат
    generator = MealyMachineGenerator(n, m, k)
    automaton_matrix = generator.generate_automaton()
    
    # Записываем выходные данные в файл
    output_file_path = os.path.join(current_dir, 'output.txt')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(f"Автоматная матрица для n={n}, m={m}, k={k}\n")
        f.write(f"Паттерн: {k} групп по ({n} 'x' ИЛИ {m} 'd') затем 'a x b'\n")
        f.write("Состояние | x | d | a | b\n")
        f.write("-" * 80 + "\n")
        
        # Получаем все состояния в порядке для согласованного вывода
        all_states = ["Qstart"] 
        
        # Добавляем состояния групп в порядке
        for group in range(k):
            for i in range(1, n + 1):
                state_name = f"ReadingX_{group}_{i}"
                if state_name in generator.states:
                    all_states.append(state_name)
            for j in range(1, m + 1):
                state_name = f"ReadingD_{group}_{j}"
                if state_name in generator.states:
                    all_states.append(state_name)
        
        # Добавляем состояния суффикса
        all_states.extend(["SuffixX", "SuffixB", "Qfinal", "Qtrap"])
        
        for state in all_states:
            if state in automaton_matrix:
                row = [state]
                for symbol in ['x', 'd', 'a', 'b']:
                    if symbol in automaton_matrix[state]:
                        next_state, output = automaton_matrix[state][symbol]
                        row.append(f"{next_state}/{output}")
                    else:
                        row.append("-/-")
                f.write(" | ".join(row) + "\n")
        
        # Тестируем слово, если предоставлено
        if test_word:
            f.write(f"\nПроверка слова: '{test_word}'\n")
            is_valid, output_sequence, path, transition_log = validate_word(test_word, automaton_matrix)
            
            f.write(f"Путь состояний: {' -> '.join(path)}\n")
            f.write("Переходы:\n")
            for i, transition in enumerate(transition_log, 1):
                f.write(f"  Шаг {i}: {transition}\n")
            f.write(f"Выходная последовательность: {''.join(output_sequence)}\n")
            f.write(f"Результат: Слово {'ПРИНЯТО' if is_valid else 'ОТВЕРГНУТО'}\n")
            
            # Показываем примеры допустимых слов
            f.write(f"\nПримеры допустимых слов для n={n}, m={m}, k={k}:\n")
            examples = []
            if k == 1:
                examples.append(f"{'x'*n}axb")
                examples.append(f"{'d'*m}axb")
            else:
                # Генерируем некоторые примеры комбинаций
                examples.append(f"{'x'*n}{'d'*m}axb")
                examples.append(f"{'d'*m}{'x'*n}axb")
                examples.append(f"{'x'*n}{'x'*n}axb")
                examples.append(f"{'d'*m}{'d'*m}axb")
            
            for example in examples:
                f.write(f"  - {example}\n")
    
    print(f"\nВыходные данные записаны в: {output_file_path}")

if __name__ == "__main__":
    main()