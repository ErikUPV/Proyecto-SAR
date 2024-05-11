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
        ''' 
        Para cada termino
        'frec': Cuantas veces se ha visto el término en la indexacióm
        'nArt': Numero de art en los que aparece
        'terDocFrec': Has para cada articulo, cuantas veces se ha visto ese token en cada articulo
        '''         
        self.articles = {} # hash de articulos --> clave entero (artid), valor: la info necesaria para diferencia los artículos dentro de su fichero
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()

        # ======== Inicializar los diccionarios del índice ========
        for (field,_) in self.fields:
            self.index[field] = {}
            self.sindex[field] = {}
            self.ptindex[field] = []
            
        
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
                for filename in sorted(files):
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
            text = self.parse_article(line)
            
            # Tokens ya vistos en el artículo, para el pesado self.weight
            visitedTokens: list = [] 
            
            # Si ya se ha indexado este articulo
            if text['url'] in self.urls: continue
            
            # ======== Actializar valores del indice ========
            artId: int = len(self.articles)
            self.articles[artId] = (docId,lineInFile)
            
            # Añadir url del artículo a sus diccionario 
            self.urls.add(text["url"])
            self.index['url'][text["url"]] = artId
            
            # ======== Actualizar los indices ========
            for (field,ifIndex) in self.fields:
                if not self.multifield and field != 'all': continue
                if not ifIndex: continue
                
                tokens: list = self.tokenize(text[field])
                                                            
                for pos, token in enumerate(tokens):
                    # ======== Actualizar valores del indice ========
                    # Si no se ha visto el token aún se inicializa. Si se ha visto antes se actualizan sus valores
                    if token not in visitedTokens: 
                        if token not in self.weight:
                            # Si el token no tiene contadores añadirlos
                            self.weight[token] = {
                                'frec': 0,
                                'nArt': 0,  
                                'terDocFrec': {}                      
                            }          
                        '''En if'''
                        self.weight[token]['nArt'] += 1
                        self.weight[token]['terDocFrec'][artId] = 0
                        visitedTokens.append(token)
                    '''En if'''
                    
                    self.weight[token]['frec'] += 1
                    self.weight[token]['terDocFrec'][artId] += 1
                        
                    # ======== Indices ========
                    if token not in self.index[field]:
                        # Si el token no está en el indice añadirlo
                        self.index[field][token] = []
                        
                    # ======== Poscionales ========
                    if not self.positional:
                        # NORMAL 
                        if artId not in self.index[field][token]:
                            # Añadir el articulo en orden creciente
                            self.index[field][token].append(artId) 
                    else:
                        # POSICIONALES -> 
                        # cada termino tiene una lista con forma [ (artId,[ocrurrencias]), (artId,[ocrurrencias]),...]                       
                        if artId not in self.index[field][token]:
                            # Añadir el articulo en orden creciente con su lista de posicionales
                            self.index[field][token].append((artId,[pos]))
                        else:
                            # Añadir posición de la ocurrencia al índice
                            self.index[field][token][1].append(pos)
                '''END FOR TOKENS'''              
            '''END FOR FIELDS'''              
        '''END FOR LINES'''
        #if self.permuterm: self.make_permuterm()
        if self.stemming: self.make_stemming()
        if self.permuterm: self.make_permuterm()             



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
        
            
        for (field,ifIndex) in self.fields:
            if not ifIndex: continue
            
            for token in self.index[field].keys():
                stem: str = self.stemmer.stem(token)
                
                if stem not in self.sindex[field]:
                    self.sindex[field][stem] = []
                
                if token not in self.sindex[field][stem]:
                    self.sindex[field][stem].append(token)
         
    
    def make_permuterm(self):
        """

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE PERMUTERM


        """
        
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        print(self.ptindex.keys())
        for field in self.ptindex: 
            # if field == "url":
            #     self.ptindex[field].extend([token for token in self.index[field].keys()])
            #     self.ptindex[field] = list(set(self.ptindex[field]))
            #     continue
               
            for token in self.index[field].keys():
                self.ptindex[field].extend((f'{token[j:]}${token[:j]}', token) for j in range(len(token)+1))
            self.ptindex[field] = sorted(list(set(self.ptindex[field])))

    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Muestra estadisticas de los indices
        
        """
        
         
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        sep1 = "="*30; sep2 = "-"*30
        res = ""
        res+=f"{sep1}\n"
        res+=f"Number of indexed files {len(self.docs)}\n"
        res+=f"{sep2}\n"
        res+=f"Number of indexed articles {len(self.articles)}\n"
        res+=f"{sep2}\n"
        
        
        
        indices = ["tokens"]
        if(self.stemming): indices.append("stemming")
        if(self.permuterm): indices.append("permuterm")
        indice_dic = {}
        for indice in indices:
        
            res+=f"{indice.upper()}:\n"
            if indice == "tokens": indice_dic = self.index
            elif indice == "stemming": indice_dic = self.sindex
            elif indice == "permuterm": indice_dic = self.ptindex
            if self.multifield:
                
                for field in self.fields:
                    
                    res+=f"\t# of tokens in '{field[0]}': {len(indice_dic[field[0]])}\n"
            else: res+=f"\t# of tokens in 'all': {len(indice_dic['all'])}\n"
            res+=f"{sep2}\n"
        
       
        if self.positional:
            res+= "Positional queries are allowed\n"
        else: res+= "Positional queries are NOT allowed\n"
        res+=f"{sep1}"
        print(res)
       # print([token for token in self.ptindex['all'] if token[0].startswith("a$")])



        



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
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        '''def depurar(l):
            l = l.lower().split()
            parentesis = False
            multi = False
            c = 0
            s = 0
            aux = []
            res = []
            for i in l:
                if not multi:
                    if i[0] == '(':
                        c += 1
                        aux.append(i)
                        parentesis = True
                    elif i[-1] == ')':
                        c -= 1
                        aux.append(i)
                        res.append(' '.join(aux))
                        aux = []
                    elif c>0:
                        aux.append(i)
                if not parentesis:
                    if i[0] == "'":
                        s += 1
                        aux.append(i)
                        multi = True
                    elif i[-1] == "'":
                        s -= 1
                        aux.append(i)
                        res.append(' '.join(aux))
                        aux = []
                    elif s>0:
                        aux.append(i)
                if s == 0 and not (parentesis or multi):
                    multi = False
                    res.append(i)
                elif c == 0 and not (parentesis or multi):
                    parentesis = False
                    res.append(i)
            return res

        if query is None or len(query) == 0:
            return []
        queryO = query
        query = depurar(query)
        if query[0] == 'not':
            n = query[1]
            q = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                else n
            q = self.reverse_posting(self.get_posting(q,'all'))
            i = 2
        else:
            n = query[0]
            q = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                else n
            q = self.get_posting(q,'all')
            i = 1
        c = 0
        while i < len(query):
            if query[i] == 'and':
                if query[i + 1] == 'not':
                    n = query[i + 2]
                    if n[0] == '(':
                        aux = self.solve_query(n[i:len(n) - 1])
                    else:
                        aux = n
                    q = self.minus_posting(q,self.get_posting(aux,'all'))
                    i+=2
                else:
                    n = query[i + 1]
                    aux = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                        else n
                    q = self.and_posting(q,self.get_posting(aux,'all'))
                    i+=1
            elif query[i] == 'or':
                if query[i + 1] == 'not':
                    n = query[i + 2]
                    aux = self.solve_query(n[i:len(n) - 1]) if n[0] == '(' \
                        else n
                    aux = self.reverse_posting(self.get_posting(aux,'all'))
                    i += 2
                else:
                    n = query[i + 1]
                    aux = self.solve_query(n[1:len(n) - 1]) if n[0] == '(' \
                        else n
                    aux = self.get_posting(aux,'all')
                    i += 1
                q = self.or_posting(q, aux)
            else:
                n = query[i]
                q = self.solve_query(n[i:len(query[i]) - 1]) if n[0] == '(' \
                    else n
                q = self.get_posting(q,'all')
            i += 1

        def short(query,q):
            query = re.findall(r'("[^"]+"|\w+)', query.lower())
            query = [i for i in query if i not in ['and','or','not']]
            idf = [math.log(len(self.articles) / len(self.get_posting(j))) for j in query]
            for i in q:
                itf = [1 + math.log(self.weight[j]['terDocFrec'][i]) for j in query]'''
        query = re.findall(r"'[^']*'|\"[^\"]*\"|\w+|\(|\)", query.lower())
        op = []
        docs = []
        for i in query:
            if i in {'and', 'not', 'or', '(', ')'}:
                op.append(i)
            else:
                docs.append(self.get_posting(i,'all'))
        w = [1 for i in docs]
        j = 0
        i = 0
        temporal = []
        res = [[]]
        ini = True
        while i < len(op):
            if ini:
                if op[i] == 'not':
                    i += 1
                    if i < len(op) and op[i] == '(':
                        res.append([])
                        i += 1
                        temporal.append('not')
                    else:
                        res[-1] = self.reverse_posting(docs[j].copy())
                        j += 1
                        ini = False
                elif i < len(op) and op[i] == '(':
                    res.append([])
                    i += 1
                else:
                    res[-1] = docs[j].copy()
                    j+=1
                    ini = False
            elif op[i] == 'and':
                i += 1
                if i < len(op) and op[i] == 'not':
                    i += 1
                    if i < len(op) and op[i] == '(':
                        #res.append(docs[j])
                        res.append([])
                        i += 1
                        temporal.append('except')
                        ini = True
                    else:
                        res[-1] = self.minus_posting(res[-1], docs[j])
                        j += 1
                elif i < len(op) and op[i] == '(':
                    res.append([])
                    i += 1
                    temporal.append('and')
                    ini = True
                else:
                    res[-1] = self.and_posting(res[-1], docs[j])
                    j += 1
            elif op[i] == 'or':
                i += 1
                if i < len(op) and op[i] == 'not':
                    i += 1
                    if i < len(op) and op[i] == '(':
                        #res.append(docs[j])
                        res.append([])
                        i += 1
                        temporal.append('ornot')
                        ini = True
                    else:
                        res[-1] = self.or_posting(res[-1], self.reverse_posting(docs[j]))
                        j += 1
                elif i < len(op) and op[i] == '(':
                    res.append([])
                    i += 1
                    temporal.append('or')
                    ini = True
                else:
                    res[-1] = self.or_posting(res[-1], docs[j])
                    j += 1
            else:
                if op[i] == ')':
                    t = temporal.pop() if len(temporal) > 0 else ''
                    aux = res.pop()
                    if t == 'and':
                        res[-1] = self.and_posting(res[-1], aux)
                    elif t == 'or':
                        res[-1] = self.or_posting(res[-1], aux)
                    elif t == 'except':
                        res[-1] = self.minus_posting(res[-1], aux)
                    elif t == 'ornot':
                        res[-1] = self.or_posting(res[-1], self.reverse_posting(aux))
                    elif t == 'not':
                        res[-1] = self.reverse_posting(aux)
                    else:
                        res[-1] = aux
                    i += 1
        return res[0]


        # Short
        #q = short(queryO,q)
        #return q





    def get_posting(self, term:str, field:Optional[str]=None):
        """

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales 
            - self.get_permuterm: para la ampliacion de permuterms 
            - self.get_stemming: para la amplaicion de stemming 


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list
        
        NECESARIO PARA TODAS LAS VERSIONES

        """
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        if len(self.tokenize(term)) > 1:
            # Si hay más de una palabra en el termiod 
            return self.get_positionals(self.tokenize(term),field)
        elif '*' in term or '?' in term:
            # Sin contineen alguno de los comodines para la búsqueda permuterm (* o ?)
            return self.get_permuterm(term,field)
        elif self.use_stemming:
            # Si está activado el stemming
            return self.get_stemming(term,field)
        else: 
            if self.positional:
                # Si no hay ninguna opción activada para el término pero se ha contruido con posicionales
                # Cada token tiene una lista con forma [ (artId,[ocrurrencias]), (artId,[ocrurrencias]),...] 
                if term not in self.index[field]:
                    return []
                else:
                    return [artId for (artId,_) in self.index[field][term]]
            else:
                # Si no hay ninguna opción activada
                return self.index[field].get(term,[])


    def get_positionals(self, terms:str, field):
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
            devuelve las ocurrencias en una posting list de un token dentro un articulo,
            si NO aparece el articulo en la posting list devuelve None
            
            param:  "artId": id del articulo a buscar en posting
                    "posting": posting list sobre la que hacer la búsqueda                
                
            return: ocurrencias list or none
            '''
            for (id, ocurrencias) in posting:
                if id == artId: return ocurrencias
            return None
            
            
        res = []
        postings = []
        for termino in terms:
            if terms not in self.index[field][termino]:
                # si algún termino NO ha sido indexado no se busca
                return res
            else:
                # Todas las posting list de cada termino de la consulta
                postings.append(self.index[field][termino])

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
                if not ValidoArtId: break             
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
        res = []
        
        if stem not in self.sindex[field]:
            # si ese stem no se ha llegado a indexar
            return res
        
        # Puede haber más de un tocen asociado a un stem
        for token in self.sindex[field][stem]:
            # Insertar de manera ordenada (de menor a mayor) en la respuesta los DocIds 
            for docId in self.index[field][token]:
                if len(res) == 0:
                    # Primer elemento
                    res.append(docId)
                    continue
                if docId > res[len(res)-1]: 
                    # si va en la última posicion
                    res.insert(len(res),docId)
                    continue
                
                for i in range(len(res)):
                    # Inserción ordenada
                    if res[i] <  docId: continue
                    if res[i] == docId: break
                    if res[i] >  docId: res.insert(i,docId); break
        return res

            

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
        def binary_search(lista, perm):
            izq = 0
            der = len(lista) - 1
            while izq <= der:
                mitad = izq + (der - izq) // 2
                if lista[mitad][0] == perm:
                    return mitad
                elif lista[mitad][0] < perm:
                    izq = mitad + 1
                else:
                    der = mitad - 1
            return -1
        res = []
        pos = term.rfind('*') + term.rfind('?') +1  # Suponemos que solo hay o un asterisco o un interrogante, no los 2 a la vez
        permuterm = f'{term[pos+1:]}${term[:pos]}'
        
        #Buscamos una posición de la lista self.ptindex[field] donde aparece el permuterm
        permuterm_pos = binary_search(self.ptindex[field],permuterm)
        
        #Esta posición puede no ser la primera, de forma que navegamos hacia atrás hasta encontrar la primera
        encontrado_primero = False
        while not encontrado_primero:
            if permuterm_pos == -1:
                pass
            elif permuterm_pos == 0:
                encontrado_primero = True
            elif self.ptindex[field][permuterm_pos - 1][0] == permuterm:
                permuterm_pos -= 1
            elif self.ptindex[field][permuterm_pos -1][0] != permuterm_pos:
                encontrado_primero = True
        
        #Si hemos encontrado la primera posición, buscamos todos los tokens cuyo permuterm es el mismo
        #y concatenamos sus postings list.    
        if encontrado_primero:
             while permuterm_pos < len(self.ptindex[field]) and self.ptindex[field][permuterm_pos][0] == permuterm:
                token = self.ptindex[field][permuterm_pos][1]
                if self.index[field][token] not in res:
                    res += self.index[field][token]
                permuterm_pos += 1
        
        #Devolvemos la postings list ordenada
        return sorted(res)
        
        # for perm, token in self.ptindex[field].values():
        #     if permuterm in perm:
        #         res += self.index[field][token]
        # return res
        



    def reverse_posting(self, p:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.

        param:  "p": posting list

        return: posting list con todos los artid exceptos los contenidos en p
        """

        j = 0
        allP = list(self.articles.keys())
        l = []
        for i,n in enumerate(allP):
            if j >= len(p):
                break
            if i != p[j]:
                l.append(i)
            else:
                j+=1
        l+=allP[n:]
        # l = [i for i in allP if i not in p]

        return l





    def and_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos en p1 y p2
        """

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        i, j = 0, 0
        l = []
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                l.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                i += 1
            else:
                j += 1
        return l




    def or_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos de p1 o p2
        """

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        i, j = 0, 0
        l = []
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                l.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                l.append(p1[i])
                i += 1
            else:
                l.append(p2[j])
                j += 1
        l += p1[i:]
        l += p2[j:]
        return l


    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se incluye por si es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular

        return: posting list con los artid incluidos de p1 y no en p2
        """
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################
        return [i for i in p1 if i not in p2]





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
        def npalabras(nantes, ndespues, texto, pos):
            cotainf = pos
            cotasup = pos
            while nantes > 0 and cotainf > 0:
                if texto[cotainf] == '\n':
                    cotainf = cotainf-1
                    break
                if texto[cotainf] == " ":
                    nantes = nantes -1
                cotainf = cotainf -1
            while ndespues > 0 and cotasup < len(texto)-1:
                if texto[cotasup] == '\n':
                    break
                if texto[cotasup] == " ":
                    ndespues = ndespues -1
                cotasup = cotasup +1
            return (cotainf+1, cotasup)
        
        terminos = []
        for t in self.tokenize(query):
            if t != 'and' and t != 'or':
                terminos.append(t)

        q = self.solve_query(query)
        for i in range(len(q) if self.show_all else min(10,len(q))):
            doc = open(self.docs[self.articles[q[i]][0]], "r")
            doc = self.parse_article(doc.readlines()[self.articles[q[i]][1]])
            print(f"{i} ({q[i]}) {doc['title']}: {doc['url']}")
            for t in terminos:
                resnippet = re.compile(f"\W+{t}\W+")
                pos = resnippet.search(doc['all'], re.IGNORECASE)
                if pos:
                    pos = pos.span()
                else:
                    pos = -1
                if pos != -1:
                    (cotainf, cotasup) = npalabras(6,7,doc['all'],pos[0])
                    #print(doc['all'][pos[0]-5:pos[0]+15])
                    print(f"...{doc['all'][cotainf+1:cotasup-1]}...\n")


        print(f"Number of results: {len(q)}")
        return len(q)
        ################
        ## COMPLETAR  ##
        ################
