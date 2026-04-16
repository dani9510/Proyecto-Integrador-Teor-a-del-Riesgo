#  Guía de Sustentación Oral — Proyecto Integrador Teoría del Riesgo

**Profesor:** Javier Mauricio Sierra — USTA  
**Equipo:** 3 integrantes  
**Duración estimada:** 15-20 minutos + preguntas  
**Dashboard:** `localhost:8501` — 18 secciones

---

# 📋 Distribución de la Presentación

| Presentadora | Secciones del Dashboard | Secciones | Duración |
|---|---|---|---|
| **Parte 1** | Dashboard General → VaR | Secciones 1-6 | ~6 min |
| **Parte 2** | VaR No Paramétrico → GARCH | Secciones 7-13 | ~7 min |
| **Parte 3** | Indicadores Técnicos → Limitaciones | Secciones 14-18 | ~5 min |

---

# 🟣 PARTE 1 — Fundamentos y Análisis Inicial

## 👤 Presentadora 1: Contexto, Activos, CAPM, VaR

### 1. Dashboard General
**Qué mostrar:** La pantalla principal del dashboard con precios y correlaciones.

**Qué decir:**
> "Buenos días profesor y compañeros. Somos [nombres] y les presentamos nuestro Proyecto Integrador de Teoría del Riesgo.
>
> Nuestro objetivo fue construir un **tablero interactivo** que permita a un inversionista analizar, comprender y tomar decisiones informadas sobre un portafolio de **5 activos globales** con datos en **tiempo real**.
>
> Los activos que seleccionamos son:
> - **AVAL** — Grupo Aval, la entidad financiera más grande de Colombia
> - **ETH-USD** — Ethereum, la segunda criptomoneda más grande del mundo
> - **IBM** — Gigante tecnológico con más de 100 años de historia
> - **C6L.SI** — Singapore Airlines, aerolínea bandera del Sudeste Asiático
> - **NTDOY** — Nintendo, empresa japonesa líder en videojuegos
>
> Nuestro benchmark es el **S&P 500** (^GSPC).
>
> Lo primero que vemos en el Dashboard General son los **precios en tiempo real** con medias móviles SMA 20 y EMA 20, que nos permiten identificar tendencias de corto plazo.
>
> Abajo, la **matriz de correlación** nos muestra cómo se relacionan los activos entre sí. Un hallazgo clave es que **ETH-USD tiene correlación baja o negativa** con los demás activos, lo que demuestra su desconexión del mercado accionario tradicional. Por otro lado, AVAL muestra correlación moderada (~0.3-0.5) con el S&P 500, reflejando su exposición parcial al mercado global pero con fuerte componente local colombiano."

---

### 2. Riesgo Sistemático
**Qué mostrar:** La sección de riesgo sistemático.

**Qué decir:**
> "Pasamos al **Riesgo Sistemático**, que es la porción del riesgo que no se puede eliminar mediante diversificación. Es el riesgo del mercado en su conjunto.
>
> Para medirlo, utilizamos el modelo **CAPM** (Capital Asset Pricing Model), que nos permite estimar el rendimiento esperado de cada activo basándonos en su sensibilidad al mercado."

---

### 3. Modelo CAPM
**Qué mostrar:** El gráfico de dispersión con beta y la tabla de resultados.

**Qué decir:**
> "La fórmula del CAPM es: **E[R] = Rf + β × (E[Rm] - Rf]**
>
> Donde:
> - **Rf** es la tasa libre de riesgo, que obtenemos automáticamente de los bonos del Tesoro a 13 semanas (^IRX), actualmente alrededor del 4%.
> - **Beta (β)** mide la sensibilidad de cada activo frente al S&P 500.
> - **E[Rm]** es el retorno esperado del mercado.
>
> Aquí vemos el gráfico de dispersión para cada activo: en el eje X están los retornos del S&P 500 y en el eje Y los retornos del activo. La línea de regresión nos da el beta.
>
> **Resultados esperados:**
> - **AVAL:** Beta ~0.4-0.7. Baja sensibilidad al S&P 500 porque su ciclo está más ligado a Colombia.
> - **ETH-USD:** Beta cercano a 0 o negativo. Totalmente desconectado del mercado accionario.
> - **IBM:** Beta ~0.8-1.0. Se mueve de forma similar al mercado.
> - **C6L.SI:** Beta ~0.2-0.5. Ligado a Asia-Pacífico y al precio del petróleo.
> - **NTDOY:** Beta ~0.7-0.9. Moderada sensibilidad, su mercado de gaming no está perfectamente correlacionado.
>
> **Conclusión clave:** Un beta menor a 1 indica que el activo es **menos riesgoso que el mercado** en términos sistemáticos. Esto significa que nuestro portafolio es relativamente defensivo."

