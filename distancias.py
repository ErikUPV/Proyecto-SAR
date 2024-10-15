import numpy as np
'''
1- Hacer Backpointers
2- Reduccion de coste
3- si la comparacion entre las palabras es demasiado grande no hace falta la matriz
4- Modificar Indexer y Searcher para usar levenstein
(Opcional)
5- Damerau Restringido
6- Damerau Intemedio
7- Backpointers tmb
'''
def levenshtein_matriz(x, y, threshold=None):
    # esta versión no utiliza threshold, se pone porque se puede
    # invocar con él, en cuyo caso se ignora
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    return D[lenX, lenY]

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
            D[i][j], B[i][j] = min(
                (D[i - 1][j] + 1, (i - 1,j)),
                (D[i][j - 1] + 1, (i, j - 1)),
                (D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), (i - 1, j - 1)),
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
    return D[lenX, lenY], res

def levenshtein_reduccion(x, y, threshold=None): #ERIK
    # completar versión con reducción coste espacial
    lenX, lenY = len(x), len(y)
    vcurrent = np.zeros(lenX + 1, dtype=int)
    vprev = np.zeros(lenX + 1, dtype=int)

    #B = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range (1, lenX + 1):
        vprev[i] = vprev[i - 1] + 1
        #B[i][0] = (i - 1, 0)
    for j in range(1, lenY + 1):
        vcurrent[0] = vprev[0] + 1
        #B[0][j] = (0, j - 1)
        for i in range(1, lenX + 1):
            vcurrent[i] = min(
                vcurrent[i - 1] + 1,
                vprev[i] + 1,
                vprev[i - 1] + (x[i - 1] != y[j - 1]),
            )
        vcurrent, vprev = vprev, vcurrent
    return vprev[lenX]

def levenshtein(x, y, threshold): #HECTOR
    # completar versión reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y)
    vcurrent = np.zeros(lenX + 1, dtype=int)
    vprev = np.zeros(lenX + 1, dtype=int)

    #B = np.zeros((lenX + 1, lenY + 1), dtype=int)
    for i in range (1, lenX + 1):
        vprev[i] = vprev[i - 1] + 1
        #B[i][0] = (i - 1, 0)
    for j in range(1, lenY + 1):
        vcurrent[0] = vprev[0] + 1
        #B[0][j] = (0, j - 1)
        for i in range(1, lenX + 1):
            vcurrent[i] = min(
                vcurrent[i - 1] + 1,
                vprev[i] + 1,
                vprev[i - 1] + (x[i - 1] != y[j - 1]),
            )
        # print(f"El minimo es: {min(vcurrent)}\n")
        if min(vcurrent) > threshold:
            return threshold+1
        vcurrent, vprev = vprev, vcurrent
    if vprev[lenX] > threshold:
        return threshold+1
    return vprev[lenX]

def levenshtein_cota_optimista(x, y, threshold): #JAVIER
    return 0 # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein restringida con matriz
    lenX, lenY = len(x), len(y)
    # COMPLETAR
    return 0 # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_edicion(x, y, threshold=None):
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE
    
def damerau_intermediate(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

opcionesSpell = {
    'levenshtein_m': levenshtein_matriz,
    'levenshtein_r': levenshtein_reduccion,
    'levenshtein':   levenshtein,
    'levenshtein_o': levenshtein_cota_optimista,
    'damerau_rm':    damerau_restricted_matriz,
    'damerau_r':     damerau_restricted,
    'damerau_im':    damerau_intermediate_matriz,
    'damerau_i':     damerau_intermediate
}

opcionesEdicion = {
    'levenshtein': levenshtein_edicion,
    'damerau_r':   damerau_restricted_edicion,
    'damerau_i':   damerau_intermediate_edicion
}

