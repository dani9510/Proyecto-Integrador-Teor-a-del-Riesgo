# 📘 Informe Completo: Proyecto Integrador — Teoría del Riesgo

**Autora:** Paula Español  
**Fecha de generación:** 13 de abril de 2026  
**Dashboard:** v3.0 — Streamlit + Plotly + Python  
**Modelos implementados:** CAPM, GARCH(1,1), GJR-GARCH, VaR, CVaR, Markowitz, Monte Carlo

---

## 1. Contexto y Justificación del Proyecto

### 1.1. ¿Qué es la Teoría del Riesgo?

La Teoría del Riesgo financiero estudia la cuantificación y gestión de la incertidumbre en los mercados. Todo activo financiero —desde una acción de Apple hasta un ETF del S&P 500— fluctúa en el tiempo, y el riesgo es la posibilidad de que esas fluctuaciones generen pérdidas. El objetivo de este proyecto no es *eliminar* el riesgo (imposible en los mercados), sino **medirlo con rigor científico** para tomar decisiones informadas.

### 1.2. ¿Por qué este proyecto es importante?

El riesgo no medido es el riesgo más peligroso. Instituciones como el Banco de la República de Colombia, la SEC de Estados Unidos y los comités de riesgo de cualquier banco de inversión dependen de estos modelos para:
- Determinar cuántos activos de capital necesitan mantener en reserva (Basilea III).
- Fijar límites de pérdida máxima por mesa de trading.
- Evaluar si un portafolio de inversión es apropiado para el perfil de un cliente.

Este proyecto replica esas metodologías a escala real, aplicadas a un portafolio diversificado de 5 activos globales con datos del mercado en tiempo real.

### 1.3. Requisitos Académicos Cubiertos

| Requisito | Sección del dashboard | Página |
|-----------|----------------------|--------|
| Descarga de datos de mercado en tiempo real | Dashboard General | Inicio |
| Modelo CAPM (Beta, retorno esperado) | Riesgo Sistemático | 4 |
| Modelo GARCH(1,1) con Student-t | Riesgo No Sistemático | 6 |
| Value at Risk (3 métodos: paramétrico, histórico, Monte Carlo) | VaR | 7-8 |
| Expected Shortfall / CVaR | VaR | 7-8 |
| Backtesting con test de Kupiec | VaR | 9 |
| Indicadores técnicos (RSI, MACD, Bollinger, Estocástico) | Indicadores Técnicos | 11 |
| Optimización de Markowitz | Portafolio Markowitz | 12 |
| Frontera eficiente y simulación Monte Carlo | Portafolio Markowitz | 12 |
| Análisis macro del portafolio vs benchmark | Análisis Macro | 13 |
| Señales de trading combinadas | Señales de Trading | 14 |
| Sección de Limitaciones y Críticas | Limitaciones y Críticas | 15 |

---

## 2. Selección de Activos: Contexto y Justificación

El portafolio se compone de **5 activos de renta variable** más el **S&P 500 como benchmark**:

### NVDA — NVIDIA Corporation

**Sector:** Tecnología — Semiconductores / Inteligencia Artificial  
**Exchange:** NASDAQ  
**Capitalización:** ~$3.5 billones (una de las empresas más valiosas del mundo)

**¿Quién es?** NVIDIA fabrica las GPU que alimentan la revolución de la inteligencia artificial. Sus chips están en centros de datos de Google, Amazon, Meta y OpenAI. Es la empresa que más se ha beneficiado del boom de la IA generativa.

**¿Por qué es importante para el proyecto?**
- Es el activo más volátil del portafolio: ideal para demostrar la capacidad del GARCH de capturar *volatility clustering* (períodos de alta volatilidad seguidos de calma).
- Su alta correlación con el mercado tech la hace un excelente caso de estudio para CAPM: su beta debería ser mayor a 1, indicando mayor sensibilidad al S&P 500.
- Permite ilustrar el concepto de **riesgo concentrado en un sector**: aunque la IA es prometedora, una corrección en el sector semiconductores impactaría severamente al portafolio.

