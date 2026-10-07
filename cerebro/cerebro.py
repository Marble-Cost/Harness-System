"""Cerebro de IA - Lector.

Recorre un proyecto (codigo, documentos) y la memoria de Claude, y arma las
"neuronas" (archivos, funciones, recuerdos) y los "hilos" que las conectan.
El resultado queda en datos/cerebro_datos.js, que lee visor.html.

Solo lee archivos de texto del proyecto; nunca lee Excel ni reportes.
Nada sale del computador.

Uso:  python cerebro.py
"""
import ast
import os
import json
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CONFIG = RAIZ / "cerebro_config.json"
SALIDA = RAIZ / "datos" / "cerebro_datos.js"

RE_FUNC_JS = re.compile(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")
RE_FLECHA_JS = re.compile(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>)")
RE_ENLACE_MEMORIA = re.compile(r"\[\[([^\]]+)\]\]")
RE_IDENT = re.compile(r"[A-Za-z_$][\w$]*")


def cargar_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[cerebro] No se pudo leer {CONFIG.name}: {e}")
        sys.exit(1)


def resolver_rutas(cfg):
    """Devuelve (carpeta del proyecto, carpeta de memoria de Claude o None).
    "proyecto" puede ser relativo a esta carpeta (ej. ".." cuando el cerebro vive
    dentro del proyecto). "memoria": "auto" la deduce como lo hace Claude Code:
    ~/.claude/projects/<ruta del proyecto con cada signo cambiado por "-">/memory."""
    proyecto = Path(cfg.get("proyecto") or "..")
    if not proyecto.is_absolute():
        proyecto = (RAIZ / proyecto).resolve()
    memoria = cfg.get("memoria")
    if memoria == "auto":
        memoria = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(proyecto)) / "memory"
    elif memoria:
        memoria = Path(memoria)
    else:
        memoria = None
    return proyecto, memoria


def leer_texto(ruta):
    try:
        return ruta.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[cerebro] Aviso: no se pudo leer {ruta}: {e}")
        return ""


def listar_archivos(proyecto, cfg):
    excl_dirs = set(cfg["carpetas_excluidas"]) | {RAIZ.name}  # el cerebro no se dibuja a sí mismo
    excl_arch = set(cfg["archivos_excluidos"])
    exts = set(cfg["extensiones"])
    maximo = cfg["tamano_maximo_kb"] * 1024
    for ruta in proyecto.rglob("*"):
        if not ruta.is_file() or ruta.suffix.lower() not in exts or ruta.name in excl_arch:
            continue
        rel = ruta.relative_to(proyecto)
        if any(p in excl_dirs for p in rel.parts[:-1]):
            continue
        try:
            if ruta.stat().st_size > maximo:
                continue
        except OSError:
            continue
        yield ruta, rel.as_posix()


def funciones_python(texto):
    """Devuelve [(nombre, linea, cuerpo_identificadores)] usando el arbol de Python."""
    try:
        arbol = ast.parse(texto)
    except SyntaxError:
        return []
    salida = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            llamados = set()
            for sub in ast.walk(nodo):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    if isinstance(f, ast.Name):
                        llamados.add(f.id)
                    elif isinstance(f, ast.Attribute):
                        llamados.add(f.attr)
            salida.append((nodo.name, nodo.lineno, llamados))
    return salida


def funciones_js(texto):
    salida = []
    for rx in (RE_FUNC_JS, RE_FLECHA_JS):
        for m in rx.finditer(texto):
            linea = texto.count("\n", 0, m.start()) + 1
            salida.append((m.group(1), linea, None))
    return salida


def importaciones_python(texto):
    try:
        arbol = ast.parse(texto)
    except SyntaxError:
        return set()
    mods = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for a in nodo.names:
                mods.add(a.name.split(".")[-1])
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            mods.add(nodo.module.split(".")[-1])
    return mods


