import itertools
from automataError import AutomataError

class Uniq:
    """
    Class to maintain unique names for an arbitrary number of new states
    """
    x = 1

    def setVal(x):
        """
        Set the starting unique value
        """
        Uniq.x = x

    def getVal():
        """
        Get a unique value
        """
        Uniq.x += 1
        return Uniq.x-1

class FiniteAutomata:
    """
    Abstract class to represent any finite automata
    """
    
    def __init__(self, Q : set, sigma : set, transitionTable : dict, s, F : set):
        self.Q = Q
        self.sigma = sigma
        self.transitionTable = transitionTable
        self.s = s
        self.F = F

    def delta(self, q, a):
        pass

    def deltaCap(self, q, s : list):
        pass

    def CheckAccept(self, s : list):
        pass

class DFA(FiniteAutomata):

    def __init__(self, Q : set, sigma : set, transitionTable : dict, s, F : set):
        """
        Define a DFA.
        Q is the set of states
        sigma is the alphabet of the language
        transition table is a mapping, such that transitionTable[state][action] = delta(state, action) 
        s is the start state
        F is the set of final state

        delta function is automatically constructed from the transitionTable
        """
        for q in Q: #Checking if automata is a complete DFA
            try:
                for x in sigma:
                    if transitionTable[q][x] not in Q:
                        raise AutomataError(AutomataError.NON_CLOSURE)
            except KeyError:
                raise AutomataError(AutomataError.NON_CLOSURE)
            except AutomataError as e:
                raise e
            except Exception as e:
                raise e

        self.Q = Q
        self.sigma = sigma
        self.transitionTable = transitionTable
        self.s = s
        self.F = F       



    def delta(self, q, a):
        if q not in self.Q:
            raise AutomataError(AutomataError.INVALID_STATE)
        if a not in self.sigma:
            raise AutomataError(AutomataError.INVALID_TRANSITION)

        return self.transitionTable[q][a]

    def delta_cap(self, q, s : list):
        if len(s) == 1:
            return self.delta(q, s[0])
        if len(s) == 0:
            return q
        
        return self.delta(self.delta_cap(q, s[:-1]), s[-1])

    def CheckAccept(self, x) -> bool:
        """
        Check if the input string is accepted by the DFA
        """
        return self.delta_cap(self.s, x) in self.F


    def CheckEq(M1, M2) -> bool:
        """
        Check if 2 DFAs are equal.
        Note that the names of states have to be equal.
        Does not check for homomorphism
        """
        if M1.Q != M2.Q:
            return False

        if M1.sigma != M2.sigma:
            return False

        if M1.s != M2.s:
            return False

        if M1.F != M2.F:
            return False

        for a in M1.sigma:
            for q in M1.Q:
                if M1.delta(q, a) != M2.delta(q,a):
                    return False
                    
        return True


    def MinimizedDFA(dfa : "DFA", makeuid : bool = True) -> "DFA":
        """
        Find the DFA with the minimum number of states that accepts the same language
        """
        # Reachability
        def ReachableDFA(dfa) -> DFA:
            """
            Runs a DFS on the DFA from the start state and removes states that are unreachable
            """
            frontier = [dfa.s]
            expanded = []
            while len(frontier) != 0:
                q = frontier.pop()
                expanded.append(q)

                for a in dfa.sigma:
                    newq = dfa.delta(q, a)
                    if newq not in expanded:
                        frontier.append(newq)

            Q = set(expanded)
            transitionTable = {k : dfa.transitionTable[k] for k in Q}

            return DFA(Q, dfa.sigma, transitionTable, dfa.s, dfa.F)

        def uid(dfa) -> DFA:
            """
            Rename the DFA with unique numbers for states.
            For clean representation purposes.
            """
            uidStates = {q : Uniq.getVal() for q in dfa.Q}
            transitionTable = {uidStates[q] : {a : uidStates[dfa.delta(q,a)] for a in dfa.sigma} for q in dfa.Q}

            return DFA({uidStates[q] for q in dfa.Q}, dfa.sigma, transitionTable, uidStates[dfa.s], {uidStates[q] for q in dfa.F})

        # Remove unreachable states
        dfa = ReachableDFA(dfa)

        partitions = set()
        oldPartition = None
        marked = set()

        # Mark initial states
        for p in dfa.Q:
            for q in dfa.Q:
                if p!=q:
                    if p in dfa.F and q not in dfa.F:
                        marked.add(frozenset([p,q]))
                    elif not (p not in dfa.F and q in dfa.F):
                        partitions.add(frozenset([p,q]))

        # Mark each state
        updateFlag = True
        while partitions != oldPartition:
            oldPartition = partitions.copy()         
            partitions = set()

            for p in dfa.Q:
                for q in dfa.Q:
                    if p==q:
                        continue
                        
                    if {p,q} in marked:
                        continue

                    for a in dfa.sigma:
                        if {dfa.delta(q, a), dfa.delta(p, a)} in marked:
                            marked.add(frozenset([q, p]))
                        else:
                            newP = frozenset([q, p])
                            temp_partitions = partitions.copy()
                            for partition in partitions:
                                if newP.intersection(partition) != set():
                                    temp_partitions.remove(partition)
                                    newP = frozenset.union(newP, partition)
                            partitions = temp_partitions
                            partitions.add(newP)
        
        # Add all other states as singleton partitions
        for q in dfa.Q:
            if not any([q in partition for partition in partitions]):
                partitions.add(frozenset({q}))

        # Define transition between equivalence classes
        partitionTransitions = {}
        for partition in partitions:
            partitionTransitions[partition] = {}
            for a in dfa.sigma:
                for p in partition:
                    break

                q = dfa.delta(p, a)
                
                for partition1 in partitions: #Bruh
                    if q in partition1:
                        partitionTransitions[partition][a] = partition1
                        break
        
        # Define start and final states
        s = [partition for partition in partitions if dfa.s in partition][0]
        F = set()
        for f in dfa.F:
            for partition in partitions:
                if f in partition:
                    F.add(partition)
                    continue
        
        if makeuid:
            return uid(DFA(partitions, dfa.sigma, partitionTransitions, s, F))
        return DFA(partitions, dfa.sigma, partitionTransitions, s, F)
        

    def Intersection(M1, M2):
        """
        Returns a DFA, the language of which is the intersection of the languages of in the 2 input DFAs
        """
        if M1.sigma != M2.sigma:
            return AutomataError

        Q = [(q1,q2) for q1 in M1.Q for q2 in M2.Q]     # Q = Q1xQ2
        sigma = M1.sigma
        transitionTable = {}                            # delta((q1,q2), a) = (delta1(q1,a), delta2(q2,a))
        for q1 in M1.Q:
            for q2 in M2.Q:
                transitionTable[(q1,q2)] = {}
                for a in sigma:
                    transitionTable[(q1,q2)][a] = (M1.delta(q1, a), M2.delta(q2, a))
        s = (M1.s, M2.s)                                # s = (s1,s2)
        F = {(q1,q2) for q1 in M1.F for q2 in M2.F}     # F = F1xF2

        return DFA(Q, sigma, transitionTable, s, F)
    
    def Union(M1, M2):
        """
        Returns a DFA, the language of which is the union of the languages of in the 2 input DFAs
        """
        if M1.sigma != M2.sigma:
            return AutomataError

        Q = [(q1,q2) for q1 in M1.Q for q2 in M2.Q]     # Q = Q1xQ2
        sigma = M1.sigma
        transitionTable = {}                            # delta((q1,q2), a) = (delta1(q1,a), delta2(q2,a))
        for q1 in M1.Q:
            for q2 in M2.Q:
                transitionTable[(q1,q2)] = {}
                for a in sigma:
                    transitionTable[(q1,q2)][a] = (M1.delta(q1, a), M2.delta(q2, a))
        s = (M1.s, M2.s)                                # s = (s1,s2)
        F = set.union({(q1,q2) for q1 in M1.Q for q2 in M2.F},{(q1,q2) for q1 in M1.F for q2 in M2.Q})  # F = (F1xQ2)U(Q1xF2)

        return DFA(Q, sigma, transitionTable, s, F)

    def Compliment(M1):
        """
        Returns a DFA, the language of which is the complement of the languages of in the input DFA
        """
        return DFA(M1.Q, M1.sigma, M1.transitionTable, M1.s, M1.Q.difference(M1.F))


    def __str__(self):
        out = "Start: " + str(self.s) + "\tAccept: " + str(self.F) + "\n"
        for q in self.Q:
            out += str(q)
            out += "\n"

            for a in self.sigma:
                out += "\t" + str(a) + " : " + str(self.delta(q,a))
                out += "\n"
        return out