**Dato relevante:** En 2023-2025, NVDA acumuló retornos superiores al 200%, lo que demuestra que los modelos de riesgo deben manejar activamente no solo caídas sino también subidas extremas.

---

### AAPL — Apple Inc.

**Sector:** Tecnología — Hardware, Servicios, Ecosistema Digital  
**Exchange:** NASDAQ  
**Capitalización:** ~$3.2 billones

**¿Quién es?** La empresa más valiosa del mundo durante más de una década. Diseña iPhones, Macs, iPads, Apple Watch y opera servicios como Apple Music, iCloud y la App Store. Su ecosistema de 2.2 mil millones de dispositivos activos genera flujos de caja recurrentes y predecibles.

**¿Por qué es importante para el proyecto?**
- Representa el **activo "blue-chip" de tecnología**: suficientemente estable para contrastar con activos más volátiles como TSLA o NVDA.
- Su beta suele estar cerca de 1, lo que la convierte en el "caso de referencia" del CAPM: ni excesivamente agresiva ni excesivamente conservadora.
- Permite demostrar cómo el **dividendo recurrente** de Apple reduce su volatilidad percibida frente a empresas tech sin dividendos.

**Dato relevante:** Apple genera más del 40% de sus ingresos por servicios, un segmento de margen alto y baja volatilidad que estabiliza el precio de la acción.

---

### GOOG — Alphabet Inc. (Google)

**Sector:** Tecnología — Búsqueda, Publicidad Digital, Nube, IA  
**Exchange:** NASDAQ  
**Capitalización:** ~$2.3 billones

**¿Quién es?** La matriz de Google, YouTube, Google Cloud, Waymo (vehículos autónomos) y DeepMind (IA). Es el monopolio de facto de la búsqueda web con el 90%+ del mercado global y genera más del 80% de sus ingresos por publicidad digital.

**¿Por qué es importante para el proyecto?**
- Ofrece una **comparación directa con AAPL**: ambas son mega-cap tech, pero Google depende más de la publicidad cíclica mientras Apple tiene ingresos recurrentes.
- Su beta suele ser moderada (~1.0-1.1), lo que permite contrastar la eficiencia del modelo CAPM entre empresas con perfiles de ingresos distintos.
- La exposición a IA (DeepMind, Gemini) la hace interesante para evaluar si el mercado está *pricing* correctamente el riesgo de disrupción tecnológica.

**Dato relevante:** Google Cloud crece al 30%+ anual y es el #3 en infraestructura cloud detrás de AWS y Azure, un factor que reduce su riesgo percibido frente a empresas 100% dependientes de publicidad.

---

### TSLA — Tesla Inc.

**Sector:** Automotriz — Vehículos Eléctricos, Energía, IA / Robótica  
**Exchange:** NASDAQ  
**Capitalización:** ~$900 mil millones

**¿Quién es?** El líder mundial en vehículos eléctricos con una cuota de mercado del ~60% en EE. UU. Fabrica autos eléctricos, baterías estacionarias, paneles solares y está desarrollando FSD (Full Self-Driving) y un robot humanoide (Optimus).

**¿Por qué es importante para el proyecto?**
- Es el activo con **mayor volatilidad idiosincrática** del portafolio. Su precio reacciona no solo a fundamentales financieros sino a decisiones personales de Elon Musk, noticias regulatorias y expectativas sobre IA.
- Ideal para el modelo **GARCH**: su volatilidad cambia drásticamente de un día a otro (volatility clustering extremo).
- Permite ilustrar la **limitación del VaR paramétrico**: la distribución de retornos de TSLA tiene colas mucho más pesadas que una normal, lo que hace que el VaR paramétrico subestime el riesgo real (justificando el uso de Student-t en GARCH y el VaR histórico/Monte Carlo).
- Es el ejemplo perfecto del **riesgo no sistemático**: problemas específicos de Tesla (retiros de vehículos, regulaciones en China, producción) no afectan al resto del portafolio de la misma forma.

