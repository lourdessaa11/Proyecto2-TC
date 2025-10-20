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

        # Paso 1: Quitar producciones unitarias (A -> B)
        self._eliminar_producciones_unitarias()

        # Paso 2: Quitar símbolos que no sirven
        self._eliminar_simbolos_inutiles()

        # Paso 3: Arreglar terminales que están mezclados con no terminales
        self._manejar_terminales()

        # Paso 4: Partir producciones largas (más de 2 símbolos)
        self._descomponer_producciones_largas()

        print("Conversión completada exitosamente")
        return self.gramatica

    def _eliminar_producciones_unitarias(self):
        """Elimina producciones de la forma A -> B donde B es no terminal."""
        sigue_cambiando = True

        while sigue_cambiando:
            sigue_cambiando = False
            nueva_gramatica = self._copiar_gramatica(self.gramatica)

            for nt, producciones in self.gramatica.items():
                for prod in producciones:
                    partes = prod.split()

                    # Si es producción unitaria (un solo no terminal)
                    if len(partes) == 1 and not self._es_terminal(partes[0]):
                        nt_referenciado = partes[0]

                        # Reemplazar con las producciones del no terminal referenciado
                        if nt_referenciado in self.gramatica:
                            for nueva_prod in self.gramatica[nt_referenciado]:
                                if nueva_prod not in nueva_gramatica[nt]:
                                    nueva_gramatica[nt].append(nueva_prod)
                                    sigue_cambiando = True

                        # Quitar la producción unitaria
                        if prod in nueva_gramatica[nt]:
                            nueva_gramatica[nt].remove(prod)

            self.gramatica = nueva_gramatica

    def _eliminar_simbolos_inutiles(self):
        """Elimina símbolos que no generan nada o no se pueden alcanzar."""
        # Primero encontrar cuáles símbolos pueden generar terminales
        generativos = set()
        cambio = True

        while cambio:
            cambio = False
            for nt, producciones in self.gramatica.items():
                if nt in generativos:
                    continue

                for prod in producciones:
                    simbolos = prod.split()
                    # Si todos los símbolos son terminales o ya son generativos
                    if all(self._es_terminal(s) or s in generativos for s in simbolos):
                        generativos.add(nt)
                        cambio = True
                        break

        # Quedarse solo con símbolos generativos
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

        # Ahora encontrar símbolos alcanzables desde S
        alcanzables = {'S'}
        cambio = True

        while cambio:
            cambio = False
            for nt in list(alcanzables):
                if nt not in self.gramatica:
                    continue
                for prod in self.gramatica[nt]:
                    for simbolo in prod.split():
                        if not self._es_terminal(simbolo) and simbolo not in alcanzables:
                            alcanzables.add(simbolo)
                            cambio = True

        # Quedarse solo con alcanzables
        gram_final = {}
        for nt, producciones in self.gramatica.items():
            if nt in alcanzables:
                gram_final[nt] = producciones

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


def crear_gramatica_proyecto():
    """Crea la gramática del proyecto según las especificaciones."""
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


# Probar el conversor
if __name__ == "__main__":
    gram_original = crear_gramatica_proyecto()

    print("=== CONVERSOR A FORMA NORMAL DE CHOMSKY ===")
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