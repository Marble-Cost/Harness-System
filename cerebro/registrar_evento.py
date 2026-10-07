"""Cerebro de IA - Anotador de eventos.

Claude Code lo ejecuta (en segundo plano) cada vez que usa una herramienta.
Si el cerebro esta apagado termina al instante sin hacer nada. Si esta
encendido, anota una linea con la accion en estado/eventos.jsonl.

Solo guarda nombres de archivos y descripciones cortas; nunca el contenido.
De los comandos de consola tampoco guarda el texto: solo las rutas de los
archivos que el comando nombra y que existen de verdad en el disco.
"""
import glob
import json
import os
import re
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
LATIDO = os.path.join(RAIZ, "estado", "latido")
EVENTOS = os.path.join(RAIZ, "estado", "eventos.jsonl")
SEGUNDOS_VIGENCIA = 30  # el servidor renueva el latido cada pocos segundos
COMANDOS = {"Bash", "PowerShell"}
MAX_RUTAS = 6  # archivos por comando que se anotan como máximo
PALABRA = re.compile(r'"([^"]+)"|\'([^\']+)\'|([^\s"\'|;&<>()]+)')


def cerebro_encendido():
    try:
        return time.time() - os.path.getmtime(LATIDO) < SEGUNDOS_VIGENCIA
    except OSError:
        return False


def _ruta_windows(p):
    """Convierte /d/Users/... (Git Bash) en D:/Users/... y expande el ~ inicial."""
    m = re.match(r"^/([a-zA-Z])/(.*)", p)
    if m:
        p = m.group(1).upper() + ":/" + m.group(2)
    if p.startswith("~"):
        p = os.path.expanduser(p)
    return p


def rutas_en_comando(comando, cwd):
    """Archivos existentes que el comando nombra (sin guardar el comando)."""
    bases = [cwd] if cwd else []
    candidatos = []
    for m in PALABRA.finditer(comando or ""):
        palabra = _ruta_windows(next(g for g in m.groups() if g is not None).strip())
        if not palabra or palabra.startswith("-") or "$" in palabra or len(palabra) > 400:
            continue
        candidatos.append(palabra)
    encontradas = []
    for palabra in candidatos:
        intentos = [palabra] if os.path.isabs(palabra) else [os.path.join(b, palabra) for b in bases]
        for intento in intentos:
            if os.path.isdir(intento):
                bases.append(intento)  # ej. cd "carpeta" && cat archivo
                break
            hallados = glob.glob(intento)[:MAX_RUTAS] if any(c in intento for c in "*?[") else [intento]
            hallados = [os.path.abspath(h) for h in hallados if os.path.isfile(h)]
            if hallados:
                encontradas.extend(h for h in hallados if h not in encontradas)
                break
        if len(encontradas) >= MAX_RUTAS:
            break
    return encontradas[:MAX_RUTAS]


def main():
    if not cerebro_encendido():
        return
    try:
        datos = json.load(sys.stdin)
    except (ValueError, OSError):
        return
    entrada = datos.get("tool_input") or {}
    evento = {
        "t": time.time(),
        "ev": datos.get("hook_event_name", ""),
        "tool": datos.get("tool_name", ""),
        "ruta": entrada.get("file_path") or entrada.get("notebook_path") or entrada.get("path") or "",
        "patron": str(entrada.get("pattern") or entrada.get("query") or "")[:80],
        "desc": str(entrada.get("description") or "")[:120],
        "tipo_agente": entrada.get("subagent_type") or datos.get("agent_type") or "",
        "agente": datos.get("agent_id") or "",
        "cwd": datos.get("cwd", ""),
    }
    if evento["tool"] in COMANDOS:
        try:
            evento["rutas"] = rutas_en_comando(str(entrada.get("command") or ""), evento["cwd"])
        except (OSError, ValueError, re.error):
            evento["rutas"] = []  # si no se entiende el comando, el aviso sale igual, sin brillo
    try:
        with open(EVENTOS, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except OSError:
        pass  # anotar es opcional: si falla, Claude sigue trabajando sin cambios


if __name__ == "__main__":
    main()
