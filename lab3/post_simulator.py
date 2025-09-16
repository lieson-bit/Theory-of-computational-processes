#!/usr/bin/env python3
# post_simulator.py - Enhanced version with INPUT section support

import sys
import re

def parse_input_file(filename):
    """Parse input file with support for INPUT section"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{filename}' not found.")
    
    # Initialize components
    A = set()
    X = set()
    A1 = set()
    R = []
    INPUT = {}
    
    # Parse each section using regex
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
    """Substitute variables with their values"""
    result = string
    for var, value in variables.items():
        result = result.replace(var, value)
    return result

def validate_string(s, A, X):
    """Validate that all characters in string are in alphabet A"""
    for char in s:
        if char not in A:
            return False, f"Symbol '{char}' not in alphabet A"
    return True, ""

def apply_rule(current_string, rule, A, X):
    """Try to apply a rule to the current string"""
    lhs, rhs = rule
    
    # Try to match the rule at every position
    for i in range(len(current_string)):
        substitutions = {}
        lhs_index = 0
        current_index = i
        match = True
        
        while lhs_index < len(lhs) and current_index < len(current_string):
            if lhs[lhs_index] in X:
                # Variable - capture everything until next constant
                var = lhs[lhs_index]
                start = current_index
                
                # Look for the end of this variable (next constant in pattern or end)
                # Find next constant in lhs after this variable
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
                    # Variable goes till end
                    value = current_string[start:]
                    current_index = len(current_string)

                
                value = current_string[start:current_index]
                substitutions[var] = value
                lhs_index += 1
            else:
                # Constant - must match exactly
                if current_string[current_index] != lhs[lhs_index]:
                    match = False
                    break
                current_index += 1
                lhs_index += 1
        
        # Check if we fully matched the pattern
        if match and lhs_index == len(lhs):
            # Substitute variables in the right side
            new_part = rhs
            for var, value in substitutions.items():
                new_part = new_part.replace(var, value)
            
            # Validate the result
            valid, error = validate_string(new_part, A, X)
            if not valid:
                raise ValueError(f"Rule application error: {error}")
            
            # Create the new string
            new_string = current_string[:i] + new_part + current_string[current_index:]
            return new_string, substitutions
    
    return current_string, None  # Return current_string instead of None

def main():
    if len(sys.argv) != 2:
        print("Usage: python post_simulator.py <input_file>")
        return

    try:
        # Parse input file
        A, X, A1, R, INPUT = parse_input_file(sys.argv[1])

        if not A1:
            print("Error: No axioms found")
            return
        axiom_template = next(iter(A1))
        current_string = substitute_variables(axiom_template, INPUT) if INPUT else axiom_template

        step = 0
        max_steps = 1000
        output_filename = "output.txt"
        final_result = ""  # Store last seen /…= value

        with open(output_filename, "w", encoding='utf-8') as output_file:
            output_file.write(f"Initial string: {current_string}\n\n")

            while step < max_steps:
                rule_applied = False

                for rule in R:
                    new_string, substitutions = apply_rule(current_string, rule, A, X)

                    if substitutions is not None:
                        # Update final_result if /…= pattern exists
                        match = re.search(r'/([1]+)=', new_string)
                        if match:
                            final_result = match.group(1)

                        # Write step
                        output_file.write(f"Step {step + 1}:\n")
                        output_file.write(f"Original string: {current_string}\n")
                        output_file.write(f"Applied rule: {rule[0]} -> {rule[1]}\n")
                        output_file.write(f"Result: {new_string}\n\n")

                        current_string = new_string
                        rule_applied = True
                        step += 1
                        break

                if not rule_applied:
                    output_file.write("Computation completed successfully. No more rules apply.\n")
                    break
            else:
                output_file.write("Computation stopped: Maximum step limit reached.\n")

            output_file.write(f"Final result: {final_result}\n")

        print(f"Computation results written to {output_filename}")
        print(f"Final computed result: {final_result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

    