"""
errores.py
==========
Nucleo del laboratorio: redondeo a cifras significativas (la "mantisa corta"),
error absoluto, error relativo y propagacion entre puntos.

Incluye los graficos que dependen directamente de estos calculos:
    Grafico 1 - serie mensual (real vs aproximado)
    Grafico 2 - variacion mes a mes con cancelacion
    Grafico 3 - error de representacion por mes

REGLAS DE PROPAGACION
-----------------------------------------------
  * Multiplicacion y division -> se SUMAN los errores RELATIVOS.
  * Suma y resta              -> se SUMAN los errores ABSOLUTOS.
Son cotas pesimistas: suponen que los errores se alinean en la peor direccion.

CONVENCION: los errores relativos se manejan como FRACCION (0.0032), no como
porcentaje. La conversion a % se hace solo al imprimir o graficar.
"""

import matplotlib
matplotlib.use("Agg")   # backend sin ventana: guarda PNG sin entorno grafico
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

from cargar_datos import DIR_GRAFICOS

# Parametros
CIFRAS = 2             # cifras significativas de la mantisa corta (seccion 4)
MONTO = 1_000_000.0    # M = 1.000.000 CLP
UMBRAL_DUDOSO = 0.10   # 10% de error relativo: umbral de la norma adoptada


# 1. REDONDEO A CIFRAS SIGNIFICATIVAS
def redondear_sig(x, cifras=CIFRAS):
    """Redondea a `cifras` cifras significativas totales. Vectorizado.

    El exponente decimal e = floor(log10(|x|)) indica donde esta la primera
    cifra significativa. Para conservar s cifras se escala el numero de modo
    que la ultima cifra util caiga en las unidades, se redondea, y se
    devuelve a su escala original.

        963.44 con s=2 -> e=2, factor=10^-1 -> 96.344 -> 96 -> 960
        1000.76 con s=2 -> e=3, factor=10^-2 -> 10.0076 -> 10 -> 1000
    """
    x = np.asarray(x, dtype=float)
    seguro = np.where(x == 0, 1.0, np.abs(x))      # evita log10(0) = -inf
    factor = 10.0 ** (cifras - 1 - np.floor(np.log10(seguro)))
    return np.where(x == 0, 0.0, np.round(x * factor) / factor)

# 2. ERRORES BASICOS
def error_absoluto(verdadero, aproximado):
    """Ea = |valor verdadero - valor aproximado|  (en pesos)."""
    return np.abs(np.asarray(verdadero, float) - np.asarray(aproximado, float))

