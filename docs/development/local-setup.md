# Uso local de Reckoner4MM

La instalación de esta fase parte de Reckoner upstream y añade un lanzador local, pruebas de ese lanzador y documentación de trabajo. La excepción mínima al código de aplicación es la corrección del fallo de lint descrita más abajo. El desarrollo P0–P2 del PRD sigue pendiente. El estado efectivo y las pruebas ejecutadas se registran en la entrega de instalación; esta guía describe el procedimiento y no afirma que una prueba haya pasado.

## Abrir y controlar la aplicación

Directorio del usuario: `/Volumes/OWC Envoy Ultra/reckoner4MM`.

Abrir `Reckoner4MM.command` desde Finder para usar el lanzador. En una terminal situada en ese directorio también se dispone de:

```bash
python3 scripts/local.py start
python3 scripts/local.py status
python3 scripts/local.py open
python3 scripts/local.py restart
python3 scripts/local.py stop
```

Frontend: `http://127.0.0.1:5174`. Backend: `http://127.0.0.1:8014`. Ambos deben escuchar únicamente en loopback. El frontend utiliza el puerto asignado sin buscar otro automáticamente (`--strictPort`). Si hay una colisión, comprobar qué servicio ocupa el puerto; no terminar procesos ajenos.

El lanzador crea automáticamente una contraseña local persistente en `.env.local`, con protección de dashboard activada. Para consultarla, **solo el usuario**, en su terminal local, puede ejecutar:

```bash
python3 scripts/local.py password
```

Ese comando muestra un secreto. Los agentes no deben invocarlo ni incluir su salida en herramientas, capturas, entregas o mensajes. La contraseña no se guarda en la documentación. Una prueba local autorizada puede consumir la contraseña internamente y leer metadatos de SQLite para verificar autenticación y persistencia; sus salidas deben permanecer sanitizadas y no revelar secretos en chat, logs o prompts.

El estado y los logs del lanzador residen en `.local-runtime/`; SQLite reside en `backend/data/tracker.db`. Estos directorios y `.env.local` están excluidos de Git. Parar o reiniciar conserva la base y la contraseña. No borrar esos archivos como mecanismo de reinicio.

## Entorno y dependencias

- Backend: Python 3.13 y `uv`, con `backend/uv.lock`. Instalación reproducible: `uv sync --frozen --python 3.13` desde `backend/`.
- Frontend: Node.js 22 y `pnpm`, con `frontend/pnpm-lock.yaml`. Instalación reproducible: `pnpm install --frozen-lockfile` desde `frontend/`.
- La configuración local apunta `FRONTEND_URL` a `http://127.0.0.1:5174` y `VITE_API_URL` a `http://127.0.0.1:8014`. No reutilizar los dominios del autor incluidos en `.env.example`.
- El arranque del piloto utiliza un entorno sin credenciales de proveedores heredadas. No rellenar claves, cookies o tokens reales ni conectar cuentas desde los ajustes.

La contraseña cifra las credenciales que Reckoner pudiera guardar en SQLite. En el código upstream, cambiarla vuelve ilegibles las credenciales cifradas con la anterior; dejarla vacía usa una clave efímera que no sobrevive al proceso. Por eso esta instalación conserva una contraseña local estable. No hay credenciales reales de proveedores en el alcance actual.

## Comprobaciones mínimas

Registrar resultado, fecha y SHA/diff de cada comprobación siguiendo [el flujo común](workflow.md):

1. Instalación desde los lockfiles sin modificarlos; `pnpm build` y `pnpm lint`, con sus códigos de salida y cualquier fallo heredado.
2. `GET /api/health`: comprobar el cuerpo `status=ok` y `db_connected=true`, además del estado HTTP. Upstream puede devolver HTTP 200 con estado `degraded`.
3. Protección del dashboard y ajustes activa; el usuario puede iniciar sesión con su contraseña local sin exponerla a los agentes.
4. La API registra 19 proveedores. Sin credenciales, el dashboard muestra el estado vacío y ajustes ofrece esos proveedores; no debe inferirse saldo cero ni conectividad real.
5. Detener y volver a iniciar conserva SQLite y la configuración local; comprobar que no se utilizan los puertos o procesos de otras aplicaciones.

La base upstream no contiene una suite de tests automatizados. La instalación incorpora [pruebas del lanzador](../../tests/test_local_launcher.py) y una [verificación local de autenticación y persistencia](../../scripts/verify_local.py). Son comprobaciones técnicas reales que pueden pasar o fallar; registrar sus resultados sin confundirlos con los avisos informativos de metodología ECC. No prueban la conectividad real de los proveedores ni las ampliaciones P0–P2. Registrar build, lint, pruebas automatizadas, HTTP y navegador por separado, sin presumir resultados por la mera existencia de estos archivos.

## Límites observados en la base upstream

Base de referencia: `CaptainASIC/reckoner@8a5d5b0d77f0461abf98e61709cf02d94c63fddb`.

| Tema | Evidencia de la base | Tratamiento en este piloto |
|---|---|---|
| Python | README anuncia 3.11+; `backend/pyproject.toml` exige 3.13+. | Usar Python 3.13. |
| Proveedores | `backend/providers/__init__.py` registra 19, incluido Warp; la tabla original enumera 18. | Usar el registro como inventario. |
| Sondeo | README anuncia 5–30 minutos; `backend/scheduler.py` programa todos cada 30 segundos e ignora `refresh_interval`. | Documentado; no corregido. |
| Docker | README afirma incluir Dockerfile; no existe en el árbol de esa revisión. | No hay receta Docker validada ni despliegue en esta fase. |
| CI y tests | No hay workflows CI ni ficheros de tests upstream; pytest aparece como dependencia de desarrollo. | Se añaden comprobaciones locales del lanzador, sin afirmar CI ni resultados no ejecutados. |
| Lint frontend | `pnpm lint` fallaba en la base por `_updated` sin usar en `frontend/src/App.tsx:39`. | Excepción mínima: retirar ese parámetro y el import de tipo `BalanceSnapshot`; el cuerpo del callback permanece igual. |
| Configuración | Los módulos de arranque upstream no cargan `.env` expresamente; el ejemplo incluye dominios del autor. | Usar la configuración explícita del lanzador local. |

Estas limitaciones no se resuelven por añadir documentación ECC. Los endpoints de proveedores, saldos reales, renovaciones y futuras suscripciones permanecen fuera de la validación de instalación.