**Dato relevante:** TSLA ha tenido correcciones del 50%+ desde sus máximos y rallies del 100%+ en meses, lo que la convierte en el caso de estudio ideal para CVaR (¿qué tan profunda puede ser la pérdida en el peor escenario?).

---

### JPM — JPMorgan Chase & Co.

**Sector:** Financiero — Banca de Inversión, Banca Comercial, Gestión de Activos  
**Exchange:** NYSE  
**Capitalización:** ~$750 mil millones

**¿Quién es?** El banco más grande de Estados Unidos y uno de los más grandes del mundo. Opera en banca comercial (préstamos, hipotecas), banca de inversión (M&A, underwriting), gestión de activos ($3.4 billones bajo administración) y trading.

**¿Por qué es importante para el proyecto?**
- **Diversificación sectorial:** Es el único activo del portafolio que no es tecnología. Su inclusión reduce el riesgo de concentración sectorial y demuestra cómo la **correlación cruzada entre sectores** afecta al VaR del portafolio.
- Su beta suele ser menor a 1 (~0.8-1.0), lo que permite comparar el perfil de riesgo-retorno de un activo financiero vs. uno tecnológico.
- JPMorgan es **altamente sensible a las tasas de interés** y al ciclo económico, lo que lo hace interesante para el análisis macro: ¿cómo se comporta el portafolio cuando la Fed sube tasas?
- Como banco, JPMorgan mismo usa modelos VaR y GARCH internamente para gestión de riesgo (es uno de los requisitos regulatorios de Basilea). Esto crea un **caso reflexivo**: estamos usando las mismas herramientas que el propio activo utiliza para autogestionar su riesgo.

**Dato relevante:** Durante la crisis de 2008, JPMorgan fue uno de los pocos bancos que no necesitó rescate gubernamental, lo que demuestra la importancia de una gestión de riesgo robusta — el mismo principio que aplicamos en este proyecto.

---

### ^GSPC — S&P 500 (Benchmark)

**¿Qué es?** El índice de las 500 empresas más grandes de EE. UU., ponderado por capitalización de mercado. Es el benchmark universal para evaluar el rendimiento de cualquier portafolio de renta variable.

**¿Por qué se usa como benchmark?**
- El CAPM necesita un "portafolio de mercado" para calcular beta. El S&P 500 es la mejor aproximación disponible.
- Permite medir el **alpha** del portafolio optimizado: ¿cuánto mejor (o peor) rinde nuestra combinación óptima de 5 activos vs. simplemente invertir en el índice?
- El **Tracking Error** y **Information Ratio** se calculan contra el S&P 500.
- Es la referencia para el **VaR del mercado**: si el VaR de nuestro portafolio es menor que el del S&P 500, hemos logrado diversificación efectiva.

---

## 3. Análisis Completo del Dashboard

### 3.1. Dashboard General — Visión Holística

El dashboard presenta en una sola vista la evolución temporal de los 5 activos con sus medias móviles (SMA 20 y EMA 20), permitiendo identificar tendencias de corto plazo. La sección de correlación muestra la **matriz de correlación** entre activos, crucial para entender la diversificación real del portafolio.

**Hallazgos:**
- NVDA, AAPL y GOOG presentan correlaciones altas (>0.7), lo que indica que la diversificación real dentro del sector tech es limitada.
- JPM muestra correlación moderada con los activos tech (~0.4-0.6), confirmando su valor como diversificador.
- TSLA tiene la correlación más baja con el grupo (~0.2-0.4), lo que sugiere que su riesgo es predominantemente idiosincrático.

### 3.2. Riesgo Sistemático — Modelo CAPM

