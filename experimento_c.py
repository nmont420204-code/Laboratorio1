import time
import tracemalloc
import os
from generador_logs import crear_bitacora_simulada
cantidades = [5000, 50000, 100000]
archivo_log = "bitacora_prueba.log"

print(f"{'Eventos':<10} | {'Tamaño (KB)':<12} | {'T. Esc. (s)':<12} | {'T. Lec. (s)':<12} | {'Eventos/s':<12} | {'Mem. Perezosa (KB)':<20} | {'Mem. Lista (KB)':<15}")
print("-" * 105)

for cantidad in cantidades:
    t_escritura, tamaño_bytes = crear_bitacora_simulada(cantidad, archivo_log)
    tamaño_kb = tamaño_bytes / 1024

    tracemalloc.start()
    inicio_perezosa = time.time()
    
    with open(archivo_log, "r", encoding="utf-8") as f:
        for linea in f:
            pass
            
    t_lectura = time.time() - inicio_perezosa
    _, mem_perezosa_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    eventos_por_segundo = cantidad / t_lectura if t_lectura > 0 else 0
    mem_perezosa_kb = mem_perezosa_bytes / 1024

    tracemalloc.start()
    with open(archivo_log, "r", encoding="utf-8") as f:
        lista_eventos = f.readlines()
        
    _, mem_lista_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    mem_lista_kb = mem_lista_bytes / 1024

    print(f"{cantidad:<10} | {tamaño_kb:<12.2f} | {t_escritura:<12.4f} | {t_lectura:<12.4f} | {eventos_por_segundo:<12.0f} | {mem_perezosa_kb:<20.2f} | {mem_lista_kb:<15.2f}")

if os.path.exists(archivo_log):
    os.remove(archivo_log)