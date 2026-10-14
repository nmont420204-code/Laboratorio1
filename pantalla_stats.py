import pygame

from estadistica import MedidasDescriptivas
from frecuencias import histograma
from statistics_engine import (
    extraer_valores_variable,
    calcular_percentil,
    cinco_numeros,
    calcular_correlacion_pearson,
    interpretar_r,
)
from telemetry import iter_events

K = 8
PESTANAS = ["Resumen", "Distribución", "Relación"]
VARIABLES = ["puntaje", "duracion", "dano"]
CLAVES = {"puntaje": "score", "duracion": "duration", "dano": "amount"}
PARES = [("duration", "score"), ("level", "score")]


def pares_por_sesion(log_dir, var_x, var_y):
    sesiones = {}
    reporte = {"Archivos procesados": 0, "Lineas leidas": 0, "Eventos validos": 0,
               "Lineas corruptas": 0, "Sesiones incompletas": 0}
    for evento in iter_events(log_dir, reporte):
        sid = evento[1]
        for p in evento[3].split(";"):
            if "=" in p:
                k, v = p.split("=", 1)
                k = k.strip()
                if k in (var_x, var_y):
                    try:
                        sesiones.setdefault(sid, {})[k] = float(v.strip())
                    except ValueError:
                        pass
    xs, ys = [], []
    for d in sesiones.values():
        if var_x in d and var_y in d:
            xs.append(d[var_x])
            ys.append(d[var_y])
    return xs, ys


