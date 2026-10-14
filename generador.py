import os
import random
import shutil

from telemetry import EscrituraBitacora

CAUSAS = ["slime", "arrow_trap", "boss", "fall"]
ENEMIGOS = ["slime", "cyclops"]


def generar_bitacora(log_dir, n_eventos, semilla=42, tam_buffer=500):
    """Escribe exactamente n_eventos lineas validas en log_dir."""
    random.seed(semilla)
    if os.path.isdir(log_dir):
        shutil.rmtree(log_dir)  # EscrituraBitacora abre en modo "a": hay que limpiar

    escritor = EscrituraBitacora(log_dir, tam_buffer)
    escritos = 0
    t = 0.0
    n_sesion = 0

    while escritos < n_eventos:
        n_sesion += 1
        sid = f"S{n_sesion:06d}"
        eventos = [("SESSION_START", "level=1")]
        for _ in range(random.randint(3, 12)):
            eventos.append(("ENEMY_KILL", f"type={random.choice(ENEMIGOS)}"))
        eventos.append(("PLAYER_DEATH", f"cause={random.choice(CAUSAS)}"))
        eventos.append(("SESSION_END",
                        f"score={random.randint(0, 1600)};duration={random.uniform(5, 35):.1f}"))

        for nombre, datos in eventos:
            if escritos == n_eventos:
                break
            t += random.uniform(0.1, 2.0)
            escritor.escribir(f"{t:.2f}|{sid}|{nombre}|{datos}")
            escritos += 1

    escritor.cerrar()


if __name__ == "__main__":
    for n in (5000, 50000, 100000):
        generar_bitacora(f"logs_{n}", n)