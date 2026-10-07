# /goal — Ciclo de trabajo con agentes: Planear → Validar → Ejecutar → Validar → Guardar

Cuando el usuario invoca `/goal`, ejecuta el siguiente ciclo de calidad con agentes especializados. El ciclo se repite hasta que cada fase pase la validación sin errores.

---

## Micro-commits a lo largo de todo el ciclo

Los micro-commits no son exclusivos de la Fase 3. Deben realizarse en **puntos estratégicos de cada fase** para que, si la sesión se cierra de forma inesperada, ningún avance se pierda.

Formato de micro-commit:
```
git add <archivo(s)>
git commit -m "wip(goal): <fase> — <descripción breve>"
```

Si el proyecto no tiene historial de git, avisa al usuario al comenzar y ofrécele iniciarlo; si prefiere no usarlo, sigue el ciclo sin commits y dilo explícitamente en el cierre.

---

## El ciclo /goal

```
FASE 0: SELECCIONAR AGENTES (de AGENTES/README.md)
      │
      ↓
FASE 1: PLANEAR (con los agentes de Fase 0)
      │
      ↓
FASE 2: VALIDAR PLAN (con agentes DISTINTOS a los de Fase 1)
      │
   (rechazado) ──→ FASE 1
      │
   (aprobado)
      ↓
FASE 3: EJECUTAR (micro-commit por archivo)
      │
      ↓
FASE 4: VALIDAR EJECUCIÓN (con agentes distintos a los de Fase 2)
      │
   (errores) ──→ FASE 1
      │
   (ok)
      ↓
FASE 5: GUARDAR
(PROGRESS + SESSION + ARQUITECTURA + commit final de documentación)
      │
      ↓
TAREA COMPLETA
```

---

## Fase 0 — SELECCIONAR AGENTES

**Cuándo entra:** siempre, antes de cualquier otra fase. Es el primer paso al invocar `/goal`.

**Qué hacer:**

1. **Analizar el grafo del proyecto**, si hay una herramienta de grafo de código disponible
   (`codebase-memory-mcp` u otra equivalente): identificar, en función de la tarea, qué archivos,
   funciones y componentes están realmente involucrados, para leer después solo lo relevante. Si
   el proyecto no está indexado o no hay herramienta, avisar al usuario y seguir con lectura
   archivo por archivo (este paso no bloquea el ciclo).
2. **Conocer el catálogo de especialistas** en `AGENTES/`. La regla es elegir en función de la
   tarea sin leer cada agente completo:
   - Leer la documentación del catálogo (`AGENTES/README.md`), que resume cada agente con su
     especialidad y cuándo usarlo; o
   - Leer la "portada" de cada agente (el encabezado con su `name` y `description` al inicio de
     cada archivo `.md`) para conocer su perfil.
   Solo después de elegir, leer completo el archivo de los agentes seleccionados.
3. **Leer `PATRONES_DE_ERROR.md`** (obligatorio, si existe) — es un catálogo de errores
   estructurales ya encontrados, escrito como checklist. Si la tarea se parece a algo ya
   construido antes, aplicar su checklist directamente en el plan de Fase 1.
4. Analizar la naturaleza de la tarea:
   - ¿Qué parte del proyecto toca (lógica, pantallas, datos, documentos)?
   - ¿Es una corrección o una funcionalidad nueva?
   - ¿Tiene implicaciones de seguridad o de cumplimiento?
5. Seleccionar entre **2 y 4 agentes**, los más pertinentes para diseñar el plan en Fase 1.
6. Informar al usuario qué agentes se seleccionaron y por qué.
7. Si el objetivo no está claro todavía, preguntar al usuario antes de continuar.

**Nota:** los agentes seleccionados aquí construyen el plan en Fase 1. La Fase 2 usará agentes *distintos* para auditar ese plan de forma independiente.

---

## Fase 1 — PLANEAR

**Cuándo entra:** después de Fase 0, o cuando una fase de validación devuelve fallas.

**Qué hacer:**

