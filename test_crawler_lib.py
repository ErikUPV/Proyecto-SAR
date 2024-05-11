'''from SAR_Crawler_lib import SAR_Wiki_Crawler
import lxml
import json'''
import time
import random

'''if __name__ == "__main__":
    crawler = SAR_Wiki_Crawler()
    url_ini = "https://es.wikipedia.org/wiki/Videojuego"
    (text, urls) = crawler.get_wikipedia_entry_content(url_ini)
    resultado = crawler.parse_wikipedia_textual_content(text, url_ini)
    with open("hola.json", mode="+w", encoding="utf-8") as fl:
        json.dump(resultado, fp=fl)
    # for section in resultado["sections"]:
    #     print(section)'''
'''if __name__ == "__main__":
    MAX = 50_000
    
    t0 = time.time()
    
    for _ in range(MAX):
        test: str = []
        for _ in range(1000):
            docId = random.randint(1, 1000)
            for i in range(len(test)):
                if test[i] <  docId: continue
                if test[i] == docId: break
                if test[i] >  docId: test.insert(i+1,docId)
            
    t1 = time.time()
    
    for _ in range(MAX):
        test: set = set()   
        for _ in range(1000):
            docId = random.randint(1, MAX)
            test.add(docId)
        test: list = sorted(test)
    
    t2 = time.time()
    
    print(f'Tiempo 1: {(t1-t0)/MAX:.8f}')
    print(f'Tiempo 2: {(t2-t1)/MAX:.8f}')'''
'''if __name__ == "__main__":
    lista = [-1,-12,1,1,1,1,-5,0,1,5,10,20,30,50,124,2,-2,-21]
    res = []
    print(f'{res = }')
    for docId in lista:
        if len(res) == 0:
            res.append(docId)
            continue
        if docId > res[len(res)-1]: 
            # si va en la última posicion
            res.insert(len(res),docId)
            continue
        
        for i in range(len(res)):
            if res[i] <  docId: continue
            if res[i] == docId: break
            if res[i] >  docId: res.insert(i,docId); break
    print(f'{res = }')'''

def insertOrdenado(lista: list, element: any) -> None:
    """
    Insetar de manera ordenada un elemento en una lista
    
    :param: lista: lista sobre la que inserar
            perm: elemento a insertar
    :result: None
    """
    izq = 0
    der = len(lista) - 1
    while izq <= der:
        mitad = izq + (der - izq) // 2
        if lista[mitad] == element:
            # Si ya está el elemento
            return
        elif lista[mitad] < element:
            izq = mitad + 1
        else:
            der = mitad - 1
            
    lista.insert(izq,element)
if __name__ == "__main__":
    lista: list = [1,2,5,6,7,9,10]
    insertOrdenado(lista, 3)
    print(f'{lista = }')
    insertOrdenado(lista, 3)
    print(f'{lista = }')
    insertOrdenado(lista, 8)
    print(f'{lista = }')
    insertOrdenado(lista, 11)
    print(f'{lista = }')
    insertOrdenado(lista, 30)
    print(f'{lista = }')
    insertOrdenado(lista, -3)
    print(f'{lista = }')
    
    
    