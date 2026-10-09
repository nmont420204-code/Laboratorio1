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

    x = partes[1].strip()
    y = partes[2].strip()

    if x == "" or y == "":
       return None

    
    #if len(partes) == 4:
    #return partes 






  
        
