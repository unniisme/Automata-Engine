from finiteAutomata import *
exp = None

def concat(a : NFA,b : NFA) -> NFA:
    return NFA.Concat(a, b)

def union(a : NFA,b : NFA) -> NFA:
    return NFA.Union(a, b)

def star(a : NFA) -> NFA:
    return a.Closure()    


tests = int(input()) 
for test in range(tests):
    s = input()

    alphabet = set([s[i+7] for i in range(len(s)) if s.startswith('symbol', i)])

    nfa = StringToNFA("", set())


    i = s.find('symbol')
    while i != -1:
        s = s[:i] + "StringToNFA('" + s[i+7] + "', alphabet)" + s[i+9:]
        i = s.find('symbol')

    exec("nfa = " + s)

    dfa = NFAtoDFA(nfa)
    dfa = dfa.MinimizedDFA()

    # nfa.CheckAccept()
    # Also works and is much faster since DFA need not be constructed.

    # print(dfa)
    
    if dfa.CheckAccept(input()):
        print("Yes")
    else:
        print("No")