class PantallaEstadisticas:
    def __init__(self, log_dir="logs"):
        self.fuente = pygame.font.Font(None, 28)
        self.fuente_chica = pygame.font.Font(None, 22)
        self.pestana = 0
        self.var = 0
        self.par = 0
        self.datos = {nombre: extraer_valores_variable(log_dir, clave)
                      for nombre, clave in CLAVES.items()}
        self.relaciones = []
        for vx, vy in PARES:
            xs, ys = pares_por_sesion(log_dir, vx, vy)
            r, n = calcular_correlacion_pearson(log_dir, vx, vy)[:2]
            self.relaciones.append((xs, ys, r, n))

    def manejar_evento(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return "salir"
            if ev.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.pestana = ev.key - pygame.K_1
            elif ev.key in (pygame.K_RIGHT, pygame.K_LEFT):
                paso = 1 if ev.key == pygame.K_RIGHT else -1
                if self.pestana == 2:
                    self.par = (self.par + paso) % len(PARES)
                else:
                    self.var = (self.var + paso) % len(VARIABLES)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(PESTANAS)):
                if self._rect_pestana(i).collidepoint(ev.pos):
                    self.pestana = i
        return None

    def _rect_pestana(self, i):
        return pygame.Rect(10 + i * 160, 10, 150, 36)

    def _texto(self, p, s, pos, color=(255, 255, 255), grande=False):
        f = self.fuente if grande else self.fuente_chica
        p.blit(f.render(s, True, color), pos)

    def dibujar(self, pantalla):
        pantalla.fill((25, 25, 35))
        for i, nombre in enumerate(PESTANAS):
            r = self._rect_pestana(i)
            color = (70, 110, 180) if i == self.pestana else (50, 50, 70)
            pygame.draw.rect(pantalla, color, r, border_radius=6)
            self._texto(pantalla, f"{i + 1}. {nombre}", (r.x + 10, r.y + 10))
        if self.pestana == 0:
            self._resumen(pantalla)
        elif self.pestana == 1:
            self._distribucion(pantalla)
        else:
            self._relacion(pantalla)
        self._texto(pantalla, "Esc: volver   1-3: pestañas   flechas: cambiar variable",
                    (20, 575), (150, 150, 150))

    def _resumen(self, p):
        nombre = VARIABLES[self.var]
        valores = self.datos[nombre]
        self._texto(p, f"Variable: {nombre}", (20, 65), (255, 220, 120), True)
        if len(valores) < 2:
            self._texto(p, "Sin datos suficientes", (20, 110), grande=True)
            return
        m = MedidasDescriptivas()
        for v in valores:
            m.agregar(v)
        media = m.media()
        desv = m.varianza() ** 0.5
        cv = desv / media if media else 0
        lineas = [
            f"n:         {m.conteo}",
            f"media:     {media:.2f}",
            f"mediana:   {calcular_percentil(valores, 50):.2f}",
            f"desv.est:  {desv:.2f}",
            f"CV:        {cv:.3f}",
            f"mínimo:    {m.min}",
            f"máximo:    {m.max}",
            f"P90:       {calcular_percentil(valores, 90):.2f}",
        ]
        for i, linea in enumerate(lineas):
            self._texto(p, linea, (20, 110 + i * 34), grande=True)

    def _distribucion(self, p):
        nombre = VARIABLES[self.var]
        valores = self.datos[nombre]
        self._texto(p, f"Distribución de {nombre}", (20, 65), (255, 220, 120), True)
        if len(valores) < 2:
            self._texto(p, "Sin datos suficientes", (20, 110), grande=True)
            return

        mn, mx = min(valores), max(valores)
        conteos, ancho = histograma(valores, mn, mx, K)
        izq, der, base, alto = 70, 760, 340, 190

        def x_de(v):
            if mx == mn:
                return (izq + der) // 2
            return izq + (v - mn) / (mx - mn) * (der - izq)

        mayor = max(conteos)
        for i, f in enumerate(conteos):
            x0, x1 = x_de(mn + i * ancho), x_de(mn + (i + 1) * ancho)
            h = alto * f / mayor
            if f:
                pygame.draw.rect(p, (90, 150, 220), (x0 + 1, base - h, max(x1 - x0 - 2, 1), h))
                self._texto(p, str(f), (x0 + 4, base - h - 18))
        pygame.draw.line(p, (200, 200, 200), (izq, base), (der, base), 2)
        pygame.draw.line(p, (200, 200, 200), (izq, base - alto), (izq, base), 2)
        for i in range(K + 1):
            v = mn + i * ancho
            self._texto(p, f"{v:.0f}" if mx - mn >= 20 else f"{v:.1f}", (x_de(v) - 12, base + 6))
        self._texto(p, "frecuencia", (5, base - alto - 20))

        b_inf, q1, med, q3, b_sup, atip = cinco_numeros(valores)
        cy = 450
        blanco = (230, 230, 230)
        pygame.draw.line(p, blanco, (x_de(b_inf), cy), (x_de(q1), cy), 2)
        pygame.draw.line(p, blanco, (x_de(q3), cy), (x_de(b_sup), cy), 2)
        pygame.draw.line(p, blanco, (x_de(b_inf), cy - 8), (x_de(b_inf), cy + 8), 2)
        pygame.draw.line(p, blanco, (x_de(b_sup), cy - 8), (x_de(b_sup), cy + 8), 2)
        pygame.draw.rect(p, blanco, (x_de(q1), cy - 20, max(x_de(q3) - x_de(q1), 1), 40), 2)
        pygame.draw.line(p, (255, 180, 80), (x_de(med), cy - 20), (x_de(med), cy + 20), 3)
        for a in atip:
            pygame.draw.circle(p, (240, 90, 90), (int(x_de(a)), cy), 5, 2)
        self._texto(p, "Q1", (x_de(q1) - 8, cy + 26))
        self._texto(p, "mediana", (x_de(med) - 25, cy + 46))
        self._texto(p, "Q3", (x_de(q3) - 8, cy + 26))
        if atip:
            self._texto(p, "atípico", (x_de(atip[0]) - 20, cy + 26), (240, 90, 90))

    def _relacion(self, p):
        ex, ey = PARES[self.par]
        xs, ys, r, n = self.relaciones[self.par]
        self._texto(p, f"{ex} (x) vs {ey} (y)", (20, 65), (255, 220, 120), True)
        if len(xs) < 2:
            self._texto(p, "Sin datos suficientes", (20, 110), grande=True)
            return
        izq, der, arr, aba = 90, 740, 110, 410
        mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)

        def px(v):
            return izq if mxx == mnx else izq + (v - mnx) / (mxx - mnx) * (der - izq)

        def py(v):
            return aba if mxy == mny else aba - (v - mny) / (mxy - mny) * (aba - arr)

        pygame.draw.line(p, (200, 200, 200), (izq, aba), (der, aba), 2)
        pygame.draw.line(p, (200, 200, 200), (izq, arr), (izq, aba), 2)
        for a, b in zip(xs, ys):
            pygame.draw.circle(p, (90, 150, 220), (int(px(a)), int(py(b))), 5)
        self._texto(p, f"{mnx:g}", (izq - 5, aba + 6))
        self._texto(p, f"{mxx:g}", (der - 10, aba + 6))
        self._texto(p, ex, ((izq + der) // 2 - 20, aba + 26))
        self._texto(p, f"{mxy:g}", (30, arr - 5))
        self._texto(p, f"{mny:g}", (30, aba - 5))
        self._texto(p, ey, (30, arr - 28))
        self._texto(p, f"n = {n}   " + interpretar_r(r, n), (20, 490), grande=True)