def error_relativo(verdadero, absoluto):
    """Er = Ea / |valor verdadero|  (FRACCION, no porcentaje)."""
    verdadero = np.abs(np.asarray(verdadero, float))
    absoluto = np.asarray(absoluto, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(verdadero == 0, np.inf, absoluto / verdadero)

def errores_de_representacion(precios, cifras=CIFRAS):
    """Aplica el redondeo y devuelve (aprox, Ea, Er) del arreglo."""
    aprox = redondear_sig(precios, cifras)
    ea = error_absoluto(precios, aprox)
    return aprox, ea, error_relativo(precios, ea)

# 3. PROPAGACION
def propagar_multiplicacion(er_a, er_b):
    """Producto o cociente: los errores RELATIVOS se suman."""
    return np.asarray(er_a, float) + np.asarray(er_b, float)

propagar_division = propagar_multiplicacion   # misma cota pesimista

def propagar_resta(ea_a, ea_b):
    """Suma o resta: los errores ABSOLUTOS se suman."""
    return np.abs(np.asarray(ea_a, float)) + np.abs(np.asarray(ea_b, float))

propagar_suma = propagar_resta

# 4. CRITERIO DE CONFIABILIDAD
def clasificar(valor, error_abs, umbral=UMBRAL_DUDOSO):
    """Decide si una diferencia calculada se puede afirmar o no.

      INDECIDIBLE : |valor| <= error_abs  -> la barra de error cruza el cero,
                    ni siquiera el signo es afirmable.
      DUDOSO      : error relativo > umbral -> el signo se afirma, la
                    magnitud no sirve para decidir.
      CONFIABLE   : error relativo <= umbral.

    El umbral de 10% se justifica porque los margenes reales de una operacion
    de cambio son de 1-3%: con mas de 10% de incerteza no se distingue una
    ganancia real de una perdida por comisiones.
    """
    valor = np.abs(np.asarray(valor, float))
    error_abs = np.abs(np.asarray(error_abs, float))
    er = error_relativo(valor, error_abs)
    etiq = np.where(valor <= error_abs, "INDECIDIBLE",
                    np.where(er > umbral, "DUDOSO", "CONFIABLE"))
    return str(etiq) if etiq.ndim == 0 else etiq

# 5. COMPRA-VENTA ENTRE DOS PUNTOS
def compra_venta(p_compra, p_venta, monto=MONTO, cifras=CIFRAS):
    """Simula comprar dolares en un mes y venderlos en otro, propagando error."""
    pc = float(redondear_sig(p_compra, cifras))
    pv = float(redondear_sig(p_venta, cifras))
    ea_pc = float(error_absoluto(p_compra, pc))
    ea_pv = float(error_absoluto(p_venta, pv))
    er_pc = float(error_relativo(p_compra, ea_pc))
    er_pv = float(error_relativo(p_venta, ea_pv))

    usd = monto / pc                                  # 1) compra
    er_usd = propagar_division(0.0, er_pc)
    ea_usd = usd * er_usd

    final = usd * pv                                  # 2) venta
    er_final = propagar_multiplicacion(er_usd, er_pv)
    ea_final = final * er_final

    ganancia = final - monto                          # 3) ganancia
    ea_g = propagar_resta(ea_final, 0.0)
    er_g = float(error_relativo(ganancia, ea_g))

    return {
        "p_compra_real": p_compra, "p_compra_aprox": pc,
        "p_venta_real": p_venta, "p_venta_aprox": pv,
        "ea_pc": ea_pc, "er_pc": er_pc, "ea_pv": ea_pv, "er_pv": er_pv,
        "usd": usd, "ea_usd": ea_usd, "er_usd": er_usd,
        "final": final, "ea_final": ea_final, "er_final": er_final,
        "ganancia": ganancia, "ea_ganancia": ea_g, "er_ganancia": er_g,
        "rentabilidad": ganancia / monto * 100.0,
        "ea_rentabilidad": ea_g / monto * 100.0,
        # Contraste: la misma operacion sin redondear, para verificar que el
        # valor real cae dentro de la banda de error.
        "ganancia_exacta": monto / p_compra * p_venta - monto,
        "clasificacion": clasificar(ganancia, ea_g),
    }

# 6. VARIACION ENTRE DOS MESES
def variacion(p_inicial, p_final, cifras=CIFRAS):
    """DeltaP = P_final - P_inicial con error absoluto propagado."""
    pi = redondear_sig(p_inicial, cifras)
    pf = redondear_sig(p_final, cifras)
    ea = propagar_resta(error_absoluto(p_inicial, pi),
                        error_absoluto(p_final, pf))
    delta = pf - pi
    return {"delta": delta, "ea": ea, "er": error_relativo(delta, ea),
            "delta_exacto": np.asarray(p_final, float) - np.asarray(p_inicial, float),
            "clasificacion": clasificar(delta, ea)}

# 7. GRAFICOS 1, 2 y 3
def _guardar(fig, nombre):
    """Guarda la figura en graficos/<nombre> y cierra para liberar memoria."""
    DIR_GRAFICOS.mkdir(exist_ok=True)
    ruta = DIR_GRAFICOS / nombre
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [ok] {ruta}")
    return ruta


def _eje_meses(ax, datos, paso=3):
    """Etiquetas de mes legibles en el eje X, una cada `paso` meses."""
    idx = np.arange(datos["n"])
    ax.set_xticks(idx[::paso])
    ax.set_xticklabels([f"{datos['anio'][i]}-{datos['mes_num'][i]:02d}"
                        for i in idx[::paso]], rotation=45, ha="right", fontsize=8)


def grafico_serie(datos, cifras=CIFRAS):
    """Grafico 1: precio real vs precio con mantisa corta, mes a mes."""
    aprox = redondear_sig(datos["precio"], cifras)
    x = np.arange(datos["n"])
    imin, imax = int(np.argmin(datos["precio"])), int(np.argmax(datos["precio"]))

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, datos["precio"], color="#1f77b4", lw=1.8, marker="o", ms=3,
            label="Precio real (SII)")
    ax.step(x, aprox, where="mid", color="#d62728", lw=1.2, ls="--",
            label=f"Aproximado ({cifras} cifras significativas)")

    # Minimo y maximo del periodo: son los meses de la pregunta A5.
    ax.scatter([imin], [datos["precio"][imin]], color="green", zorder=5, s=70)
    ax.annotate(f"min {datos['precio'][imin]:.2f}", (imin, datos["precio"][imin]),
                textcoords="offset points", xytext=(0, -20), ha="center",
                fontsize=8, color="green")
    ax.scatter([imax], [datos["precio"][imax]], color="purple", zorder=5, s=70)
    ax.annotate(f"max {datos['precio'][imax]:.2f}", (imax, datos["precio"][imax]),
                textcoords="offset points", xytext=(0, 10), ha="center",
                fontsize=8, color="purple")

    ax.set_title("Dolar observado SII - promedio mensual 2022-2025")
    ax.set_xlabel("Mes")
    ax.set_ylabel("CLP por 1 USD")
    _eje_meses(ax, datos)
    ax.grid(alpha=0.3)
    ax.legend()
    return _guardar(fig, "1_serie_mensual.png")


