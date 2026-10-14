import asyncio
import pygame

from pantalla_stats import PantallaEstadisticas


async def main():
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    stats = PantallaEstadisticas("logs")
    corriendo = True
    while corriendo:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                corriendo = False
            if stats.manejar_evento(ev) == "salir":
                corriendo = False
        stats.dibujar(pantalla)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())