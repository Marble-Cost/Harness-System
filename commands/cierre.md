# /cierre — Atajo del protocolo de fin de sesión definido en HARNESS_INICIO.md

Cuando el usuario invoca `/cierre`, ejecuta de inmediato y sin preguntas de por medio los pasos de
la sección **"🔒 ANTES DE TERMINAR LA SESIÓN"** de `HARNESS_INICIO.md` (léela ahí si no está ya en
contexto — este comando no la reemplaza, solo evita tener que escribir la frase larga cada vez).

Las frases "cierra la sesión", "actualiza los archivos de memoria" o "guarda todo" siguen
funcionando igual. `/cierre` es un atajo adicional de una palabra.

## Qué hacer, en este orden

1. **Actualizar `PROGRESS.md`** — nueva entrada `## ✅ Hecho (fecha de hoy)` al principio del
   archivo, con la próxima tarea lógica anotada al cierre de esa misma entrada.
2. **Actualizar `SESSION.md`** — qué se hizo, qué archivos cambiaron, qué decisiones se tomaron, y
   cuál es la primera tarea de la próxima sesión. Suficientemente específico para que la próxima
   sesión retome el trabajo leyendo ÚNICAMENTE `HARNESS_INICIO.md`, sin que el usuario repita
   contexto ya explicado hoy.
3. **Verificar tamaño de `PROGRESS.md` y `SESSION.md`** (`wc -l PROGRESS.md SESSION.md` o
   equivalente). Si alguno supera 800 líneas, mover las entradas/sesiones más antiguas (el final
   del archivo) a `PROGRESS_ARCHIVO.md` / `SESSION_ARCHIVO.md` (en la raíz del proyecto), hasta
   quedar por debajo de 800. Criterio: tamaño del archivo, nunca la fecha de cada sección.
4. **Commitear** lo actualizado (`git add PROGRESS.md SESSION.md` + los archivos `_ARCHIVO.md` si
   se rotó algo, `git commit -m "docs: cierre de sesión — <resumen breve>"`), salvo que ya haya un
   commit de cierre reciente del mismo trabajo (por ejemplo, si la sesión ya corrió `/goal`). Si
   el proyecto no usa git, omitir este paso y decirlo.
5. **Reindexar el grafo del proyecto**, si hay una herramienta de grafo de código disponible.
   Va DESPUÉS de los commits. Si falla o no existe, no bloquea el cierre: se informa como
   advertencia y se continúa.
6. **Actualizar el cerebro**, solo si el usuario lo activó (existe `cerebro/` y
   `.claude/settings.local.json` contiene `registrar_evento.py`): etiquetas para carpetas
   principales nuevas en `cerebro/cerebro_config.json` y `python cerebro/cerebro.py`. Informar en
   una línea los avisos nuevos de su revisión de salud; nunca corregirlos sin aprobación. Si falla,
   no bloquea el cierre.
7. **Confirmar explícitamente al usuario**: *"Memoria actualizada. Si abres una sesión nueva y
   solo me mandas a leer `@HARNESS_INICIO.md`, voy a retomar exactamente donde quedamos hoy."*
8. Si en algún momento no puedes garantizar la continuidad (un cambio quedó a medias, sin commit,
   o una decisión del usuario quedó sin registrar), dilo explícitamente ANTES del paso 7 — nunca
   prometas continuidad completa si hay algo real que se perdería.

## Argumento opcional

Si el usuario escribe `/cierre <nota>`, incorpora esa nota como contexto adicional al registrar el
cierre en `SESSION.md`.
