"""
cargar_datos.py
===============
Carga del dataset del dolar observado (SII, promedio mensual 2022-2025).

El enunciado exige cargar el CSV con numpy (np.genfromtxt) y trabajar con
arreglos de numpy en todas las operaciones posteriores.
"""

from pathlib import Path
import numpy as np

# Rutas ancladas a la raiz del repositorio, para que los modulos funcionen
# sin importar desde que carpeta se ejecuten.
RAIZ = Path(__file__).resolve().parent.parent
RUTA_CSV = RAIZ / "data" / "dolar_observado_sii_2022_2025.csv"
DIR_GRAFICOS = RAIZ / "graficos"


def cargar(ruta=RUTA_CSV):
    """Lee el CSV y devuelve los datos como arreglos de numpy."""
    # names=True -> primera fila como nombres de columna
    # dtype=None -> numpy infiere el tipo de cada columna
    datos = np.genfromtxt(ruta, delimiter=",", names=True,
                          dtype=None, encoding="utf-8")

    precio = np.asarray(datos["dolar_observado_promedio_clp"], dtype=float)
    anio = np.asarray(datos["anio"], dtype=int)
    mes = np.asarray(datos["mes"], dtype=str)
    mes_num = np.asarray(datos["mes_num"], dtype=int)

    # Si el CSV trajera celdas vacias, genfromtxt las vuelve NaN y todos los
    # calculos posteriores quedarian contaminados sin aviso.
    if np.isnan(precio).any():
        raise ValueError("El CSV contiene precios vacios o no numericos (NaN).")

    etiqueta = np.array([f"{a}-{m:02d} {nm}"
                         for a, m, nm in zip(anio, mes_num, mes)], dtype=str)

    return {"anio": anio, "mes": mes, "mes_num": mes_num,
            "precio": precio, "etiqueta": etiqueta, "n": precio.size}


def indice_de(datos, anio, mes_num):
    """Posicion de un mes dentro de los arreglos. Ej: (2022, 12) -> 11."""
    pos = np.flatnonzero((datos["anio"] == anio) & (datos["mes_num"] == mes_num))
    if pos.size == 0:
        raise ValueError(f"No existe el mes {anio}-{mes_num:02d} en el dataset.")
    return int(pos[0])