class NFA(FiniteAutomata):

    def __init__(self, Q : set, sigma : set, transitionTable : set, S : set, F : set):
        """
        Define an NFA.
        Q is the set of states
        sigma is the alphabet of the language
        transition table is a mapping, such that transitionTable[state][action] = delta(state, action) 
        S is the set of start states
        F is the set of final states

        delta function is automatically constructed from the transitionTable
        """
        self.Q = Q
        self.sigma = sigma.union({None})  #None being epsilon
        self.transitionTable = transitionTable
        self.S = S
        self.F = F 

    def delta(self, q, a = None) -> set:
        if q not in self.Q:
            raise AutomataError(AutomataError.INVALID_STATE)
        if a not in self.sigma:
            raise AutomataError(AutomataError.INVALID_TRANSITION)

        if a == None:
            # Epsilon case
            if a in self.transitionTable[q]:
                return self.transitionTable[q][a].union({q})
            return {q}
        if a not in self.transitionTable[q]:
            # Phi case
            return set([])


        return self.transitionTable[q][a]

    def GetEpsilonUnion(self, q):
        """
        Returns the set of all states that can be reached via epsilon transitions from the input state.
        """
        if type(q) == set:
            A = q.copy()
            for state in q:
                A.update(self.GetEpsilonUnion(state))
            return A
                

        if self.delta(q) == {q}:
            return {q}
        A = {q}
        for q1 in self.delta(q):
            if q1!=q:
                A.update(self.GetEpsilonUnion(q1))

        return A
                
  
    def delta_cap(self, A : set, s : list):
        if len(s) == 0:
            for q in A:
                A = A.union(self.delta(q))
            return self.GetEpsilonUnion(A)
        
        B = set()
        for q in self.delta_cap(self.delta_cap(A,[]), s[:-1]):
            B = B.union(self.delta(q, s[-1]))

        return self.GetEpsilonUnion(B)

        

    def CheckAccept(self, s : list):
        """
        Check if the input string is accepted by the NFA
        """
        if self.delta_cap(self.S, s).intersection(self.F) == set([]):
            return False
        return True

    #Kleene Algebra
    def Concat(N1, N2):
        """
        For N1 of language L1 and N2 of language L2, returns L1.L2
        Currently assumes that state names are already different. Screws up otherwise
        """
        if N1.sigma != N2.sigma:
            raise AutomataError

        transitionTable = N1.transitionTable.copy()
        transitionTable.update(N2.transitionTable) 
        for q in N1.F:
            if None in transitionTable[q].keys():
                transitionTable[q][None].update(N2.S)
            else:
                transitionTable[q][None] = N2.S

        return NFA(set.union(N1.Q,N2.Q), N1.sigma, transitionTable, N1.S, N2.F)

    def Union(N1, N2):
        """
        For N1 of language L1 and N2 of language L2, returns L1+L2
        """
        if N1.sigma != N2.sigma:
            raise AutomataError

        newState = Uniq.getVal()
        Q = set.union(N1.Q, N2.Q).union({newState})
        transitionTable = N1.transitionTable.copy()
        transitionTable.update(N2.transitionTable)
        transitionTable[newState] = {None : set.union(N1.S, N2.S)}

        return NFA(Q, N1.sigma, transitionTable, {newState}, set.union(N1.F,N2.F))

    def Closure(N1):
        """
        For N1 of language L1, returns L1*
        """
        newState = Uniq.getVal()
        Q = N1.Q.union({newState})
        transitionTable = N1.transitionTable.copy()
        transitionTable[newState] = {None : N1.S}
        for q in N1.F:
            if None in transitionTable[q].keys():
                transitionTable[q][None].update(N1.S)
            else:
                transitionTable[q][None] = N1.S

        return NFA(Q, N1.sigma, transitionTable, {newState}, N1.F.union({newState}))



    def __str__(self):
        out = "Start: " + str(self.S) + "\tAccept: " + str(self.F) + "\n"
        for q in self.Q:
            out += str(q)
            out += "\n"

            for a in self.sigma:
                if self.delta(q,a) != set():
                    out += "\t" + str(a) + " : " + str(self.delta(q,a))
                    out += "\n"
        return out


