import time

from telemetry import iter_events, reporte_datos


def medir_lectura(log_dir, repeticiones=3):
    mejor = None
    eventos = 0
    for _ in range(repeticiones):
        reporte = reporte_datos()
        inicio = time.perf_counter()
        eventos = 0
        for _evento in iter_events(log_dir, reporte):
            eventos += 1
        total = time.perf_counter() - inicio
        if mejor is None or total < mejor:
            mejor = total
    por_segundo = eventos / mejor
    us_por_linea = (mejor / eventos) * 1_000_000
    return eventos, mejor, por_segundo, us_por_linea


if __name__ == "__main__":
    carpetas = ["logs_5000", "logs_50000", "logs_100000"]
    print(f"{'Carpeta':<14}{'Eventos':>9}{'Total (s)':>12}{'Ev/s':>12}{'us/linea':>12}")
    print("-" * 59)
    for carpeta in carpetas:
        n, t, eps, us = medir_lectura(carpeta)
        print(f"{carpeta:<14}{n:>9}{t:>12.4f}{eps:>12.0f}{us:>12.2f}")