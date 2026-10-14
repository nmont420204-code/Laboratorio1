import math
from telemetry import iter_events

# 8.2 Mediana, cuartiles y valores atípicos

def extraer_valores_variable(log_dir, variable="score"):
    valores = []
    reporte_dummy = {"Archivos procesados": 0, "Lineas leidas": 0, "Eventos validos": 0, "Lineas corruptas": 0, "Sesiones incompletas": 0}
    
    for evento in iter_events(log_dir, reporte_dummy):
        partes = evento[3].split(";")
        for p in partes:
            if "=" in p:
                k, v = p.split("=", 1)
                if k.strip() == variable:
                    try:
                        valores.append(float(v.strip()))
                    except ValueError:
                        pass
    valores.sort()
    return valores

def calcular_percentil(lista, p):
    if not lista:
        return 0.0
    n = len(lista)
    if n == 1:
        return lista[0]
    
    indice = (p / 100.0) * (n - 1)
    inferior = math.floor(indice)
    superior = math.ceil(indice)
    
    if inferior == superior:
        return lista[int(indice)]
    
    # Promedio entre los dos valores cercanos
    return (lista[int(inferior)] + lista[int(superior)]) / 2.0

def analizar_distribucion(log_dir, variable="score"):
    valores = extraer_valores_variable(log_dir, variable)
    if not valores:
        return {"Mediana": 0, "Q1": 0, "Q3": 0, "IQR": 0, "P90": 0}
    
    mediana = calcular_percentil(valores, 50)
    q1 = calcular_percentil(valores, 25)
    q3 = calcular_percentil(valores, 75)
    iqr = q3 - q1
    p90 = calcular_percentil(valores, 90)
    
    return {
        "Mediana": mediana,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "P90": p90
    }

def detectar_atipicos_iqr(valores):
    if not valores:
        return [], 0, 0
    
    vals = sorted(valores)
    q1 = calcular_percentil(vals, 25)
    q3 = calcular_percentil(vals, 75)
    iqr = q3 - q1
    
    lim_inf = q1 - (1.5 * iqr)
    lim_sup = q3 + (1.5 * iqr)
    
    atipicos = []
    for v in vals:
        if v < lim_inf or v > lim_sup:
            atipicos.append(v)
            
    return atipicos, lim_inf, lim_sup

def detectar_atipicos_zscore(valores, umbral=3.0):
    if not valores or len(valores) < 2:
        return []
    
    n = len(valores)
    suma = 0
    for x in valores:
        suma += x
    media = suma / n
    
    suma_cuadrados = 0
    for x in valores:
        suma_cuadrados += (x - media) ** 2
    
    varianza = suma_cuadrados / (n - 1)
    desv = math.sqrt(varianza)
    
    if desv == 0:
        return []
        
    atipicos = []
    for x in valores:
        z = abs(x - media) / desv
        if z > umbral:
            atipicos.append((x, z))
            
    return atipicos


# 8.4 Curva de progresión (Embudo de niveles)

def analizar_progresion(log_dir):
    sesiones_por_nivel = {}
    total_sesiones = 0
    reporte_dummy = {"Archivos procesados": 0, "Lineas leidas": 0, "Eventos validos": 0, "Lineas corruptas": 0, "Sesiones incompletas": 0}
    
    for evento in iter_events(log_dir, reporte_dummy):
        tipo = evento[2]
        sid = evento[1]
        
        if tipo == "SESSION_START":
            total_sesiones += 1
            if 1 not in sesiones_por_nivel:
                sesiones_por_nivel[1] = set()
            sesiones_por_nivel[1].add(sid)
            
        elif tipo == "LEVEL_UP":
            partes = evento[3].split(";")
            lvl = None
            for p in partes:
                if "=" in p:
                    k, v = p.split("=", 1)
                    if k.strip() == "level":
                        try:
                            lvl = int(float(v.strip()))
                        except:
                            pass
            if lvl:
                if lvl not in sesiones_por_nivel:
                    sesiones_por_nivel[lvl] = set()
                sesiones_por_nivel[lvl].add(sid)
                
    if total_sesiones == 0:
        return []
        
    niveles = sorted(sesiones_por_nivel.keys())
    resultado = []
    anterior = total_sesiones
    
    for i, lvl in enumerate(niveles):
        cant = len(sesiones_por_nivel[lvl])
        supervivencia = (cant / total_sesiones) * 100
        
        if i == 0:
            abandono = 0.0
        else:
            dif = anterior - cant
            abandono = (dif / anterior) * 100 if anterior > 0 else 0.0
            
        resultado.append({
            "nivel": lvl,
            "sesiones": cant,
            "supervivencia": supervivencia,
            "abandono": abandono
        })
        anterior = cant
        
    return resultado


# 8.5 Relación entre dos variables (Pearson)