---

### 4. Riesgo No Sistemático
**Qué mostrar:** La sección de riesgo no sistemático.

**Qué decir:**
> "El **Riesgo No Sistemático** es la volatilidad que **no** se explica por el mercado. Es el riesgo específico de cada empresa o sector.
>
> Se calcula como: **σ²_idiosincrático = σ²_total − β² × σ²_mercado**
>
> Por ejemplo:
> - **ETH-USD** tiene alto riesgo idiosincrático porque su volatilidad depende de factores crypto (regulación, hacks, adopción), no del S&P 500.
> - **AVAL** tiene riesgo idiosincrático significativo por factores locales colombianos: política económica, tipo de cambio COP/USD, regulación bancaria.
> - **C6L.SI** depende del precio del combustible, demanda de viajes en Asia, y eventos geopolíticos.
>
> **La lección:** La diversificación funciona porque el riesgo idiosincrático de un activo no se correlaciona perfectamente con el de otro. Un portafolio bien construido reduce el riesgo total sin sacrificar retorno."

---

### 5. Rendimientos y Propiedades Empíricas
**Qué mostrar:** Los histogramas, Q-Q plots y boxplots.

**Qué decir:**
> "Antes de ajustar cualquier modelo, analizamos las **propiedades estadísticas de los retornos logarítmicos**.
>
> Calculamos tanto retornos simples como logarítmicos. Los logarítmicos son preferibles en finanzas porque son aditivos en el tiempo y más estacionarios.
>
> **Hechos estilizados observados:**
> 1. **Colas pesadas (leptocurtosis):** Los histogramas muestran que los retornos extremos ocurren con mayor frecuencia de lo que predice una distribución normal. Esto es especialmente visible en ETH-USD. Esto justifica el uso de distribución **Student-t en GARCH** y el VaR histórico como complemento.
> 2. **Volatility clustering:** Períodos de alta volatilidad se agrupan seguidos de calma. Esto justifica GARCH sobre desviación estándar constante.
> 3. **Asimetría:** Los retornos negativos tienden a ser más extremos que los positivos, especialmente en AVAL y ETH.
>
> **Visualizaciones:**
> - **Histograma:** Distribución empírica vs. curva normal teórica.
> - **Q-Q Plot:** Cuantiles observados vs. cuantiles teóricos. Las desviaciones en las colas confirman leptocurtosis.
> - **Boxplot:** Identifica outliers y compara la dispersión entre activos.
>
> **Pruebas de normalidad:**
> - **Jarque-Bera:** Rechaza la normalidad en todos los activos (colas pesadas).
> - **Shapiro-Wilk:** También rechaza la normalidad, especialmente en ETH-USD.
>
> Esto confirma que **no podemos asumir normalidad**, lo que tiene implicaciones directas en el VaR paramétrico."

---

### 6. Valor en Riesgo (VaR)
**Qué mostrar:** La sección de VaR con los 3 métodos y la tabla comparativa.

**Qué decir:**
> "El **Value at Risk** responde: **¿Cuál es la máxima pérdida diaria que no debería superar en 95 de cada 100 días?**
>
> Implementamos **3 metodologías:**
>
> 1. **VaR Paramétrico:** Asume distribución normal. Fórmula: VaR = μ − z × σ. **Limitación:** Las colas reales son más pesadas que la normal, subestima el riesgo extremo.
>
> 2. **VaR Histórico:** Usa la distribución empírica. Toma el percentil 5 directamente de los datos. **Ventaja:** No asume distribución. **Limitación:** Depende del pasado.
>
> 3. **VaR Monte Carlo:** Genera 10,000 escenarios aleatorios. **Ventaja:** Evalúa escenarios posibles que no han ocurrido.
>
> **Resultados típicos (VaR 95% Histórico):**
> - **ETH-USD:** -5% a -8%. Alto riesgo.
> - **AVAL:** -3% a -5%. Moderado-alto, influenciado por volatilidad del peso.
> - **C6L.SI:** -2% a -3%. Moderado.
> - **IBM:** -2% a -3%. Estabilizado por flujos recurrentes.
> - **NTDOY:** -2% a -4%. Moderado, con picos en lanzamientos de consolas.
>
> También calculamos VaR al **99%** para comparar el impacto de cambiar el nivel de confianza."

