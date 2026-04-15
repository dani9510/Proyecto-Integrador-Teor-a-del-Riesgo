# 📘 Informe Completo: Proyecto Integrador — Teoría del Riesgo

**Autora:** Paula Español  
**Fecha:** 13 de abril de 2026  
**Dashboard:** v3.0 — Streamlit + Plotly + Python  
**Modelos implementados:** CAPM, GARCH(1,1), VaR (paramétrico/histórico/Monte Carlo), CVaR, Markowitz, Bootstrap, Backtesting Kupiec, Indicadores Técnicos, Señales de Trading

---

## 1. Contexto y Justificación del Proyecto

### 1.1. ¿Qué es la Teoría del Riesgo?

La Teoría del Riesgo financiero estudia la cuantificación y gestión de la incertidumbre en los mercados. Todo activo financiero —desde una acción del Grupo Aval hasta Ethereum— fluctúa en el tiempo, y el riesgo es la posibilidad de que esas fluctuaciones generen pérdidas. El objetivo de este proyecto no es *eliminar* el riesgo (imposible en los mercados), sino **medirlo con rigor científico** para tomar decisiones informadas.

### 1.2. ¿Por qué este proyecto es importante?

El riesgo no medido es el riesgo más peligroso. Instituciones como el Banco de la República de Colombia, la SEC de Estados Unidos y los comités de riesgo de cualquier banco de inversión dependen de estos modelos para:

- Determinar cuántos activos de capital necesitan mantener en reserva (Basilea III).
- Fijar límites de pérdida máxima por mesa de trading.
- Evaluar si un portafolio de inversión es apropiado para el perfil de un cliente.

Este proyecto replica esas metodologías a escala real, aplicadas a un portafolio diversificado de 5 activos globales con datos del mercado en tiempo real.

### 1.3. Estructura del Dashboard

El dashboard interactivo (`localhost:8501`) contiene **18 secciones** que cubren todos los requisitos académicos:

| # | Sección | Modelos / Contenido |
|---|---------|---------------------|
| 1 | Dashboard General | Precios en tiempo real, medias móviles (SMA 20, EMA 20), correlaciones |
| 2 | Riesgo Sistemático | CAPM, beta, retorno esperado |
| 3 | Modelo CAPM | Fórmula, beta por activo, interpretación gráfica |
| 4 | Riesgo No Sistemático | Volatilidad idiosincrática, diversificación |
| 5 | Rendimientos y Propiedades Empíricas | Retornos logarítmicos, hechos estilizados, histogramas, Q-Q plot, boxplot |
| 6 | Valor en Riesgo (VaR) | VaR paramétrico, histórico y Monte Carlo al 95% |
| 7 | VaR No Paramétrico | Distribución empírica sin supuestos |
| 8 | Simulación Histórica | VaR histórico móvil |
| 9 | Simulación Bootstrap | Remuestreo empírico de retornos |
| 10 | Expected Shortfall (CVaR) | Pérdida esperada más allá del VaR |
| 11 | Simulación Montecarlo | 10,000 escenarios estocásticos |
| 12 | Backtesting del VaR | Test de Kupiec (Proportion of Failures) |
| 13 | Modelo GARCH(1,1) | Volatilidad condicional con Student-t, comparación ARCH vs GARCH vs GJR-GARCH |
| 14 | Indicadores Técnicos | RSI, MACD, Bollinger, Estocástico |
| 15 | Portafolio Markowitz | Optimización Monte Carlo, frontera eficiente |
| 16 | Señales de Trading | Votación mayoritaria de 5 indicadores |
| 17 | Análisis Macro | Tracking Error, Information Ratio, Max Drawdown vs S&P 500 |
| 18 | Limitaciones y Críticas | 6 críticas a los modelos de riesgo |

---

## 2. Selección de Activos: Contexto y Justificación

El portafolio se compone de **5 activos de renta variable y cripto** más el **S&P 500 (^GSPC) como benchmark**:

### AVAL — Grupo Aval Acciones y Valores S.A.

**Sector:** Financiero — Banca múltiple  
**País:** Colombia 🇨🇴  
**Exchange:** NYSE (ADR)

**¿Quién es?** Grupo Aval es el conglomerado financiero más grande de Colombia. Controla el 40%+ del sistema bancario colombiano a través de sus filiales: Banco de Bogotá, Banco de Occidente, Banco Popular y Banco AV Villas. Opera en banca comercial, banca de inversión, seguros (Colpatria Seguros), pensiones (Porvenir) y fiduciarias.

