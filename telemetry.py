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


def iter_events(log_dir, reporte): #recibe el diccionario como parametro 
    sesiones = {}
    incomp = 0 
    for path in sorted(archivos_de(log_dir)):
        reporte["Archivos procesados"] +=1
        with open(path, "r", encoding="utf-8") as f: #archivo para lectura "r"
           
            for linea in f:
                 reporte["Lineas leidas"] +=1
                 evento = parse_line(linea)
                 if evento is not None:
                    reporte["Eventos validos"] +=1
                    if evento[2] == "SESSION_START": 
                       sesiones[evento[1]] = False
                    else:
                       if evento[2] == "SESSION_END":
                          sesiones[evento[1]] = True
                       
                    yield evento #generador 
                 else:
                     reporte["Lineas corruptas"] +=1   
                                   
    for id_sesion in sesiones:                       
       if sesiones[id_sesion] == False:               
         incomp += 1
    reporte["Sesiones incompletas"] = incomp  
    
class EscrituraBitacora:            
   def __init__(self, log_dir, N, umbral=512000):
      os.makedirs(log_dir ,exist_ok=True) #crea la carpeta y no ocurre nada si ya existe
      self.log_dir = log_dir
      self.size = N
      self.umbral = umbral 
      self.buffer = []
      self.numero_archivo = 1
      self.abrir_archivo(self.numero_archivo)


   def orden_numeros_archivo(self, numero):  
         if numero <10:
            texto = "00" + str(numero) #001, 002...
         else:
            if numero <100:
               texto = "0" + str(numero) #010, 011...
            else:
               texto = str(numero)
         nombre_archivo = "events_" + texto + ".log"      
         return nombre_archivo    

   def abrir_archivo(self, numero):
      nom = self.orden_numeros_archivo(numero)
      self.path = os.path.join(self.log_dir, nom)
      self.archivo =  open(self.path, "a", encoding="utf-8") 


   def vaciar(self):
      for linea in self.buffer:
         self.archivo.write(linea + "\n")  # \n para separar los eventos 

      self.archivo.flush()   
      self.buffer = []
      self.rotacion()

   def escribir(self, linea):    
      self.buffer.append(linea)
      if self.size <= len(self.buffer):
         self.vaciar() #llama a la funcion 

   def cerrar(self):
     self.vaciar()
     self.archivo.close()     

   def rotacion(self):
      t = os.path.getsize(self.path)
      if t > self.umbral:  
        self.archivo.close()
        self.numero_archivo += 1 
        self.abrir_archivo(self.numero_archivo )


def reporte_datos():
   reporte = {
     "Archivos procesados": 0  , #contadores incian en 0 
     "Lineas leidas":  0       ,
     "Eventos validos":  0     ,
     "Lineas corruptas":  0    ,
     "Sesiones incompletas":0  

   }
   return reporte 
