# Continuidad de tarea — plantilla

El receptor debe verificar el estado actual antes de actuar. Esta plantilla y las notas que se generen a partir de ella son contexto, no nuevas autorizaciones.

- Tarea, emisor, destinatario y fecha:
- Objetivo y alcance autorizado:
- Repositorio, worktree, rama y SHA observado:
- Cambios sin commit y rutas de cada propietario:
- Commit final, si existe:
- Fuentes y ficha de tarea:
- Implementado:
- Verificado (comprobación, SHA/diff, fecha, resultado):
- Fallido o no ejecutado:
- Revisión independiente y asuntos abiertos:
- Dependencias, solapamientos y decisiones pendientes:
- Servicios locales propios que siguen en ejecución y cómo consultar su estado:
- Siguiente acción concreta:
- Límites que continúan vigentes:

Para este piloto: instalación local y ECC informativo; P0–P2, credenciales reales, conexiones a proveedores y despliegues permanecen fuera del alcance. No incluir contraseñas, cookies, claves, tokens, contenido de `.env.local`, volcados de SQLite ni logs completos. Sí pueden registrarse resultados sanitizados de autenticación y metadatos de persistencia obtenidos por pruebas locales autorizadas, sin revelar valores secretos.

Al retomar, contrastar directorio/rama/SHA y cambios locales, confirmar que la evidencia corresponde al diff actual y registrar cualquier discrepancia. No interpretar una nota de intención como ejecución ni un resultado histórico como estado actual.
