from telemetry import iter_events
from estadistica import MedidasDescriptivas
from reporte_md import leer_datos,nuevo_reporte

K=8

def contar(valores):
    conteos ={}
    for v in valores:
        conteos[v]=conteos.get(v,0)+1
    return conteos


def tabla_frencuencias(conteos):
    total =sum(conteos.values())
    if total == 0 :
        return [],0,None
    orden= sorted(conteos.items(), key= lambda par: (-par[1],par[0]))
    filas=[]
    acumulado= 0 
    for categoria, f in orden:
        acumulado += f 
        filas.append((categoria,f,100*f/ total, 100*acumulado / total))
    moda =orden [0][0]
    return filas,total,moda


def imprimir_tabla(titulo,conteos):
    filas,total,moda = tabla_frencuencias(conteos)
    linea = "-"*42
    print(f"{titulo:<18}{'f':>6}{'f%':>9}{'F%':>9}")
    print(linea)
    for categoria, f, fp,Fp in filas:
        print(f"{categoria:<18}{f:>6}{fp:>8.1f}%{Fp:>8.1f}%")
    print(linea)
    print(f"{'Total':<18}{total:>6}")
    print(f"Moda:{moda}")


def histograma(valores, minimo, maximo, k=K):
    conteos = [0] * k
    ancho = (maximo - minimo) / k
    for x in valores:
        if ancho == 0:
            i = 0                    
        else:
            i = int((x - minimo) / ancho)
            if i >= k:                 
                i = k - 1
        conteos[i] += 1
    return conteos, ancho


def imprimir_histograma(titulo, conteos, minimo, ancho):
    total = sum(conteos)
    print(titulo)
    for i, f in enumerate(conteos):
        a = minimo + i * ancho
        b = a + ancho
        cierre = "]" if i == len(conteos) - 1 else ")"
        barra = "#" * f
        pct = 100 * f / total if total else 0
        print(f"[{a:>9.1f}, {b:>9.1f}{cierre} {f:>4} {pct:>6.1f}%  {barra}")


def leer_eventos(log_dir, reporte):
    causas, enemigos, puntajes = [], [], []
    for partes in iter_events(log_dir, reporte):
        evento = partes[2].strip()
        datos = leer_datos(partes[3])
        if evento == "PLAYER_DEATH":
            causas.append(datos["cause"])
        elif evento == "ENEMY_KILL":
            enemigos.append(datos["type"])
        elif evento == "SESSION_END":
            puntajes.append(float(datos["score"]))
    return causas, enemigos, puntajes


if __name__ == "__main__":
    reporte = nuevo_reporte()
    causas, enemigos, puntajes = leer_eventos("logs", reporte)
    imprimir_tabla("CAUSAS DE MUERTE", contar(causas))
    print()
    imprimir_tabla("TIPO DE ENEMIGO", contar(enemigos))
    print()
    if puntajes:
        m = MedidasDescriptivas()
        for p in puntajes:          
            m.agregar(p)
        conteos, ancho = histograma(puntajes, m.min, m.max)
        imprimir_histograma("HISTOGRAMA DE PUNTAJE (k = 8)", conteos, m.min, ancho)
