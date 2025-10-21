import re
from collections import defaultdict

class GrammarCNFConverter:
    def __init__(self, gramatica_dict):
        """
        Inicializa el conversor con una gramática en forma de diccionario.

        Parametros:
            gramatica_dict: Diccionario donde las claves son no terminales
                          y los valores son listas de producciones.
                          Ejemplo: {'S': ['NP VP'], 'NP': ['Det N', 'he']}
        """
        self.gramatica_original = gramatica_dict
        self.gramatica = self._copiar_gramatica(gramatica_dict)
        self.nuevos_no_terminales = set()
        self.reglas_terminales = {}
        self.contador_nuevos_nt = 0

    def _copiar_gramatica(self, gramatica):
        """Hace una copia de la gramática para no modificar la original."""
        return {nt: prods[:] for nt, prods in gramatica.items()}

    def verificar_cnf(self):
        """
        Revisa si la gramática ya está en Forma Normal de Chomsky.

        Retorna:
            bool: True si está en CNF, False si no.
        """
        for no_terminal, producciones in self.gramatica.items():
            for prod in producciones:
                simbolos = prod.split()

                # Si está vacía no es válida
                if len(simbolos) == 0:
                    return False

                # Si tiene un solo símbolo, debe ser terminal
                if len(simbolos) == 1:
                    if not self._es_terminal(simbolos[0]):
                        return False

                # Si tiene dos símbolos, ambos deben ser no terminales
                elif len(simbolos) == 2:
                    if self._es_terminal(simbolos[0]) or self._es_terminal(simbolos[1]):
                        return False

                # Si tiene más de dos símbolos, no es CNF
                else:
                    return False

        return True

    def _es_terminal(self, simbolo):
        """
        Revisa si un símbolo es terminal o no terminal.
        Los terminales empiezan con minúscula.
        """
        if not simbolo or simbolo == '':
            return True
        return simbolo[0].islower()

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

        # Paso 0: Eliminar producciones epsilon (vacías)
        print("Paso 1: Eliminando producciones epsilon...")
        self._eliminar_producciones_epsilon()

        # Paso 1: Quitar producciones unitarias (A -> B)
        print("Paso 2: Eliminando producciones unitarias...")
        self._eliminar_producciones_unitarias()

        # Paso 2: Arreglar terminales que están mezclados con no terminales
        print("Paso 3: Manejando terminales...")
        self._manejar_terminales()

        # Paso 3: Partir producciones largas (más de 2 símbolos)
        print("Paso 4: Descomponiendo producciones largas...")
        self._descomponer_producciones_largas()

        # Paso 4: Eliminar símbolos inútiles AL FINAL (después de toda la conversión)
        print("Paso 5: Eliminando símbolos inútiles...")
        self._eliminar_simbolos_inutiles()

        print("Conversión completada exitosamente")
        return self.gramatica

    def _eliminar_producciones_unitarias(self):
        """
        Elimina producciones unitarias de la forma A -> B donde B es no terminal.
        Usa clausura transitiva para manejar cadenas de producciones unitarias.
        """
        # Encontrar todas las parejas unitarias (A, B) donde A ->* B
        pares_unitarios = {}

        # Inicializar: cada no terminal alcanza a sí mismo
        for nt in self.gramatica:
            pares_unitarios[nt] = {nt}

        # Encontrar todas las producciones unitarias directas
        for nt, producciones in self.gramatica.items():
            for prod in producciones:
                partes = prod.split()
                # Si es unitaria (un solo símbolo no terminal)
                if len(partes) == 1 and not self._es_terminal(partes[0]):
                    if partes[0] in self.gramatica:
                        pares_unitarios[nt].add(partes[0])

        # Calcular clausura transitiva
        cambio = True
        while cambio:
            cambio = False
            for nt in self.gramatica:
                tamaño_anterior = len(pares_unitarios[nt])
                # Si A ->* B y B ->* C, entonces A ->* C
                nuevos = set()
                for alcanzable in pares_unitarios[nt]:
                    if alcanzable in pares_unitarios:
                        nuevos.update(pares_unitarios[alcanzable])
                pares_unitarios[nt].update(nuevos)
                if len(pares_unitarios[nt]) > tamaño_anterior:
                    cambio = True

        # Construir nueva gramática sin producciones unitarias
        nueva_gramatica = {}

        for nt in self.gramatica:
            nuevas_prods = set()

            # Para cada no terminal B alcanzable desde A
            for alcanzable in pares_unitarios[nt]:
                if alcanzable not in self.gramatica:
                    continue

                # Agregar todas las producciones NO unitarias de B
                for prod in self.gramatica[alcanzable]:
                    partes = prod.split()

                    # Solo agregar si NO es unitaria
                    if not (len(partes) == 1 and not self._es_terminal(partes[0])):
                        nuevas_prods.add(prod)

            if nuevas_prods:
                nueva_gramatica[nt] = list(nuevas_prods)

        self.gramatica = nueva_gramatica

    def _eliminar_producciones_epsilon(self):
        """
        Elimina producciones epsilon (vacías) de la gramática.
        Genera todas las combinaciones necesarias para compensar la eliminación.
        """
        # Paso 1: Encontrar todos los símbolos anulables (que pueden derivar en epsilon)
        anulables = set()
        cambio = True

        while cambio:
            cambio = False
            for nt, producciones in self.gramatica.items():
                if nt in anulables:
                    continue

                for prod in producciones:
                    prod_limpio = prod.strip()

                    # Si la producción es explícitamente epsilon
                    if prod_limpio == '' or prod_limpio == 'e' or prod_limpio == 'epsilon':
                        anulables.add(nt)
                        cambio = True
                        break

                    # Si todos los símbolos de la producción son anulables
                    simbolos = prod.split()
                    if simbolos and all(s in anulables for s in simbolos):
                        anulables.add(nt)
                        cambio = True
                        break

        # Si no hay símbolos anulables, no hay nada que hacer
        if not anulables:
            return

        # Paso 2: Construir nueva gramática sin epsilon
        nueva_gramatica = {}

        for nt, producciones in self.gramatica.items():
            nuevas_prods = set()

            for prod in producciones:
                prod_limpio = prod.strip()

                # Saltar producciones epsilon explícitas
                if prod_limpio == '' or prod_limpio == 'e' or prod_limpio == 'epsilon':
                    continue

                simbolos = prod.split()
                if not simbolos:
                    continue

                # Generar todas las combinaciones quitando símbolos anulables
                combinaciones = self._generar_combinaciones(simbolos, anulables)
                nuevas_prods.update(combinaciones)

            # Solo agregar si hay producciones
            if nuevas_prods:
                nueva_gramatica[nt] = list(nuevas_prods)

        self.gramatica = nueva_gramatica

    def _generar_combinaciones(self, simbolos, anulables):
        """
        Genera todas las combinaciones posibles de una producción
        considerando que algunos símbolos pueden ser anulables.

        Por ejemplo: si tenemos A B C donde B es anulable,
        generamos: A B C, A C
        """
        if not simbolos:
            return set()

        combinaciones = set()

        # Usamos un enfoque de máscara de bits
        # Para n símbolos, hay 2^n combinaciones posibles
        n = len(simbolos)

        for mascara in range(1, 2 ** n):  # Empezamos en 1 para evitar la cadena vacía
            combinacion = []

            for i in range(n):
                # Si el bit i está activado en la máscara
                if mascara & (1 << i):
                    combinacion.append(simbolos[i])
                else:
                    # Solo omitimos el símbolo si es anulable
                    if simbolos[i] not in anulables:
                        combinacion.append(simbolos[i])

            if combinacion:  # Solo agregamos si la combinación no está vacía
                combinaciones.add(' '.join(combinacion))

        return combinaciones

    def _eliminar_simbolos_inutiles(self):
        """
        Elimina símbolos que no son productivos o no son alcanzables.
        Se ejecuta AL FINAL de la conversión cuando la gramática ya está más limpia.
        """
        if not self.gramatica:
            return

        # Determinar símbolo inicial (puede no ser 'S')
        simbolo_inicial = 'S'
        if 'S' not in self.gramatica and self.gramatica:
            simbolo_inicial = list(self.gramatica.keys())[0]

        # PASO 1: Encontrar símbolos PRODUCTIVOS (que pueden derivar en terminales)
        productivos = set()
        cambio = True

        while cambio:
            cambio = False
            for nt, producciones in self.gramatica.items():
                if nt in productivos:
                    continue

                for prod in producciones:
                    simbolos = prod.split()
                    if not simbolos:
                        continue

                    # Un no terminal es productivo si:
                    # - Tiene una producción que solo contiene terminales
                    # - O tiene una producción donde todos los no terminales son productivos
                    todos_productivos = True
                    for s in simbolos:
                        if not self._es_terminal(s) and s not in productivos:
                            todos_productivos = False
                            break

                    if todos_productivos:
                        productivos.add(nt)
                        cambio = True
                        break

        # Verificar que el símbolo inicial sea productivo
        if simbolo_inicial not in productivos:
            print(
                f"  Advertencia: El símbolo inicial '{simbolo_inicial}' no es productivo. Eliminando símbolos no productivos...")

        # Filtrar producciones manteniendo solo las que usan símbolos productivos
        gram_productivos = {}
        for nt, producciones in self.gramatica.items():
            if nt not in productivos:
                continue

            prods_validas = []
            for prod in producciones:
                simbolos = prod.split()
                if not simbolos:
                    continue

                # Mantener producción si todos sus símbolos son productivos o terminales
                if all(self._es_terminal(s) or s in productivos for s in simbolos):
                    prods_validas.append(prod)

            if prods_validas:
                gram_productivos[nt] = prods_validas

        if not gram_productivos:
            print("  Advertencia: Filtrado de productivos resultó vacío. Manteniendo gramática.")
            return

        self.gramatica = gram_productivos

        # PASO 2: Encontrar símbolos ALCANZABLES desde S
        alcanzables = {'S'}
        cambio = True

        while cambio:
            cambio = False
            nuevos_alcanzables = set()

            for nt in alcanzables:
                if nt not in self.gramatica:
                    continue

                for prod in self.gramatica[nt]:
                    for simbolo in prod.split():
                        if not self._es_terminal(simbolo):
                            if simbolo not in alcanzables:
                                nuevos_alcanzables.add(simbolo)
                                cambio = True

            alcanzables.update(nuevos_alcanzables)

        # Filtrar manteniendo solo símbolos alcanzables
        gram_final = {}
        for nt, producciones in self.gramatica.items():
            if nt in alcanzables:
                gram_final[nt] = producciones

        if not gram_final or 'S' not in gram_final:
            print("  Advertencia: Filtrado de alcanzables resultó vacío. Manteniendo gramática anterior.")
            return

        self.gramatica = gram_final

    def _manejar_terminales(self):
        """
        Cuando un terminal aparece junto con otros símbolos,
        se crea un nuevo no terminal para ese terminal.
        """
        terminales_a_reemplazar = set()

        # Buscar terminales que están mezclados con otros símbolos
        for producciones in self.gramatica.values():
            for prod in producciones:
                simbolos = prod.split()
                if len(simbolos) > 1:
                    for s in simbolos:
                        if self._es_terminal(s):
                            terminales_a_reemplazar.add(s)

        # Crear nuevos no terminales para esos terminales
        mapeo_terminal_a_nt = {}
        for terminal in terminales_a_reemplazar:
            # Crear nombre para el nuevo no terminal
            nombre_base = terminal.upper()
            nuevo_nt = nombre_base
            num = 1
            while nuevo_nt in self.gramatica or nuevo_nt in mapeo_terminal_a_nt.values():
                nuevo_nt = f"{nombre_base}{num}"
                num += 1

            mapeo_terminal_a_nt[terminal] = nuevo_nt
            self.nuevos_no_terminales.add(nuevo_nt)

        # Agregar las nuevas reglas
        for terminal, nuevo_nt in mapeo_terminal_a_nt.items():
            self.gramatica[nuevo_nt] = [terminal]

        # Reemplazar en las producciones existentes
        nueva_gram = {}
        for nt, producciones in self.gramatica.items():
            nuevas_prods = []
            for prod in producciones:
                simbolos = prod.split()
                if len(simbolos) > 1:
                    nuevos_simbolos = []
                    for s in simbolos:
                        if self._es_terminal(s) and s in mapeo_terminal_a_nt:
                            nuevos_simbolos.append(mapeo_terminal_a_nt[s])
                        else:
                            nuevos_simbolos.append(s)
                    nuevas_prods.append(' '.join(nuevos_simbolos))
                else:
                    nuevas_prods.append(prod)
            nueva_gram[nt] = nuevas_prods

        self.gramatica = nueva_gram
        self.reglas_terminales = mapeo_terminal_a_nt

    def _descomponer_producciones_largas(self):
        """
        Convierte producciones con más de 2 símbolos en varias
        producciones de exactamente 2 símbolos.
        """
        hay_cambios = True

        while hay_cambios:
            hay_cambios = False
            gram_nueva = {}

            for nt, producciones in self.gramatica.items():
                if nt not in gram_nueva:
                    gram_nueva[nt] = []

                for prod in producciones:
                    simbolos = prod.split()

                    if len(simbolos) <= 2:
                        gram_nueva[nt].append(prod)
                    else:
                        hay_cambios = True
                        # Descomponer A -> X1 X2 X3 ... Xn
                        # en A -> X1 Y1, Y1 -> X2 Y2, ..., Yn-2 -> Xn-1 Xn

                        nt_actual = nt
                        for i in range(len(simbolos) - 2):
                            # Crear nuevo no terminal
                            nuevo_nt = f"Y{self.contador_nuevos_nt}"
                            self.contador_nuevos_nt += 1
                            self.nuevos_no_terminales.add(nuevo_nt)

                            # Agregar producción: nt_actual -> simbolos[i] nuevo_nt
                            if nt_actual not in gram_nueva:
                                gram_nueva[nt_actual] = []
                            gram_nueva[nt_actual].append(f"{simbolos[i]} {nuevo_nt}")

                            nt_actual = nuevo_nt

                        # Última producción con los últimos 2 símbolos
                        if nt_actual not in gram_nueva:
                            gram_nueva[nt_actual] = []
                        gram_nueva[nt_actual].append(f"{simbolos[-2]} {simbolos[-1]}")

            self.gramatica = gram_nueva

    def obtener_gramatica_cnf(self):
        """Devuelve la gramática en CNF."""
        return self.gramatica

    def imprimir_gramatica(self, gram=None):
        """Muestra la gramática en pantalla de forma ordenada."""
        if gram is None:
            gram = self.gramatica

        print("\nGramática:")
        for nt in sorted(gram.keys()):
            prods = gram[nt]
            texto_prods = " | ".join(prods)
            print(f"{nt} -> {texto_prods}")

    def obtener_reporte(self):
        """Genera información sobre la conversión realizada."""
        reporte = {
            'reglas_originales': sum(len(p) for p in self.gramatica_original.values()),
            'reglas_cnf': sum(len(p) for p in self.gramatica.values()),
            'no_terminales_nuevos': len(self.nuevos_no_terminales),
            'mapeo_terminales': self.reglas_terminales
        }
        return reporte


