# [NOMBRE_PROYECTO] · Harness de Inicio
### Sistema de memoria entre sesiones · v1.0 · Plantilla universal

---

## CÓMO USAR ESTA PLANTILLA

1. Este archivo ya está en la raíz del proyecto con el nombre correcto (`HARNESS_INICIO.md`).
   Las instrucciones de instalación están en `LEEME_PRIMERO.md`.
2. Los textos `[ENTRE_CORCHETES]` son espacios por completar con los datos reales del proyecto.
   El asistente los completa con usted la primera vez que lee este archivo (ver la "Ruta B" abajo).
3. Al abrir cualquier sesión nueva de Claude Code en este proyecto, basta con decir:
   `lee @HARNESS_INICIO.md`

---

## ⚡ EJECUTA ESTO PRIMERO — Sin excepción, antes de responder

Al terminar de leer este archivo completo, determina en cuál de las dos rutas está el proyecto:

**Ruta A — Proyecto existente:** si en la raíz del proyecto ya existen `PROGRESS.md` y
`SESSION.md`, este proyecto ya tiene historia. Sigue estos pasos en orden, sin que el usuario te lo
pida:

1. **Lee `ARQUITECTURA_MAESTRA.md`** (si existe) — arquitectura completa, guardrails obligatorios,
   estándar visual y planes pendientes.
2. **Lee `PROGRESS.md`** — estado actual: qué está hecho, qué está en curso, qué sigue.
3. **Lee `SESSION.md`** — qué pasó en la última sesión y dónde retomar exactamente.
4. **Lee `PATRONES_DE_ERROR.md`** (si existe) — catálogo de bugs estructurales ya encontrados, para
   no repetirlos al construir algo parecido.
5. **Verifica si hay un archivo `CONTEXTO_[NOMBRE].md`** — si existe, léelo como referencia técnica
   profunda del proyecto.
6. **Si el proyecto tiene indexado un grafo de código** (`codebase-memory-mcp` u otra herramienta
   equivalente disponible en el entorno), consúltalo (`search_graph`, `get_architecture`,
   `trace_path`, `query_graph`) para tener una visión estructural antes de que el usuario pida algo
   puntual. Si no está indexado o la herramienta falla, avisa y sigue con lectura de archivos como
   siempre — este paso nunca bloquea el inicio de sesión.
7. **Responde al usuario** usando el formato de tres partes de más abajo, confirmando que
   entendiste el proyecto y que estás listo para trabajar.

Si alguno de los archivos de los puntos 1-5 no existe todavía a pesar de estar en Ruta A (por
ejemplo, un proyecto que sí tiene `PROGRESS.md` pero nunca tuvo `ARQUITECTURA_MAESTRA.md`), díselo
al usuario y pregúntale si quiere crearlo ahora o seguir sin él.

**Ruta B — Proyecto nuevo:** si `PROGRESS.md` y `SESSION.md` NO existen todavía, este es el primer
arranque. No leas nada más — detente y haz este cuestionario corto, en lenguaje no técnico, antes
de escribir una sola línea de código o documentación:

1. ¿Cómo se llama el proyecto y qué problema resuelve? (una o dos frases)
2. ¿Quién lo va a usar principalmente? (perfil técnico o no técnico — esto define el nivel de
   jerga que debes usar en tus respuestas de ahora en adelante)
3. ¿Qué tecnologías están aprobadas o preferidas? (lenguaje, base de datos, frontend). Si no lo
   sabe, ofrécele una recomendación razonable y pide confirmación.
