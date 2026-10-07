# Harness para comenzar cualquier proyecto desde cero

Este paquete le da a Claude Code una forma ordenada de trabajar con usted: recuerda lo que se hizo
en cada sesión, pide aprobación antes de hacer cambios y revisa su propio trabajo con
especialistas antes de darlo por terminado.

No hace falta saber programar para usarlo.

---

## Qué necesita

1. **Una cuenta de Claude de pago** (plan Pro o superior).
2. **Claude Code instalado**, con la sesión iniciada con esa cuenta.
3. **Conexión a internet.**

---

## Cómo empezar

1. Abra Claude Code y escriba: *"Instala Git para Windows"*. Acepte los permisos que le pida,
   cierre Claude Code y vuelva a abrirlo. Si en un computador de empresa no le deja instalarlo,
   pídaselo a TI.
2. Cree una carpeta nueva y vacía para su proyecto y descomprima ahí todo el contenido de este
   paquete.
   > La carpeta `.claude` empieza con un punto y Windows puede ocultarla. Debe estar: en el
   > Explorador de archivos, active "Ver > Elementos ocultos" para confirmarlo.
3. Abra Claude Code en esa carpeta y escriba: **`lee @HARNESS_INICIO.md`**
4. Responda las preguntas que le hará sobre su proyecto. Con sus respuestas, y solo cuando usted
   lo apruebe, Claude creará la memoria del proyecto.

---

## El día a día

| Momento | Qué escribir |
|---|---|
| Al abrir una sesión | `lee @HARNESS_INICIO.md` |
| Para una tarea importante | `/goal` y lo que quiere lograr |
| Al terminar la sesión | `/cierre` |

Claude siempre le responde en tres partes (**Lo que entendí**, **Lo que haré**, **Lo que
sugiero**) y espera su aprobación antes de modificar cualquier archivo.

---

## ¿Qué es Git y por qué es seguro?

Git funciona como el historial de versiones de un documento de Word, pero para todo su proyecto.
Cada vez que Claude hace un cambio importante, Git guarda una "foto" de cómo quedó. Si algo sale
mal, puede volver a cualquier foto anterior, como deshacer un cambio.

Es seguro porque esas fotos se guardan dentro de su propio computador, en la misma carpeta del
proyecto. Git no tiene cuenta, no se conecta a internet y no envía nada a nadie. Solo compartiría
información si usted lo conectara a propósito a un servicio en línea, y eso no está configurado en
este paquete.

---

## ¿Para qué sirve `/cierre`?

Claude no recuerda nada de una conversación a otra. `/cierre` es la forma de dejarle notas antes de
terminar: anota en la memoria del proyecto qué se hizo hoy, qué se decidió y qué sigue, y guarda
una "foto" final con Git.

Así, en la próxima sesión solo escribe `lee @HARNESS_INICIO.md` y Claude retoma exactamente donde
quedaron, sin que tenga que volver a explicarle nada. Si cierra sin escribirlo, esas notas no se
guardan.

---

## Los agentes y el ciclo `/goal`

La carpeta `AGENTES/` es un catálogo de más de 200 especialistas (programación, seguridad, pruebas,
diseño, gestión de proyectos y más). No tiene que elegirlos usted: Claude revisa el resumen del
catálogo y escoge los adecuados para cada tarea.

Al escribir `/goal` y lo que quiere lograr, Claude:
1. **Elige** de 2 a 4 especialistas según la tarea.
2. **Planea** con ellos y le presenta el plan. No hace nada hasta que usted lo apruebe.
3. **Valida el plan** con especialistas distintos, que buscan errores de forma independiente.
4. **Ejecuta** un archivo a la vez, guardando una "foto" después de cada uno.
5. **Valida el resultado** con otro grupo distinto. Si encuentran errores, vuelve a planear.
6. **Guarda** en la memoria qué se hizo y qué sigue.

**Ventajas:** menos errores, porque nadie revisa su propio trabajo, y cada error importante queda
registrado para no repetirlo. Menos consumo, porque no tiene que volver a explicar el proyecto en
cada sesión y Claude lee solo lo necesario.

`/goal` consume más que un pedido simple, porque trabajan varios especialistas. Úselo para tareas
importantes; para ajustes pequeños basta con pedírselo directamente a Claude.

