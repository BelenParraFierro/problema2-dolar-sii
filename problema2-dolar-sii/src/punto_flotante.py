"""
punto_flotante.py
=================
Preguntas B1, B2 y B4 del enunciado, mas el grafico 5 (deriva de la ida y
vuelta), que depende directamente del ejercicio B2.

  B1 - Cifras significativas = mantisa corta.
  B2 - La ida y vuelta que no vuelve (deriva CLP -> USD -> CLP).
  B4 - Cancelacion en la maquina: 874.67 - 875.66 en float32 vs float64.
"""

import numpy as np
import matplotlib.pyplot as plt

from errores import (MONTO, redondear_sig, error_absoluto, error_relativo,
                     _guardar, _eje_meses)

# B1 - CIFRAS SIGNIFICATIVAS COMO MANTISA CORTA
def b1_mantisa_corta(valor=1000.76):
    """Relaciona el redondeo decimal con el tamano de la mantisa binaria."""
    casos = []
    for s in (2, 3, 4):
        ap = float(redondear_sig(valor, s))
        ea = float(error_absoluto(valor, ap))
        casos.append({"cifras": s, "aproximado": ap, "error_absoluto": ea,
                      "error_relativo_pct": float(error_relativo(valor, ea)) * 100.0,
                      "bits_equivalentes": s * np.log2(10)})
    return {"valor": valor, "casos": casos}


# B2 - LA IDA Y VUELTA QUE NO VUELVE
def b2_ida_y_vuelta(precios, monto=MONTO):
    """Convierte CLP -> USD -> CLP con el MISMO precio y mide la deriva."""
    P = np.asarray(precios, dtype=float)

    # float64: 53 bits de mantisa
    P64 = P.astype(np.float64)
    deriva64 = (np.float64(monto) / P64) * P64 - np.float64(monto)

    # float32: 24 bits. Hay que forzar float32 en CADA paso: si se mezcla un
    # float64 numpy promueve todo y el experimento se arruina.
    P32 = P.astype(np.float32)
    usd32 = (np.float32(monto) / P32).astype(np.float32)
    vuelta32 = (usd32 * P32).astype(np.float32)
    deriva32 = vuelta32.astype(np.float64) - np.float64(monto)

    return {
        "monto": monto, "precios": P,
        "deriva64": deriva64, "deriva32": deriva32,
        "max_abs_64": float(np.max(np.abs(deriva64))),
        "max_abs_32": float(np.max(np.abs(deriva32))),
        # Correlacion con el precio: responde si la deriva "sigue el mismo
        # patron de movimiento de la curva". |r| cercano a 0 significa que no.
        "corr_32_precio": float(np.corrcoef(deriva32, P)[0, 1]),
        "corr_64_precio": float(np.corrcoef(deriva64, P)[0, 1]),
    }

# B4 - CANCELACION EN LA MAQUINA
def b4_cancelacion(a=874.67, b=875.66):
    """Calcula a - b en float32 y float64 y cuenta las cifras validas."""
    exacto = -0.99   # ni float32 ni float64 representan exacto 874.67 ni 875.66

    a32, b32 = np.float32(a), np.float32(b)
    r32 = np.float32(a32 - b32)
    r64 = np.float64(a) - np.float64(b)

    def cifras_validas(aprox):
        """Cifras correctas ~ -log10(error relativo)."""
        er = abs((float(aprox) - exacto) / exacto)
        return np.inf if er == 0 else -np.log10(er)

    return {
        "a": a, "b": b, "exacto": exacto,
        "a32_guardado": float(a32), "b32_guardado": float(b32),
        "resta32": float(r32), "resta64": float(r64),
        "er32_pct": abs((float(r32) - exacto) / exacto) * 100.0,
        "er64_pct": abs((float(r64) - exacto) / exacto) * 100.0,
        "cifras_validas_32": cifras_validas(r32),
        "cifras_validas_64": cifras_validas(r64),
        "factor_cancelacion": abs(a) / abs(exacto),
    }

# GRAFICO 5 - DERIVA DE LA IDA Y VUELTA
def grafico_deriva(datos):
    """Grafico 5: deriva de (M/P)*P - M en float32 y float64 vs el precio."""
    v = b2_ida_y_vuelta(datos["precio"], MONTO)
    x = np.arange(datos["n"])

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    ax1.plot(x, datos["precio"], color="#1f77b4", lw=1.5)
    ax1.set_ylabel("Precio (CLP)")
    ax1.set_title("Deriva de la ida y vuelta CLP -> USD -> CLP (B2)")
    ax1.grid(alpha=0.3)

    for ax, clave, color, nombre in ((ax2, "deriva32", "#d62728", "float32"),
                                     (ax3, "deriva64", "#2ca02c", "float64")):
        ax.bar(x, v[clave], color=color)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_ylabel(f"Deriva {nombre} (CLP)")
        ax.text(0.01, 0.9,
                f"max |deriva| = {v['max_abs_' + nombre[-2:]]:.3e} CLP   "
                f"corr. con el precio: r = {v['corr_' + nombre[-2:] + '_precio']:+.3f}",
                transform=ax.transAxes, fontsize=8)
        ax.grid(alpha=0.3, axis="y")

    ax3.set_xlabel("Mes")
    _eje_meses(ax3, datos)
    return _guardar(fig, "5_deriva_punto_flotante.png")