def leer_gramatica_desde_archivo(nombre_archivo):
    """
    Lee una gramática desde un archivo de texto.

    Formato esperado:
        E -> T X
        X -> + T X | e
        T -> F Y
        ...

    Parametros:
        nombre_archivo: Ruta al archivo con la gramática

    Retorna:
        dict: Diccionario con la gramática parseada
    """
    gramatica = {}

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()

        for linea in lineas:
            linea = linea.strip()

            # Ignorar líneas vacías o comentarios
            if not linea or linea.startswith('#'):
                continue

            # Separar por ->
            if '->' not in linea:
                continue

            partes = linea.split('->')
            if len(partes) != 2:
                continue

            no_terminal = partes[0].strip()
            producciones_str = partes[1].strip()

            # Separar producciones por |
            producciones = [p.strip() for p in producciones_str.split('|')]

            # MANTENER epsilon como está (no filtrar aquí, el conversor lo manejará)
            # Solo filtrar producciones completamente vacías
            producciones = [p for p in producciones if p]

            if no_terminal in gramatica:
                gramatica[no_terminal].extend(producciones)
            else:
                gramatica[no_terminal] = producciones

        # Verificar que haya al menos una producción
        if not gramatica:
            raise ValueError("El archivo no contiene producciones válidas")

        # Si no hay símbolo inicial 'S', usar el primer no terminal como S
        if 'S' not in gramatica and gramatica:
            primer_nt = list(gramatica.keys())[0]
            print(f"Advertencia: No se encontró símbolo inicial 'S', usando '{primer_nt}' como inicial")

        return gramatica

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {nombre_archivo}")
    except Exception as e:
        raise Exception(f"Error al leer la gramática: {str(e)}")


