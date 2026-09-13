# Procedencia de la adaptación ECC

Esta adaptación toma de ECC la secuencia investigar, planificar, implementar, revisar, verificar y dejar continuidad. Selecciona instrucciones y plantillas para un piloto local de Reckoner4MM; no incorpora el runtime, catálogo completo, hooks, MCP, observadores ni aprendizaje automático de ECC.

- Fuente oficial: [affaan-m/ECC](https://github.com/affaan-m/ECC).
- Revisión fijada: [`8321021c54d670126ce3b2969d5deb880b4b0c2a`](https://github.com/affaan-m/ECC/tree/8321021c54d670126ce3b2969d5deb880b4b0c2a).
- Referencias seleccionadas: [flujo de desarrollo](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/rules/common/development-workflow.md), [verificación](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/skills/verification-loop/SKILL.md), [navegación y revisión Codex](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/docs/CODEX-NAVIGATION-GUIDE.md) y [continuidad entre herramientas](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/skills/unified-memory/SKILL.md).
- Licencia ECC: MIT, Copyright (c) 2026 Affaan Mustafa. La [licencia completa](ecc-LICENSE) se conserva desde el [archivo oficial de esa revisión](https://github.com/affaan-m/ECC/blob/8321021c54d670126ce3b2969d5deb880b4b0c2a/LICENSE).
- Fuente de Reckoner: [`CaptainASIC/reckoner@8a5d5b0d77f0461abf98e61709cf02d94c63fddb`](https://github.com/CaptainASIC/reckoner/tree/8a5d5b0d77f0461abf98e61709cf02d94c63fddb). Se conserva su [licencia GPL-3.0](../../LICENSE); la incorporación de material MIT no cambia la licencia de Reckoner.

## Decisiones de adaptación

[La guía común](workflow.md) es la única fuente de las reglas del piloto. `AGENTS.md`, `CLAUDE.md` y las dos skills locales remiten a ella. La duplicación de entradas de descubrimiento para Codex y Claude no supone duplicar las políticas ni instalar ECC dos veces.

Se han omitido los umbrales genéricos de cobertura, la generación obligatoria de varios documentos para cambios pequeños y las comprobaciones periódicas indiscriminadas. Las comprobaciones se eligen según el cambio y el estado real del proyecto. Las observaciones y revisiones metodológicas de ECC son informativas: no se agregan hooks bloqueantes ni gates CI. Las pruebas técnicas locales del lanzador son una incorporación separada y sus resultados reales de éxito o fallo deben registrarse sin rebajarlos a avisos.

No se promete igualdad de capacidades entre herramientas. Estas skills son instrucciones locales que requieren que la herramienta las descubra o que el agente las lea. No son ejecución determinista, control de permisos ni prueba de que una tarea esté completa. La continuidad se redacta en documentos revisables; no se habilita ECC Memory Vault ni memoria global.