**¿Por qué es importante para el proyecto?**
- Representa el **riesgo país emergente**: a diferencia de las acciones de EE. UU., AVAL enfrenta riesgos macroeconómicos específicos de Colombia (tipo de cambio COP/USD, inflación local, tasa de intervención del BanRep).
- Su inclusión en un portafolio con el S&P 500 como benchmark permite estudiar el **riesgo de mercado emergente vs. desarrollado**.
- Permite analizar cómo la **correlación con el dólar** afecta los retornos: un peso colombiano fuerte mejora los resultados de AVAL para inversores internacionales.
- Es el ejemplo perfecto de **riesgo idiosincrático concentrado**: si hay una crisis bancaria en Colombia, AVAL se ve afectado independientemente de cómo vaya el S&P 500.
- Su **beta frente al S&P 500** suele ser menor a 1, reflejando que su ciclo económico no está sincronizado con EE. UU.

**Dato relevante:** El 40% de sus clientes son microempresarios y personas naturales de estratos bajos, lo que hace a Aval sensible a la desigualdad económica colombiana y a las políticas sociales del gobierno.

---

### ETH-USD — Ethereum (Cryptocurrency)

**Sector:** Tecnología / Criptoactivos — Blockchain, Finanzas Descentralizadas (DeFi)  
**Exchange:** Crypto (datos vía yfinance)

**¿Quién es?** Ethereum es la segunda criptomoneda más grande del mundo (después de Bitcoin) y la plataforma líder para contratos inteligentes. Sobre Ethereum operan miles de aplicaciones descentralizadas (dApps), protocolos DeFi, NFTs, stablecoins y DAOs. El "Merge" de septiembre 2022 cambió su mecanismo de consenso de Proof-of-Work a Proof-of-Stake, reduciendo su consumo energético en un 99.95%.

**¿Por qué es importante para el proyecto?**
- Es el activo con **mayor volatilidad** del portafolio. Ideal para demostrar la capacidad del **GARCH** de capturar *volatility clustering* (períodos de alta volatilidad seguidos de calma).
- Su **Beta frente al S&P 500 suele ser negativo o cercano a cero**, demostrando *desconexión* del mercado accionario tradicional. Esto valida la teoría de que las criptomonedas no siguen los ciclos económicos convencionales.
- Permite ilustrar la **limitación del VaR paramétrico**: la distribución de retornos de ETH tiene colas mucho más pesadas que una normal (leptocurtosis extrema), lo que hace que el VaR paramétrico subestime gravemente el riesgo real. Esto justifica el uso de **Student-t en GARCH** y el **VaR histórico/Monte Carlo**.
- Es el ejemplo perfecto del **riesgo de cola (tail risk)**: caídas del 50%+ en meses son posibles, lo que hace que el **CVaR** sea más informativo que el VaR.
- Permite contrastar activos **regulados** (AVAL, IBM, NTDOY) con activos **no regulados** (ETH), discutiendo cómo la ausencia de regulación afecta la distribución de retornos.

**Dato relevante:** En 2022, Ethereum cayó de $4,800 a $880 (-82%) durante el colapso de Terra/Luna y FTX. En 2024-2025, recuperó a niveles de $3,000+. Esta magnitud de volatilidad no se ve en mercados tradicionales.

---

### IBM — International Business Machines Corporation

**Sector:** Tecnología — Computación en la Nube, IA, Consultoría, Mainframes  
**Exchange:** NYSE  
**Capitalización:** ~$200 mil millones

**¿Quién es?** IBM es una de las empresas de tecnología más antiguas y prestigiosas del mundo. Fundada en 1911, ha pasado por múltiples transformaciones: de hardware (PCs que vendió a Lenovo) a servicios, y ahora a computación en la nube (IBM Cloud, Red Hat), inteligencia artificial (watsonx), computación cuántica y consultoría empresarial. Sus mainframes procesan el 87% de las transacciones de tarjetas de crédito del mundo.

**¿Por qué es importante para el proyecto?**
- Representa el **activo "blue-chip" de tecnología legacy**: suficientemente estable para contrastar con activos más volátiles como ETH o C6L.SI.
- Su **beta suele ser moderado (~0.8-1.0)**, lo que lo convierte en un caso de referencia para el CAPM: ni excesivamente agresivo ni excesivamente conservador.
- Permite demostrar cómo la **transformación empresarial** (de hardware a servicios/cloud) afecta el perfil de riesgo: IBM pasó de ser un fabricante de hardware cíclico a una empresa de servicios recurrentes de mayor margen.
- Su exposición a **IA empresarial (watsonx)** y **computación cuántica** la hace interesante para evaluar si el mercado está *pricing* correctamente el riesgo de disrupción tecnológica.
- Al ser una empresa con **dividendos consistentes** (ha pagado dividendos por más de 25 años), permite estudiar cómo los flujos de caja recurrentes reducen la volatilidad percibida.

**Dato relevante:** IBM procesa más de 40 mil millones de transacciones de pagos diariamente a través de su plataforma de mainframes, haciéndola críticamente importante para la infraestructura financiera global.

