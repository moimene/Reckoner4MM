# Continuidad — Reckoner4MM

Emisor: Codex. Destinatario: Claude o siguiente sesión Codex. Fecha: 2026-09-13.

Lee `AGENTS.md`, la skill local de tu asistente, `docs/development/workflow.md` y `docs/development/tasks/001-installation.md`.

## Estado y autorización

Instalación local terminada y piloto ECC configurado. La prueba real de continuidad con Claude queda pendiente por el fallo de autenticación descrito abajo. El PRD es backlog; P0–P2, cloud y conexiones a proveedores reales quedan para entregas posteriores.

Checkout del usuario: `/Volumes/OWC Envoy Ultra/reckoner4MM`, rama `main`. origin: `https://github.com/moimene/Reckoner4MM.git`. upstream: `https://github.com/CaptainASIC/reckoner.git`.

Base upstream: `8a5d5b0d77f0461abf98e61709cf02d94c63fddb`. Código propio: `4cf1d9b124a78ba54a40d7204da9ca75ff754dca`. Runtime final evaluado y primera publicación: `27d6a324c6142575a44ed4c5a3e475194d0baa34`. Los commits de cierre posteriores solo actualizan evidencia; consulta Git para el SHA actual y verifica sincronización antes de reanudar.

Implementado: lanzador local loopback 8014/5174, contraseña estable excluida de Git, nueve pruebas del lanzador, verificación HTTP/reinicio, correcciones mínimas de lint y recarga tras login, instrucciones y skills para ambos asistentes, procedencia y licencias. El PRD original permanece íntegro.

Verificado en la carpeta definitiva: instalación congelada, build/lint, 9/9 pruebas, salud JSON `status=ok` y `db_connected=true`, 401 sin autenticar, acceso con contraseña, catálogo de 19 proveedores sin configurar, panel vacío sin importes ficticios, ajustes, reinicio, persistencia de contraseña/SQLite y navegador sin errores JavaScript de página. Revisión independiente de código y documentación completada. Los fallos iniciales están descritos en la ficha.

La prueba real con Claude Code no pudo leer los documentos: el primer intento terminó con salida 1 por una clave heredada inválida. El control automático de aprobación rechazó inicialmente un reintento al considerar internos los documentos. Después de publicarlos, se comprobó acceso HTTP 200 anónimo y coincidencia byte a byte de los seis archivos; la nueva ejecución fue aprobada, en modo seguro y restringido, solo lectura y excluyendo la clave heredada. Aun así, la autenticación existente de Claude devolvió 401 API key is invalid (salida 1). La prueba de continuidad queda FALLIDA y pendiente de repetir cuando el usuario restablezca su autenticación con Claude. No se cambiaron ajustes globales ni se expusieron claves. Las instrucciones y la skill local de Claude están instaladas; eso acredita preparación documental, no una lectura real por Claude.

## Uso y siguiente acción

Los servicios activos pertenecen al checkout del usuario. Consultar `python3 scripts/local.py status`; abrir con `open`, reiniciar con `restart` o detener con `stop`. El usuario puede abrir `Reckoner4MM.command` desde Finder; la contraseña se muestra únicamente en su terminal local. Los agentes nunca ejecutan `password` ni capturan secretos. Pruebas autorizadas pueden consumir la contraseña internamente y devolver resultados sanitizados.

Conservar `.env.local` y `backend/data/tracker.db` juntos para preservar la clave de cifrado. Logs y procesos están en `.local-runtime/`. Nada de ello está publicado. No usar el verificador de instalación vacía si posteriormente se configuran cuentas reales.

Siguiente tarea propuesta: planificar P0 del PRD con objetivo, alcance, criterios de aceptación y responsable, comenzando por el modelo de suscripciones. No comenzar la implementación ni conectar proveedores por el mero hecho de leer este relevo. Crear un nuevo worktree `agent/…` para escribir; el coordinador integra con `--no-ff`.

ECC continúa como adaptación local e informativa: sin catálogo completo, hooks bloqueantes, memoria automática ni cambios de configuración global. Las pruebas técnicas conservan sus resultados reales de éxito o fallo.
