"""
anualidad.py
============
Pregunta A4: variacion Precio_diciembre - Precio_enero de cada ano con su
error propagado, y ranking de confiabilidad.

Incluye ademas:
    Grafico 4 - rentabilidad de comprar en el minimo y vender en cada mes
                posterior, con barras de error propagado.
    La tabla de evaluacion de errores obligatoria (evaluacion_errores.csv),
    con el error absoluto, relativo y propagado de cada mes, de cada par de
    puntos evaluado y de cada ano.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt

from cargar_datos import RAIZ
from errores import (CIFRAS, MONTO, redondear_sig, error_absoluto,
                     error_relativo, variacion, compra_venta, _guardar)

RUTA_TABLA = RAIZ / "evaluacion_errores.csv"

# A4 - VARIACION ANUAL
def variacion_anual(datos, cifras=CIFRAS):
    """Variacion enero -> diciembre de cada ano, con error propagado."""
    filas = []
    for anio in np.unique(datos["anio"]):          # unique ya viene ordenado
        m = datos["anio"] == anio
        precios, meses = datos["precio"][m], datos["mes_num"][m]

        # Se toman explicitamente los meses 1 y 12 en vez de asumir que son
        # el primero y el ultimo del arreglo: mas robusto ante desorden.
        p_ene = float(precios[meses == 1][0])
        p_dic = float(precios[meses == 12][0])
        v = variacion(p_ene, p_dic, cifras)

        filas.append({
            "anio": int(anio),
            "p_enero_real": p_ene,
            "p_enero_aprox": float(redondear_sig(p_ene, cifras)),
            "p_dic_real": p_dic,
            "p_dic_aprox": float(redondear_sig(p_dic, cifras)),
            "variacion": float(v["delta"]),
            "variacion_exacta": float(v["delta_exacto"]),
            "error_propagado": float(v["ea"]),
            "error_relativo_pct": float(v["er"]) * 100.0,
            "clasificacion": str(v["clasificacion"]),
        })
    return filas


def ranking_confiabilidad(filas):
    """Ordena los anos del resultado mas confiable al menos confiable."""
    er = np.array([f["error_relativo_pct"] for f in filas], dtype=float)
    return [filas[i] for i in np.argsort(er)]


# GRAFICO 4 - RENTABILIDAD DESDE EL MINIMO
def grafico_rentabilidad(datos, cifras=CIFRAS):
    """Comprar en el mes mas barato y vender en cada mes posterior."""
    imin = int(np.argmin(datos["precio"]))
    p_compra = float(datos["precio"][imin])
    idx = np.arange(imin + 1, datos["n"])

    rent = np.empty(idx.size)
    err = np.empty(idx.size)
    for k, j in enumerate(idx):
        r = compra_venta(p_compra, float(datos["precio"][j]), MONTO, cifras)
        rent[k], err[k] = r["rentabilidad"], r["ea_rentabilidad"]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.errorbar(np.arange(idx.size), rent, yerr=err, fmt="o-", color="#1f77b4",
                ecolor="#d62728", elinewidth=1.2, capsize=3, ms=4,
                label="Rentabilidad +- error propagado")
    ax.axhline(0, color="black", lw=0.8)

    mejor = int(np.argmax(rent))
    ax.annotate(f"mejor venta: {datos['etiqueta'][idx[mejor]]}\n"
                f"{rent[mejor]:.2f}% +- {err[mejor]:.2f}%",
                (mejor, rent[mejor]), textcoords="offset points",
                xytext=(-95, -38), fontsize=8,
                arrowprops={"arrowstyle": "->", "lw": 0.8})

    ax.set_title(f"Rentabilidad de comprar en {datos['etiqueta'][imin]} "
                 f"(P = {p_compra:.2f}) y vender despues - M = {MONTO:,.0f} CLP")
    ax.set_xlabel("Mes de venta")
    ax.set_ylabel("Rentabilidad (%)")
    ax.set_xticks(np.arange(idx.size)[::3])
    ax.set_xticklabels([f"{datos['anio'][j]}-{datos['mes_num'][j]:02d}"
                        for j in idx[::3]], rotation=45, ha="right", fontsize=8)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    return _guardar(fig, "4_rentabilidad_desde_minimo.png")


# TABLA DE EVALUACION DE ERRORES (entregable obligatorio)
def escribir_tabla(datos, cifras=CIFRAS, pares=None, ruta=RUTA_TABLA):
    """Escribe evaluacion_errores.csv con TODOS los errores calculados."""
    filas = []

    # Representacion mes a mes
    aprox = redondear_sig(datos["precio"], cifras)
    ea = error_absoluto(datos["precio"], aprox)
    er = error_relativo(datos["precio"], ea) * 100.0
    for i in range(datos["n"]):
        filas.append(["representacion", datos["etiqueta"][i],
                      f"{aprox[i]:.2f}", f"{datos['precio'][i]:.2f}",
                      f"{ea[i]:.4f}", f"{er[i]:.4f}", ""])

    # Variacion mes a mes
    v = variacion(datos["precio"][:-1], datos["precio"][1:], cifras)
    for i in range(datos["n"] - 1):
        er_i = v["er"][i] * 100.0
        filas.append(["variacion_mensual",
                      f"{datos['etiqueta'][i]} -> {datos['etiqueta'][i+1]}",
                      f"{v['delta'][i]:.2f}", f"{v['delta_exacto'][i]:.2f}",
                      f"{v['ea'][i]:.4f}",
                      "inf" if not np.isfinite(er_i) else f"{er_i:.2f}",
                      v["clasificacion"][i]])

    # Variacion anual
    for f in variacion_anual(datos, cifras):
        filas.append(["variacion_anual", f"{f['anio']} enero->diciembre",
                      f"{f['variacion']:.2f}", f"{f['variacion_exacta']:.2f}",
                      f"{f['error_propagado']:.4f}",
                      f"{f['error_relativo_pct']:.2f}", f["clasificacion"]])

    # Pares compra-venta evaluados
    for i_c, i_v, desc in (pares or []):
        r = compra_venta(float(datos["precio"][i_c]), float(datos["precio"][i_v]),
                         MONTO, cifras)
        filas.append(["compra_venta", desc,
                      f"{r['ganancia']:.2f}", f"{r['ganancia_exacta']:.2f}",
                      f"{r['ea_ganancia']:.4f}",
                      f"{r['er_ganancia']*100:.2f}", r["clasificacion"]])

    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tipo", "referencia", "valor_aproximado", "valor_exacto",
                    "error_absoluto", "error_relativo_pct", "clasificacion"])
        w.writerows(filas)

    print(f"  [ok] {ruta}  ({len(filas)} filas)")
    return ruta