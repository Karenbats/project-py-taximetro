
import time
import logging
import json
from pathlib import Path
import csv
from datetime import datetime

CARPETA = Path(__file__).parent
CONFIG = CARPETA / "config.json"
LOG = CARPETA / "taximetro.log"
HISTORIAL = CARPETA / "historial.csv"


AYUDA = """
Taxímetro digital
  i  iniciar carrera (empieza PARADO)
  p  el taxi está parado
  m  el taxi está en movimiento
  f  finalizar la carrera y ver el total
  h  ver el historial de carreras de hoy
  a  ver esta ayuda
  s  salir
  
"""

TARIFAS_POR_DEFECTO = {
    "tarifa_parado": 0.02,
    "tarifa_movimiento": 0.05
}

# Configuración del registro
log = logging.getLogger("taximetro")


def configurar_log():
    logging.basicConfig(
        filename=LOG,
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s"
    )

def guardar_carrera(inicio, duracion, importe, ruta=HISTORIAL):
    nuevo_archivo = not ruta.exists()

    with open(ruta, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)

        if nuevo_archivo:
            escritor.writerow(["fecha", "hora", "duracion_s", "importe"])

        escritor.writerow([
            inicio.strftime("%Y-%m-%d"),
            inicio.strftime("%H:%M:%S"),
            round(duracion),
            f"{importe:.2f}"
        ])

def carreras_de_hoy(ruta=HISTORIAL):
    if not ruta.exists():
        return []

    hoy = datetime.now().strftime("%Y-%m-%d")

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        carreras = []
        for fila in lector:
            if fila["fecha"] == hoy:
                carreras.append(fila)
    return carreras

def cargar_tarifas(ruta=CONFIG):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        tarifas = {
            "parado": float(datos["tarifa_parado"]),
            "movimiento": float(datos["tarifa_movimiento"])
        }

        log.info("Tarifas cargadas desde %s", ruta)
        return tarifas

    except (OSError, KeyError, ValueError):
        log.warning("No se pudo cargar la configuración. Se usan las tarifas por defecto.")
        return {
            "parado": TARIFAS_POR_DEFECTO["tarifa_parado"],
            "movimiento": TARIFAS_POR_DEFECTO["tarifa_movimiento"]
        }

def tarifa(estado, tarifas):
    if estado == "parado":
        return tarifas["parado"]
    elif estado == "movimiento":
        return tarifas["movimiento"]


def cerrar_tramo(carrera, tarifas):
    ahora = time.monotonic()
    segundos = ahora - carrera["desde"]
    importe = segundos * tarifa(carrera["estado"], tarifas)

    carrera["importe"] += importe
    carrera["desde"] = ahora


def main():
    configurar_log()
    log.info("Arranque del taxímetro")

    tarifas = cargar_tarifas()

    print(AYUDA)

    carrera = None

    while True:
        orden = input("> ").strip().lower()

        if orden == "i":
            if carrera is not None:
                print("Ya hay una carrera en marcha.")
                continue

            carrera = {
                "estado": "parado",
                "desde": time.monotonic(),
                "importe": 0.0,
                "inicio": datetime.now(),
                "inicio_mono": time.monotonic()
            }

            print("Carrera iniciada. El taxi está PARADO.")
            print(carrera)
            log.info("Carrera iniciada")

        elif orden == "p":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera, tarifas)
            carrera["estado"] = "parado"
            print("El taxi está PARADO.")

            log.info(
                "Cambio de estado a parado (%.2f € acumulados)",
                carrera["importe"]
            )

        elif orden == "m":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera, tarifas)
            carrera["estado"] = "movimiento"
            print("El taxi está EN MOVIMIENTO.")

            log.info(
                "Cambio de estado a movimiento (%.2f € acumulados)",
                carrera["importe"]
            )

        elif orden == "f":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera, tarifas)

            duracion = time.monotonic() - carrera["inicio_mono"]
            guardar_carrera(carrera["inicio"], duracion, carrera["importe"])

            log.info(
                "Carrera guardada: %d s, %.2f €", 
                round(duracion), 
                carrera["importe"]
             )
            
            print(f"Importe total: {carrera['importe']:.2f} €")

            log.info(
                "Carrera finalizada: %.2f €",
                carrera["importe"]
            )

            carrera = None

        elif orden == "h":
            carreras = carreras_de_hoy()

            if not carreras:
                print("Hoy no hay carreras registradas.")
            else:
                total = 0

            for carrera in carreras:
                duracion = int(carrera["duracion_s"])
                importe = float(carrera["importe"])
                total += importe

                print(f"  {carrera['hora']}  {duracion:>5} s  {importe:>8.2f} €")

            print(f"Total del día: {total:.2f} €")

        elif orden == "a":
            print(AYUDA)

        elif orden == "s":
            log.info("Cierre del taxímetro")
            print("Hasta luego.")
            break

        else:
            print("Orden desconocida. Escribe 'a' para ver la ayuda.")
            log.warning("Orden desconocida: '%s'", orden)


if __name__ == "__main__":
    main()
