import distancias
"""
import numpy as np
def levenshtein_edicion(x, y, threshold=None): #ALEX
    # a partir de la versión levenshtein_matriz

    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
        B[i][0] = (i-1, 0)
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        B[0][j] = (0,j-1)
        for i in range(1, lenX + 1):
            D[i][j],B[i][j] = min(
                (D[i - 1][j] + 1,(i - 1,j)),
                (D[i][j - 1] + 1,(i,j - 1)),
                (D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),(i - 1,j - 1)),
            )
    res = []
    act = (lenX, lenY)
    while D[act[0], act[1]] != 0:
        prev = B[act[0]][act[1]]
        if prev[0] == act[0]:
            res.insert(0, ('', y[act[1]-1]))
        elif prev[1] == act[1]:
            res.insert(0, (x[act[0]-1], ''))
        else:
            res.insert(0, (x[act[0]-1], y[act[1]-1]))
        act = prev
    return D[lenX, lenY], res"""


print(distancias.damerau_restricted_edicion("apato","zaaptos"))
print("paot"[4 - 1] + "zapatos"[7 - 2])
print("paot"[4 - 2] + "zapatos"[7 - 1])

def langford(N):
    N2   = 2*N
    seq  = [0]*N2
    def backtracking(num):
        #print(num)
        if num<=0:
            yield "-".join(map(str, seq))
        else:
            for i,v in enumerate(seq[:-num-1]):
                if v == 0 and seq[i+1+num]==0:
                    seq[i] = num
                    seq[i + 1 + num] = num
                    yield from backtracking(num-1)
                    seq[i] = 0
                    seq[i + 1 + num] = 0


    if N%4 in (0,3):
        yield from backtracking(N)

for i, sol in enumerate(langford(4)):
    print(i, sol)