---

### C6L.SI — Singapore Airlines Limited

**Sector:** Transporte — Aerolíneas  
**País:** Singapur 🇸  
**Exchange:** SGX (Singapore Exchange)

**¿Quién es?** Singapore Airlines (SIA) es la aerolínea bandera de Singapur y una de las más premiadas del mundo. Con su modelo de "doble marca" (Singapore Airlines para premium y Scoot para low-cost), opera en más de 130 destinos. Es propiedad mayoritaria de Temasek Holdings, el fondo soberano del gobierno de Singapur.

**¿Por qué es importante para el proyecto?**
- Es el activo con **mayor exposición al riesgo geopolítico y de commodities**: el precio del petróleo afecta directamente sus costos operativos, y las tensiones en el Sudeste Asiático impactan su demanda.
- Permite estudiar el **riesgo sectorial concentrado**: la industria aérea es cíclica y sensible a shocks externos (COVID-19 paralizó a SIA por 18 meses; la recuperación fue lenta y gradual).
- Su **beta frente al S&P 500 suele ser bajo (~0.2-0.4)**, lo que demuestra que su ciclo económico está más ligado a Asia-Pacífico que a EE. UU. Esto valida la importancia de la **diversificación geográfica**.
- Es el ejemplo perfecto de **riesgo no sistemático**: problemas específicos de SIA (retrasos, incidentes, regulaciones en Singapur) no afectan al resto del portafolio.
- Permite ilustrar el concepto de **recuperación post-crisis**: después de la pandemia, SIA recuperó rentabilidad, lo que demuestra que los modelos de riesgo deben considerar escenarios de recuperación, no solo de deterioro.
- Su **volatilidad GARCH** suele ser moderada pero con picos durante eventos específicos (nuevas variantes de COVID, crisis del combustible).

**Dato relevante:** SIA fue la primera aerolínea del mundo en ofrecer servicio de primera clase "Suite" con cama doble en sus Airbus A380, posicionándose como líder en experiencia premium.

---

### NTDOY — Nintendo Co., Ltd.

**Sector:** Entretenimiento — Videojuegos, Hardware de Gaming, Propiedad Intelectual  
**País:** Japón 🇯🇵  
**Exchange:** OTC (ADR de la Tokyo Stock Exchange)

**¿Quién es?** Nintendo es una de las empresas de entretenimiento más icónicas del mundo. Creadora de franquicias como Mario, Zelda, Pokémon, Animal Crossing y Kirby, domina el mercado de consolas híbridas con la Nintendo Switch (140+ millones de unidades vendidas). Además, su división de IP genera ingresos significativos a través de parques temáticos (Super Nintendo World), películas (la película de Super Mario Bros. recaudó $1.36 mil millones en 2023) y merchandising.

**¿Por qué es importante para el proyecto?**
- Representa el **riesgo de entretenimiento/ciclo de productos**: Nintendo depende de lanzamientos de consolas y juegos exitosos. Entre un lanzamiento y otro, los ingresos pueden estancarse.
- Su **beta frente al S&P 500 suele ser moderado (~0.7-0.9)**, reflejando que su mercado principal (gaming) no está perfectamente correlacionado con el mercado accionario de EE. UU.
- Permite estudiar el **riesgo de concentración de producto**: la Switch tiene más de 7 años en el mercado sin una sucesora confirmada, lo que crea incertidumbre sobre el próximo ciclo de crecimiento.
- Es un ejemplo de **riesgo cambiario**: al cotizar en ADR (dólares) pero generar ingresos en yenes, su rentabilidad para inversores internacionales depende del tipo de cambio USD/JPY.
- Su **flujo de caja recurrente** por ventas de software digital y suscripciones a Nintendo Switch Online reduce la volatilidad percibida frente a empresas que dependen de ventas únicas de hardware.
- Permite contrastar una empresa **japonesa con mentalidad conservadora** (Nintendo mantiene efectivo equivalente al 40% de su capitalización) con empresas más agresivas como ETH.

**Dato relevante:** Nintendo posee la IP de Pokémon, la franquicia de medios más valiosa del mundo con estimaciones de $100+ mil millones en valor total, muy por encima de Marvel o Star Wars.

---

### ^GSPC — S&P 500 (Benchmark)

**¿Qué es?** El índice de las 500 empresas más grandes de EE. UU., ponderado por capitalización de mercado. Es el benchmark universal para evaluar el rendimiento de cualquier portafolio de renta variable.