def NFAtoDFA(nfa : NFA) -> DFA:
    """
    Converts an NFA to a DFA
    """
    subsets = []
    transitionTable = {}

    # States are all subsets of states of NFA
    for i in range(len(nfa.Q)+1):
        subsets += [set(i) for i in itertools.combinations(nfa.Q, i)]   

    s = subsets.index(nfa.S)

    # Final state is any state in DFA such that its intersection with the final states of NFA is non empty    
    F = set()
    for i, subset in enumerate(subsets):
        if subset.intersection(nfa.F) != set([]):
            F.add(i)

    # Transitions
    for i,A in enumerate(subsets):
        transitionTable[i] = {}
        for x in nfa.sigma:
            transitionTable[i][x] = subsets.index(nfa.delta_cap(A, [x]))

    return DFA(set(range(len(subsets))), nfa.sigma.difference({None}), transitionTable, s, F)

def StringToNFA(string : str, alphabet : set) -> NFA:
    """
    Creates an NFA that accepts only the given string
    """
    Q = [Uniq.getVal() for i in range(len(string)+1)]
    transitionTable = {}
    for i in range(len(string)):
        transitionTable[Q[i]] = {string[i] : {Q[i+1]}}
        transitionTable[Q[-1]] = {}

    return NFA(set(Q), alphabet, transitionTable, {Q[0]}, {Q[-1]})
        



