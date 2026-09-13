# Continuidad — Reckoner4MM

Emisor: Codex. Destinatario: Claude o siguiente sesión Codex. Fecha: 2026-09-13.

Lee `AGENTS.md`, `.claude/skills/reckoner-workflow/SKILL.md`, `docs/development/workflow.md` y `tasks/001-installation.md` (ruta relativa a este documento).

Objetivo autorizado: instalar upstream y probar ECC local informativo. El PRD es backlog, no una orden de implementar P0–P2 ahora.

Checkout del usuario: `/Volumes/OWC Envoy Ultra/reckoner4MM`; implementación en `/Volumes/OWC Envoy Ultra/reckoner4MM-lanes/instalacion-ecc`, rama `agent/instalacion-ecc`. Remotos previstos: origin `moimene/Reckoner4MM`, upstream `CaptainASIC/reckoner`. Base de código propia `4cf1d9b`; documentación integrada `1373f0c`.

Implementado: runtime local loopback8014/5174, contraseña estable fuera de Git, nueve pruebas del lanzador, smoke HTTP/reinicio, correcciones mínimas lint/login y metodología compartida con procedencia/licencias.

Verificado en worktree: build/lint, 9/9 pruebas, HTTP/auth/persistencia y navegador sin importes ficticios. Revisión independiente encontró fallos concretos ya corregidos. La guarda adicional de smoke y el arranque final todavía requieren comprobación final. Instalación principal, push a GitHub y continuidad Claude: pendientes al redactar esta nota; no afirmes que están hechos hasta consultar el cierre actualizado.

Los servicios del worktree de instalación están activos temporalmente. Consultar `python3 scripts/local.py status`; el coordinador los detendrá y arrancará la copia principal. No ejecutar el subcomando password desde un agente. Tests autorizados pueden consumir la contraseña internamente y devolver únicamente resultados sanitizados.

Siguiente acción: el coordinador termina revisión, integra localmente con --no-ff, instala dependencias en la copia principal, verifica y publica main. No cambies configuraciones globales ni conectes proveedores. Tras la entrega se podrá planificar P0 del PRD; todavía no está implementado.