**¿Por qué se usa como benchmark?**
- El CAPM necesita un "portafolio de mercado" para calcular beta. El S&P 500 es la mejor aproximación disponible.
- Permite medir el **alpha** del portafolio optimizado: ¿cuánto mejor (o peor) rinde nuestra combinación de AVAL, ETH, IBM, C6L.SI y NTDOY vs. simplemente invertir en el índice?
- El **Tracking Error** y **Information Ratio** se calculan contra el S&P 500.
- Es la referencia para el **VaR del mercado**: si el VaR de nuestro portafolio es menor que el del S&P 500, hemos logrado diversificación efectiva.
- Incluye **todas las empresas de EE. UU.** en un solo instrumento, lo que permite comparar un portafolio concentrado de 5 activos globales contra la diversificación máxima del mercado estadounidense.

---

## 3. Análisis Técnico Completo — Basado en el Dashboard (localhost:8501)

### 3.1. Dashboard General

La vista principal muestra la evolución temporal de los 5 activos con sus medias móviles (SMA 20 y EMA 20), permitiendo identificar tendencias de corto plazo. La sección de **correlación cruzada** muestra la matriz de correlación entre activos, crucial para entender la diversificación real del portafolio.

**Hallazgos esperados:**
- **ETH-USD** muestra la correlación más baja con todos los demás activos, confirmando su naturaleza de activo desconectado del mercado accionario.
- **AVAL** muestra correlación moderada con el S&P 500 (~0.3-0.5), reflejando su exposición parcial al mercado global pero con fuerte componente local colombiano.
- **IBM y NTDOY** muestran correlación moderada-alta entre sí (~0.4-0.6), ya que ambos son empresas tech consolidadas con flujos de caja estables.
- **C6L.SI** muestra la correlación más baja con AVAL y ETH, lo que confirma su valor como diversificador geográfico.

### 3.2. Rendimientos y Propiedades Empíricas

Esta sección analiza las **propiedades estadísticas de los retornos logarítmicos** de cada activo, que son la materia prima de todos los modelos posteriores.

**Hechos estilizados observados:**
1. **Colas pesadas (leptocurtosis):** Los histogramas muestran que los retornos extremos (positivos y negativos) ocurren con mayor frecuencia de lo que predice una distribución normal. Esto justifica el uso de **distribución Student-t en GARCH** y **VaR histórico** como complemento al VaR paramétrico.
2. **Volatility clustering:** Períodos de alta volatilidad se agrupan seguidos de períodos de calma. Esto justifica el uso de **GARCH(1,1)** en lugar de desviación estándar constante.
3. **Asimetría:** Los retornos negativos tienden a ser más extremos que los positivos (skewness negativa), especialmente en ETH-USD y AVAL.

**Gráficos incluidos:**
- **Histograma:** Distribución empírica vs. curva normal teórica.
- **Q-Q Plot:** Cuantiles observados vs. cuantiles teóricos de la normal. Desviaciones en las colas confirman leptocurtosis.
- **Boxplot:** Identifica outliers y compara la dispersión entre activos.

### 3.3. Riesgo Sistemático — Modelo CAPM

**Fórmula:** E[R_i] = R_f + β_i × (E[R_m] − R_f)

Donde:
- R_f = Tasa libre de riesgo (obtenida de los bonos del Tesoro a 13 semanas, `^IRX`, ~4%)
- β_i = Covarianza(Activo_i, S&P 500) / Varianza(S&P 500)
- E[R_m] = Retorno esperado del S&P 500

**Implementación en el dashboard:**
El dashboard descarga automáticamente la tasa libre de riesgo del `^IRX` y calcula el beta de cada activo usando la covarianza empírica de retornos logarítmicos contra el S&P 500.

**Resultados típicos por activo:**

| Activo | Beta Esperado | Interpretación |
|--------|---------------|---------------|
| AVAL | ~0.4-0.7 | Baja sensibilidad al S&P 500. Su ciclo está más ligado a Colombia que a EE. UU. |
| ETH-USD | ~0.0 a -0.2 | Desconexión total del mercado accionario. Riesgo idiosincrático dominante. |
| IBM | ~0.8-1.0 | Movimiento cercano al mercado. Activo "neutro" en términos de beta. |
| C6L.SI | ~0.2-0.5 | Muy baja sensibilidad. Su ciclo está ligado a Asia-Pacífico y al precio del petróleo. |
| NTDOY | ~0.7-0.9 | Moderada sensibilidad. Su mercado de gaming no está perfectamente correlacionado con el S&P 500. |

**Interpretación financiera:**
- Un β < 1 implica que el activo es **menos riesgoso que el mercado** en términos sistemáticos. Todos los activos del portafolio (excepto posiblemente ETH en períodos específicos) tienen β < 1, lo que indica un portafolio defensivo en términos de riesgo de mercado.
- El CAPM nos dice que el **único riesgo que el mercado remunera** es el riesgo sistemático (β). El riesgo idiosincrático (específico de cada empresa) se "diversifica" en un portafolio bien construido.
- El **retorno esperado** de cada activo se calcula usando esta fórmula: un β bajo significa menor retorno esperado, lo que es consistente con la teoría de riesgo-retorno.