def crear_gramatica_proyecto():
    """Crea la gramática del proyecto según las especificaciones."""
    gramatica = {
        'E':['T X'],
        'X':['+ T X','e'],
        'T':['F Y'],
        'Y': ['* F Y', 'e'],
        'F': ['( E )', 'id'],
    }
    """
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
    """
    return gramatica


# Probar el conversor
if __name__ == "__main__":
    import sys

    print("=== CONVERSOR A FORMA NORMAL DE CHOMSKY ===")

    # Permitir especificar archivo desde línea de comandos
    if len(sys.argv) > 1:
        archivo_gramatica = sys.argv[1]
        print(f"\nLeyendo gramática desde: {archivo_gramatica}")
        try:
            gram_original = leer_gramatica_desde_archivo(archivo_gramatica)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("\nUsando gramática del proyecto por defecto")
        gram_original = crear_gramatica_proyecto()

    print("\nGramática Original:")
    conversor = GrammarCNFConverter(gram_original)
    conversor.imprimir_gramatica(gram_original)

    # Verificar si está en CNF
    if conversor.verificar_cnf():
        print("\nLa gramática ya está en CNF")
    else:
        print("\nLa gramática NO está en CNF")
        print("Procediendo con la conversión...")

        # Convertir
        gram_cnf = conversor.convertir_a_cnf()

        print("\nGramática convertida a CNF:")
        conversor.imprimir_gramatica(gram_cnf)

        # Mostrar reporte
        reporte = conversor.obtener_reporte()
        print(f"\n=== REPORTE ===")
        print(f"Reglas originales: {reporte['reglas_originales']}")
        print(f"Reglas en CNF: {reporte['reglas_cnf']}")
        print(f"No terminales nuevos creados: {reporte['no_terminales_nuevos']}")
        print(f"Terminales mapeados: {len(reporte['mapeo_terminales'])}")

        # Verificar que la conversión funcionó
        if conversor.verificar_cnf():
            print("\nConversión exitosa - Gramática en CNF")
        else:
            print("\nError - La gramática no quedó en CNF")
