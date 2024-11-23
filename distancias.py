import math

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
    counts = {}
    for char in x:
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1
    for char in y:
        if char in counts:
            counts[char] -= 1
        else:
            counts[char] = -1
    
    pos = 0
    neg = 0
    for valor in counts.values():
        if valor > 0:
            pos += valor
        elif valor < 0:
            neg += abs(valor)
    cota_optimista = max(pos, neg)
    
    return threshold + 1 if cota_optimista > threshold else levenshtein(x, y, threshold)

def damerau_restricted_matriz(x, y, threshold=None): #ALEX
    # completar versión Damerau-Levenstein restringida wcon matriz
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                (D[i - 2][j - 2] + 1) if i > 1 and j > 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2] else math.inf,
            )
    return D[lenX, lenY]

def damerau_restricted_edicion(x, y, threshold=None): #ALEX
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    lenX, lenY = len(x), len(y)

    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
        B[i][0] = (i-1, 0)
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        B[0][j] = (0, j-1)
        for i in range(1, lenX + 1):
            D[i][j], B[i][j] = min(
                (D[i - 1][j] + 1, (i - 1, j)),
                (D[i][j - 1] + 1, (i, j - 1)),
                (D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), (i - 1, j - 1)),
                ((D[i - 2][j - 2] + 1) if i > 1 and j > 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2] else math.inf, (i - 2, j - 2)) ,
            )
    res = []
    act = (lenX, lenY)
    while B[act[0], act[1]] != 0:
        prev = B[act[0]][act[1]]
        if prev[0] == act[0]:
            res.insert(0, ('', y[act[1] - 1]))
        elif prev[1] == act[1]:
            res.insert(0, (x[act[0] - 1], ''))
        else:
            if prev[0] + 1 == act[0] and prev[1] + 1 == act[1]:
                res.insert(0, (x[act[0] - 1], y[act[1] - 1]))
            else:
                res.insert(0, (x[prev[0]: act[0]], y[prev[1]:act[1]]))
        act = prev



    return D[lenX, lenY], res # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted(x, y, threshold=None): #HECTOR
    # versión con reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y)

    vcurrent = np.zeros(lenX+1, dtype=int)
    vprev = np.zeros(lenX+1, dtype=int)
    vdprev = np.zeros(lenX+1, dtype=int)

    
    # B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        vprev[i] = vprev[i-1] +1
        # B[i][0] = (i-1, 0)
    for j in range(1, lenY + 1):
        vcurrent[0] = vprev[0] + 1
        # B[0][j] = (0, j-1)
        for i in range(1, lenX + 1):
            vcurrent[i] = min(
                vcurrent[i - 1] + 1,
                vprev[i] + 1,
                vprev[i - 1] + (x[i - 1] != y[j - 1]),
                ((vdprev[i - 2] + 1) if i > 1 and j > 1 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2] else math.inf)
            )
        if min(vcurrent) > threshold:
            return threshold+1
        vcurrent, vprev, vdprev = vdprev, vcurrent, vprev

    if vprev[lenX] > threshold:
        return threshold+1
    return vprev[lenX]
    res = []
    act = (lenX, lenY)
    while D[act[0], act[1]] != 0:
        prev = B[act[0]][act[1]]
        if prev[0] == act[0]:
            res.insert(0, ('', y[act[1] - 1]))
        elif prev[1] == act[1]:
            res.insert(0, (x[act[0] - 1], ''))
        else:
            if prev[0] + 1 == act[0] and prev[1] + 1 == act[1]:
                res.insert(0, (x[act[0] - 1], y[act[1] - 1]))
            else:
                res.insert(0, (x[prev[0]: act[0]], y[prev[1]:act[1]]))
        act = prev
    return D[lenX, lenY], res # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None): #ALEX
    # completar versión Damerau-Levenstein intermedia con matriz
    lenX, lenY = len(x), len(y)

    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
                (D[i - 2][j - 2] + 1) if i>1 and j>1 and x[i - 1] == y[j - 2] and x[i - 2] == y[j - 1] else math.inf,
                (D[i - 3][j - 2] + 2) if i >= 3 and j >= 2 and x[i - 1] == y[j - 2] and x[i - 3] == y[j - 1] and x[i - 2] != y[j - 1] else math.inf,
                (D[i - 2][j - 3] + 2) if i >= 2 and j >= 3 and x[i - 1] == y[j - 3] and x[i - 2] == y[j - 1] and x[i - 1] != y[j - 2]  else math.inf,
            )
    return D[lenX, lenY]

