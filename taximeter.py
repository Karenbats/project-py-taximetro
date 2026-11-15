import time

AYUDA = """
Taxímetro digital
  i  iniciar carrera (empieza PARADO)
  p  el taxi está parado
  m  el taxi está en movimiento
  f  finalizar la carrera y ver el total
  a  ver esta ayuda
  s  salir
"""

TARIFA_PARADO = 0.02
TARIFA_MOVIMIENTO = 0.05


def tarifa(estado):
    if estado == "parado":
        return TARIFA_PARADO
    elif estado == "movimiento":
        return TARIFA_MOVIMIENTO

def cerrar_tramo(carrera):
    ahora = time.monotonic()
    segundos = ahora - carrera["desde"]
    importe = segundos * tarifa(carrera["estado"])

    carrera["importe"] += importe
    carrera["desde"] = ahora

def main():
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
                "importe": 0.0
            }
            print("Carrera iniciada. El taxi está PARADO.")
            print(carrera)

        elif orden == "p":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera)
            carrera["estado"] = "parado"
            print("El taxi está PARADO.")

        elif orden == "m":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera)
            carrera["estado"] = "movimiento"
            print("El taxi está EN MOVIMIENTO.")

        elif orden == "f":
            if carrera is None:
                print("Primero debes iniciar una carrera.")
                continue

            cerrar_tramo(carrera)
            print(f"Importe total: {carrera['importe']:.2f} €")
            carrera = None

        elif orden == "a":
            print(AYUDA)

        elif orden == "s":
            print("Hasta luego.")
            break

        else:
            print("Orden desconocida. Escribe 'a' para ver la ayuda.")


if __name__ == "__main__":
    main()
