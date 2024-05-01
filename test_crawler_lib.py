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
if __name__ == "__main__":
    lista: list = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
    ]
    
    primLista: list = lista.pop(0)
    
    print(f'{primLista = }')
    print(f'{lista = }')
    