1. Leer `HARNESS_INICIO.md`, `PROGRESS.md` y `SESSION.md` si no están ya en contexto.
2. Identificar con precisión cuál es la tarea o el objetivo a alcanzar.
3. Usar los **agentes seleccionados en Fase 0** para construir un **plan de acción detallado** que incluya:
   - Archivos a modificar (rutas exactas)
   - Cambios específicos a realizar en cada archivo
   - Orden de ejecución (qué va primero, qué depende de qué)
   - Si el cambio es arquitectónico (nuevo componente, nueva tabla, nueva regla): marcarlo explícitamente como `[ARQUITECTÓNICO]`
   - Riesgos identificados y cómo mitigarlos
   - Criterios de éxito medibles
4. Presentar el plan al usuario con el formato estándar:
   - **Lo que entendí** (la tarea, con el nivel de tecnicismo que corresponde al usuario)
   - **Lo que haré** (plan paso a paso)
   - **Lo que sugiero** (riesgos, alternativas, consecuencias)
5. **Esperar aprobación explícita del usuario antes de continuar.**

---

## Fase 2 — VALIDAR EL PLAN

**Cuándo entra:** inmediatamente después de que el usuario aprueba el plan.

**Agentes de esta fase** — deben ser **distintos** a los usados en Fase 1. Seleccionar entre:
- `testing-reality-checker` — certifica que el plan es ejecutable, completo y no tiene pasos imposibles
- `engineering-minimal-change-engineer` — confirma que no hay cambios innecesarios ni de alcance excesivo
- `security-compliance-auditor` — verifica que el plan no viola las reglas del harness ni las restricciones del proyecto
- `project-management-project-shepherd` — valida que el orden de ejecución y las dependencias son correctos

**Qué hacer:**

1. Cada agente evalúa el plan de forma independiente y emite un veredicto: **APROBADO** o **RECHAZADO con observaciones**.
2. Si **algún agente rechaza** el plan: documentar las observaciones, volver a **Fase 1** con ellas como contexto y repetir hasta que todos aprueben.
3. Si **todos aprueban**: informar al usuario y proceder a Fase 3.

---

## Fase 3 — EJECUTAR

**Cuándo entra:** cuando el plan ha pasado la validación de todos los agentes de Fase 2.

**Qué hacer:**

1. Seleccionar de `AGENTES/` los agentes ejecutores pertinentes para implementar el plan aprobado.
2. Ejecutar el plan **un archivo a la vez**, en el orden definido en Fase 1.
3. **Por cada archivo modificado** (inmediatamente después de editarlo):
   - Verificar que el cambio es correcto antes de continuar al siguiente archivo
   - Hacer un **micro-commit** del archivo recién modificado:
     ```
     git add <archivo>
     git commit -m "wip(goal): <nombre-archivo> — <descripción breve del cambio>"
     ```
   - Respetar todas las "Reglas que no tienen excepción" de `HARNESS_INICIO.md` y los guardrails de `ARQUITECTURA_MAESTRA.md`.
4. Al terminar todos los archivos: pasar a Fase 4.

---

## Fase 4 — VALIDAR LA EJECUCIÓN

**Cuándo entra:** inmediatamente después de terminar la ejecución de todos los archivos.

**Agentes de esta fase** — distintos a los de Fase 2:
- `engineering-code-reviewer` — revisa cada archivo modificado buscando errores, regresiones y violaciones de estilo
- `testing-evidence-collector` — documenta evidencia concreta de que el resultado funciona
- `security-senior-secops` — verifica que no se introdujeron vulnerabilidades de seguridad
- `engineering-sre` — evalúa confiabilidad: ¿hay nuevos puntos de falla? ¿los errores se manejan correctamente?

**Qué hacer:**

1. Cada agente verifica de forma independiente e informa: **APROBADO** o **ERRORES ENCONTRADOS**.
2. Si **algún agente encuentra errores**: documentarlos con precisión (archivo, línea, descripción), volver a **Fase 1** con los errores como contexto y repetir el ciclo.
3. Si **todos aprueban**: proceder a **Fase 5**.

---

## Fase 5 — GUARDAR (obligatoria, sin excepción)

