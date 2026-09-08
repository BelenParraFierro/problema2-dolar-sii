"""
main.py
=======
Ejecuta el laboratorio completo: responde A1-A5 y B1-B4, escribe la tabla de
evaluacion de errores y genera los 5 graficos en graficos/.

Uso:
    python main.py       # 2 cifras significativas (seccion 4 del enunciado)
    python main.py 3     # 3 cifras significativas (las que pide A3)
"""

import sys
from pathlib import Path

# Permite importar los modulos de src/ ejecutando `python main.py` desde la raiz.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import numpy as np

from cargar_datos import cargar, indice_de
from errores import (MONTO, UMBRAL_DUDOSO, redondear_sig,
                     errores_de_representacion, variacion, compra_venta,
                     grafico_serie, grafico_variaciones, grafico_representacion)
from anualidad import (variacion_anual, ranking_confiabilidad,
                       grafico_rentabilidad, escribir_tabla)
from punto_flotante import (b1_mantisa_corta, b2_ida_y_vuelta, b4_cancelacion,
                            grafico_deriva)

def titulo(texto):
    print("\n" + "=" * 74)
    print(texto)
    print("=" * 74)

def main(cifras=2):
    datos = cargar()
    print(f"\nDolar observado SII - promedio mensual 2022-2025 ({datos['n']} meses)")
    print(f"Mantisa corta: {cifras} cifras significativas | M = {MONTO:,.0f} CLP")
    print(f"Norma adoptada: DUDOSO si Er > {UMBRAL_DUDOSO*100:.0f}%, "
          f"INDECIDIBLE si |valor| <= error")

    titulo("A1 - Error de representacion mes a mes")

    aprox, ea, er = errores_de_representacion(datos["precio"], cifras)
    er = er * 100.0
    peor, mejor = int(np.argmax(er)), int(np.argmin(er))

    print(f"{'Mes':<20}{'Real':>10}{'Aprox':>10}{'Ea (CLP)':>11}{'Er (%)':>10}")
    print("-" * 61)
    for i in range(datos["n"]):
        marca = "  <-- peor" if i == peor else ""
        print(f"{datos['etiqueta'][i]:<20}{datos['precio'][i]:>10.2f}"
              f"{aprox[i]:>10.1f}{ea[i]:>11.2f}{er[i]:>10.4f}{marca}")

    print(f"\nMayor error relativo : {datos['etiqueta'][peor]} -> {er[peor]:.4f}% "
          f"(Ea = {ea[peor]:.2f} CLP)")
    print(f"Menor error relativo : {datos['etiqueta'][mejor]} -> {er[mejor]:.4f}%")
    print(f"Error relativo medio : {er.mean():.4f}%   maximo Ea = {ea.max():.2f} CLP")

    titulo("A2 - Evaluacion entre dos puntos (una compra-venta)")

    i_c, i_v = indice_de(datos, 2022, 1), indice_de(datos, 2022, 10)
    r = compra_venta(float(datos["precio"][i_c]), float(datos["precio"][i_v]),
                     MONTO, cifras)

    print(f"Compra: {datos['etiqueta'][i_c]}  {r['p_compra_real']:.2f} -> "
          f"{r['p_compra_aprox']:.1f}  (Ea = {r['ea_pc']:.2f}, Er = {r['er_pc']*100:.4f}%)")
    print(f"Venta : {datos['etiqueta'][i_v]}  {r['p_venta_real']:.2f} -> "
          f"{r['p_venta_aprox']:.1f}  (Ea = {r['ea_pv']:.2f}, Er = {r['er_pv']*100:.4f}%)\n")
    print(f"  1) USD = M / P_compra    = {r['usd']:.4f} USD +- {r['ea_usd']:.4f}"
          f"   (Er = {r['er_usd']*100:.4f}%)")
    print(f"  2) final = USD * P_venta = {r['final']:,.2f} CLP +- {r['ea_final']:,.2f}"
          f"   (Er = {r['er_final']*100:.4f}%)")
    print(f"  3) G = final - M         = {r['ganancia']:,.2f} CLP +- {r['ea_ganancia']:,.2f}"
          f"   (Er = {r['er_ganancia']*100:.2f}%)")
    print(f"  4) rentabilidad          = {r['rentabilidad']:.2f}% "
          f"+- {r['ea_rentabilidad']:.2f}%")
    print(f"\n  Ganancia sin redondear (referencia): {r['ganancia_exacta']:,.2f} CLP")
    print(f"  Clasificacion: {r['clasificacion']}")

    titulo("A3 - Cancelacion: diciembre 2022 vs diciembre 2023")

    p22 = float(datos["precio"][indice_de(datos, 2022, 12)])
    p23 = float(datos["precio"][indice_de(datos, 2023, 12)])

    for s in (3, cifras):   # A3 pide 3 cifras; se muestra tambien con las del run
        v = variacion(p22, p23, s)
        d, e = float(v["delta"]), float(v["ea"])
        cruza = abs(d) <= e
        print(f"\nCon {s} cifras significativas:")
        print(f"  {p22:.2f} -> {float(redondear_sig(p22, s)):.1f}   "
              f"{p23:.2f} -> {float(redondear_sig(p23, s)):.1f}")
        print(f"  DeltaP = {d:+.2f} +- {e:.2f} CLP   "
              f"Er = {float(v['er'])*100:.1f}%  -> {v['clasificacion']}")
        print(f"  Intervalo [{d-e:+.2f}, {d+e:+.2f}] -> "
              f"{'CRUZA el cero: el signo NO es afirmable' if cruza else 'NO cruza el cero: el signo SI es afirmable'}")
        print(f"  Valor exacto de referencia: {p23 - p22:+.2f} CLP")

    titulo("A4 - Anualidad: variacion enero -> diciembre")

    filas = variacion_anual(datos, cifras)
    print(f"{'Ano':<7}{'Var aprox':>13}{'Error':>9}{'Er %':>9}  "
          f"{'Estado':<13}{'Var exacta':>12}")
    print("-" * 64)
    for f in ranking_confiabilidad(filas):
        print(f"{f['anio']:<7}{f['variacion']:>+10.1f} CLP{f['error_propagado']:>9.2f}"
              f"{f['error_relativo_pct']:>8.1f}%  {f['clasificacion']:<13}"
              f"{f['variacion_exacta']:>+11.2f}")
    print("\n(de MAS confiable a MENOS confiable)")
    print("En comun los anos poco confiables: la variacion anual es CHICA, y el")
    print("error propagado es casi constante (nunca supera un escalon de")
    print("redondeo), asi que pesa mucho mas en proporcion.")

    titulo("A5 - Mejor compra y mejor venta del periodo")

    imin, imax = int(np.argmin(datos["precio"])), int(np.argmax(datos["precio"]))
    print(f"Mes mas barato: {datos['etiqueta'][imin]}  {datos['precio'][imin]:.2f} CLP")
    print(f"Mes mas caro  : {datos['etiqueta'][imax]}  {datos['precio'][imax]:.2f} CLP")

    r5 = compra_venta(float(datos["precio"][imin]), float(datos["precio"][imax]),
                      MONTO, cifras)
    print(f"\n  USD comprados   = {r5['usd']:.4f} +- {r5['ea_usd']:.4f}")
    print(f"  Pesos al vender = {r5['final']:,.2f} +- {r5['ea_final']:,.2f}")
    print(f"  Ganancia        = {r5['ganancia']:,.2f} +- {r5['ea_ganancia']:,.2f} CLP")
    print(f"  Rentabilidad    = {r5['rentabilidad']:.2f}% +- {r5['ea_rentabilidad']:.2f}%")
    print(f"  Er(ganancia)    = {r5['er_ganancia']*100:.2f}%  -> {r5['clasificacion']}")
    print(f"  Referencia sin redondear: {r5['ganancia_exacta']:,.2f} CLP")

    # Robustez del minimo y del maximo frente a sus vecinos
    for nombre, centro in (("minimo", imin), ("maximo", imax)):
        print(f"\n  El {nombre} comparado con sus vecinos:")
        for j in (centro - 1, centro + 1, centro + 2):
            if 0 <= j < datos["n"]:
                v = variacion(float(datos["precio"][centro]),
                              float(datos["precio"][j]), cifras)
                print(f"    vs {datos['etiqueta'][j]:<20} DeltaP = "
                      f"{float(v['delta']):+7.1f} +- {float(v['ea']):.2f}"
                      f"  -> {v['clasificacion']}")

    titulo("B1 - Cifras significativas = mantisa corta")
    b1 = b1_mantisa_corta(1000.76)
    print(f"Valor verdadero: {b1['valor']}")
    for c in b1["casos"]:
        print(f"  {c['cifras']} cifras -> {c['aproximado']:>8.1f}   "
              f"Ea = {c['error_absoluto']:.4f}   Er = {c['error_relativo_pct']:.4f}%"
              f"   ~{c['bits_equivalentes']:.1f} bits de mantisa")
    print("  (float32 = 24 bits de mantisa, float64 = 53 bits)")
    print("\n  Detalle: 1000.76 con 2 y con 3 cifras da el MISMO valor (1000),")
    print("  porque su tercera cifra significativa es un 0. Agregar precision")
    print("  no siempre reduce el error.")

    titulo("B2 - La ida y vuelta que no vuelve")
    b2 = b2_ida_y_vuelta(datos["precio"], MONTO)
    print(f"Se convierte {MONTO:,.0f} CLP a USD y de vuelta con el MISMO precio.")
    print(f"  Deriva maxima float64: {b2['max_abs_64']:.3e} CLP")
    print(f"  Deriva maxima float32: {b2['max_abs_32']:.3e} CLP")
    print(f"  Meses con deriva no nula (float32): "
          f"{int(np.count_nonzero(b2['deriva32']))} de {datos['n']}")
    print(f"  Correlacion deriva32 vs precio: r = {b2['corr_32_precio']:+.3f}")
    print(f"  Correlacion deriva64 vs precio: r = {b2['corr_64_precio']:+.3f}")
    print("\n  La deriva NO reproduce la forma de la curva de precios: salta")
    print("  entre valores discretos (multiplos del ulp) segun si la division")
    print("  cae o no justo sobre un numero representable.")

    titulo("B4 - Cancelacion en la maquina: 874.67 - 875.66")
    b4 = b4_cancelacion()
    print(f"  float32 guarda 874.67 como {b4['a32_guardado']:.10f}")
    print(f"  float32 guarda 875.66 como {b4['b32_guardado']:.10f}")
    print(f"\n  resta en float32 = {b4['resta32']!r}")
    print(f"  resta en float64 = {b4['resta64']!r}")
    print(f"  valor exacto     = {b4['exacto']}")
    print(f"\n  Er float32 = {b4['er32_pct']:.3e} %  -> quedan "
          f"~{b4['cifras_validas_32']:.1f} cifras validas (de 7 nominales)")
    print(f"  Er float64 = {b4['er64_pct']:.3e} %  -> quedan "
          f"~{b4['cifras_validas_64']:.1f} cifras validas (de 16 nominales)")
    print(f"\n  Factor de cancelacion |a| / |a-b| = {b4['factor_cancelacion']:.0f}x")
    print("  Conexion con A3: es el MISMO fenomeno. En A3 la mantisa corta la")
    print("  ponemos nosotros (2-3 cifras) y perdemos casi todo; aqui la pone")
    print("  el hardware (24 o 53 bits) y por eso sobreviven cifras utiles.")

    titulo("Tabla de evaluacion de errores y graficos")

    escribir_tabla(datos, cifras, pares=[
        (i_c, i_v, "A2: compra 2022-01 / venta 2022-10"),
        (imin, imax, "A5: compra minimo / venta maximo"),
    ])
    grafico_serie(datos, cifras)
    grafico_variaciones(datos, cifras)
    grafico_representacion(datos, cifras)
    grafico_rentabilidad(datos, cifras)
    grafico_deriva(datos)
    print("\nListo.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
