from GrammarCNFConverter import GrammarCNFConverter, crear_gramatica_proyecto
from CYKParser import CYKParser
import os


def mostrar_menu():
    """Muestra el menú principal."""
    print("\n" + "=" * 50)
    print("  ANALIZADOR SINTACTICO CYK")
    print("=" * 50)
    print("\n1. Ver gramatica original")
    print("2. Ver gramatica en CNF")
    print("3. Analizar una frase")
    print("4. Analizar frases desde archivo")
    print("5. Salir")
    print("-" * 50)


def ver_gramatica_original(conversor):
    """Muestra la gramatica original."""
    print("\n--- Gramatica Original ---")
    conversor.imprimir_gramatica(conversor.gramatica_original)
    input("\nPresione Enter para continuar...")


def ver_gramatica_cnf(conversor):
    """Muestra la gramatica en CNF."""
    print("\n--- Gramatica en CNF ---")
    conversor.imprimir_gramatica(conversor.gramatica)
    input("\nPresione Enter para continuar...")


def analizar_una_frase(parser):
    """Analiza una sola frase ingresada por el usuario."""
    print("\n--- Analizar Frase ---")
    frase = input("Ingrese la frase: ").strip()

    if not frase:
        print("Error: Debe ingresar una frase")
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

    # Salida 2: Tiempo de ejecucion
    print(f"Tiempo: {tiempo:.6f} segundos")

    # Salida 3: Parse tree
    if es_valida:
        arbol = parser.construir_arbol(frase)
        print("\nParse Tree:")
        parser.imprimir_arbol(arbol)
    else:
        print("\nParse Tree: No disponible (frase invalida)")

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

            # Salida 2: Tiempo de ejecucion
            print(f"Tiempo: {tiempo:.6f} segundos")

            # Salida 3: Parse tree
            if es_valida:
                arbol = parser.construir_arbol(frase)
                print("\nParse Tree:")
                parser.imprimir_arbol(arbol)
            else:
                print("\nParse Tree: No disponible (frase invalida)")

            print("-" * 50)

        input("\nPresione Enter para continuar...")

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        input("\nPresione Enter para continuar...")


def inicializar():
    """Inicializa la gramatica y el parser."""
    print("\nInicializando sistema...")

    # Cargar gramatica
    gram = crear_gramatica_proyecto()
    conversor = GrammarCNFConverter(gram)

    # Convertir a CNF si es necesario
    if not conversor.verificar_cnf():
        print("Convirtiendo gramatica a CNF...")
        gram_cnf = conversor.convertir_a_cnf()
    else:
        gram_cnf = conversor.gramatica

    # Crear parser
    parser = CYKParser(gram_cnf)

    print("Sistema listo\n")

    return conversor, parser


def main():
    """Funcion principal."""
    print("\n" + "=" * 50)
    print("  PROYECTO 2 - ALGORITMO CYK")
    print("  Teoria de la Computacion")
    print("=" * 50)

    # Inicializar sistema
    conversor, parser = inicializar()

    # Menu principal
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == '1':
            ver_gramatica_original(conversor)
        elif opcion == '2':
            ver_gramatica_cnf(conversor)
        elif opcion == '3':
            analizar_una_frase(parser)
        elif opcion == '4':
            analizar_desde_archivo(parser)
        elif opcion == '5':
            print("\nSaliendo del programa...\n")
            break
        else:
            print("\nOpcion no valida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido\n")
    except Exception as e:
        print(f"\nError: {e}\n")