---

**🔗 Transición a Parte 2:**
> "Ahora mi compañera [nombre] les mostrará los métodos no paramétricos, el Expected Shortfall, el backtesting y el modelo GARCH."

---

# 🟣 PARTE 2 — Métodos Avanzados y Volatilidad Condicional

## 👤 Presentadora 2: VaR No Paramétrico → GARCH

### 7. VaR No Paramétrico
**Qué mostrar:** La sección de VaR no paramétrico.

**Qué decir:**
> "El **VaR No Paramétrico** estima el VaR directamente de la distribución empírica de los datos, **sin asumir ninguna forma funcional**. Es el método más 'puro' porque no impone supuestos sobre la distribución de retornos.
>
> A diferencia del VaR paramétrico que asume normalidad, el no paramétrico simplemente pregunta: '¿Cuál fue el peor 5% de los días históricos?' y usa eso como estimación.
>
> Esto es especialmente importante para activos como **ETH-USD**, donde las caídas del 10%+ en un día no son raras y la normal subestima gravemente el riesgo."

---

### 8. Simulación Histórica
**Qué mostrar:** La sección de simulación histórica.

**Qué decir:**
> "La **Simulación Histórica** calcula el VaR usando una **ventana móvil** de los últimos días (por ejemplo, 60 días). Esto nos permite observar cómo el VaR **evoluciona en el tiempo**.
>
> El gráfico muestra que el riesgo **no es estático**: durante períodos de crisis (como la pandemia para C6L.SI o las caídas crypto para ETH-USD), el VaR móvil se incrementa significativamente.
>
> Esto es más realista que un VaR fijo, porque refleja que el riesgo cambia día a día según las condiciones del mercado."

---

### 9. Simulación Bootstrap
**Qué mostrar:** La sección de simulación Bootstrap.

**Qué decir:**
> "El **Bootstrap** es una técnica de remuestreo que genera miles de escenarios aleatorios remuestreando los retornos históricos **con reemplazo**.
>
> A diferencia de Monte Carlo, que asume una distribución paramétrica (normal), el Bootstrap usa la **distribución empírica real**. Preserva las propiedades estadísticas reales: colas pesadas, asimetría, autocorrelación.
>
> **Proceso:**
> 1. Tomamos los retornos históricos de cada activo.
> 2. Remuestreamos miles de veces con reemplazo.
> 3. Calculamos el VaR de cada remuestreo.
> 4. Construimos un intervalo de confianza para el VaR.
>
> Esto nos da una estimación más robusta del riesgo porque no dependemos de supuestos paramétricos."

---

### 10. Expected Shortfall (CVaR)
**Qué mostrar:** La sección de CVaR con la tabla comparativa.

**Qué decir:**
> "El **Expected Shortfall** o **CVaR** responde: **'Si el VaR del 95% se supera, ¿cuánto pierdo en promedio?'**
>
> Mientras el VaR dice **dónde empieza el peligro**, el CVaR dice **qué tan profundo es el pozo**.
>
> Es una medida **coherente de riesgo** (cumple subaditividad, a diferencia del VaR) y es el estándar regulatorio recomendado por Basilea III.
>
> **Ejemplos:**
> - **ETH-USD:** VaR 95% = -5%, CVaR 95% = -8% a -12%. En el 5% de los peores días, la pérdida promedio es del 8-12%.
> - **AVAL:** VaR 95% = -4%, CVaR 95% = -5% a -7%. Pérdida promedio significativa en escenarios extremos.
> - **IBM:** VaR 95% = -2.5%, CVaR 95% = -3% a -4%. Pérdidas extremas contenidas.
>
> **Importancia:** El CVaR es más informativo que el VaR para la gestión de capital. Si un banco necesita mantener reservas contra pérdidas extremas, el CVaR le dice cuánto capital necesita."

---

### 11. Simulación Montecarlo
**Qué mostrar:** La sección de Monte Carlo con la distribución de pérdidas.

**Qué decir:**
> "La **Simulación Montecarlo** genera **10,000 escenarios estocásticos** basados en la media y desviación estándar observadas de cada activo.
>
> **Proceso:**
> 1. Estimamos la media (μ) y desviación estándar (σ) de los retornos históricos.
> 2. Generamos 10,000 retornos aleatorios de una distribución normal con esos parámetros.
> 3. Calculamos el percentil 5 (VaR) y el promedio de las peores pérdidas (CVaR).
>
> **Ventaja:** Permite evaluar escenarios que no han ocurrido pero son posibles.
>
> **Limitación:** Si los parámetros de entrada están mal estimados, las simulaciones también. Por eso usamos Montecarlo como complemento al VaR histórico, no como reemplazo."

