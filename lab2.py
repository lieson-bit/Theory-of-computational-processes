from collections import defaultdict

class TuringMachine:
    def __init__(self, transitions, start_state, halt_state, blank='λ'):
        # transitions: dict[(state, sym)] = (next_state, write_sym, move) where move in {'L','R','E'}
        self.delta = transitions
        self.q = start_state
        self.halt = halt_state
        self.blank = blank
        self.tape = defaultdict(lambda: blank)
        self.head = 0

    def load(self, s):
        self.tape = defaultdict(lambda: self.blank)
        for i, ch in enumerate(s):
            self.tape[i] = ch
        self.head = 0

    def step(self):
        if self.q == self.halt:
            return False
        sym = self.tape[self.head]
        if (self.q, sym) not in self.delta:
            # no rule → stuck (non-halting); for lab semantics, that’s “undefined”
            return False
        nq, ws, mv = self.delta[(self.q, sym)]
        self.tape[self.head] = ws
        if mv == 'L':
            self.head -= 1
        elif mv == 'R':
            self.head += 1
        # 'E' = no move
        self.q = nq
        return True

    def run(self, max_steps=100000):
        steps = 0
        while steps < max_steps and self.q != self.halt and self.step():
            steps += 1
        return steps

    def snapshot(self, window=60):
        # show a window around the non-blank region
        keys = [k for k,v in self.tape.items() if v != self.blank]
        if not keys:
            lo = hi = 0
        else:
            lo, hi = min(keys)-2, max(keys)+3
        s = []
        for i in range(lo, hi):
            ch = self.tape[i]
            if i == self.head:
                s.append(f"[{self.q}:{ch}]")
            else:
                s.append(ch)
        return ''.join(s)

# Build the example machine
rules = [
    ('q0','1','q1','λ','R'),
    ('q1','1','q1','1','R'),
    ('q1','*','q2','*','R'),
    ('q2','1','q3','0','R'),
    ('q3','1','q3','1','R'),
    ('q3','=', 'q3','=', 'R'),
    ('q3','λ','q4','1','L'),
    ('q4','1','q4','1','L'),
    ('q4','0','q2','0','R'),
    ('q4','=', 'q5','=', 'L'),
    ('q5','1','q5','1','L'),
    ('q5','0','q5','1','L'),
    ('q5','*','q6','*','L'),
    ('q6','1','q7','1','L'),
    ('q6','λ','qz','λ','R'),
    ('q7','1','q7','1','L'),
    ('q7','λ','q0','λ','R'),
]
delta = { (q,a):(nq,ws,mv) for q,a,nq,ws,mv in rules }

tm = TuringMachine(delta, start_state='q0', halt_state='qz', blank='λ')
tm.load("11*111=")  # input: a=2, b=3
tm.run()
# Read out the tape (strip blanks)
out_cells = [tm.tape[i] for i in range(-50, 200)]
output = ''.join(ch for ch in out_cells if ch != 'λ')
print("Output tape:", output)  # Expect something like "*11111=" or "11111=" depending on where you start reading
