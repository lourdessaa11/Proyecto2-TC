from GrammarCNFConverter import GrammarCNFConverter, crear_gramatica_proyecto, leer_gramatica_desde_archivo
from CYKParser import CYKParser
import os


def mostrar_menu():
    """Muestra el menú principal."""
    print("\n" + "=" * 50)
    print("  ANALIZADOR SINTACTICO CYK")
    print("=" * 50)
    print("\n1. Ver gramática original")
    print("2. Ver gramática en CNF")
    print("3. Analizar una frase")
    print("4. Analizar frases desde archivo")
    print("5. Cargar nueva gramática desde archivo")
    print("6. Salir")
    print("-" * 50)


def ver_gramatica_original(conversor):
    """Muestra la gramática original."""
    print("\n--- Gramática Original ---")
    conversor.imprimir_gramatica(conversor.gramatica_original)
    input("\nPresione Enter para continuar...")


def ver_gramatica_cnf(conversor):
    """Muestra la gramática en CNF."""
    print("\n--- Gramática en CNF ---")
    conversor.imprimir_gramatica(conversor.gramatica)

    # Mostrar reporte
    reporte = conversor.obtener_reporte()
    print(f"\n=== ESTADÍSTICAS ===")
    print(f"Reglas originales: {reporte['reglas_originales']}")
    print(f"Reglas en CNF: {reporte['reglas_cnf']}")
    print(f"No terminales nuevos: {reporte['no_terminales_nuevos']}")

    input("\nPresione Enter para continuar...")


def analizar_una_frase(parser):
    """Analiza una sola frase ingresada por el usuario."""
    print("\n--- Analizar Frase ---")
    frase = input("Ingrese la frase: ").strip()

    if not frase:
        print("Error: Debe ingresar una frase")
        input("\nPresione Enter para continuar...")
        return

    print(f"\nFrase: {frase}")
    print("-" * 50)

    # Analizar
    es_valida, tiempo, tabla = parser.analizar(frase)

    # Salida 1: Si pertenece al lenguaje
    if es_valida:
        print("Resultado: SI")
    else:
        print("Resultado: NO")

    # Salida 2: Tiempo de ejecución
    print(f"Tiempo: {tiempo:.6f} segundos")

    # Salida 3: Parse tree
    if es_valida:
        arbol = parser.construir_arbol(frase)
        print("\nParse Tree:")
        parser.imprimir_arbol(arbol)
    else:
        print("\nParse Tree: No disponible (frase inválida)")

    input("\nPresione Enter para continuar...")


def analizar_desde_archivo(parser):
    """Analiza frases desde un archivo de texto."""
    print("\n--- Analizar desde Archivo ---")
    nombre_archivo = input("Ingrese el nombre del archivo: ").strip()

    if not os.path.exists(nombre_archivo):
        print(f"Error: El archivo '{nombre_archivo}' no existe")
        input("\nPresione Enter para continuar...")
        return

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            frases = archivo.readlines()

        print(f"\nSe encontraron {len(frases)} frases en el archivo")
        print("=" * 50)

        for i, frase in enumerate(frases, 1):
            frase = frase.strip()
            if not frase:
                continue

            print(f"\n--- Frase {i}: {frase} ---")

            # Analizar
            es_valida, tiempo, tabla = parser.analizar(frase)

            # Salida 1: Si pertenece al lenguaje
            if es_valida:
                print("Resultado: SI")
            else:
                print("Resultado: NO")

            # Salida 2: Tiempo de ejecución
            print(f"Tiempo: {tiempo:.6f} segundos")

            # Salida 3: Parse tree
            if es_valida:
                arbol = parser.construir_arbol(frase)
                print("\nParse Tree:")
                parser.imprimir_arbol(arbol)
            else:
                print("\nParse Tree: No disponible (frase inválida)")

            print("-" * 50)

        input("\nPresione Enter para continuar...")

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        input("\nPresione Enter para continuar...")


