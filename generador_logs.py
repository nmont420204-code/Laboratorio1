import time
import os

def crear_bitacora_simulada(cantidad_eventos, ruta_archivo="bitacora_prueba.log"):
    inicio = time.time()
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        for i in range(cantidad_eventos):
            f.write(f"1717000000.000|S0001|ENEMY_KILL|type=slime;wave={i%5 + 1}\n")
    tiempo_total = time.time() - inicio
    tamaño_bytes = os.path.getsize(ruta_archivo)
    return tiempo_total, tamaño_bytes