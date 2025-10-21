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
    print("5. Cargar gramatica desde archivo .txt")
    print("6. Salir")
    print("-" * 50)

def ver_gramatica_original(conversor):
    """Imprime la gramática original."""
    if conversor is None:
        print("\nNo hay gramática cargada")
        input("\nPresione Enter para continuar...")
        return
    print("\n=== Gramática original ===")
    for nt in sorted(conversor.gramatica_original.keys()):
        rhs = " | ".join(conversor.gramatica_original[nt])
        print(f"{nt} -> {rhs}")
    input("\nPresione Enter para continuar...")

def ver_gramatica_cnf(conversor):
    """Convierte (si hace falta) e imprime la gramática en CNF."""
    if conversor is None:
        print("\nNo hay gramática cargada")
        input("\nPresione Enter para continuar...")
        return

    print("\nVerificando si la gramática está en CNF...")
    if conversor.verificar_cnf():
        print("La gramática ya está en CNF")
        conversor.imprimir_gramatica()
    else:
        print("La gramática NO está en CNF")
        print("Convirtiendo gramatica a CNF...")
        gram_cnf = conversor.convertir_a_cnf()
        conversor.imprimir_gramatica(gram_cnf)

        # Reporte breve
        rep = conversor.obtener_reporte()
        print("\n=== REPORTE ===")
        print(f"Reglas originales: {rep['reglas_originales']}")
        print(f"Reglas en CNF: {rep['reglas_cnf']}")
        print(f"No terminales nuevos creados: {rep['no_terminales_nuevos']}")
        print(f"Terminales mapeados: {len(rep['mapeo_terminales'])}")
    input("\nPresione Enter para continuar...")

def analizar_frase(parser):
    """Pide una frase y la analiza con CYK."""
    if parser is None:
        print("\nNo hay parser inicializado")
        input("\nPresione Enter para continuar...")
        return

    print("\n--- Analizar una frase ---")
    print("Ingrese la frase con tokens separados por espacios.")
    print("Ejemplo (para 1.txt): id + id * id   o   ( id ) * id")
    frase = input("Frase: ").strip()
    if not frase:
        print("No se ingreso frase")
        input("\nPresione Enter para continuar...")
        return

    es_valida, tiempo, tabla = parser.analizar(frase)
    if es_valida:
        print("\n✓ VALIDA - Pertenece al lenguaje")
    else:
        print("\n✗ INVALIDA - No pertenece al lenguaje")
    print(f"Tiempo: {tiempo:.6f} segundos")

    # Mostrar tabla para frases cortas
    if len(frase.split()) <= 12:
        parser.mostrar_tabla(frase)

    # Intentar un arbol (opcional)
    arbol = parser.reconstruir_arbol(frase)
    if arbol:
        print("\nÁrbol de Parsing:")
        parser.imprimir_arbol(arbol)

    input("\nPresione Enter para continuar...")

def analizar_desde_archivo(parser):
    """Lee un archivo con una frase por línea y analiza cada una."""
    if parser is None:
        print("\nNo hay parser inicializado")
        input("\nPresione Enter para continuar...")
        return

    print("\n--- Analizar frases desde archivo ---")
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
            es_valida, tiempo, _ = parser.analizar(frase)
            if es_valida:
                print("Resultado: SI")
            else:
                print("Resultado: NO")
            print(f"Tiempo: {tiempo:.6f} segundos")

        print("\nFin del análisis por archivo")
    except Exception as e:
        print(f"\nError al leer o procesar el archivo: {e}")
    input("\nPresione Enter para continuar...")

def cargar_gramatica_desde_archivo():
    """Carga una gramática desde un archivo .txt y devuelve (gram, start_symbol)."""
    print("\n--- Cargar Gramática ---")
    ruta = input("Ingrese la ruta del archivo .txt (ej. 1.txt): ").strip()
    if not os.path.exists(ruta):
        print(f"Error: El archivo '{ruta}' no existe")
        input("\nPresione Enter para continuar...")
        return None, None
    try:
        gram, start = GrammarCNFConverter.cargar_gramatica_desde_txt(ruta)
        print(f"\nGramática cargada. Símbolo inicial: {start}")
        return gram, start
    except Exception as e:
        print(f"Error al leer la gramática: {e}")
        input("\nPresione Enter para continuar...")
        return None, None

def inicializar(gram=None, start_symbol='S'):
    """Prepara conversor y parser a partir de una gramática (o la por defecto)."""
    print("\nInicializando sistema...")
    if gram is None:
        gram = crear_gramatica_proyecto()
        start_symbol = 'S'

    conversor = GrammarCNFConverter(gram, start_symbol)
    # Convertir a CNF (si hace falta) una sola vez para preparar el parser
    if not conversor.verificar_cnf():
        print("Convirtiendo gramatica a CNF...")
        gram_cnf = conversor.convertir_a_cnf()
    else:
        gram_cnf = conversor.gramatica

    parser = CYKParser(gram_cnf, start_symbol=conversor.start_symbol)
    print("Listo.")
    return conversor, parser

def main():
    """Función principal del programa."""
    conversor, parser = inicializar()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()

        if opcion == '1':
            ver_gramatica_original(conversor)
        elif opcion == '2':
            ver_gramatica_cnf(conversor)
        elif opcion == '3':
            analizar_frase(parser)
        elif opcion == '4':
            analizar_desde_archivo(parser)
        elif opcion == '5':
            gram, start = cargar_gramatica_desde_archivo()
            if gram is not None:
                conversor, parser = inicializar(gram, start_symbol=start)
        elif opcion == '6':
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