if __name__=="__main__":

    dfa = DFA({0,1,2,3}, {"0","1"}, {0 : {"0" : 0, "1" : 2}, 1 : {"0" : 1, "1" : 2}, 2 : {"0" : 2, "1" : 2}, 3 : {"0" : 3, "1" : 2}}, 0, {2})
    print(dfa)
    print(dfa.MinimizedDFA())
    while True:
        print(dfa.CheckAccept(input()))



    """Uniq.setVal(-1)
    Q = [Uniq.getVal() for i in range(2)]
    sig = {"0", "1"}
    delt1 = {Q[0] : {"0" : {0}, "1":{0,1}}, Q[1] : {}}
    nfa1 = NFA(set(Q), sig, delt1, {Q[0]}, {Q[1]})
    dfa1 = NFAtoDFA(nfa1)

    Q = [Uniq.getVal() for i in range(3)]
    delt2 = {Q[0] : {"0" : {Q[1], Q[0]}, 
                    "1" : {Q[0]}},
            Q[1] : {"1" : {Q[2]}},
            Q[2] : {"0" : {Q[2]},
                    "1" : {Q[2]}}}
    nfa2 = NFA(Q, sig, delt2, {Q[0]}, {Q[2]})
    dfa2 = NFAtoDFA(nfa2)

    dfa = dfa1.Union(dfa2)
    print(dfa1)
    print(dfa2)
    print(dfa)

    while True:
        x = input()
        print(dfa1.CheckAccept(x))
        print(dfa2.CheckAccept(x))
        print(dfa.CheckAccept(x))"""