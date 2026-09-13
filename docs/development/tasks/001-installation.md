# 001 — Instalación local y piloto ECC

Fecha: 2026-09-13. Coordinador: Codex. Autorización: plan de instalación aprobado por Moisés.

## Objetivo y alcance

Instalar upstream en el checkout del usuario, conservar el PRD, vincular origin al repositorio público Reckoner4MM y demostrar un flujo común Codex/Claude. P0–P2, conexiones reales a proveedores y cloud quedan pendientes.

Base upstream: `8a5d5b0d77f0461abf98e61709cf02d94c63fddb`. ECC: `8321021c54d670126ce3b2969d5deb880b4b0c2a`.
Código de instalación: commit `4cf1d9b` (incluye correcciones y pruebas). Integración documental: `1373f0c63a7dd407e66dccbfcd829aca2942794f`.
PRD original SHA-256: `0bd3e0a2f965f001a3f8c3c8ec994f57df3be34f6df96035b216fee5122ab12f`.

## Distribución

- Codex coordinador, `agent/instalacion-ecc`, worktree `reckoner4MM-lanes/instalacion-ecc`: lanzador, exclusiones, pruebas, PRD, dos correcciones mínimas frontend.
- Agente de documentación, `agent/ecc-docs`, worktree propio: instrucciones, skills y docs ECC. Commits `a15a257`, `d5edaec`, `eaf562f`. Revisión de estos documentos por el coordinador; merge con `--no-ff`.
- Agente `runtime_review`, contexto independiente de solo lectura: aislamiento, propiedad de procesos y correcciones frontend. Sin escritura en el worktree del implementador.

## Evidencia inicial obtenida en el worktree

| Comprobación | Resultado | Referencia |
|---|---|---|
| uv y pnpm con lockfiles congelados | VERIFICADO | Python 3.13.14, Node 22.23.1; lockfiles iguales al upstream |
| Build frontend final | VERIFICADO | `pnpm build`, salida 0; fuente equivalente a `4cf1d9b` |
| Lint inicial | FALLIDO, corregido | `_updated` sin uso, fallo heredado reproducido |
| Lint final | VERIFICADO | `pnpm lint`, salida 0; fuente `4cf1d9b` |
| Pruebas del lanzador | VERIFICADO | `python3 -m unittest discover -s tests -v`, 9/9 |
| HTTP y reinicio | VERIFICADO | health JSON, 401 anónimo, login,19 proveedores, saldo null, snapshots y password conservados, JWT antiguo invalidado |
| Navegador inicial | FALLIDO, corregido | Tras login se conservaba error de lectura anónima |
| Navegador final | VERIFICADO | Chrome/Playwright: login, panel vacío y ajustes; cero pageerrors, sin recarga manual |
| Repetición posterior de login | FALLIDO por límite upstream | Cinco intentos por IP/5 minutos; se preserva el limitador; comprobación final ejecutada posteriormente; véase cierre |
| Checkout principal y publicación | VERIFICADO | `main` integrado y publicado como `27d6a324c6142575a44ed4c5a3e475194d0baa34`; cierre documental posterior sin cambios de código |
| Continuidad real con Claude | FALLIDO por autenticación externa | Dos ejecuciones terminaron con salida 1 y HTTP 401 API key is invalid. Las instrucciones están preparadas; lectura real no acreditada. |

Las pruebas ocurrieron durante edición: la fuente evaluada se incorporó en `4cf1d9b`; la última guarda del smoke exige también `is_configured=false` antes de sondear y pasó en la ejecución definitiva descrita a continuación. No hay CI remoto ni tests de proveedores reales.

## Revisión independiente y correcciones

1. Fallo al guardar estado después de crear proceso: rollback corregido para usar el mapa en memoria; regresión automatizada y comprobación independiente.
2. Comprobaciones locales afectadas por proxies heredados: opener de salud sin proxy.
3. Reinicio interpretaba TIME_WAIT como listener: SO_REUSEADDR, conservando rechazo de puertos ocupados.
4. Smoke podía confiar en snapshot antiguo: exigir también ausencia real de proveedores configurados antes de refresh.
5. Login: recarga de caché y ajustes, sin forzar consultas a proveedores. La revisión confirma la separación de `reload` y `refresh`.

Los controles metodológicos permanecen informativos. Las pruebas técnicas conservan su resultado efectivo.


## Cierre en el checkout definitivo