def damerau_intermediate_edicion(x, y, threshold=None): #ALEX
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz
    lenX, lenY = len(x), len(y)

    D = np.zeros((lenX + 1, lenY + 1), dtype=int)
    B = np.zeros((lenX + 1, lenY + 1), dtype=tuple)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
        B[i][0] = (i-1,0)
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        B[0][j] = (0,j - 1)
        for i in range(1, lenX + 1):
            D[i][j], B[i][j]= min(
                (D[i - 1][j] + 1, (i - 1, j)),
                (D[i][j - 1] + 1, (i, j - 1)),
                (D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), (i - 1, j - 1)),
                ((D[i - 2][j - 2] + 1) if i > 1 and j > 1 and x[i - 1] == y[j - 2] and x[i - 2] == y[j - 1] else math.inf, (i - 2, j - 2)),
                ((D[i - 3][j - 2] + 2) if i>2 and j>1 and x[i - 1] == y[j - 2] and x[i - 3] == y[j - 1] and x[i - 2] != y[
                    j - 1] else math.inf, (i - 3, j - 2)),
                ((D[i - 2][j - 3] + 2) if i>1 and j>2 and x[i - 1] == y[j - 3] and x[i - 2] == y[j - 1] and x[i - 1] != y[
                    j - 2] else math.inf,(i - 2, j - 3)),
            )
    res = []
    act = (lenX, lenY)
    while D[act[0], act[1]] != 0:
        prev = B[act[0]][act[1]]
        if prev[0] == act[0]:
            res.insert(0, ('', y[act[1] - 1]))
        elif prev[1] == act[1]:
            res.insert(0, (x[act[0] - 1], ''))
        else:
            if prev[0] + 1 == act[0] and prev[1] + 1 == act[1]:
                res.insert(0, (x[act[0] - 1], y[act[1] - 1]))
            else:
                res.insert(0, (x[prev[0]: act[0]], y[prev[1]:act[1]]))
        act = prev
    return D[lenX, lenY],res
    
def damerau_intermediate(x, y, threshold=None): #JAVI
    lenX, lenY = len(x), len(y)
    
    # Inicialización de los cuatro vectores columna
    vprev3 = np.zeros(lenY + 1, dtype=int)  # Almacena tres filas anteriores
    vprev2 = np.zeros(lenY + 1, dtype=int)  # Almacena dos filas anteriores
    vprev = np.zeros(lenY + 1, dtype=int)   # Almacena la fila anterior
    vcurrent = np.zeros(lenY + 1, dtype=int)  # Almacena la fila actual
    
    # Inicializar la primera fila de vcurrent para operaciones de inserción
    for j in range(1, lenY + 1):
        vcurrent[j] = j

    # Recorro cada carácter de x
    for i in range(1, lenX + 1):
        # Inicializar la nueva fila de vcurrent
        vnext = np.zeros(lenY + 1, dtype=int)
        vnext[0] = i
        
        for j in range(1, lenY + 1):
            cost = 0 if x[i - 1] == y[j - 1] else 1
            vnext[j] = min(
                vcurrent[j] + 1,         # Eliminación
                vnext[j - 1] + 1,        # Inserción
                vcurrent[j - 1] + cost   # Sustitución
            )
            
            # Transposición básica `ab ↔ ba` (costo 1)
            if i > 1 and j > 1 and x[i - 1] == y[j - 2] and x[i - 2] == y[j - 1]:
                vnext[j] = min(vnext[j], vprev[j - 2] + 1)
                
            # Transposición intermedia `acb ↔ ba` (costo 2)
            if i > 2 and j > 1 and x[i - 3] == y[j - 1] and x[i - 1] == y[j - 2]:
                vnext[j] = min(vnext[j], vprev2[j - 2] + 2)
                
            # Transposición intermedia `ab ↔ bca` (costo 2)
            if i > 1 and j > 2 and x[i - 1] == y[j - 3] and x[i - 2] == y[j - 1] and x[i - 3] == y[j - 2]:
                vnext[j] = min(vnext[j], vprev3[j - 3] + 2)
        
        if threshold is not None and all(val > threshold for val in vnext):
            return threshold + 1
        
        vprev3, vprev2, vprev, vcurrent = vprev2, vprev, vcurrent, vnext

    return vcurrent[lenY]

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

