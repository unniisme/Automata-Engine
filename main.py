from finiteAutomata import *
import sys

exp = None

# Functions wrappers as given in the question

def concat(a : NFA,b : NFA) -> NFA:
    return NFA.Concat(a, b)

def union(a : NFA,b : NFA) -> NFA:
    return NFA.Union(a, b)

def star(a : NFA) -> NFA:
    return a.Closure()    


tests = int(input()) 
for test in range(tests):
    s = input()

    # Determine alphabet set of input expression
    alphabet = set([s[i+7] for i in range(len(s)) if s.startswith('symbol', i)])

    # Initialize empty nfa
    nfa = StringToNFA("", set())

    # In string, replace symbol(x) with StringToNFA('x')
    i = s.find('symbol')
    while i != -1:
        s = s[:i] + "StringToNFA('" + s[i+7] + "', alphabet)" + s[i+9:]
        i = s.find('symbol')

    # Run the string as a python script
    exec("nfa = " + s)

    # Convert NFA to minimized DFA
    dfa = NFAtoDFA(nfa)
    dfa = dfa.MinimizedDFA()

    # Debugging
    if "--dfa" in sys.argv:
        print(dfa)

    if "--nfa" in sys.argv:
        print(nfa)

    # nfa.CheckAccept()
    # Also works and is much faster since DFA need not be constructed.

    if dfa.CheckAccept(input()):
        print("Yes")
    else:
        print("No")
