import os

class MealyMachineGenerator:
    def __init__(self, n, m, k):
        self.n = n
        self.m = m 
        self.k = k
        self.states = ["Qstart", "SuffixA", "SuffixX", "SuffixB", "Qfinal", "Qtrap"]
        self.transitions = {}
        
    def generate_automaton(self):
        self._generate_all_states()
        self._generate_all_transitions()
        return self.transitions
    
    def _generate_all_states(self):
        # Generate states for all k groups
        for group in range(self.k):
            # X-group states: ReadingX_group_i (i from 1 to n)
            for i in range(1, self.n + 1):
                state_name = f"ReadingX_{group}_{i}"
                self.states.append(state_name)
                
            # D-group states: ReadingD_group_j (j from 1 to m)  
            for j in range(1, self.m + 1):
                state_name = f"ReadingD_{group}_{j}"
                self.states.append(state_name)
    
    def _generate_all_transitions(self):
        # Initialize all states with trap transitions
        for state in self.states:
            self.transitions[state] = {}
            for symbol in ['x', 'd', 'a', 'b']:
                self.transitions[state][symbol] = ("Qtrap", "0")
        
        # Start state transitions
        self.transitions["Qstart"] = {
            'x': ("ReadingX_0_1", "0"),
            'd': ("ReadingD_0_1", "0"),
            'a': ("Qtrap", "0"),
            'b': ("Qtrap", "0")
        }
        
        # Generate transitions for all groups
        for group in range(self.k):
            self._add_x_group_transitions(group)
            self._add_d_group_transitions(group)
            
        # CORRECTED Suffix transitions - FIXED!
        # After completing groups, we go to SuffixA and expect 'a'
        # Then SuffixA --a--> SuffixX (expect 'x')
        # Then SuffixX --x--> SuffixB (expect 'b') 
        # Then SuffixB --b--> Qfinal (output 1)
        
        self.transitions["SuffixA"] = {
            'a': ("SuffixX", "0"),  # After groups, expect 'a' to start suffix
            'x': ("Qtrap", "0"),
            'd': ("Qtrap", "0"),
            'b': ("Qtrap", "0")
        }
        self.transitions["SuffixX"] = {
            'x': ("SuffixB", "0"),  # After 'a', expect 'x'
            'a': ("Qtrap", "0"),
            'd': ("Qtrap", "0"), 
            'b': ("Qtrap", "0")
        }
        self.transitions["SuffixB"] = {
            'b': ("Qfinal", "1"),   # After 'x', expect 'b' to finish
            'x': ("Qtrap", "0"),
            'a': ("Qtrap", "0"),
            'd': ("Qtrap", "0")
        }
        
    def _add_x_group_transitions(self, group):
        for i in range(1, self.n + 1):
            state_name = f"ReadingX_{group}_{i}"
            
            if i < self.n:
                # Continue in same x-group - read another 'x'
                self.transitions[state_name]['x'] = (f"ReadingX_{group}_{i+1}", "0")
            else:
                # Completed x-group (got n x's)
                if group < self.k - 1:
                    # More groups needed - can start either x-group or d-group
                    self.transitions[state_name]['x'] = (f"ReadingX_{group+1}_1", "0")
                    self.transitions[state_name]['d'] = (f"ReadingD_{group+1}_1", "0")
                else:
                    # Last group completed - now expect 'a' to start suffix
                    self.transitions[state_name]['a'] = ("SuffixA", "0")
        
    def _add_d_group_transitions(self, group):
        for j in range(1, self.m + 1):
            state_name = f"ReadingD_{group}_{j}"
            
            if j < self.m:
                # Continue in same d-group - read another 'd'
                self.transitions[state_name]['d'] = (f"ReadingD_{group}_{j+1}", "0")
            else:
                # Completed d-group (got m d's)
                if group < self.k - 1:
                    # More groups needed - can start either x-group or d-group
                    self.transitions[state_name]['x'] = (f"ReadingX_{group+1}_1", "0")
                    self.transitions[state_name]['d'] = (f"ReadingD_{group+1}_1", "0")
                else:
                    # Last group completed - now expect 'a' to start suffix
                    self.transitions[state_name]['a'] = ("SuffixA", "0")

