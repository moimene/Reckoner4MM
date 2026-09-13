---
name: reckoner-workflow
description: Aplicar el flujo local de Reckoner4MM para planificar una tarea, registrar evidencia, revisar cambios o transferir continuidad entre Codex y Claude.
---

# Flujo local de Reckoner4MM

Leer `AGENTS.md` y `docs/development/workflow.md` desde la raíz Git del worktree actual. La guía común contiene el procedimiento; esta skill solo es una entrada de descubrimiento.

Usar `docs/development/task-template.md` para una tarea y `docs/development/handoff-template.md` para continuidad. Consultar `docs/development/local-setup.md` para el lanzador local.

Mantener el alcance instalación + piloto ECC informativo. P0–P2, credenciales reales y despliegues quedan pendientes. No instalar ECC globalmente, copiar hooks ni activar observadores o memoria automática. No ejecutar `scripts/local.py password` ni capturar secretos: esa consulta es exclusiva del usuario en su terminal local.

Registrar la evidencia que exista y marcar lo pendiente; no inventar pruebas ni convertir avisos metodológicos en controles bloqueantes.