Fecha: 2026-09-13. Directorio: `/Volumes/OWC Envoy Ultra/reckoner4MM`.
Versión de runtime evaluada: `27d6a324c6142575a44ed4c5a3e475194d0baa34`; código de aplicación y lanzador equivalente a `4cf1d9b124a78ba54a40d7204da9ca75ff754dca`.
El cierre documental posterior no cambia las fuentes evaluadas.

| Comprobación final | Resultado observado |
|---|---|
| `uv sync --frozen --python 3.13`, desde backend | Salida 0; Python 3.13.14. Aviso de copia entre volúmenes, sin error. |
| `pnpm install --frozen-lockfile`, desde frontend | Salida 0; Node 22.23.1 y pnpm 10.33.0. Aviso de script esbuild omitido; la compilación posterior funcionó. |
| `pnpm build` y `pnpm lint`, desde frontend | Ambas salidas 0. |
| `python3 -m unittest discover -s tests -v` | Salida 0; 9/9 pruebas del lanzador. |
| `python3 scripts/verify_local.py --restart` | Salida 0; salud HTTP/JSON, autenticación, rutas protegidas, catálogo 19, panel vacío y snapshots sin proveedores: PASS. Guarda `is_configured=false` ejecutada antes del refresh. |
| Persistencia tras reinicio | PASS: contraseña y snapshots SQLite conservados; JWT anterior invalidado según diseño upstream; nuevo login correcto. |
| Chrome/Playwright en instalación definitiva | Login, texto “No providers configured”, ajustes y catálogo accesibles. Sin recarga manual; cero errores JavaScript de página. Capturas locales sanitizadas conservadas por el coordinador. |
| Listeners y reapertura | Solo `127.0.0.1:8014` y `127.0.0.1:5174`. `open` reutiliza los servicios propios y abre el navegador. |
| Historial, PRD, licencias y lockfiles | Upstream fijado es ancestro de main; SHA-256 del PRD idéntico al original; GPL y ambos lockfiles sin cambios; licencia MIT ECC incluida. |
| Revisión de material publicado | 116 archivos versionados y 679 objetos Git examinados antes del primer push; ninguna ruta de entorno/SQLite/runtime ni contraseña local o patrón de secreto de alta confianza detectados. Es un control dirigido, no una auditoría exhaustiva de seguridad. |
| Remotos y primera publicación | origin `moimene/Reckoner4MM`; upstream `CaptainASIC/reckoner`. Push de main a origin con salida 0. |

La revisión independiente de `runtime_review` aprobó estáticamente `4cf1d9b` sin hallazgos pendientes en su alcance. También contrastó las guías locales con `27d6a32` sin contradicciones materiales. La verificación de navegador es automatizada y la captura del panel fue inspeccionada visualmente por el coordinador; no se presenta como UAT humana ni prueba de cuentas reales.

## Continuidad con Claude y resultado del piloto

La prueba real con Claude Code no pudo leer los documentos: el primer intento terminó con salida 1 por una clave heredada inválida. El control automático de aprobación rechazó inicialmente un reintento al considerar internos los documentos. Después de publicarlos, se comprobó acceso HTTP 200 anónimo y coincidencia byte a byte de los seis archivos; la nueva ejecución fue aprobada, en modo seguro y restringido, solo lectura y excluyendo la clave heredada. Aun así, la autenticación existente de Claude devolvió 401 API key is invalid (salida 1). La prueba de continuidad queda FALLIDA y pendiente de repetir cuando el usuario restablezca su autenticación con Claude. No se cambiaron ajustes globales ni se expusieron claves. Las instrucciones y la skill local de Claude están instaladas; eso acredita preparación documental, no una lectura real por Claude.

El piloto deja una ficha de tarea, dos carriles de escritura aislados, revisión independiente, fusiones con `--no-ff`, reglas compartidas y una entrega reanudable. Los avisos metodológicos siguen siendo informativos. Los fallos observados de lint, login, reinicio y autenticación de la herramienta permanecen registrados, aunque algunos se resolvieron después.

Siguiente tarea propuesta: convertir P0 del PRD en una ficha breve y revisar el modelo de suscripciones antes de implementarlo. P0–P2, cloud y proveedores reales no se han implementado ni autorizado en esta entrega.

Revisión independiente del cierre documental: sin falso PASS de Claude ni contradicciones materiales; corregida una frase residual que presentaba como pendiente la comprobación final ya ejecutada.
