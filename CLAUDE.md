# Reckoner4MM — entrada para Claude

Leer [AGENTS.md](AGENTS.md) y [el flujo común](docs/development/workflow.md). La guía común define el alcance y la evidencia; este archivo no duplica ni sustituye esas instrucciones.

La skill del proyecto está en `.claude/skills/reckoner-workflow/SKILL.md`. Usarla cuando esté disponible; si no se descubre en la sesión, leer su contenido directamente.

Este piloto incorpora documentación y skills locales de forma informativa. No instalar ECC globalmente, copiar hooks de Claude a Codex ni habilitar observadores, memoria automática o conectores. La instalación de Reckoner no autoriza las ampliaciones P0–P2, el uso de credenciales reales ni despliegues.

Para iniciar la aplicación, seguir [la guía local](docs/development/local-setup.md). Visualizar la contraseña mediante `scripts/local.py password` pertenece exclusivamente al usuario en su terminal: los agentes no ejecutan ese subcomando ni capturan su salida. Las pruebas locales autorizadas pueden consumir la contraseña internamente y leer metadatos SQLite para verificar autenticación y persistencia; no deben mostrar secretos ni trasladarlos a chat, logs o prompts. Sus resultados técnicos de éxito o fallo se registran como tales; los avisos de metodología ECC siguen siendo informativos.