---

## El Cerebro de IA (opcional)

La carpeta `cerebro/` trae una vista en 3D de su proyecto con forma de cerebro. Nace casi vacío y
crece con el proyecto: cada archivo, función y recuerdo de la IA se vuelve una neurona, y los
hilos muestran cómo se conectan.

- **Verlo pensar en vivo:** mientras la IA trabaja, las neuronas que usa se encienden y una
  bitácora cuenta en lenguaje sencillo lo que hace ("Leyendo...", "Editando...", "Lanzó un
  agente...").
- **Se revisa solo:** el botón "Salud" avisa si un recuerdo menciona archivos que ya no existen, si
  hay recuerdos repetidos o pendientes olvidados. Solo avisa; nunca cambia nada por su cuenta.
- **Privado y liviano:** corre solo en su computador (nada sale a internet) y solo se enciende
  cuando usted lo abre. Apagado, no consume nada.

**Funciona con cualquier asistente de IA.** El cerebro tiene dos formas de ver el trabajo:

| Modo | Con qué funciona | Qué muestra en vivo |
|---|---|---|
| **Universal** | Cualquier IA (Claude, ChatGPT/Codex, Gemini, Cursor, Copilot…) o una persona editando a mano | Cada archivo que se **crea, modifica o borra**, y las neuronas que nacen |
| **Detallado** | Solo Claude Code (usa sus avisos automáticos) | Además, lo que la IA **lee, busca y ejecuta**, y los agentes que lanza |

El modo universal está siempre activo. El detallado se suma solo si el proyecto usa Claude Code.
Para que el cerebro diga el nombre de su asistente en lugar de "la IA", escríbalo en
`cerebro/cerebro_config.json`, en `"asistente"` (por ejemplo `"Gemini"`).

**Cómo activarlo:** con Claude Code, Claude se lo ofrece la primera vez que lee
`HARNESS_INICIO.md`. Con otra IA, pídale: *"Lee HARNESS_INICIO.md y activa el cerebro sin el paso
de avisos de Claude Code"*, o simplemente haga doble clic en `cerebro/abrir_cerebro.bat`. Necesita
**Python** instalado y Edge o Chrome.

**Con otra IA, el resto del paquete:** pídale al asistente que lea `HARNESS_INICIO.md` al empezar
cada sesión; las reglas, la memoria del proyecto y el protocolo de cierre funcionan igual. Las
órdenes `/goal` y `/cierre` son propias de Claude Code: con otra IA, escriba en palabras "haz el
ciclo de trabajo de HARNESS_INICIO.md" o "cierra la sesión".

**Cómo abrirlo:** doble clic en `cerebro/abrir_cerebro.bat`. Para apagarlo, cierre la ventana negra
que se abre junto con el navegador.

---

## Seguridad

- Lo que conversa con Claude se procesa en línea: nunca comparta contraseñas, claves ni datos
  reales de personas o clientes.
- No le pida a Claude que lea archivos con datos confidenciales.
- Antes de poner archivos con datos reales dentro del proyecto, pídale a Claude que los agregue al
  `.gitignore`, para que no queden en el historial.

---

## Qué trae el paquete

| Archivo o carpeta | Para qué sirve |
|---|---|
| `HARNESS_INICIO.md` | El punto de partida: lo único que se le pide leer a Claude al abrir cada sesión. |
| `.claude/commands/goal.md` | Instrucciones del ciclo `/goal`. |
| `.claude/commands/cierre.md` | Instrucciones de `/cierre`. |
| `AGENTES/` | Catálogo de especialistas. |
| `.gitignore` | Lista de lo que nunca debe guardarse en el historial. |
| `cerebro/` | El Cerebro de IA (opcional): vista 3D del proyecto y de Claude trabajando en vivo. |

El catálogo `AGENTES/` es una copia del proyecto de código abierto "The Agency"
(`msitarzewski/agency-agents`), con licencia MIT. Su licencia se conserva en `AGENTES/LICENSE` y
debe mantenerse si comparte el paquete.

El dibujo 3D del cerebro usa la librería de código abierto three.js (versión 0.185.1, licencia
MIT), incluida en `cerebro/lib/three/` con su licencia en `LICENSE.txt`, para que funcione sin
internet.
