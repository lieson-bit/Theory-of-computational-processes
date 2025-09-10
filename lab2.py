class TuringMachine:
    def __init__(self, input_tape):
        self.tape = list(input_tape)
        self.head = 0
        self.state = 'q0'
        self.steps = 0
        
    def _get_current_symbol(self):
        if self.head < 0 or self.head >= len(self.tape):
            return 'B'
        return self.tape[self.head]
    
    def _set_current_symbol(self, symbol):
        if self.head < 0:
            self.tape = [symbol] + ['B'] * (-self.head - 1) + self.tape
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape = self.tape + ['B'] * (self.head - len(self.tape)) + [symbol]
        else:
            self.tape[self.head] = symbol
    
    def _move(self, direction):
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        elif direction != 'S':
            raise ValueError(f"Invalid direction: {direction}")
    
    def _print_state(self):
        tape_str = ''.join(self.tape)
        head_pos = ' ' * self.head + '^'
        print(f"Step {self.steps:3d}: State={self.state:2s} | Tape: {tape_str}")
        print(f"           {' ' * 12} {head_pos}")
    
    def run(self, max_steps=500, verbose=True):
        if verbose:
            print("Initial state:")
            self._print_state()
            print("\n" + "="*50)

        # CORRECTED TRANSITION RULES
        transitions = {
            # Start state - find first 1 to mark
            ('q0', '1'): ('X', 'R', 'q1'),
            ('q0', '*'): ('*', 'R', 'q9'),
            ('q9', '1'): ('y', 'R', 'q9'),
            ('q9', '='): ('=', 'S', 'halt'),

            # After marking left 1, go to right side
            ('q1', '1'): ('1', 'R', 'q1'),
            ('q1', '*'): ('*', 'R', 'q2'),

            # Find first 1 on right side to copy
            ('q2', '1'): ('Y', 'R', 'q3'),
            ('q2', 'Y'): ('Y', 'R', 'q2'),
            ('q2', '='): ('=', 'L', 'q7'),

            # Go to end of tape to add new 1
            ('q3', '1'): ('1', 'R', 'q3'),
            ('q3', '='): ('=', 'R', 'q4'),
            ('q4', '_'): ('1', 'L', 'q5'),
            ('q4', '1'): ('1', 'R', 'q4'),

            # Return to right side
            ('q5', '1'): ('1', 'L', 'q5'),
            ('q5', '='): ('=', 'L', 'q6'),
            ('q6', '1'): ('1', 'L', 'q6'),
            ('q6', 'Y'): ('Y', 'L', 'q6'),
            ('q6', '*'): ('*', 'R', 'q2'),

            # All right 1s processed, return to left - RESET Y's to 1's
            ('q7', 'Y'): ('1', 'L', 'q7'),  # Reset Y to 1
            ('q7', '1'): ('1', 'L', 'q7'),
            ('q7', '*'): ('*', 'L', 'q8'),

            # Cleanup - all left 1s processed
            ('q8', '1'): ('1', 'L', 'q8'),
            ('q8', 'X'): ('X', 'R', 'q0'),  # ADDED: Clean up any remaining Y's
            
        }

        while self.state != 'halt' and self.steps < max_steps:
            current_symbol = self._get_current_symbol()
            key = (self.state, current_symbol)

            if key not in transitions:
                if verbose:
                    print(f"\nNo transition defined for (state={self.state}, symbol={current_symbol})")
                    print("Current tape:", ''.join(self.tape))
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
                print("Computation completed successfully!")
            else:
                print(f"Computation stopped after {self.steps} steps")

            result = ''.join([c for c in self.tape if c == '1'])
            print(f"Final result: {len(result)} ones -> {result}")

        return self.tape, self.state

def create_input_string(a, b):
    """Create input string in the format '111*111=' for given numbers"""
    left_ones = '1' * a
    right_ones = '1' * b
    return f"{left_ones}*{right_ones}=______________"

def test_multiplication():
    """Test the multiplication Turing machine"""
    test_cases = [
        (1, 1),  # 1 × 1 = 1
        (2, 1),  # 2 × 1 = 2
        (1, 2),  # 1 × 2 = 2
        (2, 2),  # 2 × 2 = 4
        (2, 3),  # 2 × 3 = 6
        (3, 2),  # 3 × 2 = 6
    ]
    
    print("Testing Multiplication Turing Machine")
    print("=" * 40)
    
    for a, b in test_cases:
        input_str = create_input_string(a, b)
        expected = a * b
        
        print(f"\nTesting {a} × {b} = {expected}")
        print(f"Input: {input_str}")
        
        tm = TuringMachine(input_str)
        final_tape, final_state = tm.run(verbose=False, max_steps=500)
        
        result_ones = ''.join([c for c in final_tape if c == '1'])
        
        print(f"Expected: {expected} ones")
        print(f"Got:      {len(result_ones)} ones")
        
        if len(result_ones) == expected:
            print("✓ SUCCESS!")
        else:
            print("✗ FAILED!")
            print(f"Final tape: {''.join(final_tape)}")
        
        print("-" * 40)

def debug_case(a, b):
    """Debug a specific case with verbose output"""
    print(f"\nDEBUGGING {a} × {b}:")
    print("=" * 30)
    
    input_str = create_input_string(a, b)
    expected = a * b
        
    print(f"Input: {input_str}")
    print(f"Expected: {expected} ones")
    
    tm = TuringMachine(input_str)
    final_tape, final_state = tm.run(verbose=True, max_steps=200)
    
    result_ones = ''.join([c for c in final_tape if c == '1'])
    
    print(f"\nExpected: {expected} ones, Got: {len(result_ones)} ones")
    if len(result_ones) == expected:
        print("✓ SUCCESS!")
    else:
        print("✗ FAILED!")
        print(f"Final tape: {''.join(final_tape)}")

if __name__ == "__main__":
    # Run comprehensive tests
    test_multiplication()
    
    # Debug specific cases that are failing
    print("\n" + "="*60)
  
    
    debug_case(2, 1)
    debug_case(2, 2)