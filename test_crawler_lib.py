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
if __name__ == "__main__":
    diccionario: dict = {
        1: (2,[2,23,45]),
        2: (2,[2,23,45]),
        5: 2
    }
    clave, aux = diccionario.popitem()
    print(f'{clave = }, {aux = }')
    print(isinstance(aux, tuple))
    