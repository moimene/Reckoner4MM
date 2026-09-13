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

## Evidencia obtenida en el worktree

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
| Repetición posterior de login | FALLIDO por límite upstream | Cinco intentos por IP/5 minutos; se preserva el limitador; verificar una vez al arrancar el checkout final |
| Checkout principal y publicación | PENDIENTE | Por ejecutar tras cierre de revisión |
| Continuidad real con Claude | PENDIENTE | Lectura independiente de estas instrucciones sin ejecutar tareas |

Las pruebas ocurrieron durante edición: la fuente evaluada se incorporó en `4cf1d9b`; la última guarda del smoke exige también `is_configured=false` antes de sondear y se volverá a ejecutar en el checkout final. No hay CI remoto ni tests de proveedores reales.

## Revisión independiente y correcciones

1. Fallo al guardar estado después de crear proceso: rollback corregido para usar el mapa en memoria; regresión automatizada y comprobación independiente.
2. Comprobaciones locales afectadas por proxies heredados: opener de salud sin proxy.
3. Reinicio interpretaba TIME_WAIT como listener: SO_REUSEADDR, conservando rechazo de puertos ocupados.
4. Smoke podía confiar en snapshot antiguo: exigir también ausencia real de proveedores configurados antes de refresh.
5. Login: recarga de caché y ajustes, sin forzar consultas a proveedores. La revisión confirma la separación de `reload` y `refresh`.

Los controles metodológicos permanecen informativos. Las pruebas técnicas conservan su resultado efectivo.
