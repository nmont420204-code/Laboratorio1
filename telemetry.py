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


  
        