def grafico_variaciones(datos, cifras=CIFRAS):
    """Grafico 2: DeltaP mes a mes. En gris, donde el error domina."""
    v = variacion(datos["precio"][:-1], datos["precio"][1:], cifras)
    delta, ea = v["delta"], v["ea"]
    x = np.arange(delta.size)

    # Indecidible cuando |DeltaP| <= error: la barra cruza el cero y el
    # signo deja de ser afirmable.
    indecidible = np.abs(delta) <= ea
    colores = np.where(indecidible, "#999999",
                       np.where(delta >= 0, "#2ca02c", "#d62728"))

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x, delta, color=colores, yerr=ea, capsize=2,
           error_kw={"elinewidth": 0.8, "ecolor": "black"})
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title(f"Variacion mes a mes con error propagado "
                 f"({cifras} cifras) - gris = cancelacion")
    ax.set_xlabel("Mes (respecto del anterior)")
    ax.set_ylabel("Delta P (CLP)")
    ax.set_xticks(x[::3])
    ax.set_xticklabels([f"{datos['anio'][i+1]}-{datos['mes_num'][i+1]:02d}"
                        for i in x[::3]], rotation=45, ha="right", fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    # Leyenda manual: los colores se asignan barra por barra.
    ax.legend(handles=[Patch(color="#2ca02c", label="Subio (afirmable)"),
                       Patch(color="#d62728", label="Bajo (afirmable)"),
                       Patch(color="#999999", label="INDECIDIBLE: |dP| <= error")],
              fontsize=8)

    print(f"       -> {int(indecidible.sum())} de {delta.size} variaciones "
          f"resultan indecidibles")
    return _guardar(fig, "2_variaciones_cancelacion.png")


def grafico_representacion(datos, cifras=CIFRAS):
    """Grafico 3: error absoluto y relativo del redondeo, mes a mes."""
    _, ea, er = errores_de_representacion(datos["precio"], cifras)
    er = er * 100.0
    x = np.arange(datos["n"])
    peor = int(np.argmax(er))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    ax1.bar(x, ea, color="#ff7f0e")
    ax1.set_ylabel("Error absoluto (CLP)")
    ax1.set_title(f"Error de representacion con {cifras} cifras significativas")
    ax1.grid(alpha=0.3, axis="y")

    ax2.bar(x, er, color=["#8b0000" if i == peor else "#1f77b4" for i in x])
    ax2.axhline(er.mean(), color="black", ls="--", lw=1,
                label=f"promedio = {er.mean():.3f}%")
    ax2.annotate(f"peor mes: {datos['etiqueta'][peor]}\n{er[peor]:.3f}%",
                 (peor, er[peor]), textcoords="offset points",
                 xytext=(5, -25), fontsize=8, color="#8b0000")
    ax2.set_ylabel("Error relativo (%)")
    ax2.set_xlabel("Mes")
    ax2.grid(alpha=0.3, axis="y")
    ax2.legend(fontsize=8)
    _eje_meses(ax2, datos)
    return _guardar(fig, "3_error_representacion.png")