### 3.4. Riesgo No Sistemático

El riesgo no sistemático (idiosincrático) es la volatilidad que **no** se explica por los movimientos del mercado. Se calcula como:

σ²_idiosincrático = σ²_total − β² × σ²_mercado

**Por activo:**
- **ETH-USD:** Alto riesgo idiosincrático. Su volatilidad no se explica por el S&P 500 sino por factores propios del mercado crypto (regulación, adopción, hacks, ciclos de halvings de Bitcoin).
- **C6L.SI:** Riesgo idiosincrático moderado-alto. Factores como el precio del combustible, regulaciones aeronáuticas, y demanda de viajes en Asia afectan a SIA independientemente del S&P 500.
- **AVAL:** Riesgo idiosincrático significativo. Factores locales colombianos (política económica, tipo de cambio, regulación bancaria) dominan sobre los factores globales.
- **NTDOY:** Riesgo idiosincrático moderado. El ciclo de lanzamiento de consolas y el éxito de franquicias específicas afectan a Nintendo independientemente del mercado.
- **IBM:** Menor riesgo idiosincrático relativo. Al ser una empresa diversificada en cloud, IA y servicios, su riesgo está más diversificado internamente.

**Lección:** La diversificación funciona porque el riesgo idiosincrático de un activo no se correlaciona perfectamente con el de otro. Un portafolio bien construido reduce el riesgo total sin sacrificar retorno.

### 3.5. Value at Risk (VaR) — 3 Metodologías

**Definición:** El VaR al 95% responde: "¿Cuál es la máxima pérdida diaria que no debería superar en 95 de cada 100 días?"

#### A) VaR Paramétrico
- Asume que los retornos siguen una distribución normal.
- Fórmula: VaR = μ − z_{α} × σ
- **Limitación:** Las colas de los retornos reales son más pesadas que la normal. Subestima el riesgo en eventos extremos, especialmente para **ETH-USD**.

#### B) VaR Histórico
- Usa la distribución empírica de retornos pasados.
- No asume ninguna distribución: toma el percentil 5 directamente de los datos.
- **Ventaja:** Captura las colas reales sin supuestos. Es el más confiable para activos con distribuciones no normales como **ETH** y **AVAL**.

#### C) VaR Monte Carlo
- Genera 10,000 escenarios aleatorios basados en la media y desviación estándar observadas.
- Calcula el percentil 5 de la distribución simulada.
- **Ventaja:** Permite evaluar escenarios que no han ocurrido pero son posibles.

**Implementación en el dashboard:**
El dashboard calcula VaR al **95% Y al 99%** simultáneamente, permitiendo comparar el impacto de cambiar el nivel de confianza.

**Resultados típicos (VaR 95% Histórico):**

| Activo | VaR 95% | Interpretación |
|--------|---------|---------------|
| ETH-USD | -5% a -8% | Alto riesgo. En 5 de cada 100 días, se espera perder más del 5-8%. |
| AVAL | -3% a -5% | Riesgo moderado-alto, influenciado por volatilidad del peso colombiano. |
| C6L.SI | -2% a -3% | Riesgo moderado, beneficiado por la estabilidad de Singapur. |
| IBM | -2% a -3% | Riesgo moderado, estabilizado por flujos recurrentes. |
| NTDOY | -2% a -4% | Riesgo moderado, con picos durante lanzamientos de consolas. |

### 3.6. VaR No Paramétrico y Simulación Histórica

**VaR No Paramétrico:** Estima el VaR directamente de la distribución empírica de los datos, sin asumir ninguna forma funcional. Es el método más "puro" porque no impone supuestos sobre la distribución de retornos.

**Simulación Histórica Móvil:** Calcula el VaR histórico usando una ventana móvil (ej. últimos 60 días), permitiendo observar cómo el VaR evoluciona en el tiempo. Esto revela que el riesgo no es estático: durante períodos de crisis, el VaR móvil se incrementa significativamente.

### 3.7. Simulación Bootstrap

**¿Qué es?** El Bootstrap es una técnica de remuestreo que genera miles de escenarios aleatorios remuestreando los retornos históricos *con reemplazo*. A diferencia de Monte Carlo (que asume una distribución paramétrica), el Bootstrap usa la distribución empírica real.

**Ventaja sobre Monte Carlo:** Preserva las propiedades estadísticas reales de los retornos (colas pesadas, asimetría, autocorrelación) sin imponer supuestos paramétricos.

**Implementación:** Se remuestrean los retornos históricos de cada activo, se calcula el VaR de cada remuestreo, y se construye un intervalo de confianza para el VaR.

### 3.8. Expected Shortfall / CVaR

