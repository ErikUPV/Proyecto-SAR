import os
import sys

def comparar_archivos_directorios(dir1, dir2):
    archivos_dir1 = os.listdir(dir1)
    archivos_dir2 = os.listdir(dir2)

    # Comparar archivos uno a uno
    for archivo1, archivo2 in zip(archivos_dir1, archivos_dir2):
        ruta_archivo1 = os.path.join(dir1, archivo1)
        ruta_archivo2 = os.path.join(dir2, archivo2)
        comparar_archivos(ruta_archivo1, ruta_archivo2)

def comparar_archivos(archivo1, archivo2):
    with open(archivo1, 'r', encoding='utf-8') as f1, open(archivo2, 'r', encoding='utf-8') as f2:
        for num_linea, (linea1, linea2) in enumerate(zip(f1, f2), start=1):
            if linea1 != linea2:
                print(f'DIFERENCIA ENTRE LOS ARCHIVOS {archivo1} y {archivo2}')
                print(f'Diferencia encontrada en la línea {num_linea}:')
                print(f'Archivo 1: {linea1.strip()}')
                print(f'Archivo 2: {linea2.strip()}')
                print('')
                break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usos:\npython script.py directorio1 directorio2\n python script.py archivo1 archivo1")
    else:
        ruta1 = sys.argv[1]
        ruta2 = sys.argv[2]
        if os.path.isfile(ruta1) and os.path.isfile(ruta2):
            comparar_archivos(ruta1, ruta2)
        elif os.path.isdir(ruta1) and os.path.isdir(ruta2):
            comparar_archivos_directorios(ruta1, ruta2)
        else:
            print("Usos:\npython script.py directorio1 directorio2\n python script.py archivo1 archivo1")
