# Flujo común del piloto ECC

El objetivo de esta fase es instalar Reckoner localmente y probar una forma común de trabajar con Codex y Claude. Se conserva la base upstream y sus lockfiles, con una excepción mínima de instalación: retirar un parámetro sin usar y su import de tipo en `frontend/src/App.tsx` para resolver el fallo de lint, sin cambiar el comportamiento del callback. Las ampliaciones P0, P1 y P2 del PRD, los datos reales de proveedores y los despliegues se abordarán en una fase posterior.

Esta es una adaptación documental de ECC, con [procedencia y licencia](ecc-provenance.md). Sus nuevos controles son **informativos**: una omisión genera un aviso y queda pendiente en el informe; no se introduce un bloqueo de Git, hook, CI o ejecución. Un aviso tampoco convierte una prueba ausente en una prueba superada. Las pruebas técnicas del lanzador y su verificación local tienen resultados reales de éxito o fallo; este carácter informativo no permite ignorar o reclasificar esos resultados.

## 1. Situar el trabajo

Abrir una [ficha de tarea](task-template.md) breve: objetivo, alcance autorizado, resultado esperado y responsable. Identificar repositorio, worktree, rama, SHA base y rutas que pertenecen al carril. Contrastar esas identidades con Git antes de editar o reanudar.

El checkout del usuario está en `/Volumes/OWC Envoy Ultra/reckoner4MM`; los carriles trabajan en worktrees propios y ramas `agent/…`. El coordinador asigna rutas distintas y ordena los cambios que tengan dependencias. Si hay solapamientos o cambió la base, comunicarlo y ajustar el reparto antes de tocar trabajo ajeno. La integración la realiza el coordinador, con paths explícitos y sin incluir cambios ajenos; las fusiones usan `--no-ff` para conservar la atribución de los carriles.

## 2. Investigar y ejecutar lo acordado

Leer el código y las instrucciones aplicables, elegir la comprobación mínima que demuestre el resultado y anotar el plan en la ficha. Para este piloto, usar [la guía de instalación local](local-setup.md) y conservar la resolución de dependencias con lockfiles congelados.

Aplicar únicamente los cambios asignados. La excepción aprobada de lint se documenta en [la guía local](local-setup.md); no aprovecharla para corregir otros defectos funcionales heredados, reescribir proveedores, instalar herramientas globales o desarrollar suscripciones. Documentar los hallazgos y proponer una tarea posterior cuando corresponda. Las instrucciones de despliegue y obtención de credenciales del README original son referencia upstream, no autorización para ejecutarlas.

## 3. Verificar y revisar

Registrar cada comprobación con directorio, comando o procedimiento, fecha, SHA evaluado, código de salida cuando exista y resultado observado. Si se prueba un árbol con cambios sin commit, indicar además los paths y el identificador del diff; no atribuir el resultado únicamente al SHA de `HEAD`. Después del commit, el revisor contrasta que ese diff coincide con el cambio incorporado.

Una revisión independiente de código o documentación debe venir de otro agente o contexto de revisión que no haya implementado el cambio. Entregarle el diff y la evidencia, permitir que inspeccione las fuentes y registrar sus hallazgos, resoluciones y limitaciones. Releer la propia respuesta no cuenta como revisión independiente.

Estados de evidencia: `VERIFICADO`, `FALLIDO`, `NO_EJECUTADO` o `PENDIENTE`. Separar revisión estática, build, lint, pruebas automatizadas del lanzador, comprobación HTTP y recorrido manual de navegador. Mantener visibles los fallos upstream; no alterar un umbral, excluir una prueba o rebajar una comprobación para obtener un resultado verde. Si cambia el código relevante, revisar qué evidencia ha quedado desactualizada y repetir solo lo necesario.

## 4. Cerrar o transferir

Completar la ficha con archivos cambiados, commit final, resultado visible, evidencia y asuntos pendientes. Para continuar en otra sesión o herramienta, usar [la plantilla de continuidad](handoff-template.md). La siguiente sesión vuelve a comprobar Git y los archivos citados; un resumen guardado no acredita el estado actual ni amplía la autorización.

Mantener la documentación revisable en el repositorio. Contraseñas, cookies, tokens, credenciales de proveedores, `.env.local`, `backend/data/` y `.local-runtime/` permanecen fuera de Git y de las fichas. No adjuntar logs completos, volcados de SQLite o transcripciones; conservar solo evidencia mínima sanitizada. Evitar inspecciones indiscriminadas: una prueba local autorizada puede consumir la contraseña internamente y leer metadatos de SQLite para comprobar autenticación y persistencia, sin mostrar valores secretos ni trasladarlos a chat, logs, prompts o capturas. Los agentes no ejecutan `scripts/local.py password`: la visualización de la contraseña mediante ese subcomando pertenece exclusivamente al usuario en su terminal local.

## Cómo evaluar el piloto

- Aislamiento: las modificaciones corresponden a las rutas del carril; un solapamiento queda registrado y se resuelve con el coordinador.
- Evidencia: un informe de otro SHA o diff se marca desactualizado y no se reutiliza como prueba del cambio actual.
- Continuidad: una sesión nueva puede identificar objetivo, estado comprobado, pendientes y siguiente paso sin recuperar secretos ni inferir permisos.
- Revisión: consta un revisor independiente y qué diff inspeccionó; en ausencia de esa revisión se registra `PENDIENTE`.
- Honestidad del cierre: un build correcto no se presenta como pruebas funcionales completas, conexión real a proveedores o entrega de P0–P2.

Estas situaciones sirven para observar y mejorar la metodología. No constituyen una suite de tests instalada ni un gate obligatorio nuevo.
