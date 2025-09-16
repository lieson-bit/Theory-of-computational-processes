#!/usr/bin/env python3
# Enhanced version with debug output

import sys
import re

def parse_set(line):
    m = re.search(r"\{(.*)\}", line)
    if not m:
        return []
    items = [s.strip() for s in m.group(1).split(',') if s.strip() != '']
    return items

def normalize_rule(line):
    line = line.strip().rstrip(',').replace("->", "->")
    if '->' not in line:
        return None
    lhs, rhs = [s.strip() for s in line.split('->', 1)]
    return (lhs, rhs)

def read_input_file(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    
    A = X = A1 = R = INPUT = None
    rules = []
    
    # Parse each section
    sections = re.findall(r'(\w+)\s*=\s*\{([^}]*)\}', content)
    for section_name, section_content in sections:
        if section_name == 'A':
            A = [s.strip() for s in section_content.split(',') if s.strip()]
        elif section_name == 'X':
            X = [s.strip() for s in section_content.split(',') if s.strip()]
        elif section_name == 'A1':
            A1 = [s.strip() for s in section_content.split(',') if s.strip()]
        elif section_name == 'R':
            rule_lines = [s.strip() for s in section_content.split(',') if s.strip()]
            for rule_line in rule_lines:
                rule = normalize_rule(rule_line)
                if rule:
                    rules.append(rule)
        elif section_name == 'INPUT':
            pairs = [s.strip() for s in section_content.split(',') if s.strip()]
            INPUT = {}
            for pair in pairs:
                if '=' in pair:
                    var, val = [s.strip() for s in pair.split('=', 1)]
                    INPUT[var] = val
    
    return A, X, A1, rules, INPUT

def match_pattern(s, pattern, variables):
    """Simple pattern matcher for Post system"""
    # Convert pattern to regex
    regex_pattern = ''
    i = 0
    while i < len(pattern):
        # Check for variables
        found_var = False
        for var in variables:
            if pattern.startswith(var, i):
                regex_pattern += f'(?P<{var}>.*?)'
                i += len(var)
                found_var = True
                break
        
        if not found_var:
            # Escape literal characters
            regex_pattern += re.escape(pattern[i])
            i += 1
    
    match = re.match(regex_pattern, s)
    if not match:
        return None
    
    return match.groupdict()

def apply_rule(s, rule, variables):
    lhs, rhs = rule
    match = match_pattern(s, lhs, variables)
    if not match:
        return None
    
    # Substitute variables in right hand side
    result = rhs
    for var, value in match.items():
        result = result.replace(var, value)
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_simulator.py input.txt")
        return
    
    try:
        A, X, A1, rules, INPUT = read_input_file(sys.argv[1])
        
        print("Configuration loaded:")
        print(f"A: {A}")
        print(f"X: {X}")
        print(f"A1: {A1}")
        print(f"Rules: {rules}")
        print(f"INPUT: {INPUT}")
        print()
        
        # Build initial string
        axiom = A1[0]
        initial = axiom
        for var, value in INPUT.items():
            initial = initial.replace(var, value)
        
        print(f"Initial string: {initial}")
        
        # Run simulation
        current = initial
        step = 0
        max_steps = 100
        
        with open("output.txt", "w") as f:
            f.write(f"Initial: {current}\n\n")
            
            while step < max_steps:
                applied = False
                
                for rule in rules:
                    result = apply_rule(current, rule, X)
                    if result:
                        f.write(f"Step {step + 1}:\n")
                        f.write(f"  Current: {current}\n")
                        f.write(f"  Rule: {rule[0]} -> {rule[1]}\n")
                        f.write(f"  Result: {result}\n\n")
                        
                        current = result
                        applied = True
                        step += 1
                        break
                
                if not applied:
                    f.write("No applicable rules found. Computation halted.\n")
                    print("Computation completed successfully.")
                    break
            else:
                f.write("Maximum step limit reached.\n")
                print("Warning: Maximum step limit reached")
            
            f.write(f"Final result: {current}\n")
        
        print(f"Results written to output.txt")
        print(f"Final result: {current}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()