def frontmatter_memoria(texto):
    nombre, desc = None, ""
    if texto.startswith("---"):
        fin = texto.find("\n---", 3)
        cabeza = texto[3:fin] if fin > 0 else ""
        for linea in cabeza.splitlines():
            if linea.startswith("name:"):
                nombre = linea[5:].strip().strip("\"'")
            elif linea.startswith("description:"):
                desc = linea[12:].strip().strip("\"'")
    return nombre, desc


RE_RUTA = re.compile(r"(?<![\w/.:])((?:[A-Za-z0-9_\-.]+/)*[A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)*\.(?:py|html|md|json|sql|bat|js|ps1))\b")
PALABRAS_VACIAS = set("""para como esta este esto pero porque cuando donde desde hasta entre sobre todo toda todos
todas cada solo sólo sino tiene tienen hace hacer debe deben puede pueden será sería están estaba fueron
mismo misma otro otra otros otras nunca siempre antes después ahora también usuario proyecto archivo""".split())
EXT_CODIGO = {"py", "js", "html", "bat", "ps1"}


def _palabras(texto):
    import unicodedata
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9_]{4,}", t) if w not in PALABRAS_VACIAS}


def _cuerpo_sin_cabecera(texto):
    if texto.startswith("---"):
        fin = texto.find("\n---", 3)
        if fin > 0:
            return texto[fin + 4:]
    return texto


def revisar_salud(proyecto, memoria, neuronas, hilos, textos, cfg):
    """Etapa 3: detecta recuerdos rotos, repetidos y viejos, y piezas sueltas.
    Solo avisa; nunca cambia nada."""
    salud = {}

    def avisar(nid, tipo, gravedad, texto):
        salud.setdefault(nid, []).append({"k": tipo, "g": gravedad, "t": texto})

    # Todos los archivos que existen de verdad (incluidas carpetas que el cerebro no dibuja)
    rutas_reales, nombres_reales = set(), set()
    for raiz, dirs, archivos in os.walk(proyecto):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for a in archivos:
            rel = os.path.relpath(os.path.join(raiz, a), proyecto).replace(os.sep, "/")
            rutas_reales.add(rel.lower())
            nombres_reales.add(a.lower())
    if memoria and memoria.is_dir():
        for a in memoria.iterdir():
            nombres_reales.add(a.name.lower())
    for a in RAIZ.rglob("*"):  # archivos del propio cerebro
        if a.is_file():
            nombres_reales.add(a.name.lower())
    ignorar = {x.lower() for x in cfg.get("ignorar_menciones", [])}

    def existe(token):
        t = token.lower().lstrip("./")
        if "/" not in t:
            return t in nombres_reales
        return t in rutas_reales or any(r.endswith("/" + t) for r in rutas_reales) or t.rsplit("/", 1)[-1] in nombres_reales

    memorias = [n for n in neuronas if n["t"] == "memoria"]
    dias = cfg.get("dias_para_viejo", 30)
    umbral = cfg.get("umbral_parecido", 0.45)
    bolsas = {}
    for n in memorias:
        stem = n["id"][2:]
        texto = _cuerpo_sin_cabecera(textos.get("__mem__" + stem, ""))
        # 1. Recuerdos rotos
        faltan = sorted({tok for tok in RE_RUTA.findall(texto) if tok.lower() not in ignorar and not existe(tok)})
        if faltan:
            lista = ", ".join(faltan[:4]) + (f" y {len(faltan) - 4} más" if len(faltan) > 4 else "")
            avisar(n["id"], "roto", "alto",
                   f"Menciona {lista}, que ya no existe en el proyecto. Si el recuerdo es histórico puede ser intencional; si no, conviene actualizarlo.")
        # 3. Recuerdos viejos
        desc = (n.get("d") or "").lower()
        if "pendiente" in desc and not re.search(r"resuelto|cerrado|cancelado", (desc + " " + texto).lower()):
            try:
                antig = (time.time() - (memoria / (stem + ".md")).stat().st_mtime) / 86400
            except OSError:
                antig = 0
            if antig > dias:
                avisar(n["id"], "viejo", "medio",
                       f"Está marcado como pendiente y no se actualiza hace {int(antig)} días. Vale la pena confirmar si sigue vigente.")
        bolsas[n["id"]] = _palabras(texto + " " + (n.get("d") or ""))

    # 2. Recuerdos repetidos (parecido aproximado por palabras en común)
    ids = list(bolsas)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = bolsas[ids[i]], bolsas[ids[j]]
            if len(a) < 8 or len(b) < 8:
                continue
            parecido = len(a & b) / len(a | b)
            if parecido >= umbral:
                pct = int(parecido * 100)
                na, nb = ids[i][2:], ids[j][2:]
                avisar(ids[i], "repetido", "medio", f"Se parece mucho al recuerdo «{nb}» ({pct}% de palabras en común). Quizás convenga unirlos.")
                avisar(ids[j], "repetido", "medio", f"Se parece mucho al recuerdo «{na}» ({pct}% de palabras en común). Quizás convenga unirlos.")

    # 4. Piezas sueltas: archivos de código sin ninguna conexión con el resto
    conectados = set()
    for h in hilos:
        if h["k"] == "contiene":
            continue
        for extremo in (h["s"], h["t"]):
            conectados.add(extremo if not extremo.startswith("f:") else "a:" + extremo[2:].split("::")[0])
    for n in neuronas:
        if n["t"] == "archivo" and n["e"] in EXT_CODIGO and n["id"] not in conectados:
            avisar(n["id"], "suelto", "medio", "Ningún otro archivo, documento o recuerdo lo usa ni lo menciona. Podría ser un resto que ya no se usa.")

    resumen = {}
    for lista in salud.values():
        for p in lista:
            resumen[p["k"]] = resumen.get(p["k"], 0) + 1
    return salud, resumen