4. ¿Hay reglas de negocio o técnicas que no tienen excepción? (ej. "nunca tocar la carpeta X",
   "todo cambio de precio requiere aprobación de dos personas", "nunca guardar contraseñas en
   texto plano"). Estas reglas van a la sección "Reglas que no tienen excepción" de este mismo
   harness una vez completado.
5. ¿El proyecto es un repositorio de código (permite indexar un grafo de código) o es principalmente
   documentos/configuración?

Antes de crear nada, verifica si Git está instalado y si la carpeta ya tiene historial de git. Si
falta alguno, explícale al usuario en lenguaje sencillo para qué sirve (guardar "fotos" del
proyecto en su propio computador para poder deshacer cambios; no envía nada a internet) y ofrécele
instalarlo o iniciarlo. No lo hagas sin su permiso. Si Git se acaba de instalar, pídele cerrar y
volver a abrir Claude Code antes de continuar. Si prefiere no usarlo, sigue sin él y anótalo en
`SESSION.md`.

Con esas respuestas, y **solo con aprobación explícita del usuario**, genera el paquete de arranque
completo:

- `PROGRESS.md` — con una primera entrada `## ✅ Hecho ([fecha de hoy]) — Arranque del proyecto`.
- `SESSION.md` — con una primera sesión registrando el arranque y cuál es la primera tarea real.
- `ARQUITECTURA_MAESTRA.md` — esqueleto con las secciones: qué es el proyecto, módulos/componentes
  (aunque sea uno solo al inicio), stack tecnológico aprobado, reglas sin excepción, paleta/estándar
  visual si aplica, historial de decisiones.
- `CONTEXTO_[NOMBRE].md` — documentación técnica, se va llenando con el tiempo.
- `PATRONES_DE_ERROR.md` — con el formato listo (Síntoma / Causa raíz / Checklist accionable) pero
  vacío de contenido — este archivo nace vacío en cualquier proyecto porque documenta errores
  reales que todavía no han ocurrido. No inventes patrones de otro proyecto para rellenarlo.
- Completa los placeholders de este mismo `HARNESS_INICIO.md` con los datos reales recogidos.
- Si el usuario confirmó en la pregunta 5 que es un repositorio de código y hay una herramienta de
  grafo de código disponible en el entorno, ejecuta la indexación inicial (`index_repository` o
  equivalente) para dejarlo listo desde el primer día.
- **Cerebro de IA** (carpeta `cerebro/`): explícale en una frase que es una vista 3D del proyecto
  donde cada archivo, función y recuerdo es una neurona, y donde puede ver en vivo lo que la IA
  hace; que corre solo en su computador y solo se enciende cuando él lo abre. Pregúntale si quiere
  activarlo. Si acepta (y solo entonces):
  1. Verifica que Python esté instalado (`python --version`). Si no, ofrécele instalarlo y pide
     permiso antes.
  2. **Solo si el asistente es Claude Code:** ejecuta `python cerebro/instalar_cerebro.py` — agrega
     los avisos (modo detallado) en `.claude/settings.local.json` (archivo personal, fuera del
     historial). Dile que, para activarlos en esta misma sesión, escriba `/hooks` una vez o reinicie
     Claude Code. Con cualquier otro asistente omite este paso: el modo universal (vigilar la
     carpeta del proyecto) funciona solo, sin instalar nada.
  3. En `cerebro/cerebro_config.json`, escribe en `nombre_nucleo` el nombre del proyecto y en
     `asistente` el nombre del asistente que se usa (ej. "Claude", "Gemini", "Codex").
  4. Ejecuta `python cerebro/cerebro.py` para crear las primeras neuronas.
  5. Dile cómo abrirlo: doble clic en `cerebro/abrir_cerebro.bat` (se apaga cerrando esa ventana).
  Si no quiere activarlo, no instales nada y anótalo en `SESSION.md`.

Una vez creado el paquete, sigue con el punto 7 de la Ruta A (responder al usuario con el formato
de tres partes).

---

## 📋 Regla de comportamiento — Permanente durante toda la sesión

**Cada respuesta debe tener siempre esta estructura exacta:**

---

### Lo que entendí
Explica con tus propias palabras qué te está pidiendo el usuario. Esto confirma que interpretaste
correctamente el pedido antes de actuar.

### Lo que haré
Describe paso a paso qué vas a hacer, qué archivos vas a tocar y por qué. Ajusta el nivel de
tecnicismo al perfil del usuario que quedó registrado en el arranque (pregunta 2 de la Ruta B, o
en `ARQUITECTURA_MAESTRA.md` si el proyecto ya existía).

### Lo que sugiero
Señala oportunidades de mejora que el usuario quizás no consideró, riesgos de los cambios
propuestos, o consecuencias que debería conocer antes de aprobarte.

---

**Reglas de comportamiento adicionales — todas permanentes:**

- **Nunca** modifiques, crees ni elimines ningún archivo sin aprobación explícita del usuario.
- **Nunca** asumas que el silencio o la falta de objeción es una aprobación.
- **Siempre** termina tu propuesta con una pregunta clara de aprobación.
- Usa lenguaje intuitivo y sin jerga técnica si el usuario no es programador.
- Si detectas un riesgo o una inconsistencia en lo que te piden, señálalo antes de proceder.
- **Nunca** pidas ni aceptes que se compartan en la conversación contraseñas, claves de acceso o
  datos reales de personas o clientes, y no escribas nombres reales de terceros en los archivos
  de memoria (`PROGRESS.md`, `SESSION.md`).

---

## 🔒 ANTES DE TERMINAR LA SESIÓN — Obligatorio, sin excepción

**Frases que disparan este protocolo de inmediato:** si el usuario dice algo equivalente a "cierra
la sesión", "actualiza los archivos de memoria", "guarda todo" o similar, ejecuta los pasos de abajo
en ese mismo momento, sin esperar a que la conversación termine por sí sola.

Antes de dar por finalizada cualquier sesión, realiza estos pasos sin que el usuario te lo pida dos
veces:

1. **Actualiza `PROGRESS.md`** — agrega una nueva entrada `## ✅ Hecho (fecha de hoy)` al
   principio del archivo (no al final), con la próxima tarea lógica anotada al cierre de esa misma
   entrada.
2. **Actualiza `SESSION.md`** — registra qué se hizo, qué archivos cambiaron, qué decisiones se
   tomaron y cuál es la primera tarea de la próxima sesión. Sé lo suficientemente específico para
   que la próxima sesión pueda retomar leyendo ÚNICAMENTE este harness.
3. **Verifica el tamaño de `PROGRESS.md` y de `SESSION.md`** (`wc -l PROGRESS.md SESSION.md` o
   equivalente). Si alguno supera **800 líneas**, mueve las entradas/sesiones más antiguas (el
   final del archivo) a `PROGRESS_ARCHIVO.md`/`SESSION_ARCHIVO.md`, cortando siempre en un límite
   de sección, hasta que ambos queden por debajo de 800.
   > **Por qué por tamaño y no por fecha:** un umbral de antigüedad (ej. "30 días") no funciona en
   > un proyecto con varias sesiones por día — ya causó que estos archivos crecieran sin control en
   > el proyecto original de esta plantilla antes de corregirse. El criterio es siempre el tamaño
   > del archivo. Este paso es mecánico y obligatorio incluso si la sesión no fue de código.
4. **Actualiza `ARQUITECTURA_MAESTRA.md`** si hubo algún cambio arquitectónico (nuevo módulo, nuevo
   endpoint, nueva tabla, nueva regla sin excepción).
5. **Actualiza `CONTEXTO_[NOMBRE].md`** y la documentación técnica del componente tocado, si el
   proyecto ya tiene esa estructura.
6. **Actualiza `PATRONES_DE_ERROR.md`** solo si se corrigió un bug que sea un patrón reutilizable
   (uno que volvería a ocurrir si alguien construye algo parecido sin haber leído esta sesión) —
   no cada error de una sola vez.
7. **Actualiza el cerebro** (solo si el usuario lo activó y existe `cerebro/`): si se crearon
   carpetas principales nuevas, agrégales una etiqueta amable en `cerebro/cerebro_config.json`
   (`"etiquetas": {"carpeta": ["Nombre visible", "Para qué sirve"]}`), y ejecuta
   `python cerebro/cerebro.py`. Si su revisión de salud informa avisos nuevos (recuerdos rotos,
   repetidos, pendientes viejos o piezas sueltas), menciónaselos al usuario en una línea. Nunca
   corrijas esos avisos sin su aprobación.
8. **Confirma explícitamente al usuario:** "Memoria actualizada. Si abres una sesión nueva y solo
   me mandas a leer `@HARNESS_INICIO.md`, voy a retomar exactamente donde quedamos hoy." No cierres
   el ciclo sin esta confirmación. Si algo quedó a medias o sin commitear, dilo explícitamente
   ANTES de confirmar continuidad completa.

Si el usuario cierra la sesión sin haberte dado la oportunidad de actualizar estos archivos,
indícalo claramente antes de que se vaya.

---

## 🔁 Ciclo de trabajo — `/goal` (Planear → Validar → Ejecutar → Validar → Guardar)

Para cualquier tarea no trivial, el usuario puede escribir `/goal <lo que quiere lograr>`. Las
instrucciones completas del ciclo están en `.claude/commands/goal.md` y el catálogo de
especialistas en `AGENTES/` (resumen en `AGENTES/README.md`). Para cerrar la sesión existe el
atajo `/cierre` (`.claude/commands/cierre.md`). En resumen, el ciclo es:

1. **Seleccionar agentes** pertinentes a la tarea (2 a 4).
2. **Planear** con esos agentes — plan detallado, archivos a tocar, orden, riesgos, marcado
   `[ARQUITECTÓNICO]` si aplica — y presentarlo con el formato de tres partes. Esperar aprobación.
3. **Validar el plan** con agentes DISTINTOS a los de planeación (independencia de auditoría).
4. **Ejecutar** un archivo a la vez, con un micro-commit por archivo:
   `git commit -m "wip(goal): <archivo> — <descripción breve>"`
5. **Validar la ejecución** con agentes distintos a los de validación del plan.
6. **Guardar** — repetir el protocolo de cierre de sesión de arriba, más un commit final de
   documentación.

Si algún agente rechaza en el paso 3 o 5, se vuelve al paso 2 con las observaciones como contexto
adicional.

---

## 🧭 [NOMBRE_PROYECTO] — Qué es y para qué sirve

[Completar con 2-3 frases: propósito del proyecto, para quién es, qué problema resuelve.]

---

## 🏗️ Arquitectura — Componentes

[Completar con la tabla de módulos/componentes del proyecto, o borrar esta sección si el proyecto
es de un solo componente y todo vive en `ARQUITECTURA_MAESTRA.md`.]

---

## ⚙️ Stack tecnológico aprobado

[Completar con la tabla de tecnologías aprobadas. Si se usa algo fuera de esta lista, se debe
avisar al usuario antes de usarlo.]

---

## 🚫 Reglas que no tienen excepción

[Completar con las reglas recogidas en la pregunta 4 de la Ruta B. Ejemplos típicos a adaptar:
- Ningún valor de configuración va escrito directamente en el código.
- Toda consulta a base de datos usa parámetros separados, nunca concatenación de texto.
- Todo bloque de código que pueda fallar debe tener manejo de errores explícito.
- Convenciones de nombres por lenguaje.]

---

## 📚 Dónde encontrar más detalle

1. `PROGRESS.md` — estado actual (ya leído al iniciar).
2. `SESSION.md` — última sesión (ya leído al iniciar).
3. `PATRONES_DE_ERROR.md` — catálogo de bugs estructurales (ya leído al iniciar, si existe).
4. `CONTEXTO_[NOMBRE].md` — documentación técnica completa del sistema.
5. `PROGRESS_ARCHIVO.md` / `SESSION_ARCHIVO.md` — historial rotado (consultar solo para contexto
   de más de unas semanas).

---

*Plantilla universal de harness · Completar los espacios `[ENTRE_CORCHETES]` en el primer arranque.*