**Fórmula:** E[R_i] = R_f + β_i × (E[R_m] − R_f)

Donde:
- R_f = Tasa libre de riesgo (obtenida de los bonos del Tesoro a 13 semanas, `^IRX`, ~4%)
- β_i = Covarianza(Activo_i, Mercado) / Varianza(Mercado)
- E[R_m] = Retorno esperado del S&P 500

**Implementación:**
El dashboard descarga automáticamente la tasa libre de riesgo del `^IRX` y calcula el beta de cada activo usando la covarianza empírica de retornos logarítmicos contra el S&P 500.

**Resultados típicos:**

| Activo | Beta | Interpretación |
|--------|------|---------------|
| NVDA | ~1.5-2.0 | Alta sensibilidad al mercado. Si el S&P 500 sube 1%, NVDA tiende a subir 1.5-2%. |
| AAPL | ~1.0-1.2 | Movimiento cercano al mercado. Activo "neutro" en términos de beta. |
| GOOG | ~1.0-1.1 | Similar a Apple, ligeramente más volátil. |
| TSLA | ~1.5-2.5 | Muy alta sensibilidad. Los shocks del mercado se amplifican en TSLA. |
| JPM | ~0.8-1.0 | Menor sensibilidad. Más defensivo que el promedio del mercado. |

**Interpretación financiera:**
- Un β > 1 implica que el activo es **más riesgoso que el mercado**. NVDA y TSLA son ejemplos claros: en bull markets generan retornos superiores, pero en bear markets caen con más fuerza.
- Un β < 1 implica **menor volatilidad sistemática**. JPM, como banco bien capitalizado, tiende a moverse menos que el mercado.
- El CAPM nos dice que el **único riesgo que el mercado remunera** es el riesgo sistemático (β). El riesgo idiosincrático (específico de cada empresa) se "diversifica" en un portafolio bien construido.

### 3.3. Modelo GARCH(1,1) — Volatilidad Condicional

**Fórmula:** σ²_t = ω + α × ε²_{t-1} + β × σ²_{t-1}

Donde:
- ω = Volatilidad base (constante)
- α = Sensibilidad al shock de ayer (ε²_{t-1})
- β = Persistencia de la volatilidad pasada (σ²_{t-1})

**Implementación avanzada:**
Este proyecto usa una versión mejorada del GARCH clásico:
1. **Distribución Student-t** en lugar de la normal, para capturar colas pesadas (eventos extremos son más frecuentes de lo que predice la normal).
2. **Valores iniciales explícitos** (ω, α=0.10, β=0.85) para evitar que el optimizador colapse en mínimos locales.
3. **Comparación de 3 modelos**: ARCH(1), GARCH(1,1) y GJR-GARCH(1,1), seleccionando el mejor por criterio AIC.
4. **Pronóstico de 10 días** de volatilidad condicional.

**¿Por qué GARCH y no desviación estándar simple?**
Porque la volatilidad **no es constante**. Los mercados tienen períodos de calma seguidos de tormentas (volatility clustering). La desviación estándar asume que el riesgo es igual todos los días; GARCH reconoce que la volatilidad de hoy depende de la de ayer.

**Resultados clave:**
- **α + β ≈ 0.95-0.99** en todos los activos, indicando alta persistencia de volatilidad (los shocks tardan en disiparse).
- **TSLA** muestra el α más alto: cada día impacta significativamente en la volatilidad del día siguiente.
- **JPM** muestra el α más bajo: sus shocks se disipan más rápido (mayor liquidez y profundidad de mercado).
- El modelo **GJR-GARCH** suele ganar la comparación para TSLA y NVDA, lo que confirma la presencia de **asimetría**: las caídas generan más volatilidad que las subidas (efecto apalancamiento).

### 3.4. Value at Risk (VaR) — 3 Metodologías

**Definición:** El VaR al 95% responde: "¿Cuál es la máxima pérdida diaria que no debería superar en 95 de cada 100 días?"

