from finiteAutomata import *

nfa = StringToNFA("010010", {"0","1"})
dfa = NFAtoDFA(nfa)
dfa = dfa.MinimizedDFA()

print(dfa)


def comp(s):
    if s == "0":
        return "1"
    else:
        return "0"

Q = set([(q,b) for q in dfa.Q for b in [0,1]])
tt = {}
for q,b in Q:
    tt[(q,b)] = {}
    for a in dfa.sigma:
        tt[(q,b)][a] = {(dfa.delta(q, a), b)}
        if b==0:
            tt[(q,b)][None] = {(dfa.delta(q, "1"),1)}

S = {(dfa.s, 0)}
F = {(q,1) for q in dfa.F}

nfa = NFA(Q, dfa.sigma, tt, S, F)


while True:
    print(nfa.CheckAccept(input()))