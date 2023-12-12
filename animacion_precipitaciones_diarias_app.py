import os
import imageio

def crear_animacion(carpeta_entrada, nombre_salida, velocidad=1, starting=""):
    imagenes = []
    
    # Obtener la lista de archivos en la carpeta de entrada
    archivos = os.listdir(carpeta_entrada)
    
    # Filtrar los archivos para incluir solo los PNG
    archivos_png = [archivo for archivo in archivos if archivo.lower().endswith(".png") and archivo.startswith(starting)]

    # Ordenar los archivos alfabéticamente
    #archivos_png.sort()
    print(archivos_png)

    # Leer cada imagen y agregarla a la lista
    for archivo_png in archivos_png:
        ruta_completa = os.path.join(carpeta_entrada, archivo_png)
        imagen = imageio.imread(ruta_completa)
        imagenes.append(imagen)

    # Crear la animación
    ruta_salida = f"{nombre_salida}.gif"
    imageio.mimsave(ruta_salida, imagenes, duration=velocidad)

    print(f"Animación creada con éxito: {ruta_salida}")

