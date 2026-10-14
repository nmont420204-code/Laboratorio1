from telemetry import iter_events 
from estadistica import MedidasDescriptivas

def leer_datos(texto):
    datos = {}
    separar= texto.split(";")
    for pareja in separar:
        partir_pareja = pareja.split("=")
        datos[partir_pareja[0].strip()]= partir_pareja[1].strip()
    return datos

def clasificar(log_dir, reporte):
    puntaje=MedidasDescriptivas()
    duración=MedidasDescriptivas()
    daño=MedidasDescriptivas()
    for partes in iter_events(log_dir,reporte):
        evento=partes[2].strip()
        datos = leer_datos(partes[3])
        if evento == "SESSION_END":
            puntaje.agregar(float(datos["score"]))
            duración.agregar(float(datos["duration"]))
        elif evento=="DAMAGE_TAKEN":
           daño.agregar(float(datos["amount"]))
    return puntaje,duración,daño

def imprimir(nombre,o_md):
    print(nombre)
    print("conteo:",o_md.conteo)
    if o_md.conteo > 0:
        print("suma:",o_md.suma)
        print("máximo:",o_md.max)
        print("minimo:",o_md.min)
        print("rango:",o_md.rango())
        print("media:",o_md.media())
    if o_md.conteo > 1:
        print("varianza:",o_md.varianza())
        print("desviación:",o_md.desviación())
        if o_md.media() != 0:
            print("coef_variación:",o_md.coef_variación())

if __name__ == "__main__":
    reporte= {"Archivos procesados":0, "Lineas leidas": 0, "Eventos validos":0, "Lineas corruptas": 0}
    puntaje, duracion, dano = clasificar("logs", reporte)
    imprimir("PUNTAJE", puntaje)
    imprimir("DURACION", duracion)
    imprimir("DANO RECIBIDO", dano)  
    print (reporte)