def construir():
    cfg = cargar_config()
    proyecto, memoria = resolver_rutas(cfg)
    if not proyecto.is_dir():
        print(f"[cerebro] La carpeta del proyecto no existe: {proyecto}")
        sys.exit(1)

    inicio = time.time()
    neuronas, hilos = [], []
    textos = {}
    funcs_por_nombre = {}
    llamados_py = []

    def agregar_hilo(a, b, tipo):
        if a != b:
            hilos.append({"s": a, "t": b, "k": tipo})

    # 1. Archivos y sus funciones
    for ruta, rel in listar_archivos(proyecto, cfg):
        texto = leer_texto(ruta)
        textos[rel] = texto
        ext = ruta.suffix.lower().lstrip(".")
        carpeta = rel.split("/")[0] if "/" in rel else "(raiz)"
        neuronas.append({"id": "a:" + rel, "n": ruta.name, "t": "archivo", "e": ext,
                         "g": carpeta, "v": texto.count("\n") + 1, "r": rel})
        if ext == "py":
            fs = funciones_python(texto)
        elif ext in ("js", "html"):
            fs = funciones_js(texto)
        else:
            fs = []
        vistos = set()
        for nombre, linea, llamados in fs:
            if nombre in vistos:
                continue
            vistos.add(nombre)
            fid = f"f:{rel}::{nombre}"
            neuronas.append({"id": fid, "n": nombre, "t": "funcion", "e": ext,
                             "g": carpeta, "v": 1, "r": rel, "l": linea})
            agregar_hilo("a:" + rel, fid, "contiene")
            funcs_por_nombre.setdefault(nombre, []).append(fid)
            if llamados:
                llamados_py.append((fid, llamados))

    nombres_archivo = {}
    for rel in textos:
        nombres_archivo.setdefault(rel.rsplit("/", 1)[-1], []).append(rel)
    modulos_py = {rel.rsplit("/", 1)[-1][:-3]: rel for rel in textos if rel.endswith(".py")}
    minimo = cfg["largo_minimo_nombre_funcion"]
    unicas = {n: ids[0] for n, ids in funcs_por_nombre.items() if len(ids) == 1 and len(n) >= minimo}

    # 2. Llamadas entre funciones de Python
    for fid, llamados in llamados_py:
        for nombre in llamados:
            destino = unicas.get(nombre)
            if destino:
                agregar_hilo(fid, destino, "llama")

    # 3. Importaciones de Python entre archivos del proyecto
    for rel, texto in textos.items():
        if rel.endswith(".py"):
            for mod in importaciones_python(texto):
                if mod in modulos_py:
                    agregar_hilo("a:" + rel, "a:" + modulos_py[mod], "importa")

    # 4. Archivos que usan funciones definidas en OTRO archivo, y menciones de archivos
    patron_archivos = re.compile("|".join(re.escape(n) for n in sorted(nombres_archivo, key=len, reverse=True))) if nombres_archivo else None
    for rel, texto in textos.items():
        if not rel.endswith(".md"):
            usados = set(RE_IDENT.findall(texto)) & unicas.keys()
            for nombre in usados:
                destino = unicas[nombre]
                if not destino.startswith(f"f:{rel}::"):
                    agregar_hilo("a:" + rel, destino, "usa")
        if patron_archivos:
            for nombre in set(patron_archivos.findall(texto)):
                for destino in nombres_archivo[nombre]:
                    if destino != rel:
                        agregar_hilo("a:" + rel, "a:" + destino, "menciona")

    # 5. Memoria de Claude
    n_memoria = 0
    if memoria and memoria.is_dir():
        notas = {}
        for ruta in sorted(memoria.glob("*.md")):
            texto = leer_texto(ruta)
            nombre, desc = frontmatter_memoria(texto)
            mid = "m:" + ruta.stem
            notas[ruta.stem] = mid
            if nombre:
                notas[nombre] = mid
            neuronas.append({"id": mid, "n": nombre or ruta.stem, "t": "memoria", "e": "md",
                             "g": "memoria", "v": texto.count("\n") + 1, "d": desc[:240]})
            textos["__mem__" + ruta.stem] = texto
            n_memoria += 1
        for ruta in sorted(memoria.glob("*.md")):
            texto = textos["__mem__" + ruta.stem]
            origen = notas[ruta.stem]
            for enlace in RE_ENLACE_MEMORIA.findall(texto):
                destino = notas.get(enlace.strip()) or notas.get(enlace.strip().replace("-", "_"))
                if destino:
                    agregar_hilo(origen, destino, "recuerda")
            for m in re.finditer(r"\]\(([^)]+\.md)\)", texto):
                destino = notas.get(Path(m.group(1)).stem)
                if destino:
                    agregar_hilo(origen, destino, "recuerda")
            if patron_archivos:
                for nombre in set(patron_archivos.findall(texto)):
                    for destino in nombres_archivo[nombre]:
                        agregar_hilo(origen, "a:" + destino, "menciona")
            usados = set(RE_IDENT.findall(texto)) & unicas.keys()
            for nombre in usados:
                agregar_hilo(origen, unicas[nombre], "menciona")

    # Quitar hilos repetidos
    unicos, vistos = [], set()
    for h in hilos:
        clave = (h["s"], h["t"], h["k"])
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(h)

    salud, resumen_salud = revisar_salud(proyecto, memoria, neuronas, unicos, textos, cfg)
    datos = {"salud": salud, "salud_resumen": resumen_salud, "proyecto": proyecto.name, "nucleo": cfg.get("nombre_nucleo") or proyecto.name, "asistente": cfg.get("asistente") or "la IA", "etiquetas": cfg.get("etiquetas", {}), "generado": time.strftime("%Y-%m-%d %H:%M:%S"),
             "neuronas": neuronas, "hilos": unicos}
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("window.CEREBRO=" + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";",
                      encoding="utf-8")
    n_arch = sum(1 for n in neuronas if n["t"] == "archivo")
    print(f"[cerebro] Listo en {time.time() - inicio:.1f} s: {n_arch} archivos, "
          f"{len(neuronas) - n_arch - n_memoria} funciones, {n_memoria} recuerdos, {len(unicos)} hilos. Salud: {resumen_salud or 'sin avisos'}.")


if __name__ == "__main__":
    construir()