def cargar_nueva_gramatica():
    """Carga una nueva gramática desde un archivo."""
    print("\n--- Cargar Nueva Gramática ---")
    print("\nFormato esperado del archivo:")
    print("  E -> T X")
    print("  X -> + T X | e")
    print("  T -> F Y")
    print("  ...")
    print("\nNotas:")
    print("  - Use '->' para separar no terminal de producciones")
    print("  - Use '|' para separar múltiples producciones")
    print("  - Líneas vacías y que empiecen con '#' serán ignoradas")

    nombre_archivo = input("\nIngrese el nombre del archivo: ").strip()

    if not os.path.exists(nombre_archivo):
        print(f"Error: El archivo '{nombre_archivo}' no existe")
        input("\nPresione Enter para continuar...")
        return None, None

    try:
        print("\nCargando gramática...")
        gram = leer_gramatica_desde_archivo(nombre_archivo)

        print("\nGramática cargada exitosamente:")
        print(f"  - {len(gram)} no terminales")
        print(f"  - {sum(len(prods) for prods in gram.values())} producciones")

        # Crear conversor
        conversor = GrammarCNFConverter(gram)

        # Mostrar gramática original
        print("\n--- Gramática Cargada ---")
        conversor.imprimir_gramatica(gram)

        # Convertir a CNF
        print("\nConvirtiendo a CNF...")
        if not conversor.verificar_cnf():
            gram_cnf = conversor.convertir_a_cnf()
            print("\n--- Gramática en CNF ---")
            conversor.imprimir_gramatica(gram_cnf)
        else:
            gram_cnf = conversor.gramatica
            print("\nLa gramática ya está en CNF")

        # Crear parser
        parser = CYKParser(gram_cnf)

        print("\n✓ Gramática cargada y lista para usar")
        input("\nPresione Enter para continuar...")

        return conversor, parser

    except Exception as e:
        print(f"\nError al cargar la gramática: {e}")
        input("\nPresione Enter para continuar...")
        return None, None


def inicializar(usar_gramatica_proyecto=True):
    """
    Inicializa la gramática y el parser.

    Parametros:
        usar_gramatica_proyecto: Si True, usa la gramática del proyecto por defecto
    """
    print("\nInicializando sistema...")

    if usar_gramatica_proyecto:
        # Cargar gramática del proyecto
        gram = crear_gramatica_proyecto()
        conversor = GrammarCNFConverter(gram)
        print("Usando gramática del proyecto por defecto")
    else:
        print("Modo: Cargar gramática personalizada al inicio")
        return None, None

    # Convertir a CNF si es necesario
    if not conversor.verificar_cnf():
        print("Convirtiendo gramática a CNF...")
        gram_cnf = conversor.convertir_a_cnf()
    else:
        gram_cnf = conversor.gramatica

    # Crear parser
    parser = CYKParser(gram_cnf)

    print("Sistema listo\n")

    return conversor, parser


def main():
    """Función principal."""
    print("\n" + "=" * 50)
    print("  PROYECTO 2 - ALGORITMO CYK")
    print("  Teoría de la Computación")
    print("=" * 50)

    # Preguntar si quiere cargar gramática personalizada o usar la del proyecto
    print("\n¿Qué gramática desea usar?")
    print("1. Gramática del proyecto (por defecto)")
    print("2. Cargar gramática desde archivo")
    opcion_inicial = input("Seleccione una opción (1-2): ").strip()

    if opcion_inicial == '2':
        conversor, parser = cargar_nueva_gramatica()
        if conversor is None or parser is None:
            print("\nNo se pudo cargar la gramática. Usando gramática del proyecto.")
            conversor, parser = inicializar(usar_gramatica_proyecto=True)
    else:
        conversor, parser = inicializar(usar_gramatica_proyecto=True)

    # Menú principal
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            ver_gramatica_original(conversor)
        elif opcion == '2':
            ver_gramatica_cnf(conversor)
        elif opcion == '3':
            analizar_una_frase(parser)
        elif opcion == '4':
            analizar_desde_archivo(parser)
        elif opcion == '5':
            nueva_conversor, nuevo_parser = cargar_nueva_gramatica()
            if nueva_conversor is not None and nuevo_parser is not None:
                conversor = nueva_conversor
                parser = nuevo_parser
                print("\n✓ Gramática actualizada exitosamente")
        elif opcion == '6':
            print("\nSaliendo del programa...\n")
            break
        else:
            print("\nOpción no válida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido\n")
    except Exception as e:
        print(f"\nError: {e}\n")