# Reckoner4MM — instrucciones para agentes

Leer [el flujo común](docs/development/workflow.md) antes de trabajar. Esa guía es la referencia compartida de Codex y Claude; las skills locales solo remiten a ella.

- Alcance vigente: instalación local de Reckoner upstream y piloto informativo de metodología ECC. Las ampliaciones P0, P1 y P2 del PRD quedan pendientes.
- Checkout del usuario: `/Volumes/OWC Envoy Ultra/reckoner4MM`. Cada carril de implementación trabaja en su propio worktree y rama `agent/…`, con rutas asignadas; verificar el directorio, la rama y el SHA antes de editar.
- Codex puede descubrir `.agents/skills/reckoner-workflow/SKILL.md`. Si la instalación no la descubre, leerla directamente y seguir la guía común; no instalar un plugin global para compensarlo.
- Los controles nuevos de ECC son avisos y registros. No hay hooks bloqueantes, aprendizaje automático, memoria global ni nuevos umbrales de cobertura.
- Conservar la licencia GPL de Reckoner y la atribución MIT del material ECC en `docs/development/ecc-LICENSE`.
- Credenciales reales de proveedores, conexiones a cuentas y despliegues quedan fuera del piloto. No leer, imprimir, copiar ni versionar contraseñas, cookies, tokens, `.env.local`, la base SQLite o logs completos.
- `python3 scripts/local.py password` es exclusivamente para el usuario en su terminal local. Los agentes no deben ejecutarlo ni capturar su salida.
- No mezclar un resultado de build, una prueba manual y una revisión de código. Registrar qué se comprobó y contra qué SHA; lo no comprobado sigue pendiente.