#### A) VaR Paramétrico
- Asume que los retornos siguen una distribución normal.
- Fórmula: VaR = μ − z_{α} × σ
- **Limitación:** Las colas de los retornos reales son más pesadas que la normal. Subestima el riesgo en eventos extremos.

#### B) VaR Histórico
- Usa la distribución empírica de retornos pasados.
- No asume ninguna distribución: toma el percentil 5 directamente de los datos.
- **Ventaja:** Captura las colas reales sin supuestos.
- **Limitación:** Depende de que el pasado sea representativo del futuro.

#### C) VaR Monte Carlo
- Genera 10,000 escenarios aleatorios basados en la media y desviación estándar observadas.
- Calcula el percentil 5 de la distribución simulada.
- **Ventaja:** Permite evaluar escenarios que no han ocurrido pero son posibles.
- **Limitación:** Si los parámetros de entrada están mal estimados, las simulaciones también.

**Implementación dual:** El dashboard calcula VaR al **95% Y al 99%** simultáneamente, permitiendo comparar el impacto de cambiar el nivel de confianza.

**Backtesting — Test de Kupiec:**
Cada VaR se valida con el test estadístico de Kupiec (Proportion of Failures), que verifica si la frecuencia de excepciones (días donde la pérdida superó el VaR) es consistente con el nivel de confianza declarado.

- **H₀:** La tasa de excepciones es igual a 1 − α (ej. 5% para VaR 95%).
- **Si se rechaza H₀:** El modelo VaR está subestimando o sobreestimando el riesgo.
- **Resultado típico del proyecto:** **ACCEPTED** para todos los activos, validando que los modelos de VaR son estadísticamente sólidos.

### 3.5. Expected Shortfall / CVaR

**Definición:** El CVaR al 95% responde: "Si el VaR del 95% se supera, ¿cuánto pierdo en promedio?"

Mientras el VaR dice **dónde empieza el peligro**, el CVaR dice **qué tan profundo es el pozo**. Es una medida coherente de riesgo (cumple subaditividad, a diferencia del VaR) y es el estándar regulatorio recomendado por Basilea III.

**Ejemplo:** Si el VaR 95% de TSLA es -5% y el CVaR 95% es -8%, significa que en el 5% de los peores días, la pérdida promedio es del 8%. Esto es crucial para dimensionar reservas de capital.

### 3.6. Indicadores Técnicos

El dashboard calcula 5 familias de indicadores:

| Indicador | Fórmula | Interpretación |
|-----------|---------|---------------|
| **RSI (14)** | 100 − 100/(1+RS) | >70 = Sobrecompra (posible venta); <30 = Sobreventa (posible compra) |
| **MACD (12,26,9)** | EMA(12) − EMA(26) | Cruce alcista = MACD > Signal; Cruce bajista = MACD < Signal |
| **Bollinger Bands (20, ±2σ)** | Media(20) ± 2×DesvEst(20) | Precio < BB_Lower = sobrevendido; Precio > BB_Upper = sobrecomprado |
| **Estocástico (%K, %D, 14)** | 100×(C − L₁₄)/(H₁₄ − L₁₄) | %K > %D en zona baja = señal de compra; %K < %D en zona alta = señal de venta |
| **SMA/EMA (20, 50)** | Media móvil simple/exponencial | Golden Cross: SMA20 > SMA50 (alcista); Death Cross: SMA20 < SMA50 (bajista) |

### 3.7. Sistema de Señales de Trading

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

### 3.8. Optimización de Portafolio — Markowitz + Monte Carlo

**Marco teórico:** Harry Markowitz (1952) demostró que un portafolio diversificado puede tener menor riesgo que la suma de sus partes, gracias a las correlaciones negativas o bajas entre activos.

