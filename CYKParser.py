import time

class CYKParser:
    def __init__(self, gramatica_cnf, start_symbol='S'):
        """
        Inicializa el parser CYK con una gramática en CNF.

        Parametros:
            gramatica_cnf: Diccionario con la gramática en Forma Normal de Chomsky
            start_symbol:  Símbolo inicial a verificar en la celda (0, n-1)
        """
        self.gramatica = gramatica_cnf
        self.start_symbol = start_symbol
        self.tabla = None
        self.backpointers = None

    def _es_terminal(self, simbolo):
        """Verifica si un símbolo es terminal: criterio contrario a mayúscula inicial."""
        return not (simbolo and simbolo[0].isupper())

    def analizar(self, frase):
        """
        Aplica el algoritmo CYK a la frase (lista de tokens separados por espacios).

        Parametros:
            frase: string con tokens separados por espacios (ej. 'id + id * id')

        Retorna:
            (bool, float, tabla)
        """
        palabras = frase.split()  # importante: no forzar lower() para respetar símbolos
        n = len(palabras)

        if n == 0:
            # CYK clásico no trabaja con cadena vacía; se acepta solo si Start -> ε
            es_vacia = any(prod == '' for prod in self.gramatica.get(self.start_symbol, []))
            return es_vacia, 0.0, None

        tiempo_inicio = time.time()

        # Tabla triangular superior: tabla[i][j] = set de NT que generan palabras[i..j]
        self.tabla = [[set() for _ in range(n)] for _ in range(n)]
        self.backpointers = [[{} for _ in range(n)] for _ in range(n)]

        # Inicializar la diagonal con A -> a
        for i in range(n):
            w = palabras[i]
            for nt, producciones in self.gramatica.items():
                for prod in producciones:
                    partes = prod.split()
                    if len(partes) == 1 and partes[0] == w:
                        self.tabla[i][i].add(nt)
                        # Backpointer hoja terminal
                        self.backpointers[i][i].setdefault(nt, []).append((w, None, None))

        # Rellenar la tabla
        for longitud in range(2, n + 1):        # tamaño del segmento
            for i in range(n - longitud + 1):   # inicio del segmento
                j = i + longitud - 1            # fin del segmento
                for k in range(i, j):           # partición
                    # Revisar reglas binarias A -> B C
                    for nt, producciones in self.gramatica.items():
                        for prod in producciones:
                            partes = prod.split()
                            if len(partes) == 2:
                                B, C = partes
                                if B in self.tabla[i][k] and C in self.tabla[k + 1][j]:
                                    self.tabla[i][j].add(nt)
                                    self.backpointers[i][j].setdefault(nt, []).append((B, C, k))

        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio

        es_valida = self.start_symbol in self.tabla[0][n - 1]
        return es_valida, tiempo_total, self.tabla

    # ------------------- Utilidades de visualización -------------------

    def mostrar_tabla(self, frase):
        """
        Muestra la tabla CYK de forma legible.

        Parametros:
            frase: Frase analizada
        """
        if self.tabla is None:
            print("No hay tabla para mostrar")
            return

        palabras = frase.split()
        n = len(palabras)

        print("\n" + "=" * 50)
        print("TABLA CYK")
        print("=" * 50)

        # Encabezado
        encabezado = " " * 12
        for j in range(n):
            encabezado += f"{palabras[j]:>10}"
        print(encabezado)
        print("-" * (12 + 10 * n))

        # Filas
        for i in range(n):
            fila = f"i={i:2} | j={i:2} | "
            for j in range(n):
                if j < i:
                    fila += f"{'':>10}"
                else:
                    celda = "{" + ",".join(sorted(self.tabla[i][j])) + "}"
                    fila += f"{celda:>10}"
            print(fila)

    # Opcional: reconstrucción de un árbol simple (puedes integrar si lo deseas)
    def reconstruir_arbol(self, frase):
        """
        Reconstruye un árbol (si existe) usando backpointers. Devuelve None si no hay.
        """
        if self.tabla is None or not frase:
            return None
        palabras = frase.split()
        n = len(palabras)
        if self.start_symbol not in self.tabla[0][n - 1]:
            return None

        def build(i, j, A):
            # Hoja
            if i == j:
                # Buscar producción terminal A -> w
                for prod in self.backpointers[i][j].get(A, []):
                    w, B, C = prod
                    if B is None and C is None:
                        return (A, palabras[i])
            # Interno
            for (B, C, k) in self.backpointers[i][j].get(A, []):
                left = build(i, k, B)
                right = build(k + 1, j, C)
                if left and right:
                    return (A, left, right)
            return None

        return build(0, n - 1, self.start_symbol)

    def imprimir_arbol(self, nodo, nivel=0):
        """Imprime un árbol binario de forma simple."""
        if nodo is None:
            return
        if isinstance(nodo, tuple):
            etiqueta = nodo[0]
            print("  " * nivel + str(etiqueta))
            for hijo in nodo[1:]:
                if isinstance(hijo, tuple):
                    self.imprimir_arbol(hijo, nivel + 1)
                else:
                    print("  " * (nivel + 1) + str(hijo))
        else:
            print("  " * nivel + str(nodo))
