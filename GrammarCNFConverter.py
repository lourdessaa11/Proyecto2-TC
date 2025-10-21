import re
from collections import defaultdict

# Expresión regular para detectar no terminales (por convención, mayúscula inicial)
_NONTERMINAL_RE = re.compile(r'^[A-Z][A-Za-z0-9_]*$')


def crear_gramatica_proyecto():
    """Crea la gramática del proyecto (la del documento)."""
    gramatica = {
        'S': ['NP VP'],
        'VP': ['VP PP', 'V NP', 'cooks', 'drinks', 'eats', 'cuts'],
        'PP': ['P NP'],
        'NP': ['Det N', 'he', 'she'],
        'V': ['cooks', 'drinks', 'eats', 'cuts'],
        'P': ['in', 'with'],
        'N': ['cat', 'dog', 'beer', 'cake', 'juice', 'meat', 'soup',
              'fork', 'knife', 'oven', 'spoon'],
        'Det': ['a', 'the']
    }
    return gramatica


class GrammarCNFConverter:
    def __init__(self, gramatica_dict, start_symbol='S'):
        """
        Inicializa el conversor con una gramática (diccionario) y símbolo inicial.

        Parametros:
            gramatica_dict: dict {NT: [produccion, ...]}
            start_symbol:   símbolo inicial de la gramática (string)
        """
        self.start_symbol = start_symbol
        self.gramatica_original = self._copiar_gramatica(gramatica_dict)
        self.gramatica = self._copiar_gramatica(gramatica_dict)
        self.nuevos_no_terminales = set()
        self.reglas_terminales = {}
        self.contador_nuevos_nt = 0

    def _copiar_gramatica(self, gramatica):
        """Hace una copia de la gramática para no modificar la original."""
        return {nt: prods[:] for nt, prods in gramatica.items()}

    def _es_no_terminal(self, simbolo):
        """Devuelve True si el símbolo luce como no terminal (Mayúscula inicial)."""
        return bool(_NONTERMINAL_RE.match(simbolo)) if simbolo else False

    def _es_terminal(self, simbolo):
        """
        Revisa si un símbolo es terminal o no terminal.
        Criterio: si NO cumple la regex de no terminal, lo consideramos terminal.
        """
        if simbolo is None or simbolo == '':
            return True
        return not self._es_no_terminal(simbolo)

    def verificar_cnf(self):
        """
        Revisa si la gramática ya está en Forma Normal de Chomsky.

        Regla CNF:
          - A -> a               (un solo terminal)
          - A -> B C             (dos no terminales)
        No se permiten epsilon (salvo Start -> ε) ni unitarias, ni mezclas.

        Retorna:
            bool: True si está en CNF, False si no.
        """
        for nt, producciones in self.gramatica.items():
            for prod in producciones:
                if prod == '':
                    # epsilon solo permitido si es el símbolo inicial
                    if nt != self.start_symbol:
                        return False
                    continue

                simbolos = prod.split()
                if len(simbolos) == 1:
                    # Debe ser un terminal
                    if not self._es_terminal(simbolos[0]):
                        return False
                elif len(simbolos) == 2:
                    # Deben ser NO terminales
                    if not (self._es_no_terminal(simbolos[0]) and self._es_no_terminal(simbolos[1])):
                        return False
                else:
                    return False
        return True

    def convertir_a_cnf(self):
        """
        Convierte la gramática completa a Forma Normal de Chomsky.

        Retorna:
            dict: La gramática convertida a CNF
        """
        if self.verificar_cnf():
            print("La gramática ya está en CNF, no necesita conversión")
            return self.gramatica

        print("Iniciando conversión a CNF...")

        # Paso 0: Normalizar epsilon explícita 'e' o 'ε' a '' (si viniera de archivo)
        self._normalizar_epsilon_literal()

        # Paso 1: Eliminar producciones epsilon (excepto Start -> ε si corresponde)
        self._eliminar_producciones_epsilon()

        # Paso 2: Quitar producciones unitarias (A -> B)
        self._eliminar_producciones_unitarias()

        # Paso 3: Quitar símbolos inútiles usando self.start_symbol
        self._eliminar_simbolos_inutiles()

        # Paso 4: Reemplazar terminales en RHS mixtos (A -> B a C ...) por NT intermedios
        self._reemplazar_terminales_en_mixtas()

        # Paso 5: Descomponer producciones largas a binarias
        self._descomponer_producciones_largas()

        return self.gramatica

    def _normalizar_epsilon_literal(self):
        """Convierte 'e' o 'ε' en cadenas vacías '' dentro de las producciones."""
        for nt, producciones in list(self.gramatica.items()):
            nuevas = []
            for prod in producciones:
                p = prod.strip()
                if p.lower() == 'ε' or p == 'e':
                    nuevas.append('')
                else:
                    nuevas.append(p)
            self.gramatica[nt] = nuevas

    def _anulables(self):
        """Calcula el conjunto de no terminales que pueden generar ε."""
        anulables = set()
        cambio = True
        while cambio:
            cambio = False
            for nt, prods in self.gramatica.items():
                if nt in anulables:
                    continue
                for prod in prods:
                    if prod == '':
                        anulables.add(nt)
                        cambio = True
                        break
                    simbolos = prod.split()
                    if simbolos and all(self._es_no_terminal(s) and s in anulables for s in simbolos):
                        anulables.add(nt)
                        cambio = True
                        break
        return anulables

    def _eliminar_producciones_epsilon(self):
        """
        Elimina epsilon-producciones, conservando Start -> ε si el lenguaje lo tenía.
        """
        anulables = self._anulables()
        conservar_start_epsilon = (self.start_symbol in anulables)

        nuevas = defaultdict(set)
        for A, prods in self.gramatica.items():
            for prod in prods:
                if prod == '':
                    # saltamos por ahora, lo reponemos al final si aplica
                    continue
                simbolos = prod.split()
                # generar todas las variantes eliminando opcionalmente anulables
                indices = [i for i, s in enumerate(simbolos) if self._es_no_terminal(s) and s in anulables]
                # subconjuntos de índices a eliminar
                from itertools import chain, combinations
                def powerset(iterable):
                    s = list(iterable)
                    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
                for subset in powerset(indices):
                    if len(subset) == len(simbolos):
                        # No queremos producir ε aquí; lo gestionamos al final
                        continue
                    nueva = [s for i, s in enumerate(simbolos) if i not in subset]
                    nuevas[A].add(' '.join(nueva) if nueva else '')

        # Reponer Start -> ε si corresponde
        self.gramatica = {A: [p for p in ps if p != ''] for A, ps in nuevas.items()}
        if conservar_start_epsilon:
            self.gramatica.setdefault(self.start_symbol, [])
            if '' not in self.gramatica[self.start_symbol]:
                self.gramatica[self.start_symbol].append('')

    def _eliminar_producciones_unitarias(self):
        """Elimina reglas A -> B (unitarias) expandiéndolas."""
        unitarias = defaultdict(set)
        # Inicialmente, A -> B si hay producción unitaria
        for A, prods in self.gramatica.items():
            for prod in prods:
                partes = prod.split()
                if len(partes) == 1 and self._es_no_terminal(partes[0]):
                    unitarias[A].add(partes[0])

        # Clausura transitiva
        cambio = True
        while cambio:
            cambio = False
            for A in list(unitarias.keys()):
                nuevos = set()
                for B in unitarias[A]:
                    nuevos |= unitarias.get(B, set())
                nuevos -= unitarias[A]
                if nuevos:
                    unitarias[A] |= nuevos
                    cambio = True

        # Expandir reemplazando A -> B por A -> (todas de B menos unitarias)
        nueva = defaultdict(set)
        for A, prods in self.gramatica.items():
            for prod in prods:
                partes = prod.split()
                if len(partes) == 1 and self._es_no_terminal(partes[0]):
                    # omitir, se expandirá por B
                    continue
                nueva[A].add(prod)

            for B in unitarias.get(A, set()):
                for prodB in self.gramatica.get(B, []):
                    partesB = prodB.split()
                    if len(partesB) == 1 and self._es_no_terminal(partesB[0]):
                        continue
                    nueva[A].add(prodB)

        self.gramatica = {A: sorted(list(ps)) for A, ps in nueva.items()}

    def _eliminar_simbolos_inutiles(self):
        """
        Elimina símbolos no generativos y no alcanzables desde self.start_symbol.
        """
        # Generativos
        generativos = set()
        cambio = True
        while cambio:
            cambio = False
            for nt, producciones in self.gramatica.items():
                if nt in generativos:
                    continue
                for prod in producciones:
                    simbolos = prod.split()
                    if all(self._es_terminal(s) or s in generativos for s in simbolos):
                        generativos.add(nt)
                        cambio = True
                        break

        gram_temp = {}
        for nt, producciones in self.gramatica.items():
            if nt in generativos:
                prods_validas = []
                for prod in producciones:
                    simbolos = prod.split()
                    if all(self._es_terminal(s) or s in generativos for s in simbolos):
                        prods_validas.append(prod)
                if prods_validas:
                    gram_temp[nt] = prods_validas
        self.gramatica = gram_temp

        # Alcanzables desde start_symbol
        alcanzables = {self.start_symbol}
        cambio = True
        while cambio:
            cambio = False
            for nt in list(alcanzables):
                for prod in self.gramatica.get(nt, []):
                    for s in prod.split():
                        if self._es_no_terminal(s) and s not in alcanzables:
                            alcanzables.add(s)
                            cambio = True

        self.gramatica = {
            nt: [p for p in prods if all((not self._es_no_terminal(s)) or s in alcanzables for s in p.split())]
            for nt, prods in self.gramatica.items() if nt in alcanzables
        }

        # Limpiar producciones vacías que no sean del start (si quedó)
        for nt in list(self.gramatica.keys()):
            if nt != self.start_symbol:
                self.gramatica[nt] = [p for p in self.gramatica[nt] if p != '']
        if self.start_symbol in self.gramatica and not self.gramatica[self.start_symbol]:
            del self.gramatica[self.start_symbol]

    def _nombre_nt_para_terminal(self, t):
        """
        Construye un nombre de no terminal para levantar un terminal en RHS mixto.
        Mantiene nombres simples para letras, y usa nombres legibles para símbolos.
        """
        if t.isalpha():
            return t.upper()
        mapa = {
            '+': 'PLUS', '*': 'TIMES', '(': 'LPAREN', ')': 'RPAREN',
            '-': 'MINUS', '/': 'DIV', '=': 'EQ', '.': 'DOT', ',': 'COMMA'
        }
        return mapa.get(t, 'T_' + '_'.join(str(ord(c)) for c in t))

    def _reemplazar_terminales_en_mixtas(self):
        """
        En RHS con mezcla de terminales y no terminales,
        levanta cada terminal a un no terminal especial: T -> t
        """
        mapeo_terminal_a_nt = {}
        nueva = defaultdict(list)

        for nt, producciones in self.gramatica.items():
            for prod in producciones:
                if prod == '':
                    nueva[nt].append(prod)
                    continue

                simbolos = prod.split()
                if len(simbolos) >= 2:
                    sustituidos = []
                    cambio = False
                    for s in simbolos:
                        if self._es_terminal(s):
                            cambio = True
                            if s not in mapeo_terminal_a_nt:
                                cand = self._nombre_nt_para_terminal(s)
                                # evitar choque con existentes
                                base = cand
                                idx = 1
                                while cand in self.gramatica or cand in nueva or cand in mapeo_terminal_a_nt.values():
                                    cand = f"{base}_{idx}"
                                    idx += 1
                                mapeo_terminal_a_nt[s] = cand
                            sustituidos.append(mapeo_terminal_a_nt[s])
                        else:
                            sustituidos.append(s)
                    if cambio:
                        nueva[nt].append(' '.join(sustituidos))
                    else:
                        nueva[nt].append(prod)
                else:
                    # A -> a  o  A -> B   (se deja tal cual)
                    nueva[nt].append(prod)

        # Agregar reglas T -> t
        for t, T in mapeo_terminal_a_nt.items():
            nueva[T].append(t)
            self.nuevos_no_terminales.add(T)

        self.reglas_terminales = mapeo_terminal_a_nt
        self.gramatica = {A: sorted(list(dict.fromkeys(ps))) for A, ps in nueva.items()}

    def _descomponer_producciones_largas(self):
        """
        Convierte producciones con más de 2 símbolos en una cadena de binarias.
        """
        gram_nueva = defaultdict(list)
        for nt, producciones in self.gramatica.items():
            for prod in producciones:
                if prod == '':
                    gram_nueva[nt].append(prod)
                    continue
                simbolos = prod.split()
                if len(simbolos) <= 2:
                    gram_nueva[nt].append(prod)
                    continue

                # Descomponer A -> X1 X2 X3 ... Xn
                nt_actual = nt
                for i in range(len(simbolos) - 2):
                    X1 = simbolos[i]
                    Y = self._crear_nuevo_nt()
                    gram_nueva[nt_actual].append(f"{X1} {Y}")
                    nt_actual = Y
                gram_nueva[nt_actual].append(f"{simbolos[-2]} {simbolos[-1]}")

        self.gramatica = {A: sorted(list(dict.fromkeys(ps))) for A, ps in gram_nueva.items()}

    def _crear_nuevo_nt(self):
        """Crea un nuevo no terminal con nombre único."""
        self.contador_nuevos_nt += 1
        nombre = f"X{self.contador_nuevos_nt}"
        self.nuevos_no_terminales.add(nombre)
        return nombre

    def imprimir_gramatica(self, gramatica=None):
        """Imprime la gramática (por NT en orden alfabético)."""
        g = self.gramatica if gramatica is None else gramatica
        print("\nGramática:")
        for nt in sorted(g.keys()):
            rhs = " | ".join(g[nt])
            print(f"{nt} -> {rhs}")

    def obtener_reporte(self):
        """Devuelve un pequeño resumen de la conversión."""
        return {
            'reglas_originales': sum(len(v) for v in self.gramatica_original.values()),
            'reglas_cnf': sum(len(v) for v in self.gramatica.values()),
            'no_terminales_nuevos': len(self.nuevos_no_terminales),
            'mapeo_terminales': dict(self.reglas_terminales)
        }

    def cargar_gramatica_desde_txt(ruta):
        """
        Lee una gramática desde un archivo .txt con líneas del tipo:
            A -> B C | a | e
        - La primera LHS encontrada se toma como símbolo inicial.
        - 'e' o 'ε' se interpretan como epsilon (cadena vacía).
        - Se permite usar terminales no alfabéticos (+, *, (, ), etc.) sin comillas.
        """
        gram = {}
        start = None
        with open(ruta, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#') or '->' not in linea:
                    continue
                lhs, rhs = [x.strip() for x in linea.split('->', 1)]
                if start is None:
                    start = lhs
                alternativas = [a.strip() for a in rhs.split('|')]
                for alt in alternativas:
                    if alt == '' or alt.lower() == 'ε' or alt == 'e':
                        gram.setdefault(lhs, []).append('')
                    else:
                        gram.setdefault(lhs, []).append(alt)
        return gram, (start or 'S')