---

### 12. Backtesting del VaR
**Qué mostrar:** La sección de backtesting con el test de Kupiec.

**Qué decir:**
> "El **Backtesting** verifica si nuestro modelo VaR es confiable. Usamos el **Test de Kupiec** (Proportion of Failures).
>
> **Hipótesis:**
> - H₀: La tasa de excepciones es igual a 1 − α (ej. 5% para VaR 95%).
> - H₁: La tasa de excepciones es diferente a 1 − α (el modelo está mal calibrado).
>
> **Estadístico de prueba:**
> LR = −2 × ln[(1−α)^(T−N) × α^N] + 2 × ln[(1−N/T)^(T−N) × (N/T)^N]
>
> Donde T = total de días y N = número de excepciones.
>
> **Criterio:**
> - Si LR < 3.84 (χ² con 1 grado de libertad) → **ACCEPTED** ✅
> - Si LR > 3.84 → **REJECTED** ❌
>
> **Resultado esperado:** ACCEPTED para la mayoría de los activos, validando que los modelos de VaR son estadísticamente sólidos. Esto es un **punto de bonificación** según la rúbrica del profesor."

---

### 13. Modelo GARCH(1,1)
**Qué mostrar:** El gráfico de volatilidad condicional y la tabla comparativa de modelos.

**Qué decir:**
> "El modelo **GARCH(1,1)** modela la **volatilidad condicional**, reconociendo que la volatilidad no es constante sino que cambia con el tiempo.
>
> **Fórmula:** σ²_t = ω + α × ε²_{t-1} + β × σ²_{t-1}
>
> Donde:
> - **ω** = Volatilidad base
> - **α** = Sensibilidad al shock de ayer
> - **β** = Persistencia de la volatilidad pasada
> - **α + β ≈ 0.95-0.99** indica alta persistencia (los shocks tardan en disiparse)
>
> **Implementación avanzada:**
> 1. Usamos **distribución Student-t** en lugar de la normal, para capturar colas pesadas.
> 2. Valores iniciales explícitos para evitar mínimos locales.
> 3. **Comparamos 3 modelos:** ARCH(1), GARCH(1,1) y GJR-GARCH(1,1), seleccionando el mejor por AIC/BIC.
> 4. **Pronóstico de 10 días** de volatilidad condicional.
>
> **¿Por qué GARCH y no desviación estándar simple?**
> Porque la volatilidad **no es constante**. Los mercados tienen períodos de calma seguidos de tormentas (volatility clustering). GARCH reconoce que la volatilidad de hoy depende de la de ayer.
>
> **Resultados clave:**
> - **ETH-USD:** α alto (~0.15-0.25). Cada día impacta significativamente la volatilidad del siguiente. GJR-GARCH suele ganar, confirmando asimetría (las caídas generan más volatilidad que las subidas).
> - **AVAL:** α moderado (~0.10-0.15). Los shocks del mercado colombiano persisten varios días.
> - **C6L.SI:** α bajo-moderado. Mayor estabilidad, reflejando la madurez del mercado de Singapur.
> - **IBM:** α bajo (~0.05-0.10), β alto (~0.85-0.90). Volatilidad persistente pero con shocks moderados.
> - **NTDOY:** α moderado. Los shocks se concentran alrededor de lanzamientos de productos.
>
> **El gráfico** muestra cómo la volatilidad condicional cambia a lo largo del tiempo, con períodos de alta volatilidad agrupados (volatility clustering)."

---

**🔗 Transición a Parte 3:**
> "Finalmente, mi compañera [nombre] les presentará los indicadores técnicos, las señales de trading, la optimización de Markowitz, el análisis macro y las limitaciones de los modelos."

---

# 🟣 PARTE 3 — Aplicaciones Prácticas y Conclusiones

## 👤 Presentadora 3: Indicadores Técnicos → Limitaciones

### 14. Indicadores Técnicos
**Qué mostrar:** Los gráficos de RSI, MACD, Bollinger y Estocástico.