def calcular_correlacion_pearson(log_dir, var_x="duration", var_y="score"):
    sesiones = {}
    reporte_dummy = {"Archivos procesados": 0, "Lineas leidas": 0, "Eventos validos": 0, "Lineas corruptas": 0, "Sesiones incompletas": 0}
    
    for evento in iter_events(log_dir, reporte_dummy):
        sid = evento[1]
        if sid not in sesiones:
            sesiones[sid] = {}
            
        partes = evento[3].split(";")
        for p in partes:
            if "=" in p:
                k, v = p.split("=", 1)
                k_trim = k.strip()
                if k_trim in [var_x, var_y]:
                    try:
                        sesiones[sid][k_trim] = float(v.strip())
                    except:
                        pass
                        
    n = 0
    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0
    sum_y2 = 0.0
    
    for sid in sesiones:
        if var_x in sesiones[sid] and var_y in sesiones[sid]:
            x = sesiones[sid][var_x]
            y = sesiones[sid][var_y]
            n += 1
            sum_x += x
            sum_y += y
            sum_xy += (x * y)
            sum_x2 += (x ** 2)
            sum_y2 += (y ** 2)
            
    if n < 2:
        return 0.0, n, sum_x, sum_y, sum_xy
        
    numerador = (n * sum_xy) - (sum_x * sum_y)
    denominador = math.sqrt(((n * sum_x2) - (sum_x ** 2)) * ((n * sum_y2) - (sum_y ** 2)))
    
    if denominador == 0:
        return 0.0, n, sum_x, sum_y, sum_xy
        
    r = numerador / denominador
    return r, n, sum_x, sum_y, sum_xy


# 8.6 Comparación por dificultad

def comparar_por_dificultad(log_dir):
    datos = {"easy": [], "normal": [], "hard": []}
    sesion_diff = {}
    sesion_score = {}
    reporte_dummy = {"Archivos procesados": 0, "Lineas leidas": 0, "Eventos validos": 0, "Lineas corruptas": 0, "Sesiones incompletas": 0}
    
    for evento in iter_events(log_dir, reporte_dummy):
        sid = evento[1]
        tipo = evento[2]
        partes = evento[3].split(";")
        
        if tipo == "SESSION_START":
            for p in partes:
                if "=" in p:
                    k, v = p.split("=", 1)
                    if k.strip() == "difficulty":
                        sesion_diff[sid] = v.strip().lower()
        elif tipo == "SESSION_END":
            for p in partes:
                if "=" in p:
                    k, v = p.split("=", 1)
                    if k.strip() == "score":
                        try:
                            sesion_score[sid] = float(v.strip())
                        except:
                            pass
                            
    for sid in sesion_score:
        d = sesion_diff.get(sid, "normal")
        if d in datos:
            datos[d].append(sesion_score[sid])
            
    resultados = {}
    for d in datos:
        lista = datos[d]
        n = len(lista)
        if n > 0:
            suma = 0
            for x in lista:
                suma += x
            media = suma / n
            
            suma_c = 0
            for x in lista:
                suma_c += (x - media) ** 2
            
            varianza = suma_c / (n - 1) if n > 1 else 0.0
            desv = math.sqrt(varianza)
        else:
            media = 0.0
            desv = 0.0
            
        resultados[d] = {"n": n, "media": media, "desv": desv}
        
    dif = resultados["hard"]["media"] - resultados["easy"]["media"]
    resultados["diferencia_hard_easy"] = dif
    return resultados


# 8.7 Resumen de costo en memoria

def obtener_tabla_costo_memoria():
    return [
        {"estadistica": "media, mínimo, máximo", "una_sola_pasada": "Sí", "memoria": "O(1)", "por_que": "Solo usamos variables contadoras simples."},
        {"estadistica": "varianza, desviación, CV", "una_sola_pasada": "Sí", "memoria": "O(1)", "por_que": "Acumulamos sumas y sumas al cuadrado."},
        {"estadistica": "correlación de Pearson", "una_sola_pasada": "Sí", "memoria": "O(S)", "por_que": "Guardamos los valores por cada sesión."},
        {"estadistica": "tabla de frecuencias", "una_sola_pasada": "Sí", "memoria": "O(C)", "por_que": "Usamos un diccionario según las categorías."},
        {"estadistica": "histograma de k intervalos", "una_sola_pasada": "No", "memoria": "O(N)", "por_que": "Necesitamos recorrer y agrupar por rangos."},
        {"estadistica": "mediana, cuartiles, P90", "una_sola_pasada": "No", "memoria": "O(N)", "por_que": "Obliga a ordenar todos los datos para hallar posiciones."}
    ]
    


# Para el panel de estadísticas (pantalla_stats.py)

def cinco_numeros(valores):
    """Devuelve: bigote_inf, q1, mediana, q3, bigote_sup, atipicos."""
    vals = sorted(valores)
    q1 = calcular_percentil(vals, 25)
    med = calcular_percentil(vals, 50)
    q3 = calcular_percentil(vals, 75)
    atipicos, lim_inf, lim_sup = detectar_atipicos_iqr(vals)
    dentro = [v for v in vals if lim_inf <= v <= lim_sup]
    return min(dentro), q1, med, q3, max(dentro), atipicos


def interpretar_r(r, n):
    if n < 2:
        return "No hay datos suficientes para calcular r."
    fuerza = "débil" if abs(r) < 0.3 else "moderada" if abs(r) < 0.7 else "fuerte"
    sentido = "positiva" if r > 0 else "negativa"
    return f"Correlación {fuerza} y {sentido} (r = {r:.2f})."