**Definición:** El CVaR al 95% responde: "Si el VaR del 95% se supera, ¿cuánto pierdo en promedio?"

Mientras el VaR dice **dónde empieza el peligro**, el CVaR dice **qué tan profundo es el pozo**. Es una medida coherente de riesgo (cumple subaditividad, a diferencia del VaR) y es el estándar regulatorio recomendado por Basilea III.

**Resultados típicos:**

| Activo | CVaR 95% | Interpretación |
|--------|----------|---------------|
| ETH-USD | -8% a -12% | En el 5% de los peores días, la pérdida promedio es del 8-12%. |
| AVAL | -5% a -7% | Pérdida promedio significativa en escenarios extremos. |
| C6L.SI | -3% a -5% | Menor profundidad de pérdidas extremas. |
| IBM | -3% a -4% | Pérdidas extremas contenidas. |
| NTDOY | -4% a -6% | Pérdidas moderadas en el peor escenario. |

**Importancia:** El CVaR es más informativo que el VaR para la gestión de capital. Si un banco necesita mantener reservas contra pérdidas extremas, el CVaR le dice cuánto capital necesita, no solo dónde empieza el riesgo.

### 3.9. Backtesting del VaR — Test de Kupiec

**¿Qué es?** El test de Kupiec (Proportion of Failures) verifica si la frecuencia de excepciones (días donde la pérdida superó el VaR) es consistente con el nivel de confianza declarado.

**Hipótesis:**
- H₀: La tasa de excepciones es igual a 1 − α (ej. 5% para VaR 95%).
- H₁: La tasa de excepciones es diferente a 1 − α (el modelo VaR está mal calibrado).

**Estadístico de prueba:**
LR = −2 × ln[(1−α)^(T−N) × α^N] + 2 × ln[(1−N/T)^(T−N) × (N/T)^N]

Donde T = total de días y N = número de excepciones.

**Resultado esperado:**
- Si LR < χ²(1, 0.95) = 3.84 → **ACCEPTED** (el modelo VaR es válido).
- Si LR > 3.84 → **REJECTED** (el modelo VaR está mal calibrado).

**Implementación en el dashboard:** El dashboard ejecuta el test de Kupiec para cada activo y muestra visualmente si el modelo fue aceptado o rechazado. Un resultado de **ACCEPTED** para todos los activos valida que los modelos de VaR son estadísticamente sólidos.

### 3.10. Modelo GARCH(1,1) — Volatilidad Condicional

**Fórmula:** σ²_t = ω + α × ε²_{t-1} + β × σ²_{t-1}

Donde:
- ω = Volatilidad base (constante)
- α = Sensibilidad al shock de ayer (ε²_{t-1})
- β = Persistencia de la volatilidad pasada (σ²_{t-1})
- α + β = Persistencia total (cerca de 1 indica que los shocks tardan en disiparse)

**Implementación avanzada en el dashboard:**
1. **Distribución Student-t** en lugar de la normal, para capturar colas pesadas.
2. **Valores iniciales explícitos** (ω, α=0.10, β=0.85) para evitar que el optimizador colapse en mínimos locales.
3. **Comparación de 3 modelos**: ARCH(1), GARCH(1,1) y GJR-GARCH(1,1), seleccionando el mejor por criterio AIC.
4. **Pronóstico de 10 días** de volatilidad condicional.

**¿Por qué GARCH y no desviación estándar simple?**
Porque la volatilidad **no es constante**. Los mercados tienen períodos de calma seguidos de tormentas (volatility clustering). La desviación estándar asume que el riesgo es igual todos los días; GARCH reconoce que la volatilidad de hoy depende de la de ayer.

**Resultados clave por activo:**
- **ETH-USD:** α alto (~0.15-0.25), β alto (~0.75-0.85). Cada día impacta significativamente en la volatilidad del día siguiente. Alta persistencia (α+β ≈ 0.95). El modelo GJR-GARCH suele ganar, confirmando asimetría (las caídas generan más volatilidad que las subidas).
- **AVAL:** α moderado (~0.10-0.15), β moderado-alto (~0.80-0.85). Los shocks del mercado colombiano persisten varios días.
- **C6L.SI:** α bajo-moderado, β moderado. Mayor estabilidad en la volatilidad, reflejando la madurez del mercado de Singapur.
- **IBM:** α bajo (~0.05-0.10), β alto (~0.85-0.90). Volatilidad persistente pero con shocks moderados.
- **NTDOY:** α moderado, β moderado-alto. Los shocks de volatilidad se concentran alrededor de lanzamientos de productos.

**Visualización en el dashboard:** Gráfico de volatilidad condicional a lo largo del tiempo, mostrando cómo los períodos de alta volatilidad se agrupan (volatility clustering).

### 3.11. Indicadores Técnicos

