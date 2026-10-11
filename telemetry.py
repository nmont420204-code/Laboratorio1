import glob
import os

def parse_line(linea):
    linea_limpia = linea.strip()
    partes = linea_limpia.split("|")

    if len(partes) !=4:
         return None
    try:
     float(partes[0]) #texto se puede convertir a decimal?       
    except ValueError:
     return None
    
    sesion = partes[1].strip()
    evento = partes[2].strip()
    if sesion == "" or evento == "":
       return None

    parejas = partes[3].split(";") #calve=valor;clave=valor
    for pareja in parejas: #recorrer la lista
      
      clave_valor = pareja.split("=")
      if len(clave_valor) !=2: #verificar que tenga dos elementos 
         return None
      clave = clave_valor[0].strip()
      valor = clave_valor[1].strip()
      if clave == "" or valor == "":
         return None

      if clave == "score" or clave == "level" or clave == "duration" or clave == "wave" or clave== "amount" or clave == "time":
       try:
        float(valor)  
       except ValueError:
        return None
    
    return partes #si todo esta bien muestra la lista


def archivos_de(log_dir):
   x = os.path.join(log_dir, "*.log") #archivo que termine en .log
   archivos= glob.glob(x) #busca los archivos que coinciden con el patron
   return archivos
   
def iter_events(log_dir):
    for path in sorted(archivos_de(log_dir)):
       
        with open(path, "r", encoding="utf-8") as f: #archivo para lectura "r"
           
            for linea in f:
                 evento = parse_line(linea)
                 if evento is not None:
                    yield evento #generador 

class EscrituraBitacora:            
   def __init__(self, log_dir, N ):
      os.makedirs(log_dir ,exist_ok=True) #crea la carpeta y no ocurre nada si ya existe
      path = os.path.join(log_dir, "events_001.log")
      self.archivo =  open(path, "a", encoding="utf-8") 

      self.size = N
      self.buffer = []
   def vaciar(self):
      for linea in self.buffer:
         self.archivo.write(linea + "\n")  # \n para separar los eventos 

      self.archivo.flush()   
      self.buffer = []

   def escribir(self, linea):    
      self.buffer.append(linea)
      if self.size <= len(self.buffer):
         self.vaciar() #llama a la funcion 
         


         



     