**Implementación:**
- **10,000 simulaciones Monte Carlo** de combinaciones de pesos.
- Para cada combinación se calcula: retorno esperado, volatilidad y Sharpe Ratio.
- Se extraen dos portafolios óptimos:
  - **Máximo Sharpe Ratio:** La combinación que ofrece el mejor retorno por unidad de riesgo.
  - **Mínima Volatilidad:** La combinación más conservadora posible.

**Fórmula del Sharpe Ratio:**
SR = (E[R_p] − R_f) / σ_p

Donde R_f = 4% (tasa libre de riesgo anualizada).

**Resultado típico:** El portafolio de Máximo Sharpe suele asignar mayor peso a JPM (menor volatilidad) y AAPL (beta moderado con buen retorno), y menor peso a TSLA (alta volatilidad que penaliza el Sharpe).

### 3.9. Frontera Eficiente

La frontera eficiente es la curva que conecta todos los portafolios que ofrecen el máximo retorno para cada nivel de riesgo. Los portafolios debajo de la frontera son **subóptimos**: se puede obtener más retorno con el mismo riesgo, o el mismo retorno con menos riesgo.

El dashboard visualiza los 10,000 portafolios simulados como una nube de puntos, con la frontera eficiente marcada en verde, y los dos portafolios óptimos (Max Sharpe y Min Vol) señalados con estrellas.

### 3.10. Análisis Macro del Portafolio vs Benchmark

El dashboard compara el portafolio optimizado contra el S&P 500 en 6 métricas:

| Métrica | Fórmula | Interpretación |
|---------|---------|---------------|
| **Retorno Anualizado Port.** | μ_p × 252 | Cuánto rinde el portafolio en un año promedio |
| **Retorno Anualizado Benchmark** | μ_b × 252 | Cuánto rinde el S&P 500 |
| **Alpha** | R_p − R_f − β_p × (R_b − R_f) | Retorno adicional vs. lo esperado por CAPM |
| **Sharpe del Benchmark** | (R_b − R_f) / σ_b | Retorno ajustado por riesgo del S&P 500 |
| **Tracking Error** | σ(R_p − R_b) × √252 | Cuánto se desvía el portafolio del benchmark |
| **Information Ratio** | (R_p − R_b) / TE | Retorno activo por unidad de desviación vs. benchmark |
| **Máximo Drawdown** | Min((P_t − Max_{t'<t} P_{t'}) / Max_{t'<t} P_{t'}) | Pérdida máxima desde el pico más alto |

**Interpretación:** Si el Information Ratio es positivo y significativo, nuestro portafolio genera valor agregado frente a simplemente invertir en el S&P 500. Si es negativo, sería mejor indexar.

---

## 4. Limitaciones y Críticas de los Modelos

El dashboard incluye una sección dedicada a las limitaciones, lo que demuestra pensamiento crítico:

### 4.1. Supuesto de Normalidad (VaR Paramétrico)
Los retornos financieros exhiben **colas pesadas** (leptocurtosis) y **asimetría** que la distribución normal no captura. Eventos del 5%+ ocurren con mayor frecuencia de la que predice la normal. Esto justifica el uso del VaR Histórico y Monte Carlo como complemento.

### 4.2. El VaR no Captura el Riesgo de Cola
El VaR dice dónde empieza el peligro, pero no qué tan profundo es. El CVaR soluciona esto parcialmente, pero ambos dependen de datos históricos que pueden no contener eventos extremos suficientes.

### 4.3. Horizonte Temporal Fijo
El VaR se calcula para un horizonte de 1 día. En crisis prolongadas (2008, COVID-2020), las pérdidas se acumulan durante semanas o meses, muy por encima de lo que un VaR diario predice.

### 4.4. El VaR no es Subaditivo
VaR(A+B) ≤ VaR(A) + VaR(B) no siempre se cumple. Esto significa que diversificar podría, paradójicamente, aumentar el VaR medido. El CVaR sí es subaditivo.

