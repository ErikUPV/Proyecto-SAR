import json
from nltk.stem.snowball import SnowballStemmer
import os
import re
import sys
import math
from pathlib import Path
from typing import Optional, List, Union, Dict
import pickle

class SAR_Indexer:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de artículos de Wikipedia
        
        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [
        ("all", True), ("title", True), ("summary", True), ("section-name", True), ('url', False),
    ]
    def_field = 'all'
    PAR_MARK = '%'
    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10

    all_atribs = ['urls', 'index', 'sindex', 'ptindex', 'docs', 'weight', 'articles',
                  'tokenizer', 'stemmer', 'show_all', 'use_stemming']

    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas 

        """
        self.urls = set() # hash para las urls procesadas,
        self.index = {} # hash para el indice invertido de terminos --> clave: termino, valor: posting list
        self.sindex = {} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        self.ptindex = {} # hash para el indice permuterm.
        self.docs = {} # diccionario de terminos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados.
        self.articles = {} # hash de articulos --> clave entero (artid), valor: la info necesaria para diferencia los artículos dentro de su fichero
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################


    def set_showall(self, v:bool):
        """

        Cambia el modo de mostrar los resultados.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v:bool):
        """

        Cambia el modo de mostrar snippet.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v



    #############################################
    ###                                       ###
    ###      CARGA Y GUARDADO DEL INDICE      ###
    ###                                       ###
    #############################################


    def save_info(self, filename:str):
        """
        Guarda la información del índice en un fichero en formato binario
        
        """
        info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'wb') as fh:
            pickle.dump(info, fh)

    def load_info(self, filename:str):
        """
        Carga la información del índice desde un fichero en formato binario
        
        """
        #info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'rb') as fh:
            info = pickle.load(fh)
        atrs = info[0]
        for name, val in zip(atrs, info[1:]):
            setattr(self, name, val)

    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################

    def already_in_index(self, article:Dict) -> bool:
        """

        Args:
            article (Dict): diccionario con la información de un artículo

        Returns:
            bool: True si el artículo ya está indexado, False en caso contrario
        """
        return article['url'] in self.urls


    def index_dir(self, root:str, **args):
        """
        
        Recorre recursivamente el directorio o fichero "root" 
        NECESARIO PARA TODAS LAS VERSIONES
        
        Recorre recursivamente el directorio "root"  y indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """
        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        file_or_dir = Path(root)
        
        if file_or_dir.is_file():
            # is a file
            self.index_file(root)
        elif file_or_dir.is_dir():
            # is a directory
            for d, _, files in os.walk(root):
                for filename in files:
                    if filename.endswith('.json'):
                        fullname = os.path.join(d, filename)
                        self.index_file(fullname)
        else:
            print(f"ERROR:{root} is not a file nor directory!", file=sys.stderr)
            sys.exit(-1)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################
        
        
    def parse_article(self, raw_line:str) -> Dict[str, str]:
        """
        Crea un diccionario a partir de una linea que representa un artículo del crawler

        Args:
            raw_line: una linea del fichero generado por el crawler

        Returns:
            Dict[str, str]: claves: 'url', 'title', 'summary', 'all', 'section-name'
        """
        
        article = json.loads(raw_line)
        sec_names = []
        txt_secs = ''
        for sec in article['sections']:
            txt_secs += sec['name'] + '\n' + sec['text'] + '\n'
            txt_secs += '\n'.join(subsec['name'] + '\n' + subsec['text'] + '\n' for subsec in sec['subsections']) + '\n\n'
            sec_names.append(sec['name'])
            sec_names.extend(subsec['name'] for subsec in sec['subsections'])
        article.pop('sections') # no la necesitamos 
        article['all'] = article['title'] + '\n\n' + article['summary'] + '\n\n' + txt_secs
        article['section-name'] = '\n'.join(sec_names)

        return article
                
    
    def index_file(self, filename:str):
        """
        Indexa el contenido de un fichero.
        
        input: "filename" es el nombre de un fichero generado por el Crawler cada línea es un objeto json
            con la información de un artículo de la Wikipedia

        NECESARIO PARA TODAS LAS VERSIONES

        dependiendo del valor de self.multifield y self.positional se debe ampliar el indexado
        """
        # En la version basica solo se debe indexar el contenido "article"
        #################
        ### COMPLETAR ###
        #################
        
        # ======== Actializar valores del indice ========
        docId: int = len(self.docs) 
        self.docs[docId] = os.path.abspath(filename)
        
        for lineInFile, line in enumerate(open(filename)):
            # Dict[str, str]: claves: 'url', 'title', 'summary', 'all', 'section-name'
            text: str = self.parse_article(line)
            tokens: list = self.tokenize(text['all'])
            
            # ======== Actializar valores del indice ========
            artId: int = len(self.articles)
            self.articles[artId] = (docId,lineInFile)
            self.urls.add(text["url"])
                
            
            for i, token in enumerate(tokens):
                # ======== Actializar valores del indice ========
                if token not in self.weight:
                    # Si el token no tiene contador añadirlo
                    self.index[token] = 1
                else:
                    self.index['all'][token] += 1
                    
                # ======== Actializar el indice ========
                if token not in self.index:
                    # Si el token no está en el indice añadirlo
                    self.index[token] = []
                    
                # Poscionales 
                if not self.positional:
                    # NORMAL 
                    if artId not in self.index[token]:
                        # Añadir el articulo en orden creciente
                        self.index[token].append(artId) 
                else:
                    # POSICIONALES -> cada termino tiene una lista con forma [ (artId,[ocrurrencias]), (artId,[ocrurrencias]),...]                       
                    if artId not in self.index[token]:
                        # Añadir el articulo en orden creciente con su lista de posicionales
                        self.index[token].append((artId,[i]))
                    else:
                        # Añadir posición de la ocurrencia al índice
                        self.index[token][1].append(i)
                    



    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def tokenize(self, text:str):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()


    def make_stemming(self):
        """

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE STEMMING.

        "self.stemmer.stem(token) devuelve el stem del token"

        """
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        
        # recuperar los tokens y sacarles sus steams.
        for token in self.index.keys():
            stem: str = self.stemmer.stem(token)
            
            if stem not in self.sindex:
                self.sindex[stem] = []
            
            if token not in self.sindex[stem]:
                self.sindex[stem].append(token)
         
    
    def make_permuterm(self):
        """

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE PERMUTERM


        """
        pass
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################




    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Muestra estadisticas de los indices
        
        """
        
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        with open("stats.json", mode='w+') as fl:
            json.dump(self.index, fl)
        #print(self.index)

        



    #################################
    ###                           ###
    ###   PARTE 2: RECUPERACION   ###
    ###                           ###
    #################################

    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query:str, prev:Dict={}):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """

        if query is None or len(query) == 0:
            return []
        '''
        query = query.split()
        pila = [[]]
        i = 0
        c = 0
        while i < len(query):
            if query[i] != 'AND' or query[i] != 'OR':
                i += 1
                print(aux)
                pila[-1] = self.and_posting(pila[-1], aux)
            elif query[i] == 'OR':
                i += 1
                if query[i] == 'NOT':
                    i += 1
                    aux = self.reverse_posting(self.get_posting(query[i]))
                else:
                    aux = self.get_posting(query[i])
                print(aux)
                pila[-1] = self.or_posting(pila[-1], aux)
            elif query[i] == 'NOT':
                i += 1
                pila[-1] = self.reverse_posting(query[i])
            else:
                pila[-1] = self.get_posting(query[i])
            i += 1
        return pila[0]'''
        query = self.depurar(query)
        if query[0] == 'NOT':
            n = query[1]
            q = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                else n
            q = self.reverse_posting(self.get_posting(q))
            i = 2
        else:
            n = query[0]
            q = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                else n
            q = self.get_posting(q)
            i = 1
        c = 0
        while i < len(query):
            if query[i] == 'AND' or query[i] == 'OR':
                if query[i + 1] == 'NOT':
                    c = 1
                    n = query[i + 1 + c]
                    aux = self.solve_query(n[i:len(n) - 1]) if n[0] == '(' \
                        else n
                    aux = self.reverse_posting(self.get_posting(aux))
                else:
                    n = query[i + 1]
                    aux = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                        else n
                    aux = self.get_posting(aux)

                if query[i] == 'AND':
                    i += 1
                    q = self.and_posting(q, aux)
                elif query[i] == 'OR':
                    i += 1
                    q = self.or_posting(q, aux)
                i += c
                c = 0
            else:
                if query[i] == 'NOT':
                    n = query[i + 1]
                    q = self.solve_query(n[i:len(n) - 1]) if n[0] == '(' \
                        else n
                    q = self.reverse_posting(self.get_posting(q))
                    i += 1
                else:
                    n = query[i]
                    q = self.solve_query(n[i:len(query[i]) - 1]) if n[0] == '(' \
                        else n
                    q = self.get_posting(q)
            i += 1
        return q

        def depurar(l):
            l = l.split()
            c = 0
            aux = []
            res = []
            for i in l:
                if i[0] == '(':
                    c += 1
                    aux.append(i)
                elif i[-1] == ')':
                    c -= 1
                    aux.append(i)
                    res.append(' '.join(aux))
                    aux = []
                elif c == 0:
                    res.append(i)
                else:
                    aux.append(i)
            return res
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################




    def get_posting(self, term:str, field:Optional[str]=None):
        """

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales (None)
            - self.get_permuterm: para la ampliacion de permuterms ('p')
            - self.get_stemming: para la amplaicion de stemming ('s')


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list
        
        NECESARIO PARA TODAS LAS VERSIONES

        """

        if field == None:
            l = self.get_positionals(term)
        elif field=='s':
            l = self.get_stemming(term)
        elif field=='p':
            l = self.get_permuterm(term)
        return l
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        pass



    def get_positionals(self, terms:str, index):
        """

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################
        def getOcurrencias(artId: int, posting: list) -> Optional[list]: 
            '''
            devuelve las ocurrencias de un articulo entre una posting list de un token,
            si NO aparece el articulo en la posting list devuelve None
            
            param:  "artId": id del articulo a buscar en posting
                    "posting": posting list sobre la que hacer la búsqueda                
                
            return: ocurrencias list or none
            '''
            for (id, ocurrencias) in posting:
                if id == artId: return ocurrencias
            return None
            
            
        res = []
        terminos = self.tokenize(terms)
        # Todas las posting list de cada termino de la consulta
        postings = [self.index[posting] for posting in terminos]

        # Iterar sobre todos los articulos que estén en la primera postingList
        # si ya no aparecen en ella no serán devueltos en la consulta
        # 
        # Cada token tiene una lista con forma [ (artId,[ocrurrencias]), (artId,[ocrurrencias]),...] 
        for (artId,ocurrenciasArtId) in postings.pop(0): # Primera posting list
            ValidoArtId: bool = True
            
            # mirar las ocurrencias en las listas asociadas a los siguientes términos
            for posRelativa, posting in enumerate(postings):
                econtradoPos: bool = False
                
                # Recuperar ocurrencias del siguiente token del artIds
                ocurrenciasAux = getOcurrencias(artId,posting)
                
                # Si el articulo NO aparece en la posting list del siguiente token fuera
                if ocurrenciasAux is None: 
                    ValidoArtId = False
                    break
                
                # Ver si en las posición que tendría que tener el siguiene token en el artículo está
                for pos in ocurrenciasArtId:
                    if (pos + posRelativa + 1) in ocurrenciasAux:
                        econtradoPos = True
                        break
                '''End for mirar posiciones de cada artId'''
                
                ValidoArtId = econtradoPos
                if not ValidoArtId : break             
            '''End for mirar otras postings'''
            
            if ValidoArtId: 
                res.append(artId)
        '''End for mirar todos artId''' 
        return res # Ya está ordenado de menor a mayor

    def get_stemming(self, term:str, field: Optional[str]=None):
        """

        Devuelve la posting list asociada al stem de un termino.
        NECESARIO PARA LA AMPLIACION DE STEMMING

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        
        stem = self.stemmer.stem(term)
        '''res = []'''
        res = set()
        
        # Puede haber más de un tocken asociado a un stem
        for token in self.sindex[stem]:
            # Insertar de manera ordenada (de menor a mayor) en la respuesta los DocIds 
            for docId in self.index[token]:
                '''for i in range(len(res)):
                    if res[i] <  docId: continue
                    if res[i] == docId: break
                    if res[i] >  docId: res.insert(i+1,docId)'''
                res.add(docId)
    
        '''return res'''
        return sorted(res)
            

    def get_permuterm(self, term:str, field:Optional[str]=None):
        """

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################
        pass



    def reverse_posting(self, p:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.

        param:  "p": posting list

        return: posting list con todos los artid exceptos los contenidos en p
        """

        j = 0
        allP = self.articles.keys()
        l = []
        for i in allP:
            if i != p[j]:
                l.append(i)
        # l = [i for i in allP if i not in p]

        return l





    def and_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos en p1 y p2
        """

        i, j = 0, 0
        l = []
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                i+=1
                j+=1
                l.append(p1[i])
            if p1[i] < p2[j]:
                i+=1
            else:
                j+=1
        l += p1[i:]
        l += p2[j:]
        return l

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################



    def or_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos de p1 o p2
        """
        i, j = 0, 0
        l = []
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                i += 1
                j += 1
                l.append(p1[i])
            if p1[i] < p2[j]:
                i += 1
                l.append(p1[j])
            else:
                j += 1
                l.append(p2[i])
        l += p1[i:]
        l += p2[j:]
        return l
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################


    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se incluye por si es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos de p1 y no en p2
        """
        return [i for i in p1 if i not in p2]
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################





    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################

    def solve_and_count(self, ql:List[str], verbose:bool=True) -> List:
        results = []
        for query in ql:
            if len(query) > 0 and query[0] != '#':
                r = self.solve_query(query)
                results.append(len(r))
                if verbose:
                    print(f'{query}\t{len(r)}')
            else:
                results.append(0)
                if verbose:
                    print(query)
        return results


    def solve_and_test(self, ql:List[str]) -> bool:
        errors = False
        for line in ql:
            if len(line) > 0 and line[0] != '#':
                query, ref = line.split('\t')
                reference = int(ref)
                result = len(self.solve_query(query))
                if reference == result:
                    print(f'{query}\t{result}')
                else:
                    print(f'>>>>{query}\t{reference} != {result}<<<<')
                    errors = True                    
            else:
                print(query)
        return not errors


    def solve_and_show(self, query:str):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados 

        param:  "query": query que se debe resolver.

        return: el numero de artículo recuperadas, para la opcion -T
        """
        return len(self.solve_query(query))
        ################
        ## COMPLETAR  ##
        ################







        

