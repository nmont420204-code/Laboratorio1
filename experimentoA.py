import time
import os
import glob
from telemetry import EscrituraBitacora

total= 100000
tam= [1, 10, 100, 1000] 

def limpiar_carpeta(carpeta):
    for archivo in glob.glob(os.path.join(carpeta, "*.log")): # borra los .log de una ejecución anterior
        os.remove(archivo)

def medir(N):
 carpeta = "exper_A" + str(N) 
 limpiar_carpeta(carpeta)

 t= EscrituraBitacora(carpeta, N)
  
 inicio = time.time()
 for i in range(total):
     linea = str(1717000000 + i) + ".000|S0001|ENEMY_KILL|type=slime;wave=1"
     t.escribir(linea)
     
 t.cerrar()
 fin = time.time()

 return fin - inicio 

resultados = []
for N in tam:
   segundos = medir(N)
   resultados.append((N, segundos))  # pareja (tamaño, tiempo)
   print("buffer", N, "->", round(segundos, 3), "s")

print(resultados)

    