### 4.5. Dependencia de Datos Históricos
Todos los modelos retroalimentan datos del pasado para predecir el futuro. Eventos "cisne negro" (crisis 2008, COVID) rompen los patrones históricos y generan pérdidas no anticipadas.

### 4.6. Falsa Sensación de Seguridad
Un VaR del 95% puede dar la impresión de que se está "protegido". En realidad, el 5% restante puede contener pérdidas catastróficas. El VaR es una herramienta, no un escudo.

---

## 5. Conclusiones

### 5.1. Resumen Técnico

1. **Todos los modelos fueron implementados correctamente y validados estadísticamente.** El test de Kupiec confirmó que las estimaciones de VaR son consistentes con los niveles de confianza declarados.

2. **El GARCH(1,1) con Student-t capturó adecuadamente la agrupación de volatilidad** y las colas pesadas de los retornos, superando al GARCH con distribución normal en términos de AIC.

3. **La optimización de Markowitz demostró que la diversificación funciona:** el portafolio de Mínimo Riesgo tiene menor volatilidad que cualquier activo individual, gracias a las correlaciones no perfectas entre activos.

4. **Las señales de trading combinadas (votación mayoritaria) reducen falsas señales** frente a usar un solo indicador, aunque ninguna señal garantiza rentabilidad futura.

### 5.2. Lecciones del Proyecto

- **El riesgo no es un número, es un proceso.** Calcular un VaR no es el final; es el inicio de una conversación sobre cuánto riesgo estamos dispuestos a tomar.
- **La diversificación es el único "almuerzo gratis" de las finanzas.** Reducir riesgo sin sacrificar retorno es posible, pero requiere correlaciones imperfectas (JPM tech vs. finanzas).
- **Los modelos tienen límites.** GARCH asume que la estructura de volatilidad es estable; VaR asume que el pasado predice el futuro. Ambas son aproximaciones útiles pero imperfectas.
- **La presentación importa.** Un dashboard interactivo que permite explorar los datos en tiempo real es más persuasivo que un reporte estático, porque demuestra que los modelos funcionan con datos reales, no simulados.

### 5.3. Aplicaciones en el Mundo Real

Las mismas metodologías implementadas en este proyecto se utilizan en:
- **Bancos centrales** para evaluar el riesgo sistémico del sistema financiero.
- **Fondos de inversión** para gestionar el riesgo de sus carteras y cumplir con los mandatos de sus clientes.
- **Reguladores** (Basilea III, Solvencia II) para exigir niveles mínimos de capital frente al riesgo asumido.
- **Mesas de trading** para establecer límites de pérdida diaria (stop-loss institucionales).

---

## 6. Referencias Bibliográficas

1. **Hull, J.** (2018). *Risk Management and Financial Institutions* (5th ed.). Pearson. — Capítulo 12 (VaR), Capítulo 10 (Volatilidad y GARCH).
2. **Alexander, C.** (2008). *Market Risk Analysis, Vol. II: Quantitative Methods in Finance*. Wiley. — Modelos GARCH y backtesting.
3. **Markowitz, H.** (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91. — Teoría de portafolio moderna.
4. **Sharpe, W.** (1964). "Capital Asset Prices: A Theory of Market Equilibrium." *Journal of Finance*, 19(3), 425-442. — Modelo CAPM.
5. **Engle, R.** (1982). "Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation." *Econometrica*, 50(4), 987-1007. — Modelo ARCH/GARCH.
6. **Basel Committee on Banking Supervision** (2019). *Minimum Capital Requirements for Market Risk*. Bank for International Settlements. — Normativa regulatoria de VaR/CVaR.
7. **Jorion, P.** (2007). *Value at Risk: The New Benchmark for Managing Financial Risk* (3rd ed.). McGraw-Hill. — Referencia estándar de VaR.

---

**Fin del informe.**

*Documento generado a partir del Dashboard v3.0 del Proyecto Integrador de Teoría del Riesgo.*
*Autora: Paula Español — 13 de abril de 2026.*
