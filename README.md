# La ganancia que se evapora

Cancelación y propagación del error con el dólar observado del SII (2022–2025).

**Universidad Católica del Maule** — Computación Numérica, Laboratorio evaluado 1
**Integrantes:** Belén Marcela Parra Fierro

---

## Qué hace este proyecto

Toma el precio mensual del dólar observado publicado por el SII, lo guarda con
**pocas cifras significativas** (simulando una mantisa corta de punto flotante) y
mide cómo ese error de representación se propaga a través de las operaciones de
compra y venta de divisas.

## Instalación y uso

```bash
git clone <url-del-repositorio>
cd problema2-dolar-sii

python -m venv .venv
source .venv/bin/activate        # en Windows:  .venv\Scripts\activate
pip install -r requirements.txt

python main.py                   # análisis completo con 2 cifras significativas
python main.py 3                 # el mismo análisis con 3 cifras
```

## Estructura

```
problema2-dolar-sii/
├── README.md                    <- este archivo
├── INFORME.md                   <- documento de entrega con la conclusión
├── main.py                      <- ejecuta todo: A1–A5, B1–B4, tabla y gráficos
├── requirements.txt             <- numpy, matplotlib
├── evaluacion_errores.csv       <- tabla de salida (generada)
├── data/
│   └── dolar_observado_sii_2022_2025.csv
├── src/
│   ├── cargar_datos.py          <- carga del CSV con np.genfromtxt
│   ├── errores.py               <- error absoluto, relativo y propagado
│   │                               + gráficos 1, 2 y 3
│   ├── anualidad.py             <- variación y error año a año
│   │                               + gráfico 4 + tabla de errores
│   └── punto_flotante.py        <- float32/float64, ida y vuelta, cancelación
│                                   + gráfico 5
└── graficos/                    <- PNG generados
```

Cada gráfico vive en el módulo que produce sus datos, de modo que `src/`
contiene exactamente los cuatro archivos que pide el enunciado.

## Parámetros del modelo

Cifras significativas (mantisa corta) = 2

Monto de trabajo = 1.000.000 CLP

Umbral de resultado dudoso = 10 % de error relativo

### Reglas de propagación aplicadas

- Multiplicación y división → se **suman los errores relativos**.
- Suma y resta → se **suman los errores absolutos**.

Son cotas pesimistas: suponen que los errores individuales se alinean en la peor
dirección posible.

### Criterio de confiabilidad adoptado

El enunciado pide establecer una norma propia frente a la cancelación. La que se
usa en todo el proyecto es:

| Clasificación  | Condición                  | Interpretación                                                            |
| --------------- | --------------------------- | -------------------------------------------------------------------------- |
| `INDECIDIBLE` | \|valor\| ≤ error absoluto | La barra de error cruza el cero: no se puede afirmar ni siquiera el signo. |
| `DUDOSO`      | error relativo > 10 %       | El signo es afirmable, pero la magnitud no sirve para decidir.             |
| `CONFIABLE`   | error relativo ≤ 10 %      | El resultado soporta una recomendación.                                   |

El umbral de 10 % se justifica porque los márgenes reales de una operación de
cambio de divisas son del orden de 1–3 %: un resultado con más de 10 % de
incerteza no permite distinguir una ganancia real de una pérdida por comisiones.

## Resultados principales (con 2 cifras significativas)

| Resultado                                   | Valor                                  |
| ------------------------------------------- | -------------------------------------- |
| Mes con mayor error de representación      | abril 2022 → 0,599 % (Ea = 4,88 CLP)  |
| Mes con menor error de representación      | agosto 2024 → 0,011 % (Ea = 0,10 CLP) |
| Error relativo medio de los 48 meses        | 0,293 %                                |
| Mes más barato del período                | febrero 2023 → 798,26 CLP             |
| Mes más caro del período                  | enero 2025 → 1.000,76 CLP             |
| Mejor jugada (comprar mín. / vender máx.) | 25,00 % ± 0,37 % de rentabilidad      |
| Variaciones mensuales indecidibles          | 5 de 47                                |
| Años confiables (A4)                       | 2025 (5,8 %) y 2024 (6,2 %)            |
| Años dudosos (A4)                          | 2022 (10,6 %) y 2023 (20,8 %)          |

**Caso emblemático de cancelación (A3):** diciembre 2022 → diciembre 2023 con
3 cifras significativas da ΔP = −1,00 ± 0,67 CLP, es decir un **error relativo
del 67 %** para una diferencia real de apenas −0,99 CLP.

## Salidas generadas

`evaluacion_errores.csv` reúne toda la evaluación de error en un solo archivo,
con una columna `tipo` que separa las secciones: error de representación de cada
mes, las 47 variaciones mensuales, la variación anual de cada año y cada par
compra-venta evaluado (101 filas en total).

| Gráfico                            | Descripción                            | Módulo               |
| ----------------------------------- | --------------------------------------- | --------------------- |
| `1_serie_mensual.png`             | Serie del dólar, real vs. aproximado   | `errores.py`        |
| `2_variaciones_cancelacion.png`   | ΔP mes a mes; en gris las indecidibles | `errores.py`        |
| `3_error_representacion.png`      | Error absoluto y relativo del redondeo  | `errores.py`        |
| `4_rentabilidad_desde_minimo.png` | Rentabilidad comprando en el mínimo    | `anualidad.py`      |
| `5_deriva_punto_flotante.png`     | Deriva de la ida y vuelta CLP→USD→CLP | `punto_flotante.py` |

## Fuente de datos

Dólar observado del Servicio de Impuestos Internos (SII), promedio mensual, enero
2022 – diciembre 2025. Archivo `data/dolar_observado_sii_2022_2025.csv`
(48 registros: `anio, mes, mes_num, dolar_observado_promedio_clp`).