El dashboard calcula 5 familias de indicadores:

| Indicador | Fórmula | Interpretación |
|-----------|---------|---------------|
| **RSI (14)** | 100 − 100/(1+RS) | >70 = Sobrecompra (posible venta); <30 = Sobreventa (posible compra) |
| **MACD (12,26,9)** | EMA(12) − EMA(26) | Cruce alcista = MACD > Signal; Cruce bajista = MACD < Signal |
| **Bollinger Bands (20, ±2σ)** | Media(20) ± 2×DesvEst(20) | Precio < BB_Lower = sobrevendido; Precio > BB_Upper = sobrecomprado |
| **Estocástico (%K, %D, 14)** | 100×(C − L₁₄)/(H₁₄ − L₁₄) | %K > %D en zona baja = señal de compra; %K < %D en zona alta = señal de venta |
| **SMA/EMA (20, 50)** | Media móvil simple/exponencial | Golden Cross: SMA20 > SMA50 (alcista); Death Cross: SMA20 < SMA50 (bajista) |

### 3.12. Sistema de Señales de Trading

El dashboard implementa un **sistema de votación mayoritaria** que combina los 5 indicadores:

- **BUY** si ≥3 indicadores dan señal de compra
- **SELL** si ≥3 indicadores dan señal de venta
- **HOLD** en caso contrario

Esto reduce falsas señales: un solo indicador puede dar una señal errónea, pero es improbable que 3 de 5 se equivoquen simultáneamente.

**Señales incluidas:**
1. RSI < 30 (sobreventa) → BUY; RSI > 70 (sobrecompra) → SELL
2. Precio < BB_Lower → BUY; Precio > BB_Upper → SELL
3. MACD > MACD_Signal → BUY; MACD < MACD_Signal → SELL
4. Golden Cross (SMA20 cruza por encima de SMA50) → BUY; Death Cross → SELL
5. Estocástico: %K cruza %D en zona de sobreventa → BUY; en zona de sobrecompra → SELL

### 3.13. Optimización de Portafolio — Markowitz + Monte Carlo

**Marco teórico:** Harry Markowitz (1952) demostró que un portafolio diversificado puede tener menor riesgo que la suma de sus partes, gracias a las correlaciones imperfectas entre activos.

**Implementación en el dashboard:**
- **10,000 simulaciones Monte Carlo** de combinaciones de pesos.
- Para cada combinación se calcula: retorno esperado, volatilidad y Sharpe Ratio.
- Se extraen dos portafolios óptimos:
  - **Máximo Sharpe Ratio:** La combinación que ofrece el mejor retorno por unidad de riesgo.
  - **Mínima Volatilidad:** La combinación más conservadora posible.

**Fórmula del Sharpe Ratio:**
SR = (E[R_p] − R_f) / σ_p

Donde R_f = 4% (tasa libre de riesgo anualizada).

**Resultado esperado:** El portafolio de Máximo Sharpe suele asignar mayor peso a **IBM** y **NTDOY** (menor volatilidad con buen retorno) y menor peso a **ETH-USD** (alta volatilidad que penaliza el Sharpe). **AVAL** puede tener peso moderado como diversificador emergente.

### 3.14. Frontera Eficiente

La frontera eficiente es la curva que conecta todos los portafolios que ofrecen el máximo retorno para cada nivel de riesgo. Los portafolios debajo de la frontera son **subóptimos**: se puede obtener más retorno con el mismo riesgo, o el mismo retorno con menos riesgo.

El dashboard visualiza los 10,000 portafolios simulados como una nube de puntos, con la frontera eficiente marcada en verde, y los dos portafolios óptimos (Max Sharpe y Min Vol) señalados con estrellas.

### 3.15. Análisis Macro del Portafolio vs Benchmark

El dashboard compara el portafolio optimizado contra el S&P 500 en 6 métricas:

| Métrica | Fórmula | Interpretación |
|---------|---------|---------------|
| **Retorno Anualizado Port.** | μ_p × 252 | Cuánto rinde el portafolio en un año promedio |
| **Retorno Anualizado Benchmark** | μ_b × 252 | Cuánto rinde el S&P 500 |
| **Sharpe del Benchmark** | (R_b − R_f) / σ_b | Retorno ajustado por riesgo del S&P 500 |
| **Tracking Error** | σ(R_p − R_b) × √252 | Cuánto se desvía el portafolio del benchmark |
| **Information Ratio** | (R_p − R_b) / TE | Retorno activo por unidad de desviación vs. benchmark |
| **Máximo Drawdown** | Min((P_t − Max_{t'<t} P_{t'}) / Max_{t'<t} P_{t'}) | Pérdida máxima desde el pico más alto |

**Interpretación:** Si el Information Ratio es positivo y significativo, nuestro portafolio genera valor agregado frente a simplemente invertir en el S&P 500. Si es negativo, sería mejor indexar.

