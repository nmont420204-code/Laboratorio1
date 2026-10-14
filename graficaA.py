import math
import pygame
import os

repeticiones = {
    1:    [2.043, 2.134, 2.119, 2.049, 2.038],
    10:   [0.298, 0.281, 0.349, 0.299, 0.341],
    100:  [0.109, 0.093, 0.116, 0.129, 0.132],
    1000: [0.101, 0.087, 0.088, 0.093, 0.097],
}

datos = []   
for n in repeticiones:
    t = repeticiones[n]
    datos.append((n, sum(t) / len(t), min(t), max(t)))



pygame.init()
ANCHO, ALTO = 800, 500
superficie = pygame.Surface((ANCHO, ALTO))
superficie.fill((255, 255, 255))

MARGEN_IZQ, MARGEN_INF, MARGEN_SUP, MARGEN_DER = 90, 80, 60, 40
x0 = MARGEN_IZQ                
y0 = ALTO - MARGEN_INF
ancho_graf = ANCHO - MARGEN_IZQ - MARGEN_DER
alto_graf = ALTO - MARGEN_SUP - MARGEN_INF    


y_max = 2.5     

def px(n):      
    return x0 + math.log10(n) / 3 * ancho_graf

def py(t):      
    return y0 - t / y_max * alto_graf


NEGRO = (20, 20, 25)
pygame.draw.line(superficie, NEGRO, (x0, y0), (x0 + ancho_graf, y0), 2)   # eje X
pygame.draw.line(superficie, NEGRO, (x0, y0), (x0, y0 - alto_graf), 2)    # eje Y

AZUL, ROJO = (40, 100, 200), (200, 50, 50)

puntos = []
for n, prom, mini, maxi in datos:
    x = px(n)
    pygame.draw.line(superficie, ROJO, (x, py(mini)), (x, py(maxi)), 3)   
    puntos.append((x, py(prom)))

for i in range(len(puntos) - 1):
    pygame.draw.line(superficie, AZUL, puntos[i], puntos[i + 1], 3)       
for punto in puntos:
    pygame.draw.circle(superficie, AZUL, punto, 6)                        

    fuente = pygame.font.Font(None, 24)

for n, prom, mini, maxi in datos:                      
    texto = fuente.render(str(n), True, NEGRO)
    superficie.blit(texto, (px(n) - texto.get_width() / 2, y0 + 10))

for k in range(6):                                      
    valor = y_max * k / 5
    texto = fuente.render(f"{valor:.1f}", True, NEGRO)
    superficie.blit(texto, (x0 - texto.get_width() - 8, py(valor) - 8))

titulo = fuente.render("Experimento A: tiempo de escritura vs tamano de buffer", True, NEGRO)
superficie.blit(titulo, ((ANCHO - titulo.get_width()) / 2, 15))

rotulo_x = fuente.render("Tamano de buffer N", True, NEGRO)
superficie.blit(rotulo_x, (x0 + (ancho_graf - rotulo_x.get_width()) / 2, ALTO - 35))

rotulo_y = pygame.transform.rotate(fuente.render("Tiempo (s)", True, NEGRO), 90)
superficie.blit(rotulo_y, (20, y0 - alto_graf / 2 - rotulo_y.get_height() / 2))

for i in range(len(datos)):                             
    etiqueta = fuente.render(f"{datos[i][1]:.3f}", True, AZUL)
    superficie.blit(etiqueta, (puntos[i][0] + 10, puntos[i][1] - 24))

os.makedirs("experimentoA", exist_ok=True)
pygame.image.save(superficie, "experimentoA/figura_a.png")