# INFORME — La ganancia que se evapora

**Universidad Católica del Maule** — Computación Numérica, Laboratorio evaluado 1
**Integrantes:** Belén Marcela Parra Fierro

---

## A1 - Error de representación mes a mes

Redondeando los 48 precios a 2 cifras significativas:

| Métrica                       | Mes         | Valor real | Aproximado | Ea (CLP) | Er (%)           |
| ------------------------------ | ----------- | ---------- | ---------- | -------- | ---------------- |
| **Mayor error relativo** | abril 2022  | 815,12     | 820        | 4,88     | **0,5987** |
| Menor error relativo           | agosto 2024 | 929,90     | 930        | 0,10     | 0,0108           |
| Error relativo medio           | —          | —         | —         | —       | 0,2925           |

Tabla completa en `evaluacion_errores.csv` (filas `representacion`).
Gráfico: `graficos/3_error_representacion.png`.

- Abril 2022 quedó con el mayor error, con 2 cifras significativas los valores representables van de 10 en 10, como 815,12 cae casi exactamente a mitad de camino entre 810 y 820, que es el peor caso posible del redondeo. ()El error absoluto máximo es siempre medio escalón.)

---

## A2 - Evaluación entre dos puntos

**Operación evaluada:** comprar en enero 2022 y vender en octubre 2022, con
M = 1.000.000 CLP.

| Paso   | Operación               | Resultado                | Error                 | Er (%)         |
| ------ | ------------------------ | ------------------------ | --------------------- | -------------- |
| Compra | 822,05 → 820            | —                       | Ea = 2,05             | 0,2494         |
| Venta  | 955,89 → 960            | —                       | Ea = 4,11             | 0,4300         |
| 1      | USD = M / P_compra       | 1.219,5122 USD           | ± 3,0412             | 0,2494         |
| 2      | final = USD × P_venta   | 1.170.731,71 CLP         | ± 7.953,28           | 0,6793         |
| 3      | **G = final − M** | **170.731,71 CLP** | **± 7.953,28** | **4,66** |
| 4      | rentabilidad             | 17,07 %                  | ± 0,80 %             | 4,66           |

Ganancia sin redondear (referencia): 162.812,48 CLP.
Clasificación: **CONFIABLE**.

---

## A3 - Cancelación: diciembre 2022 vs diciembre 2023

Con **3 cifras significativas**, como pide el enunciado:

| Dato           | Real   | Aproximado | Ea   |
| -------------- | ------ | ---------- | ---- |
| Diciembre 2022 | 875,66 | 876        | 0,34 |
| Diciembre 2023 | 874,67 | 875        | 0,33 |

**ΔP = 875 − 876 = −1,00 ± 0,67 CLP → error relativo = 67,0 %**

Intervalo de confianza: [−1,67 ; −0,33]. Valor exacto de referencia: −0,99 CLP.

Con 2 cifras el resultado empeora todavía más: ΔP = −10,00 ± 9,01 CLP (Er = 90,1 %).

- El peso bajo, pero afirmarlo con seguridad cuando lo que bajo fue tan poco es complicado.

---

## A4 - Anualidad (variación enero → diciembre)

Ordenado del resultado **más confiable al menos confiable**:

| Año | ΔP aproximado | Error propagado | Er (%) | Clasificación | ΔP exacto |
| ---- | -------------- | --------------- | ------ | -------------- | ---------- |
| 2025 | −80,0 CLP     | ± 4,60         | 5,8    | CONFIABLE      | −84,60    |
| 2024 | +70,0 CLP      | ± 4,31         | 6,2    | CONFIABLE      | +74,31     |
| 2022 | +60,0 CLP      | ± 6,39         | 10,6   | DUDOSO         | +53,61     |
| 2023 | +40,0 CLP      | ± 8,33         | 20,8   | DUDOSO         | +48,33     |

Tabla en `evaluacion_errores.csv` (filas `variacion_anual`).

- Lo que los años poco confiables tienen en común es la variación anual que sí cambia mucho.

---

## A5 - Mejor compra y mejor venta

|             | Mes                    | Precio real | Aproximado |
| ----------- | ---------------------- | ----------- | ---------- |
| Más barato | **febrero 2023** | 798,26      | 800        |
| Más caro   | **enero 2025**   | 1.000,76    | 1000       |

Operación completa con M = 1.000.000 CLP:

| Magnitud               | Valor                    | Error                 |
| ---------------------- | ------------------------ | --------------------- |
| USD comprados          | 1.250,0000               | ± 2,7247             |
| Pesos al vender        | 1.250.000,00             | ± 3.673,95           |
| **Ganancia**     | **250.000,00 CLP** | **± 3.673,95** |
| **Rentabilidad** | **25,00 %**        | **± 0,37 %**   |

Error relativo de la ganancia: **1,47 % → CONFIABLE**.
Referencia sin redondear: 253.676,75 CLP.
Gráfico: `graficos/4_rentabilidad_desde_minimo.png`.

**Robustez del mínimo frente a sus meses vecinos:**