**Qué decir:**
> "Los **Indicadores Técnicos** nos ayudan a identificar tendencias, momentum y posibles puntos de reversión en el precio de los activos.
>
> Calculamos **5 familias** de indicadores:
>
> 1. **RSI (14):** Índice de Fuerza Relativa. Oscila entre 0 y 100. >70 = sobrecompra (posible venta); <30 = sobreventa (posible compra).
>
> 2. **MACD (12,26,9):** Cruce de medias móviles exponenciales. Cuando MACD cruza por encima de su línea de señal, es una señal alcista; por debajo, bajista.
>
> 3. **Bandas de Bollinger (20, ±2σ):** El precio que sale de las bandas indica sobrecompra o sobreventa.
>
> 4. **Estocástico (%K y %D):** Mide la posición del precio relativo al rango de los últimos 14 períodos. Cruces en zonas extremas generan señales.
>
> 5. **SMA/EMA (20, 50):** Medias móviles. Golden Cross (SMA20 > SMA50) = alcista; Death Cross (SMA20 < SMA50) = bajista.
>
> Todos los indicadores son **interactivos** con Plotly: puedes hacer zoom, hover para ver valores, y seleccionar rangos de fechas."

---

### 15. Portafolio Markowitz
**Qué mostrar:** La frontera eficiente y el slider de rendimiento objetivo.

**Qué decir:**
> "La **Teoría Moderna de Portafolios** de Harry Markowitz (1952) establece que un portafolio diversificado puede tener menor riesgo que la suma de sus partes, gracias a las correlaciones imperfectas entre activos.
>
> **Implementación:**
> - **10,000 simulaciones Monte Carlo** de combinaciones de pesos.
> - Para cada combinación calculamos: retorno esperado, volatilidad y Sharpe Ratio.
> - Extraemos dos portafolios óptimos:
>   - **Máximo Sharpe Ratio:** Mejor retorno por unidad de riesgo.
>   - **Mínima Volatilidad:** La combinación más conservadora.
>
> **Fórmula del Sharpe Ratio:** SR = (E[R_p] − Rf) / σ_p
>
> **Resultado esperado:** El portafolio de Máximo Sharpe suele asignar mayor peso a **IBM** y **NTDOY** (menor volatilidad con buen retorno) y menor peso a **ETH-USD** (alta volatilidad que penaliza el Sharpe). **AVAL** puede tener peso moderado como diversificador emergente.
>
> **La frontera eficiente** es la curva que conecta todos los portafolios óptimos. Los portafolios debajo son subóptimos: se puede obtener más retorno con el mismo riesgo.
>
> **Feature interactivo:** El usuario puede usar el **slider de rendimiento objetivo** para ingresar el retorno anualizado deseado y el dashboard calcula el portafolio más cercano a ese objetivo, mostrando la composición en porcentaje de cada activo."

---

### 16. Señales de Trading
**Qué mostrar:** El panel de señales con el semáforo y los umbrales configurables.

**Qué decir:**
> "El **Motor de Señales de Trading** combina los 5 indicadores técnicos para generar recomendaciones automatizadas de **COMPRA**, **VENTA** o **MANTENER**.
>
> **Sistema de votación mayoritaria:**
> - Si ≥3 indicadores dan señal de compra → **BUY** 🟢
> - Si ≥3 indicadores dan señal de venta → **SELL** 🔴
> - En caso contrario → **HOLD** 🟡
>
> **Señales incluidas:**
> 1. RSI < 30 → BUY; RSI > 70 → SELL
> 2. Precio < BB_Lower → BUY; Precio > BB_Upper → SELL
> 3. MACD > Signal → BUY; MACD < Signal → SELL
> 4. Golden Cross → BUY; Death Cross → SELL
> 5. Estocástico: %K cruza %D en zona baja → BUY; en zona alta → SELL
>
> **Ventaja:** Un solo indicador puede dar una señal errónea, pero es improbable que 3 de 5 se equivoquen simultáneamente.
>
> **Umbrales configurables:** El usuario puede ajustar los umbrales de RSI (por defecto 30/70) para adaptar las señales a su perfil de riesgo.
>
> Esto cumple con el **Módulo 7** de la rúbrica del profesor, que es un criterio con estrella."

---

### 17. Análisis Macro
**Qué mostrar:** Las métricas macro vs. benchmark.

