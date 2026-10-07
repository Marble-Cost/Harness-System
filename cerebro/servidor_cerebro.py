"""Cerebro de IA - Servidor local en vivo.

Sirve el visor y transmite al navegador, al instante, cada accion que
Claude anota con registrar_evento.py (Server-Sent Events en /eventos).

Solo escucha en 127.0.0.1: nada sale del computador.
Mientras corre, renueva el archivo estado/latido; al cerrarse, el cerebro
queda "apagado" y el anotador deja de escribir.

Uso:  python servidor_cerebro.py
"""
import json
import subprocess
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ESTADO = RAIZ / "estado"
LATIDO = ESTADO / "latido"
EVENTOS = ESTADO / "eventos.jsonl"
PUERTO = 8765


def cargar_config():
    try:
        return json.loads((RAIZ / "cerebro_config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[cerebro] No se pudo leer cerebro_config.json: {e}")
        sys.exit(1)


CFG = cargar_config()
from cerebro import resolver_rutas  # misma regla de rutas que el lector
_proy, _mem = resolver_rutas(CFG)
PROYECTO = os.path.normcase(str(_proy))
MEMORIA = os.path.normcase(str(_mem)) if _mem else None
PUERTO = int(CFG.get("puerto", PUERTO))


def neurona_de(ruta):
    """Id de la neurona que corresponde a un archivo, o None si no es del proyecto ni de la memoria."""
    original = os.path.abspath(ruta)
    abs_ruta = os.path.normcase(original)  # solo para comparar; Windows no distingue mayúsculas
    if abs_ruta.startswith(PROYECTO + os.sep):
        return "a:" + original[len(PROYECTO) + 1:].replace(os.sep, "/")
    if MEMORIA and abs_ruta.startswith(MEMORIA + os.sep) and abs_ruta.endswith(".md"):
        return "m:" + os.path.splitext(os.path.basename(original))[0]
    return None


def traducir(ev):
    """Convierte un evento crudo en lo que el visor necesita: neurona y texto amable."""
    tool = ev.get("tool", "")
    ruta = ev.get("ruta", "")
    neurona, nombre = None, ""
    if ruta:
        nombre = os.path.basename(ruta)
        neurona = neurona_de(ruta)
    # Comandos de consola: neuronas de los archivos que el comando nombra
    neuronas = [n for n in (neurona_de(r) for r in ev.get("rutas") or []) if n]
    neuronas = list(dict.fromkeys(neuronas))  # sin repetidas, en el orden del comando
    if not neurona and neuronas:
        neurona = neuronas[0]
    acciones = {
        "Read": ("leer", f"Leyendo {nombre}"),
        "Edit": ("editar", f"Editando {nombre}"),
        "MultiEdit": ("editar", f"Editando {nombre}"),
        "Write": ("crear", f"Escribiendo {nombre}"),
        "NotebookEdit": ("editar", f"Editando {nombre}"),
        "Grep": ("buscar", f"Buscando \"{ev.get('patron', '')}\""),
        "Glob": ("buscar", f"Buscando archivos \"{ev.get('patron', '')}\""),
        "Bash": ("comando", ev.get("desc") or "Ejecutando un comando"),
        "PowerShell": ("comando", ev.get("desc") or "Ejecutando un comando"),
        "Agent": ("agente", f"Lanzó un agente: {ev.get('desc') or ev.get('tipo_agente') or 'ayudante'}"),
        "Task": ("agente", f"Lanzó un agente: {ev.get('desc') or ev.get('tipo_agente') or 'ayudante'}"),
        "WebSearch": ("buscar", "Buscando en internet"),
        "WebFetch": ("leer", "Consultando una página web"),
        # Modo universal: cambios vistos en la carpeta (cualquier IA o persona)
        "_creado": ("crear", f"Se creó {nombre}"),
        "_modificado": ("editar", f"Se modificó {nombre}"),
        "_borrado": ("borrar", f"Se borró {nombre}"),
        "_varios": ("editar", ev.get("desc") or "Cambiaron varios archivos"),
    }
    hook = ev.get("ev", "")
    if hook == "UserPromptSubmit":
        accion, texto = "pedido", "Recibió un pedido nuevo"
    elif hook == "Stop":
        accion, texto = "fin", "Terminó y responde"
    elif hook == "SubagentStop":
        accion, texto = "fin_agente", "Un agente terminó su trabajo"
    elif tool in acciones:
        accion, texto = acciones[tool]
    elif tool.startswith("mcp__claude-in-chrome"):
        accion, texto = "leer", "Mirando el navegador"
    elif tool.startswith("mcp__codebase-memory"):
        accion, texto = "buscar", "Consultando el mapa del código"
    elif tool in ("Skill", "ToolSearch"):
        accion, texto = "herramienta", "Preparando una herramienta"
    elif tool.startswith("mcp__"):
        accion, texto = "herramienta", "Usando la herramienta " + tool.split("__")[-1].replace("_", " ")
    else:
        accion, texto = "herramienta", f"Usando {tool or 'una herramienta'}"
    return {"t": ev.get("t"), "accion": accion, "texto": texto, "neurona": neurona,
            "neuronas": neuronas or ([neurona] if neurona else []),
            "agente": ev.get("agente") or "", "tipo_agente": ev.get("tipo_agente") or ""}


class Manejador(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(RAIZ), **k)

    def log_message(self, formato, *args):
        pass  # silencio en consola: solo mostramos mensajes propios

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/eventos":
            return self.transmitir()
        if self.path.startswith("/estado/"):
            self.send_error(404)
            return
        return super().do_GET()

    def transmitir(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            pos = EVENTOS.stat().st_size if EVENTOS.exists() else 0
            ultimo_ping = time.time()
            version_enviada = VERSION_DATOS[0]
            while True:
                if VERSION_DATOS[0] != version_enviada:  # el cerebro se rehízo: nacen neuronas
                    version_enviada = VERSION_DATOS[0]
                    self.wfile.write(b'data: {"tipo": "recarga"}\n\n')
                    self.wfile.flush()
                if EVENTOS.exists() and EVENTOS.stat().st_size > pos:
                    with open(EVENTOS, "r", encoding="utf-8") as f:
                        f.seek(pos)
                        lineas = f.readlines()
                        pos = f.tell()
                    for linea in lineas:
                        try:
                            dato = traducir(json.loads(linea))
                        except (ValueError, KeyError):
                            continue
                        self.wfile.write(("data: " + json.dumps(dato, ensure_ascii=False) + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                elif time.time() - ultimo_ping > 15:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    ultimo_ping = time.time()
                time.sleep(0.2)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return  # el navegador cerró la pestaña


VERSION_DATOS = [0]  # sube cada vez que el cerebro se rehace mientras está abierto
CAMBIAN_ARCHIVOS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
ESPERA_TRAS_CAMBIO = 4  # segundos de calma antes de rehacer (agrupa varias ediciones seguidas)


CADA_CUANTO_MIRAR = 1.5  # segundos entre revisiones de la carpeta (modo universal)
MAX_AVISOS_JUNTOS = 10  # si cambian muchos archivos a la vez, se resume en una línea
EXTS = {e.lower() for e in CFG.get("extensiones", [])}
EXCLUIDAS = set(CFG.get("carpetas_excluidas", [])) | {RAIZ.name}


def foto_carpeta():
    """Fecha de última modificación de cada archivo que el cerebro dibuja."""
    foto = {}
    for raiz, dirs, archivos in os.walk(str(_proy)):
        dirs[:] = [d for d in dirs if d not in EXCLUIDAS]
        for a in archivos:
            if os.path.splitext(a)[1].lower() in EXTS:
                p = os.path.join(raiz, a)
                try:
                    foto[p] = os.path.getmtime(p)
                except OSError:
                    continue
    if _mem and os.path.isdir(_mem):
        for a in os.listdir(_mem):
            if a.endswith(".md"):
                p = os.path.join(str(_mem), a)
                try:
                    foto[p] = os.path.getmtime(p)
                except OSError:
                    continue
    return foto


def anotar(tool, ruta="", desc=""):
    linea = {"t": time.time(), "ev": "Carpeta", "tool": tool, "ruta": ruta, "patron": "", "desc": desc,
             "tipo_agente": "", "agente": "", "cwd": ""}
    with open(EVENTOS, "a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")


def vigilar_cambios(parar):
    """Modo detallado (avisos de Claude Code) + modo universal (mirar la carpeta,
    sirve con cualquier IA o persona). Cuando algo cambia, rehace el cerebro en
    segundo plano para que las neuronas nuevas nazcan en vivo en el visor."""
    pos, pendiente, ultimo = 0, False, 0.0
    recientes = {}  # rutas que Claude ya anunció: no se repiten como "Se modificó"
    anterior, ultima_mirada = foto_carpeta(), time.time()
    while not parar.is_set():
        try:
            if EVENTOS.exists() and EVENTOS.stat().st_size > pos:
                with open(EVENTOS, "r", encoding="utf-8") as f:
                    f.seek(pos)
                    lineas = f.readlines()
                    pos = f.tell()
                for linea in lineas:
                    try:
                        ev = json.loads(linea)
                    except ValueError:
                        continue
                    if ev.get("tool") in CAMBIAN_ARCHIVOS:
                        pendiente, ultimo = True, time.time()
                        if ev.get("ruta"):
                            recientes[os.path.normcase(os.path.abspath(ev["ruta"]))] = time.time()
            if time.time() - ultima_mirada >= CADA_CUANTO_MIRAR:
                ultima_mirada = time.time()
                actual = foto_carpeta()
                cambios = [("_creado", p) for p in actual if p not in anterior]
                cambios += [("_modificado", p) for p in actual if p in anterior and actual[p] != anterior[p]]
                cambios += [("_borrado", p) for p in anterior if p not in actual]
                anterior = actual
                if cambios:
                    pendiente, ultimo = True, time.time()
                    nuevos = [(t, p) for t, p in cambios
                              if time.time() - recientes.get(os.path.normcase(p), 0) > 15]
                    for t, p in nuevos[:MAX_AVISOS_JUNTOS]:
                        anotar(t, p)
                    if len(nuevos) > MAX_AVISOS_JUNTOS:
                        anotar("_varios", desc=f"Cambiaron {len(nuevos) - MAX_AVISOS_JUNTOS} archivos más")
            if pendiente and time.time() - ultimo > ESPERA_TRAS_CAMBIO:
                pendiente = False
                r = subprocess.run([sys.executable, str(RAIZ / "cerebro.py")], cwd=str(RAIZ),
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
                if r.returncode == 0:
                    VERSION_DATOS[0] += 1
                else:
                    print(f"[cerebro] Aviso: no se pudo rehacer el cerebro: {r.stderr.strip()[-300:]}")
        except (OSError, subprocess.SubprocessError) as e:
            print(f"[cerebro] Aviso al vigilar cambios: {e}")
        parar.wait(0.5)


def latir(parar):
    while not parar.is_set():
        try:
            LATIDO.touch()
        except OSError as e:
            print(f"[cerebro] Aviso: no se pudo renovar el latido: {e}")
        parar.wait(5)


def main():
    ESTADO.mkdir(exist_ok=True)
    EVENTOS.write_text("", encoding="utf-8")  # cada encendido empieza limpio
    parar = threading.Event()
    threading.Thread(target=latir, args=(parar,), daemon=True).start()
    threading.Thread(target=vigilar_cambios, args=(parar,), daemon=True).start()
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador)
    servidor.daemon_threads = True
    print(f"[cerebro] Encendido en http://127.0.0.1:{PUERTO}/visor.html")
    print("[cerebro] Cierre esta ventana (o Ctrl+C) para apagarlo.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("[cerebro] Apagando...")
    finally:
        parar.set()
        try:
            LATIDO.unlink()
        except OSError:
            pass  # si no existe, el cerebro ya figura apagado
        servidor.server_close()


if __name__ == "__main__":
    main()