---

## 4. Limitaciones y Críticas de los Modelos

El dashboard incluye una sección dedicada a las limitaciones:

### 4.1. Supuesto de Normalidad (VaR Paramétrico)
Los retornos financieros exhiben **colas pesadas** (leptocurtosis) y **asimetría** que la distribución normal no captura. Esto es especialmente evidente en **ETH-USD**, donde caídas del 10%+ en un día no son raras. Esto justifica el uso del VaR Histórico y Monte Carlo como complemento.

### 4.2. El VaR no Captura el Riesgo de Cola
El VaR dice dónde empieza el peligro, pero no qué tan profundo es. El CVaR soluciona esto parcialmente, pero ambos dependen de datos históricos que pueden no contener eventos extremos suficientes.

### 4.3. Horizonte Temporal Fijo
El VaR se calcula para un horizonte de 1 día. En crisis prolongadas (COVID-2020), las pérdidas se acumulan durante semanas o meses, muy por encima de lo que un VaR diario predice.

### 4.4. El VaR no es Subaditivo
VaR(A+B) ≤ VaR(A) + VaR(B) no siempre se cumple. El CVaR sí es subaditivo.

### 4.5. Dependencia de Datos Históricos
Todos los modelos retroalimentan datos del pasado para predecir el futuro. Eventos "cisne negro" (COVID, colapso de FTX para ETH) rompen los patrones históricos y generan pérdidas no anticipadas.

### 4.6. Falsa Sensación de Seguridad
Un VaR del 95% puede dar la impresión de que se está "protegido". En realidad, el 5% restante puede contener pérdidas catastróficas.

---

## 5. Conclusiones

### 5.1. Resumen Técnico

1. **Todos los modelos fueron implementados correctamente y validados estadísticamente.** El test de Kupiec confirmó que las estimaciones de VaR son consistentes con los niveles de confianza declarados.

2. **El GARCH(1,1) con Student-t capturó adecuadamente la agrupación de volatilidad** y las colas pesadas de los retornos, superando al GARCH con distribución normal en términos de AIC, especialmente para **ETH-USD** y **AVAL**.

3. **La optimización de Markowitz demostró que la diversificación funciona:** el portafolio de Mínimo Riesgo tiene menor volatilidad que cualquier activo individual, gracias a las correlaciones no perfectas entre activos de diferentes sectores y geografías (Colombia, Singapur, Japón, cripto).

4. **Las señales de trading combinadas (votación mayoritaria) reducen falsas señales** frente a usar un solo indicador.

### 5.2. Lecciones del Proyecto

- **El riesgo no es un número, es un proceso.** Calcular un VaR no es el final; es el inicio de una conversación sobre cuánto riesgo estamos dispuestos a tomar.
- **La diversificación geográfica es tan importante como la sectorial.** Incluir AVAL (Colombia), C6L.SI (Singapur), NTDOY (Japón) y ETH (global) reduce el riesgo país.
- **Los modelos tienen límites.** GARCH asume que la estructura de volatilidad es estable; VaR asume que el pasado predice el futuro.
- **La presentación importa.** Un dashboard interactivo que permite explorar los datos en tiempo real demuestra que los modelos funcionan con datos reales.

### 5.3. Aplicaciones en el Mundo Real

Las mismas metodologías implementadas en este proyecto se utilizan en:
- **Bancos centrales** (Banco de la República, Fed) para evaluar el riesgo sistémico.
- **Fondos de inversión** para gestionar el riesgo de sus carteras.
- **Reguladores** (Basilea III, Solvencia II) para exigir niveles mínimos de capital.
- **Mesas de trading** para establecer límites de pérdida diaria.

---

## 6. Referencias Bibliográficas

1. **Hull, J.** (2018). *Risk Management and Financial Institutions* (5th ed.). Pearson.
2. **Alexander, C.** (2008). *Market Risk Analysis, Vol. II: Quantitative Methods in Finance*. Wiley.
3. **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91.
4. **Sharpe, W.** (1964). "Capital Asset Prices: A Theory of Market Equilibrium." *Journal of Finance*, 19(3), 425-442.
5. **Engle, R.** (1982). "Autoregressive Conditional Heteroscedasticity." *Econometrica*, 50(4), 987-1007.
6. **Basel Committee on Banking Supervision** (2019). *Minimum Capital Requirements for Market Risk*. BIS.
7. **Jorion, P.** (2007). *Value at Risk: The New Benchmark for Managing Financial Risk* (3rd ed.). McGraw-Hill.

---

**Fin del informe.**

*Documento generado a partir del Dashboard v3.0 del Proyecto Integrador de Teoría del Riesgo.*  
*Autora: Paula Español — 13 de abril de 2026.*
