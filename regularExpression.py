# A regular expression parser
from finiteAutomata import *

class RegularExpression:

    PLUS = "+"
    CONCAT = "."
    STAR = "*"

    EPSILON = "e"

    OPs = [PLUS, CONCAT, STAR]
    Ps = ["(", ")"]

    def EvaluateString(exp:str):
        return RegularExpression.EvaluateExpression(RegularExpression.Tokenize(exp))

    def EvaluateExpression(expr:list):
        """
        Returns a nested list structure which represents an expression tree
        """
        if len(expr) == 1:
            if type(expr[0]) == list:
                return RegularExpression.EvaluateExpression(expr[0])
            else:
                return expr[0]

        if expr[0] in RegularExpression.OPs:
            return expr

        stack = []

        eval = []

        index = 0
        while index < len(expr): # Split parenthesis
            if expr[index] == RegularExpression.Ps[0]:
                stack.append(index)
            if expr[index] == RegularExpression.Ps[1]:
                startIndex = stack.pop()
                expr = expr[:startIndex] + [RegularExpression.EvaluateExpression(expr[startIndex+1:index])] + expr[index+1:]
                index = startIndex
            index += 1

        index = 0
        while index < len(expr): # *
            if expr[index] == RegularExpression.STAR:
                expr = expr[:index-1] + [[RegularExpression.STAR, expr[index-1]]] + expr[index+1:]
                index = index-1
            index+=1
        
        index = 0
        while index < len(expr): # .
            if expr[index] == RegularExpression.CONCAT:
                expr = [RegularExpression.EvaluateExpression(expr[:index]), RegularExpression.EvaluateExpression(expr[index+1:])]
                break
            index+=1

        index = 0
        while index < len(expr): # +
            if expr[index] == RegularExpression.PLUS:
                expr = [RegularExpression.PLUS, RegularExpression.EvaluateExpression(expr[:index]), RegularExpression.EvaluateExpression(expr[index+1:])]
                break
            index+=1

        
        return expr


    def Tokenize(exp:str):
        if exp == "":
            return []
        
        if exp[0] in (RegularExpression.OPs + RegularExpression.Ps):
            return [exp[0]] + RegularExpression.Tokenize(exp[1:])

        breaks = []
        for e in (RegularExpression.OPs + RegularExpression.Ps):
            if e in exp:
                breaks.append(exp.index(e))

        if len(breaks) == 0:
            return [exp]
        
        return [exp[:min(breaks)]] + RegularExpression.Tokenize(exp[min(breaks):])

        
def REtoNFA(exp:list, alphabet:set) -> NFA:
    if type(exp) == str:
        return StringToNFA(exp, alphabet)
    if exp[0] == RegularExpression.PLUS:
        return NFA.Union(REtoNFA(exp[1], alphabet), REtoNFA(exp[2], alphabet))
    if exp[0] == RegularExpression.STAR:
        return NFA.Closure(REtoNFA(exp[1], alphabet))

    nfa = REtoNFA(exp[0], alphabet)
    for e in exp[1:]:
        nfa = nfa.Concat(REtoNFA(e, alphabet))

    return nfa



if __name__ == '__main__':
    iS = input()
    iS = iS.replace("{}", "(q+w+e+r+t+y+u+i+o+p+a+s+d+f+g+h+j+k+l+z+x+c+v+b+n+m)")
    print(iS)
    nfa = REtoNFA(RegularExpression.EvaluateString(iS), set("qwertyuiopasdfghjklzxcvbnm "))
    #dfa = NFAtoDFA(nfa)
    #dfa = dfa.MinimizedDFA()
    #print(len(dfa.Q))
    while True:
        print(nfa.CheckAccept(input()))