**Cuándo entra:** inmediatamente después de que la Fase 4 aprueba sin errores. No esperar instrucción del usuario — ejecutar siempre.

**Qué hacer, en este orden:**

1. **Actualizar `PROGRESS.md`:** agregar la nueva entrada `## ✅ Hecho (fecha de hoy) — ...` al
   principio del archivo, actualizar la fecha de la línea "Actualizado" y cerrar la entrada con
   su propio "Siguiente:" (la próxima tarea lógica).
2. **Rotación de `PROGRESS.md`:** correr `wc -l PROGRESS.md` (o equivalente). Si supera 800
   líneas, mover las entradas más antiguas (el final del archivo) a `PROGRESS_ARCHIVO.md`,
   cortando siempre en un límite de entrada, hasta quedar debajo de 800.
3. **Actualizar `SESSION.md`:** nueva sección al inicio con fecha de hoy — qué se hizo, qué
   archivos cambiaron, qué decisiones se tomaron y cuál es la primera tarea de la próxima sesión.
4. **Rotación de `SESSION.md`:** misma regla mecánica de 800 líneas, hacia `SESSION_ARCHIVO.md`.
   El criterio es siempre el **tamaño** del archivo, nunca la fecha de cada sección. Este paso se
   ejecuta siempre, sin preguntar si hace falta: se verifica con el comando y se actúa.
5. **Actualizar `ARQUITECTURA_MAESTRA.md`** solo si el ciclo incluyó cambios marcados como
   `[ARQUITECTÓNICO]`: registrar la decisión tomada y por qué.
6. **Actualizar `CONTEXTO_[NOMBRE].md`** y la documentación técnica del componente tocado, si el
   ciclo modificó código o comportamiento del proyecto. Si el ciclo fue solo de mantenimiento del
   propio harness, este paso no aplica.
7. **Actualizar `PATRONES_DE_ERROR.md`** solo si en el ciclo se corrigió un error que sea un
   PATRÓN reutilizable. Pregunta guía: *si alguien construye algo parecido dentro de dos semanas,
   sin haber leído esta sesión, ¿volvería a cometer el mismo error?* Si la respuesta es sí,
   agregar una entrada (Síntoma / Causa raíz / Checklist accionable). Aplica sin importar quién
   encontró el error: un agente en Fase 2, uno en Fase 4 o el propio usuario.
8. **Commit final de documentación:**
   ```
   git add PROGRESS.md SESSION.md
   git commit -m "docs(goal): cierre ciclo — <resumen de la tarea completada>"
   ```
   (agregar los demás archivos de documentación que se hayan modificado o rotado)
9. Confirmar al usuario: **"Todo guardado. Micro-commits por archivo + commit de documentación realizados. Si la sesión se cierra ahora, el trabajo está seguro."** Mencionar si hubo rotación (de cuántas líneas a cuántas) y si se agregó un patrón nuevo.

**Tarea completa.**

---

## Reglas permanentes durante todo el ciclo

- **Nunca modificar un archivo sin aprobación explícita del usuario.**
- **Nunca asumir que el silencio es aprobación.**
- **Nunca saltarse la Fase 0** — la selección de agentes correctos define la calidad del plan.
- **Nunca saltarse la Fase 2** — la validación del plan es obligatoria antes de ejecutar.
- **Nunca saltarse la Fase 4** — aunque todo parezca haber salido bien.
- **Nunca saltarse la Fase 5** — el guardado es la red de seguridad del ciclo.
- Los agentes de Fase 0/1 y los de Fase 2 son distintos por diseño; los de Fase 2 y los de Fase 4 también.
- Ajustar el lenguaje al perfil del usuario registrado en `HARNESS_INICIO.md`.
- Si surge una duda que solo el usuario puede resolver, pausar y preguntar antes de continuar.

---

## Argumento opcional

Si el usuario escribe `/goal <descripción>`, usar esa descripción como punto de partida para la Fase 0.
Si escribe `/goal` sin argumento, preguntar al usuario cuál es el objetivo antes de comenzar.