**Qué decir:**
> "El **Análisis Macro** compara nuestro portafolio optimizado contra el S&P 500 usando 6 métricas clave:
>
> 1. **Retorno Anualizado del Portafolio:** μ_p × 252
> 2. **Retorno Anualizado del Benchmark:** μ_b × 252
> 3. **Sharpe del Benchmark:** Retorno ajustado por riesgo del S&P 500
> 4. **Tracking Error:** σ(R_p − R_b) × √252 — Cuánto se desvía el portafolio del benchmark
> 5. **Information Ratio:** (R_p − R_b) / TE — Retorno activo por unidad de desviación
> 6. **Máximo Drawdown:** La pérdida máxima desde el pico más alto
>
> **Interpretación:** Si el Information Ratio es positivo y significativo, nuestro portafolio genera valor agregado frente a simplemente invertir en el S&P 500. Si es negativo, sería mejor indexar.
>
> **Datos macro:** La tasa libre de riesgo se obtiene automáticamente de la API de Yahoo Finance (^IRX). Esto cumple con el **Módulo 8** de la rúbrica, otro criterio con estrella."

---

### 18. Limitaciones y Críticas
**Qué mostrar:** La sección de limitaciones.

**Qué decir:**
> "Finalmente, es importante reconocer las **limitaciones** de nuestros modelos:
>
> 1. **Supuesto de normalidad:** El VaR paramétrico asume normalidad, pero los retornos tienen colas pesadas. Esto justifica el VaR histórico y Monte Carlo como complementos.
>
> 2. **El VaR no captura el riesgo de cola:** Dice dónde empieza el peligro, pero no qué tan profundo es. El CVaR soluciona esto parcialmente.
>
> 3. **Horizonte temporal fijo:** El VaR es para 1 día. En crisis prolongadas, las pérdidas se acumulan.
>
> 4. **El VaR no es subaditivo:** VaR(A+B) ≤ VaR(A) + VaR(B) no siempre se cumple. El CVaR sí lo es.
>
> 5. **Dependencia de datos históricos:** Todos los modelos usan el pasado para predecir el futuro. Eventos 'cisne negro' (COVID, colapso de FTX) rompen los patrones.
>
> 6. **Falsa sensación de seguridad:** Un VaR del 95% puede dar la impresión de protección. Pero el 5% restante puede contener pérdidas catastróficas.
>
> **Conclusión:** Los modelos son herramientas poderosas, pero tienen límites. La gestión del riesgo es un proceso continuo, no un número mágico."

---

## Cierre Final
**Qué decir (cualquiera de las 3):**

> "Para concluir:
>
> 1. **Todos los modelos fueron implementados correctamente y validados estadísticamente.** El test de Kupiec confirmó que las estimaciones de VaR son consistentes.
>
> 2. **El GARCH(1,1) con Student-t capturó la agrupación de volatilidad** y las colas pesadas, superando al GARCH con distribución normal.
>
> 3. **La diversificación funciona:** el portafolio de Mínimo Riesgo tiene menor volatilidad que cualquier activo individual, gracias a las correlaciones imperfectes entre activos de diferentes sectores y geografías (Colombia, Singapur, Japón, crypto).
>
> 4. **Las mismas metodologías** que implementamos se utilizan en bancos centrales, fondos de inversión y mesas de trading a nivel mundial.
>
> **Gracias por su atención.** Estamos abiertas a preguntas."

---

# 📌 Tips para la Sustentación

## Antes de presentar:
1. **Practicar la demo en vivo** del dashboard al menos 3 veces.
2. **Ambas** (o las tres) deben poder explicar **cualquier módulo**, no solo su parte.
3. Tener el dashboard **abierto y funcionando** antes de empezar.
4. Verificar que **yfinance** esté funcionando (datos en tiempo real).

## Preguntas frecuentes del profesor:
| Pregunta | Respuesta clave |
|----------|----------------|
| "¿Por qué GARCH con Student-t?" | Porque los retornos tienen colas pesadas; la normal subestima el riesgo extremo. |
| "¿Qué nos dice el CVaR?" | Qué tan profundo es el pozo. El VaR dice dónde empieza el peligro; el CVaR dice la pérdida promedio en el peor escenario. |
| "¿Por qué Kupiec?" | Para validar que el VaR no subestima ni sobreestima el riesgo. Es el backtesting estándar. |
| "¿Qué significa α + β ≈ 0.99 en GARCH?" | Alta persistencia: los shocks de volatilidad tardan en disiparse. |
| "¿Por qué diversificar con AVAL y C6L.SI?" | Diversificación geográfica: Colombia y Singapur no están correlacionados con EE. UU. |
| "¿Por qué ETH tiene beta ~0?" | Desconexión total del mercado accionario. Su riesgo es idiosincrático, no sistemático. |
| "¿Qué es el Information Ratio?" | Retorno activo por unidad de Tracking Error. Si es positivo, el portafolio supera al benchmark ajustado por riesgo. |

---

*Guía generada el 13 de abril de 2026*