| Comparación         | ΔP   | Error   | Clasificación        |
| -------------------- | ----- | ------- | --------------------- |
| feb 2023 vs ene 2023 | +30,0 | ± 5,40 | DUDOSO                |
| feb 2023 vs mar 2023 | +10,0 | ± 2,24 | DUDOSO                |
| feb 2023 vs abr 2023 | +0,0  | ± 5,58 | **INDECIDIBLE** |

- La rentabilidad global es sólida (25 % con ± 0,37 %,la señal es ~68 veces el error), pero el mes exacto del mínimo no lo es: febrero y abril de 2023 son indistinguibles con esta precisión. O sea, la estrategia funciona pero la fecha exacta de compra no está determinada.

---

## B1 - Cifras significativas = mantisa corta

Un número en punto flotante se guarda como ± m × bᵉ, con la mantisa m de tamaño
fijo. Quedarse con *s* cifras significativas decimales es exactamente lo
mismo: fijar un presupuesto de *s* dígitos para la mantisa en base 10. El
exponente absorbe la escala; la mantisa fija la precisión relativa.

Equivalencia aproximada: como log₂(10) ≈ 3,32, cada dígito decimal vale unos
3,32 bits.

Representación de **1000,76**:

| Cifras | Aproximado | Ea   | Er (%) | Bits equivalentes |
| ------ | ---------- | ---- | ------ | ----------------- |
| 2      | 1000       | 0,76 | 0,0759 | ~6,6              |
| 3      | 1000       | 0,76 | 0,0759 | ~10,0             |
| 4      | 1001       | 0,24 | 0,0240 | ~13,3             |

Referencia: float32 usa 24 bits de mantisa; float64 usa 53 bits.


Agregar precisión no siempre reduce el error.

---

## B2 - La ida y vuelta que no vuelve

Se convierte M = 1.000.000 CLP a dólares y de vuelta a pesos con el mismo
precio. En aritmética exacta (M/P)·P = M siempre; en punto flotante no.

| Formato | Deriva máxima        | Correlación con el precio |
| ------- | --------------------- | -------------------------- |
| float64 | 1,164 × 10⁻¹⁰ CLP | r = +0,015                 |
| float32 | 6,250 × 10⁻² CLP   | r = +0,373                 |

Gráfico: `graficos/5_deriva_punto_flotante.png`.

- La deriva no sigue el mismo patrón de movimiento de la curva de precios. La deriva salta entre valores discretos según si la división cae o no justo sobreun número representable, y eso no tiene relación con si el dólar subió o bajó. Con float64 la deriva es ~10⁻¹⁰ CLP: irrelevante para cualquier uso práctico.

---

## B4 - Cancelación en la máquina

Cálculo de 874,67 − 875,66:

|                            | Valor                |
| -------------------------- | -------------------- |
| float32 guarda 874,67 como | 874,6699829102       |
| float32 guarda 875,66 como | 875,6599731445       |
| **Resta en float32** | −0,989990234375     |
| **Resta en float64** | −0,9900000000000091 |
| Valor exacto               | −0,99               |

| Formato | Error relativo      | Cifras válidas | Cifras nominales |
| ------- | ------------------- | --------------- | ---------------- |
| float32 | 9,864 × 10⁻⁴ %   | ~5              | 7                |
| float64 | 9,196 × 10⁻¹³ % | ~14             | 16               |

Factor de cancelación: |a| / |a−b| = **884×**.

- En A3 la mantisa corta la ponemos nosotros (2–3 cifras) y
  perdemos casi toda la precisión; aquí la pone el hardware (24 o 53 bits) y por
  eso todavía sobreviven cifras útiles. En ambos casos el error relativo del
  resultado se multiplica por el mismo factor ~884.

---

## Conclusión final

### ¿Cuándo conviene comprar?

- Primer semestre de 2023.

### ¿Cuándo conviene vender?

El máximo fue **enero 2025 (1.000,76 CLP)**. Comparado con sus vecinos:

| Comparación         | ΔP    | Error   | Clasificación      |
| -------------------- | ------ | ------- | ------------------- |
| ene 2025 vs dic 2024 | −20,0 | ± 3,06 | DUDOSO              |
| ene 2025 vs feb 2025 | −40,0 | ± 4,14 | DUDOSO              |
| ene 2025 vs mar 2025 | −70,0 | ± 3,31 | **CONFIABLE** |

### La mejor jugada completa

- Comprar en **febrero 2023** y vender en **enero 2025**:**25,00 % ± 0,37 %** de rentabilidad, es decir 250.000 ± 3.674 CLP. La señal es unas 68 veces mayor que la incertidumbre.

### Tramos donde NO se puede recomendar

- **Abril 2023 → mayo 2023:** ΔP = 0,00 ± 5,20 → INDECIDIBLE.
- **Agosto 2024 → septiembre 2024:** ΔP = 0,00 ± 3,89 → INDECIDIBLE.
- **Mayo 2025 → junio 2025:** ΔP = 0,00 ± 2,97 → INDECIDIBLE.
- **Año 2023 completo:** Er = 20,8 % → DUDOSO.

Afirmar que el dólar "subió" o "bajó" en cualquiera de esos tramos sería irresponsable con esta precisión.

### La lección de método

- Restar dos números grandes y parecidos conserva el error absoluto pero destruye el error relativo, así que una diferencia pequeña obtenida de números grandes no es confiable aunque los operandos lo fueran.
