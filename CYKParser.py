import time

class CYKParser:
    def __init__(self, gramatica_cnf):
        """
        Inicializa el parser CYK con una gramática en CNF.

        Parametros:
            gramatica_cnf: Diccionario con la gramática en Forma Normal de Chomsky
        """
        self.gramatica = gramatica_cnf
        self.tabla = None
        self.backpointers = None

    def analizar(self, frase):
        """
        Ejecuta el algoritmo CYK para ver si la frase pertenece al lenguaje.

        Parametros:
            frase: String con la frase a analizar

        Retorna:
            tuple: (valida, tiempo, tabla) - si es válida, tiempo de ejecución, tabla CYK
        """
        palabras = frase.lower().split()
        n = len(palabras)

        if n == 0:
            return False, 0.0, None

        # Crear las tablas necesarias
        self.tabla = [[set() for _ in range(n)] for _ in range(n)]
        self.backpointers = [[{} for _ in range(n)] for _ in range(n)]

        tiempo_inicio = time.time()

        # Paso 1: Llenar la diagonal (palabras individuales)
        for i in range(n):
            palabra = palabras[i]
            # Buscar qué no terminales pueden generar esta palabra
            for nt, producciones in self.gramatica.items():
                for prod in producciones:
                    # Si es una producción terminal que coincide
                    if len(prod.split()) == 1 and self._es_terminal(prod) and prod == palabra:
                        self.tabla[i][i].add(nt)

        # Paso 2: Llenar el resto de la tabla
        # Para subcadenas de longitud 2 hasta n
        for longitud in range(2, n + 1):
            for i in range(n - longitud + 1):
                j = i + longitud - 1

                # Probar todos los puntos donde partir la subcadena
                for k in range(i, j):
                    # Revisar todas las reglas de la gramática
                    for nt, producciones in self.gramatica.items():
                        for prod in producciones:
                            partes = prod.split()
                            # Solo nos interesan reglas con 2 símbolos (A -> B C)
                            if len(partes) == 2:
                                B, C = partes

                                # Si B genera la primera parte y C la segunda
                                if B in self.tabla[i][k] and C in self.tabla[k + 1][j]:
                                    self.tabla[i][j].add(nt)

                                    # Guardar info para reconstruir el árbol después
                                    if nt not in self.backpointers[i][j]:
                                        self.backpointers[i][j][nt] = []
                                    self.backpointers[i][j][nt].append((B, C, k))

        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio

        # La frase es válida si S está en la esquina superior derecha
        es_valida = 'S' in self.tabla[0][n - 1]

        return es_valida, tiempo_total, self.tabla

    def _es_terminal(self, simbolo):
        """Verifica si un símbolo es terminal (minúscula)."""
        return simbolo and simbolo[0].islower()

    def construir_arbol(self, frase):
        """
        Construye el árbol de parsing para una frase válida.

        Parametros:
            frase: String con la frase a analizar

        Retorna:
            dict: Árbol de parsing
        """
        palabras = frase.lower().split()
        n = len(palabras)

        if n == 0 or self.tabla is None:
            return None

        def construir_subarbol(i, j, simbolo):
            """
            Construye recursivamente un subárbol para el símbolo en [i,j]
            """
            # Caso base: es una palabra
            if i == j:
                return {
                    'simbolo': simbolo,
                    'palabra': palabras[i],
                    'es_terminal': True
                }

            # Caso recursivo: dividir en dos partes
            if simbolo in self.backpointers[i][j]:
                # Tomar la primera opción (puede haber varias)
                B, C, k = self.backpointers[i][j][simbolo][0]

                return {
                    'simbolo': simbolo,
                    'es_terminal': False,
                    'hijos': [
                        construir_subarbol(i, k, B),
                        construir_subarbol(k + 1, j, C)
                    ]
                }

            return None

        # Construir desde S
        if 'S' in self.tabla[0][n - 1]:
            return construir_subarbol(0, n - 1, 'S')
        else:
            return None

    def imprimir_arbol(self, arbol, nivel=0):
        """
        Muestra el árbol de parsing en pantalla.

        Parametros:
            arbol: Árbol de parsing
            nivel: Nivel de indentación
        """
        if arbol is None:
            print(" " * nivel + "None")
            return

        if arbol.get('es_terminal', False):
            print(" " * nivel + f"{arbol['simbolo']} -> '{arbol['palabra']}'")
        else:
            print(" " * nivel + arbol['simbolo'])
            for hijo in arbol.get('hijos', []):
                self.imprimir_arbol(hijo, nivel + 2)

    def mostrar_tabla(self, frase):
        """
        Muestra la tabla CYK de forma legible.

        Parametros:
            frase: Frase analizada
        """
        if self.tabla is None:
            print("No hay tabla para mostrar")
            return

        palabras = frase.lower().split()
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
                    fila += " " * 10
                else:
                    contenido = ",".join(sorted(self.tabla[i][j]))
                    fila += f"{contenido:>10}"
            print(fila)

    def analizar_detallado(self, frase):
        """
        Hace un análisis completo de la frase.

        Parametros:
            frase: Frase a analizar

        Retorna:
            dict: Información detallada del análisis
        """
        es_valida, tiempo, tabla = self.analizar(frase)
        arbol = self.construir_arbol(frase) if es_valida else None

        return {
            'frase': frase,
            'valida': es_valida,
            'tiempo': tiempo,
            'num_palabras': len(frase.split()),
            'arbol': arbol,
            'tabla': tabla
        }


# Función para probar todo junto
def probar_sistema():
    """Función para probar el parser con ejemplos."""
    from GrammarCNFConverter import crear_gramatica_proyecto, GrammarCNFConverter

    # Preparar gramática
    gram = crear_gramatica_proyecto()
    conversor = GrammarCNFConverter(gram)
    gram_cnf = conversor.convertir_a_cnf()

    print("=== SISTEMA DE PARSING CYK ===")
    print("Gramática en CNF lista")
    conversor.imprimir_gramatica(gram_cnf)

    # Crear parser
    parser = CYKParser(gram_cnf)

    # Frases de prueba
    frases_prueba = [
        "she eats a cake",
        "the cat drinks the beer",
        "he cuts meat with a knife",
        "eats cake",  # Invalida
        "she drinks",  # Invalida
        "a fork with the spoon",  # Invalida
        "the dog eats the meat in the oven with a knife"
    ]

    print("\n" + "=" * 60)
    print("PRUEBAS")
    print("=" * 60)

    for frase in frases_prueba:
        print(f"\n--- Frase: '{frase}' ---")

        # Analizar
        resultado = parser.analizar_detallado(frase)

        # Mostrar resultado
        if resultado['valida']:
            print("✓ VÁLIDA - Pertenece al lenguaje")
            print(f"Tiempo: {resultado['tiempo']:.6f} segundos")
            print(f"Palabras: {resultado['num_palabras']}")

            # Mostrar árbol
            print("\nÁrbol de Parsing:")
            parser.imprimir_arbol(resultado['arbol'])
        else:
            print("✗ INVÁLIDA - No pertenece al lenguaje")
            print(f"Tiempo: {resultado['tiempo']:.6f} segundos")

        # Tabla para frases cortas
        if resultado['num_palabras'] <= 6:
            parser.mostrar_tabla(frase)

        print("-" * 40)


if __name__ == "__main__":
    probar_sistema()