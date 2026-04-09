# 📊 Reporte Técnico: Análisis de Riesgo y Modelos Econométricos
**Proyecto Integrador - Teoría del Riesgo**
**Perfil:** Persona 2 — Riesgo Financiero

---

## 1. Resumen Ejecutivo
El presente documento detalla la implementación y los resultados de los modelos de riesgo financiero aplicados a un portafolio diversificado de 6 activos (`AVAL`, `ETH-USD`, `IBM`, `C6L.SI`, `NTDOY` y el benchmark `^GSPC`). Se han utilizado técnicas de frontera para la estimación de volatilidad, retornos esperados y métricas de valor en riesgo, asegurando la robustez estadística mediante pruebas de backtesting.

---

## 2. Metodología Aplicada

### 2.1. Modelo CAPM (Capital Asset Pricing Model)
Se calculó la relación entre cada activo y el mercado utilizando el índice **S&P 500** como benchmark.
- **Beta ($\beta$):** Mide la sensibilidad del activo ante movimientos del mercado.
- **Retorno Esperado ($E[R]$):** Calculado usando una Tasa Libre de Riesgo ($R_f$) dinámica basada en los bonos del tesoro a 13 semanas (`^IRX`).

### 2.2. Modelos de Volatilidad GARCH(1,1)
Para capturar la agrupación de volatilidad (*volatility clustering*), se ajustó un modelo **GARCH(1,1)** sobre los retornos logarítmicos.
- **Métrica Top:** Se incluyeron los **Residuos Estandarizados** para validar que el modelo eliminó la autocorrelación en la varianza.
- **Diagnóstico:** Uso del **AIC** para certificar la calidad del ajuste.

### 2.3. Value at Risk (VaR) y CVaR
Se implementaron tres metodologías para la medición de pérdidas potenciales con un 95% de confianza:
1. **VaR Paramétrico:** Basado en la distribución normal.
2. **VaR Histórico:** Basado en la distribución empírica de datos pasados.
3. **VaR Monte Carlo:** Generado mediante 10,000 simulaciones estocásticas.
4. **CVaR (Expected Shortfall):** Mide la pérdida promedio en el 5% de los peores escenarios.

---

## 3. Resultados y Hallazgos Clave

| Activo | Ticker | Beta ($\beta$) | $E[R]$ Anual | VaR 95% (H) | CVaR 95% | Vol. GARCH |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IBM** | `IBM` | 0.78 | 13.3% | -2.6% | -4.7% | 2.47% |
| **Nintendo** | `NTDOY` | 0.79 | 13.4% | -3.6% | -4.9% | 1.89% |
| **Grupo Aval** | `AVAL` | 0.74 | 12.7% | -3.8% | -5.2% | 2.60% |
| **Singapore Air**| `C6L.SI`| 0.24 | 6.5% | -1.2% | -2.5% | 0.81% |
| **Ethereum** | `ETH-USD`| -0.13 | 1.9% | -5.7% | -8.5% | 3.85% |

### 🔍 Interpretación Detallada de los Datos (Deep Dive)

#### 1. Binomio Riesgo-Retorno: El Caso de Nintendo e IBM
Al observar los datos de **Nintendo (NTDOY)** e **IBM**, notamos que el mercado les asigna una prima de riesgo casi idéntica. Sus Betas de **0.78** y **0.79** sugieren que ambos activos son un 20% menos volátiles que el S&P 500. 
- **Curiosidad del Retorno:** Sus retornos esperados ($E[R]$) de **~13.4%** son los más altos del grupo para activos tradicionales. Esto nos dice que, ante una recuperación del mercado, estos dos serían los motores de rentabilidad de tu portafolio sin exponerte a un riesgo extremo.

#### 2. La Anomalía de Ethereum (`ETH-USD`)
Ethereum presenta un fenómeno fascinante en tus datos: un **Beta negativo (-0.13)**. 
- **Interpretación Real:** En finanzas, un Beta cercano a cero o negativo no siempre significa "seguridad", sino **Desconexión**. Mientras que las acciones siguen los ciclos económicos de EE. UU., Ethereum sigue sus propios ciclos tecnológicos y de adopción.
- **Riesgo de Tail (CVaR):** Su **CVaR de -8.5%** es alarmante frente al resto. Si ocurre un "lunes negro", la caída promedio de Ethereum sería casi el triple que la de **Singapore Airlines** (-2.5%). Es el activo que más capital te puede "quemar" en un evento extremo.

#### 3. El "Ancla" de Estabilidad: Singapore Airlines (`C6L.SI`)
Con un Beta de **0.24**, este activo actúa como un amortiguador. 
- **Dato Clave:** Su **VaR del -1.2%** implica que, estadísticamente, solo pierdes más de esa cantidad 1 de cada 20 días. En un portafolio de riesgo, tener un activo así permite "dormir tranquilo" mientras los otros (como AVAL o ETH) fluctúan agresivamente.

#### 4. Análisis de Volatilidad GARCH
Nuestro modelo GARCH detectó que la **"Memoria de Volatilidad"** de **Grupo Aval (2.60%)** es mayor que la de **IBM (2.47%)**. 
- **Qué significa:** Esto sugiere que los shocks de precio en el sector bancario colombiano tienden a durar más días en el sistema antes de disiparse, comparado con la tecnología estadounidense, que es más líquida y "limpia" sus shocks más rápido.

---

## 4. Validación y Backtesting Avanzado
Se aplicó el **Test de Kupiec** (Proportion of Failures) para validar la precisión del VaR Paramétrico.
- **Resultado:** **ACCEPTED** para todos los activos.
- **Significancia:** Esto valida que la "capa de protección" que diseñamos (tu VaR del 95%) es matemáticamente honesta. No estamos subestimando el riesgo ni asustando al inversor innecesariamente.

---

## 5. Glosario Rápido para Sustentación (Tips para la "Persona 2")
Si el profesor te pregunta "¿Qué hiciste?", puedes usar estas interpretaciones basadas en tus datos:
- **"¿Por qué incluiste GARCH?":** Porque la volatilidad no es constante; el modelo GARCH nos dio la 'volatilidad inteligente' que se adapta a los cambios del mercado de ayer para predecir el riesgo de hoy.
- **"¿Qué nos dice el CVaR?":** Nos dice qué tan profundo es el pozo. El VaR nos dice dónde empieza el peligro, pero el CVaR nos dice cuánta sangre hay en el peor escenario posible.
- **"¿Por qué CAPM con ^IRX?":** Porque todo retorno debe compararse con la 'inversión libre de riesgo'. Mi modelo descuenta el 4% que dan los bonos para ver si realmente vale la pena arriesgarse en estas acciones.

---
**Generado por:** Antigravity AI (Nivel Senior)
**Fecha:** 8 de abril de 2026
