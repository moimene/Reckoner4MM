# PRD: Reckoner ampliado a suscripciones (nombre de trabajo: Reckoner Ledger)

Versión 0.1, borrador para discusión. 13 de septiembre de 2026.
Autor: Moisés Menéndez. Base técnica: fork de [CaptainASIC/reckoner](https://github.com/CaptainASIC/reckoner) (GPL-3.0).

## 1. Resumen

Reckoner hoy es un panel de una sola página que consulta saldos y créditos prepago de 18 proveedores de IA y cloud mediante conectores por API, token o cookie de sesión, los guarda como instantáneas en SQLite y los refresca en segundo plano cada 5 a 30 minutos ([README](https://github.com/CaptainASIC/reckoner/blob/main/README.md)). Su modelo de datos solo conoce dos cosas: la configuración de un proveedor y una instantánea de saldo (`provider_configs`, `balance_snapshots`) ([database.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/models/database.py)).

Este documento define la ampliación de ese sensor operativo a un controlador de coste completo para APIs y suscripciones: un registro de compromisos recurrentes (planes fijos, planes con bolsa de créditos, prepago, pago por uso), presupuestos, imputación por proyecto o cliente, calendario de renovaciones y alertas. La regla de diseño es que cada euro que aparezca en el panel tenga un origen declarado (API, factura, CSV o alta manual) y una fecha de lectura.

## 2. Problema

Quien opera varios agentes, prototipos y servicios cloud paga por cuatro vías distintas que ningún proveedor consolida:

| Tipo de gasto | Ejemplo real del stack | Qué ve hoy Reckoner |
|---|---|---|
| Crédito prepago | OpenRouter, Anthropic, RunPod, Firecrawl | Saldo restante, si el proveedor lo expone |
| Pago por uso | OpenAI con Admin key, AWS Cost Explorer, GCP Billing | Gasto de 30 días o del mes en curso |
| Suscripción fija | ChatGPT Plus, Claude Pro, Perplexity Pro, Copilot, Vercel Pro | Nada, o "key válida" |
| Suscripción con bolsa de créditos | Railway Pro (20 USD incluidos), Manus (créditos mensuales) | El crédito, pero no la cuota que lo financia |

Consecuencias concretas:

1. El total del panel (`total_usd_balance`) suma saldos disponibles, no obligaciones. Un usuario con 300 USD de saldo y 600 USD/mes en suscripciones ve un número tranquilizador que no describe su gasto ([schemas.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/models/schemas.py)).
2. Las renovaciones anuales se descubren en el extracto bancario. No existe fecha de renovación ni aviso previo.
3. Ocho de los 18 conectores dependen de cookies de sesión o JWT copiados del navegador, con caducidades de 90 días a 5 meses ([.env.example](https://github.com/CaptainASIC/reckoner/blob/main/.env.example)). Cuando caducan, el proveedor pasa a `error` sin que nadie lo relacione con el gasto que sigue produciéndose.
4. No hay imputación. Un despacho o una consultora necesita saber qué cliente, asunto o proyecto consumió el crédito, y hoy el dato muere en `raw_data`.
5. No hay histórico consultable: las instantáneas se guardan pero la API solo devuelve la última por proveedor ([credits.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/routers/credits.py)).

Coste de no resolverlo: cargos de renovación no deseados, agentes que fallan por saldo agotado en producción, y una hora al mes de revisar consolas a mano por cada 5 o 6 proveedores.

## 3. Objetivos

Objetivos de usuario:

- G1. Responder en una pantalla "¿cuánto gasto este mes y cuánto gastaré al cierre?" con desglose fijo, variable, crédito incluido y excedente.
- G2. Recibir aviso 30, 7 y 1 día antes de cada renovación, y al 50, 80 y 100 % de cada presupuesto.
- G3. Imputar cada coste a un `project_id`, `client_id` o `matter_id` y obtener el total por eje en menos de 5 segundos.
- G4. Saber cuándo va a caducar una credencial de conector antes de que el proveedor pase a `error`.

Objetivos del producto:

- G5. Mantener la compatibilidad con la interfaz `BaseProvider.fetch_balance()` para que los 18 conectores actuales y los futuros del upstream sigan funcionando sin cambios ([base.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/providers/base.py)).
- G6. Que el 100 % de los importes mostrados tengan `source_type`, `source_ref` y `observed_at`.

## 4. No objetivos

- Contabilidad formal: asientos, IVA, retenciones, conciliación bancaria. El producto exporta a CSV para que eso lo haga el ERP o el contable.
- Ejecutar pagos, cancelar o modificar suscripciones en el proveedor. Solo lectura y aviso.
- Multiusuario o multiempresa en v1. Se mantiene el modelo de una contraseña y un JWT de 30 días del upstream ([auth.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/auth.py)). Se prepara el esquema con `workspace_id` pero no se expone.
- Extracción de saldos de suscripciones de interfaz web (planes de chat de consumo) mediante automatización de navegador. Es frágil, suele violar condiciones de uso y no aporta un dato que la cuota fija no dé ya.
- Sustituir la telemetría de tokens por agente (Langfuse, Helicone, OpenTelemetry). Reckoner Ledger ingesta agregados; no traza peticiones.

## 5. Usuarios e historias

Persona A, operador individual (el caso de partida): abogado o consultor con 10 a 25 servicios entre APIs de modelos, cloud y SaaS, que paga con una o dos tarjetas y quiere control sin montar un ERP.

Persona B, responsable de plataforma en un equipo pequeño: mantiene agentes en producción para clientes internos y debe repercutir coste por proyecto.

Persona C, agente autónomo: un proceso que antes de ejecutar una tarea cara consulta si queda presupuesto.

Historias, en orden de prioridad:

1. Como operador, quiero dar de alta una suscripción con importe, ciclo, moneda, fecha de renovación y método de pago para que aparezca en el coste mensual previsto aunque el proveedor no tenga API.
2. Como operador, quiero ver el coste del mes en curso separado en fijo, variable, crédito incluido consumido y excedente, para saber qué parte puedo recortar.
3. Como operador, quiero un aviso previo a cada renovación para decidir si renuevo o cancelo.
4. Como operador, quiero vincular el conector de saldo de Railway con la suscripción Railway Pro para que el panel muestre "20 USD de cuota, 14,20 USD de crédito consumido, 0 USD de excedente" en una sola tarjeta.
5. Como responsable de plataforma, quiero imputar porcentajes de cada suscripción o conector a proyectos y clientes para obtener el coste por proyecto al cierre.
6. Como operador, quiero saber cuándo caduca el token de Manus o la cookie de Anthropic para renovarlos antes de que el conector falle.
7. Como operador, quiero importar un CSV de facturas o de un extracto de tarjeta y que el sistema proponga a qué suscripción corresponde cada línea, con confirmación manual.
8. Como responsable de plataforma, quiero definir un presupuesto mensual por proveedor y por proyecto y recibir alerta al 50, 80 y 100 %.
9. Como agente autónomo, quiero consultar por API si un proyecto tiene presupuesto disponible antes de lanzar una tarea, para detenerme si no lo hay.
10. Como operador, quiero ver el histórico de saldo de un proveedor en los últimos 90 días para detectar consumos anómalos.

Casos límite que el diseño debe cubrir: planes anuales pagados por adelantado (prorrateo mensual), suscripciones en EUR y USD en el mismo panel, periodos de prueba con fecha de conversión a pago, cambios de precio anunciados por el proveedor, suscripciones pausadas y créditos promocionales con caducidad.

## 6. Modelo de dominio

El upstream tiene `provider_configs` y `balance_snapshots`. La ampliación añade el concepto de compromiso y separa tres planos que hoy se mezclan: qué se ha contratado, qué se ha observado y cómo se reparte.

```
vendors ──< subscriptions ──< subscription_events
   │              │
   │              └──< allocations >── cost_objects (project / client / matter)
   │
   └──< provider_configs ──< balance_snapshots   (upstream, sin cambios)
                    │
                    └──< credential_expiries

cost_events  (una fila por importe observado: API, factura, CSV, manual)
budgets      (por vendor, subscription, cost_object o global)
alert_rules ──< alerts
fx_rates
```

Tablas nuevas y campos mínimos:

`vendors`: `id`, `name`, `category` (ai, cloud, saas, tools), `website`, `billing_portal_url`, `provider_id` (FK opcional a `provider_configs`).

`subscriptions`: `id`, `vendor_id`, `product`, `plan_type` (fixed, fixed_with_credits, prepaid, usage, trial), `billing_cycle` (monthly, annual, custom_days), `amount`, `currency`, `included_credit_amount`, `included_credit_currency`, `overage_provider_id` (FK al conector que mide el excedente), `start_date`, `next_renewal_date`, `auto_renew`, `cancel_deadline_days`, `payment_method`, `owner`, `contract_url`, `status` (active, paused, review, cancelled), `notes`.

`subscription_events`: `id`, `subscription_id`, `type` (created, renewed, price_changed, paused, cancelled, plan_changed), `effective_date`, `old_value`, `new_value`, `source_type`.

`cost_events`: `id`, `vendor_id`, `subscription_id` (nullable), `provider_id` (nullable), `kind` (fixed_fee, usage, credit_purchase, credit_consumption, overage, refund), `amount`, `currency`, `amount_base`, `base_currency`, `period_start`, `period_end`, `observed_at`, `source_type` (api, invoice, csv, manual), `source_ref`, `confidence` (confirmed, proposed), `raw_data`.

`cost_objects`: `id`, `type` (project, client, matter, team, environment), `code`, `name`, `parent_id`.

`allocations`: `id`, `target_type` (subscription, provider), `target_id`, `cost_object_id`, `percentage`, `valid_from`, `valid_to`. La suma de porcentajes de un mismo objetivo y fecha debe ser 100.

`budgets`: `id`, `scope_type` (global, vendor, subscription, cost_object), `scope_id`, `period` (monthly, annual), `amount`, `currency`, `thresholds` (JSON, por defecto 50, 80, 100).

`credential_expiries`: `provider_id`, `credential_key`, `expires_at`, `warn_days`, `source` (declared, inferred). Los conectores que dependen de cookie o JWT declaran la vida útil documentada en `.env.example` (Manus 90 días, Plaud 5 meses) y el sistema avisa antes.

`alert_rules` y `alerts`: regla (tipo, ámbito, umbral, canal) y ocurrencia (regla, fecha, valor, estado acknowledged).

`fx_rates`: `date`, `from`, `to`, `rate`, `source`. Moneda base configurable; EUR por defecto para este despliegue.

Cambio en el upstream: `BalanceSnapshot.category` pasa de literal `"ai" | "cloud"` a `ai | cloud | saas | tools` y se añade `subscription_id: Optional[str]`. El resto del esquema no cambia ([types/index.ts](https://github.com/CaptainASIC/reckoner/blob/main/frontend/src/types/index.ts)).

## 7. Cálculos

Coste mensual previsto para un periodo P y un ámbito S:

\[
C_{P}(S) = F(S) + V_{obs}(S) + V_{proy}(S) - K_{aplic}(S)
\]

donde \(F\) es la suma de cuotas fijas normalizadas a mes (los planes anuales se dividen por 12; los planes de N días se normalizan por 30,44/N), \(V_{obs}\) es el consumo variable observado hasta hoy, \(V_{proy}\) es la proyección lineal del consumo restante (media diaria de los últimos 7 días por días que faltan, con la opción de curva de los 3 últimos meses cuando existen), y \(K_{aplic}\) es el crédito incluido o promocional que absorbe consumo antes de facturarse.

Excedente de una suscripción con bolsa de créditos:

\[
O = \max(0,\ U_{periodo} - K_{incluido})
\]

con \(U_{periodo}\) tomado del conector vinculado (`overage_provider_id`) y reseteado en `next_renewal_date`.

Todas las cifras se guardan en moneda original y en moneda base con el tipo del día de observación. El panel muestra la base y, al pasar el cursor, la original.

## 8. Requisitos

### P0. Sin esto no resuelve el problema

R1. Alta, edición y baja de suscripciones desde la interfaz, con los campos de la tabla `subscriptions`.
- Dado un vendor existente, cuando el usuario crea una suscripción mensual de 20 USD con renovación el 3 de cada mes, entonces aparece en la lista con estado `active` y `next_renewal_date` calculada.
- Dado un plan anual de 240 EUR, cuando se consulta el coste mensual previsto, entonces contribuye 20 EUR a \(F\).
- Dado un importe negativo o una moneda no ISO 4217, cuando se guarda, entonces la API responde 422 con el campo erróneo.

R2. Vista de coste mensual con cuatro bloques (fijo, variable, crédito incluido, excedente) y proyección al cierre.
- Dado un mes con 3 suscripciones fijas y 2 conectores con gasto, cuando se abre el panel, entonces cada bloque muestra su total y la suma coincide con \(C_P\) al céntimo.
- Dado que un conector está en `error`, cuando se calcula la proyección, entonces el bloque variable marca ese proveedor como "sin dato desde {fecha}" y no lo interpola en silencio.

R3. Vinculación conector-suscripción para planes con bolsa de créditos.
- Dado Railway Pro con 20 USD incluidos y el conector Railway con 14,20 USD consumidos, cuando se muestra la tarjeta, entonces indica cuota 20, consumido 14,20, excedente 0 y días hasta reinicio.
- Dado un consumo de 27,50 USD, entonces el excedente es 7,50 y aparece en el bloque de excedente del mes.

R4. Calendario de renovaciones y alertas T-30, T-7 y T-1, con canal en la propia aplicación y correo.
- Dada una suscripción con renovación en 7 días, cuando corre el job diario, entonces crea una alerta `renewal_due` una sola vez (idempotente por suscripción y umbral).
- Dada una suscripción con `auto_renew = false`, entonces la alerta indica "vence, no se renueva" en lugar de "se cobrará".

R5. Presupuestos con umbrales 50, 80 y 100 % por proveedor y global.
- Dado un presupuesto global de 500 EUR y un coste previsto de 410 EUR, cuando corre el job, entonces existe una alerta al 80 % y no al 100 %.

R6. Trazabilidad de origen. Todo importe en la interfaz muestra `source_type`, `source_ref` y `observed_at`.
- Dado un importe introducido a mano, cuando se muestra, entonces lleva la etiqueta "manual" y el usuario que lo introdujo.

R7. Caducidad de credenciales.
- Dado un conector con `auth_type = session_cookie` o JWT y una vida declarada de 90 días, cuando faltan 10 días, entonces se emite alerta `credential_expiring` con enlace a las instrucciones de renovación del README.

R8. Histórico consultable: endpoint que devuelve las instantáneas de un proveedor entre dos fechas, con reducción a un punto por hora si el rango supera 7 días.

R9. Compatibilidad con conectores upstream: la suite de pruebas debe ejecutar los 18 `fetch_balance()` con credenciales simuladas y guardar la instantánea sin modificar sus ficheros.

### P1. Importante, siguientes iteraciones

R10. Imputación por `cost_objects` con `allocations` porcentuales y vista de coste por proyecto, cliente o asunto en el periodo.
- Dada una suscripción de 100 EUR asignada 60/40 a dos proyectos, cuando se consulta el coste por proyecto, entonces muestra 60 y 40 y la suma cuadra con el total del proveedor.
- Dado que los porcentajes suman 90, cuando se guarda, entonces la API rechaza con mensaje explícito.

R11. Importación CSV de extracto de tarjeta o de facturas descargadas, con motor de emparejamiento por nombre de comercio, importe y periodicidad. Las coincidencias se guardan como `proposed` hasta confirmación manual.

R12. Ingesta de facturas por correo (Gmail) con extracción de vendor, importe, moneda y periodo. Igual que R11: nada entra como `confirmed` sin revisión humana. Este flujo es la única vía realista para las suscripciones de interfaz web sin API.

R13. Multimoneda con tabla `fx_rates` alimentada a diario desde una fuente pública y moneda base configurable.

R14. Exportación CSV y JSON del periodo por vendor, suscripción y cost object.

R15. Tokens de API de solo lectura, distintos del JWT de sesión, para que otros sistemas y agentes consulten el panel sin poder cambiar credenciales.

### P2. Deseable

R16. Endpoint `GET /api/ledger/budget-check?cost_object=...&estimated_cost=...` que responde `allow | warn | deny` para que un agente compruebe presupuesto antes de ejecutar (historia 9). Publicado también como servidor MCP de solo lectura con tres herramientas: `get_monthly_cost`, `get_budget_status`, `list_upcoming_renewals`.

R17. Detección de anomalías: aviso cuando el consumo diario de un conector supera 3 veces la media de los 14 días anteriores.

R18. Registro de cambios de precio anunciados por el proveedor (`subscription_events.price_changed`) con fecha de efecto y recálculo de la proyección desde esa fecha.

R19. Recomendaciones de recorte: suscripciones sin uso observado durante dos ciclos, créditos que caducan sin consumir, solapamiento de planes.

### No se hará (en esta versión)

Multiusuario con roles, pagos, cancelaciones automáticas, automatización de navegador contra portales de suscripción, trazas de tokens por petición.

## 9. Arquitectura y cambios sobre el upstream

Backend (FastAPI, SQLite con aiosqlite, APScheduler) se mantiene. Cambios:

- `models/database.py`: migraciones versionadas (tabla `schema_version`) en lugar de `CREATE TABLE IF NOT EXISTS` incremental. Las tablas nuevas de la sección 6.
- `routers/`: nuevos `subscriptions.py`, `ledger.py` (coste mensual, histórico, coste por cost object), `budgets.py`, `alerts.py`, `imports.py`. `credits.py` no cambia; `GET /api/credits/` añade `subscription_id` a cada instantánea.
- `scheduler.py`: además del refresco de saldos, un job diario `run_ledger_jobs` que materializa `cost_events` de tipo `fixed_fee` en la fecha de renovación, evalúa presupuestos, renovaciones y caducidades, y actualiza `fx_rates`.
- `providers/base.py`: sin cambios en la firma. Se añade un método opcional `credential_lifetime_days()` con valor `None` por defecto; los conectores de cookie o JWT lo sobrescriben.
- `crypto.py`: el cifrado Fernet derivado de `RECKONER_PASSWORD` se mantiene para credenciales ([crypto.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/crypto.py)). Los tokens de solo lectura (R15) se guardan como hash, nunca en claro.

Frontend (React 19, TypeScript, Tailwind): nueva navegación con cuatro vistas: Panel (el actual, con el resumen de coste mensual arriba), Suscripciones, Presupuestos y alertas, Imputación. `SummaryBar` pasa de mostrar saldo total a mostrar coste previsto del mes, con el saldo total como segunda cifra.

Almacenamiento: SQLite sigue siendo válido para un despliegue personal. Se abstrae el acceso para poder migrar a Postgres (Supabase o Neon) cuando haya más de un usuario, sin reescribir routers.

Despliegue: sin cambios respecto al upstream (dos servicios en Railway o Docker) ([README, Quick Start](https://github.com/CaptainASIC/reckoner/blob/main/README.md#quick-start)).

## 10. Seguridad y privacidad

- Las credenciales de conectores siguen cifradas en reposo. Con `RECKONER_PASSWORD` vacío el upstream genera una clave aleatoria por proceso; en este producto la contraseña pasa a ser obligatoria porque el sistema guardará datos financieros.
- Los mensajes de error hacia el cliente siguen saneados como hace `_error_snapshot` para no filtrar tokens ([base.py](https://github.com/CaptainASIC/reckoner/blob/main/backend/providers/base.py)).
- Los conectores por cookie de sesión (Anthropic, Mistral, Groq, CivitAI) se etiquetan en la interfaz como "no oficial, puede romperse o incumplir condiciones del proveedor". El usuario decide.
- La ingesta de correo (R12) solo lee mensajes que coincidan con un filtro de remitentes declarados y guarda referencia al mensaje, no el cuerpo completo.
- Ninguna acción de escritura sobre proveedores externos. El principio es fail-closed: si un conector falla, el panel lo dice, no estima.
- Datos personales: el sistema guarda importes y comercios, que en España pueden considerarse datos económicos del titular. Al ser autoalojado y de un solo usuario, el responsable es el propio usuario; documentarlo en el README.

## 11. Métricas de éxito

Línea base a medir la primera semana tras el despliegue interno, antes de activar alertas.

Indicadores adelantados (primer mes):
- Suscripciones dadas de alta respecto al inventario real: objetivo 100 % de las que se pagan con tarjeta identificada.
- Porcentaje de importes con `source_type` distinto de `manual`: objetivo 60 % al cierre del tercer mes.
- Alertas de renovación emitidas con al menos 7 días de antelación: 100 %.
- Conectores en `error` más de 24 horas sin alerta de credencial previa: 0.

Indicadores retrasados (trimestre):
- Cargos de renovación no deseados: 0 (línea base: los detectados en extractos de los últimos 6 meses).
- Interrupciones de agentes por saldo agotado: 0 (línea base: incidentes registrados).
- Tiempo mensual de revisión manual de consolas: de la línea base medida a menos de 15 minutos.
- Desviación entre coste previsto al día 15 y coste real al cierre: menor del 10 %.

## 12. Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| APIs de facturación inexistentes o cambiantes en la mayoría de SaaS | El registro manual domina y se desactualiza | Ingesta de facturas por correo (R12) y recordatorio de verificación trimestral por suscripción |
| Cookies y JWT caducan o el proveedor cambia el endpoint | Conectores en `error` | R7, más etiqueta de fragilidad y pruebas de contrato por conector |
| Proyección lineal poco fiable en consumos irregulares | Alertas falsas o tardías | Mostrar intervalo (mínimo, lineal, máximo) y permitir desactivar proyección por proveedor |
| Licencia GPL-3.0 del upstream | Obliga a publicar el código si se distribuye el binario o servicio modificado a terceros | Uso interno autoalojado no distribuido; si se ofrece a clientes, publicar el fork o reescribir la capa de suscripciones como servicio separado que consuma la API de Reckoner |
| SQLite y un solo proceso | Límite cuando haya varios usuarios | Abstracción de repositorio desde el inicio (sección 9) |

## 13. Fases

Fase 1 (P0, 4 a 6 semanas de trabajo efectivo): modelo de datos con migraciones, CRUD de suscripciones, coste mensual con cuatro bloques, vinculación conector-suscripción, renovaciones, presupuestos globales y por proveedor, caducidad de credenciales, histórico. Criterio de salida: el propio stack (Railway, Supabase, Vercel, APIs de modelos, SaaS de suscripción) cargado y cuadrado contra el extracto de un mes.

Fase 2 (P1): imputación por cost objects, importación CSV, ingesta de correo con revisión, multimoneda, exportación, tokens de solo lectura.

Fase 3 (P2): comprobación de presupuesto para agentes y servidor MCP, anomalías, cambios de precio, recomendaciones.

## 14. Preguntas abiertas

| Pregunta | Responsable | Bloquea |
|---|---|---|
| ¿Moneda base EUR con tipo del día de observación, o tipo medio mensual como hace la contabilidad? | Moisés | Fase 1 (afecta a cómo se guardan `amount_base`) |
| ¿Se contribuye al upstream el cambio de `category` y `credential_lifetime_days()` o se mantiene solo en el fork? | Moisés | No |
| ¿Qué fuente de tipos de cambio (BCE diario es suficiente para EUR/USD)? | Moisés | Fase 2 |
| ¿La ingesta de correo lee la cuenta personal o una cuenta dedicada de facturación? | Moisés | Fase 2 (privacidad y filtro de remitentes) |
| ¿Los cost objects se sincronizan con el Expediente o Matter de NDA Suite, o son un catálogo propio? | Moisés | Fase 2 (define la FK o el mapeo) |
| ¿Vale una proyección lineal para el primer trimestre o se exige desde el inicio la curva de 3 meses? | Moisés | No |

## 15. Fuentes

- Repositorio: https://github.com/CaptainASIC/reckoner
- README (funciones, proveedores, API, arquitectura): https://github.com/CaptainASIC/reckoner/blob/main/README.md
- Plantilla de variables de entorno y notas por proveedor: https://github.com/CaptainASIC/reckoner/blob/main/.env.example
- Esquema SQLite actual: https://github.com/CaptainASIC/reckoner/blob/main/backend/models/database.py
- Esquemas Pydantic: https://github.com/CaptainASIC/reckoner/blob/main/backend/models/schemas.py
- Clase base de conectores: https://github.com/CaptainASIC/reckoner/blob/main/backend/providers/base.py
- Planificador de refresco: https://github.com/CaptainASIC/reckoner/blob/main/backend/scheduler.py
- Cifrado de credenciales: https://github.com/CaptainASIC/reckoner/blob/main/backend/crypto.py
- Tipos del frontend: https://github.com/CaptainASIC/reckoner/blob/main/frontend/src/types/index.ts
- Licencia GPL-3.0: https://github.com/CaptainASIC/reckoner/blob/main/LICENSE