def validate_word(word, automaton_matrix):
    """Validate if a word is accepted by the automaton"""
    current_state = "Qstart"
    output_sequence = []
    path = [current_state]
    transition_log = []
    
    print(f"\nValidating word: '{word}'")
    print(f"Expected pattern: k groups of (n x's OR m d's) followed by 'a x b'")
    
    for i, char in enumerate(word):
        if char not in ['x', 'd', 'a', 'b']:
            print(f"Error: Invalid character '{char}' at position {i}")
            return False, output_sequence, path, transition_log
            
        if current_state not in automaton_matrix:
            print(f"Error: Unknown state '{current_state}'")
            return False, output_sequence, path, transition_log
            
        if char not in automaton_matrix[current_state]:
            print(f"Error: No transition for '{char}' from state '{current_state}'")
            print(f"Available transitions from {current_state}: {list(automaton_matrix[current_state].keys())}")
            return False, output_sequence, path, transition_log
            
        next_state, output = automaton_matrix[current_state][char]
        transition_info = f"{current_state} --{char}--> {next_state}"
        print(f"Step {i+1}: {transition_info} (output: {output})")
        
        transition_log.append(transition_info)
        output_sequence.append(output)
        current_state = next_state
        path.append(current_state)
    
    # Check if we ended in final state
    is_accepted = (current_state == "Qfinal")
    print(f"Final state: {current_state}, Accepted: {is_accepted}")
    
    return is_accepted, output_sequence, path, transition_log

def main():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(current_dir, 'input.txt')
    
    print(f"Looking for input file at: {input_file_path}")
    
    # Check if file exists
    if not os.path.exists(input_file_path):
        print("Input file not found. Creating a default input.txt file...")
        
        # Create a default input file
        with open(input_file_path, 'w', encoding='utf-8') as f:
            f.write("n=2 m=3 k=2\n")
            f.write("xxdddaxb\n")
        
        print("Default input.txt created with n=2, m=3, k=2 and test word 'xxdddaxb'")
    
    # Read parameters from file
    test_word = None
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not lines:
                print("Input file is empty. Using default values.")
                n, m, k = 2, 3, 1
            else:
                # First line should contain parameters
                params_line = lines[0]
                params = dict(item.split('=') for item in params_line.split())
                n = int(params['n'])
                m = int(params['m']) 
                k = int(params['k'])
                
                # Second line (if exists) should contain test word
                if len(lines) > 1:
                    test_word = lines[1].replace(" ", "")  # Remove spaces from test word
                    
        print(f"Successfully read parameters: n={n}, m={m}, k={k}")
        print(f"Pattern: {k} groups of ({n} x's OR {m} d's) followed by 'a x b'")
        if test_word:
            print(f"Test word: '{test_word}'")
            print(f"Expected: {k} groups + 'a x b' = total length: {k * max(n, m) + 3}")
            print(f"Actual length: {len(test_word)}")
        else:
            print("No test word provided in input.txt")
            
    except Exception as e:
        print(f"Error reading input file: {e}")
        print("Using default values: n=2, m=3, k=1")
        n, m, k = 2, 3, 1
    
    # Generate automaton
    generator = MealyMachineGenerator(n, m, k)
    automaton_matrix = generator.generate_automaton()
    
    # Write output to file
    output_file_path = os.path.join(current_dir, 'output.txt')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(f"Автоматная матрица для n={n}, m={m}, k={k}\n")
        f.write(f"Паттерн: {k} групп по ({n} 'x' ИЛИ {m} 'd') затем 'a x b'\n")
        f.write("Состояние | x | d | a | b\n")
        f.write("-" * 80 + "\n")
        
        # Get all states in order for consistent output
        all_states = ["Qstart"] 
        
        # Add group states in order
        for group in range(k):
            for i in range(1, n + 1):
                state_name = f"ReadingX_{group}_{i}"
                if state_name in generator.states:
                    all_states.append(state_name)
            for j in range(1, m + 1):
                state_name = f"ReadingD_{group}_{j}"
                if state_name in generator.states:
                    all_states.append(state_name)
        
        # Add suffix states
        all_states.extend(["SuffixA", "SuffixX", "SuffixB", "Qfinal", "Qtrap"])
        
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
        
        # Test the word if provided
        if test_word:
            f.write(f"\nПроверка слова: '{test_word}'\n")
            is_valid, output_sequence, path, transition_log = validate_word(test_word, automaton_matrix)
            
            f.write(f"Путь состояний: {' -> '.join(path)}\n")
            f.write("Переходы:\n")
            for i, transition in enumerate(transition_log, 1):
                f.write(f"  Шаг {i}: {transition}\n")
            f.write(f"Выходная последовательность: {''.join(output_sequence)}\n")
            f.write(f"Результат: Слово {'ПРИНЯТО' if is_valid else 'ОТВЕРГНУТО'}\n")
            
            # Show examples of valid words
            f.write(f"\nПримеры допустимых слов для n={n}, m={m}, k={k}:\n")
            examples = []
            if k == 1:
                examples.append(f"{'x'*n}axb")
                examples.append(f"{'d'*m}axb")
            else:
                # Generate some example combinations
                examples.append(f"{'x'*n}{'d'*m}axb")
                examples.append(f"{'d'*m}{'x'*n}axb")
                examples.append(f"{'x'*n}{'x'*n}axb")
                examples.append(f"{'d'*m}{'d'*m}axb")
            
            for example in examples:
                f.write(f"  - {example}\n")
    
    print(f"\nOutput written to: {output_file_path}")

if __name__ == "__main__":
    main()