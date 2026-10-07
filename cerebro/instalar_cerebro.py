"""Cerebro de IA - Instalador de los avisos (hooks) de Claude Code.

Agrega a <proyecto>/.claude/settings.local.json los avisos que permiten ver a Claude
trabajar en vivo dentro del cerebro. Conserva todo lo que el archivo ya tenga,
deja un respaldo y verifica que el resultado sea JSON válido.

Uso:
    python instalar_cerebro.py           instala (si ya estaba, no duplica)
    python instalar_cerebro.py --quitar  quita solo los avisos del cerebro
"""
import json
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from cerebro import cargar_config, resolver_rutas  # noqa: E402

EVENTOS = ("PreToolUse", "UserPromptSubmit", "Stop", "SubagentStop")
MARCA = "registrar_evento.py"


def aviso():
    return {"type": "command", "command": sys.executable,
            "args": [str(RAIZ / "registrar_evento.py")], "async": True, "timeout": 5}


def es_del_cerebro(grupo):
    return any(MARCA in " ".join([h.get("command", "")] + h.get("args", [])) for h in grupo.get("hooks", []))


def main():
    quitar = "--quitar" in sys.argv
    proyecto, _ = resolver_rutas(cargar_config())
    # settings.local.json: lleva rutas propias de este computador, por eso no va al historial
    destino = proyecto / ".claude" / "settings.local.json"
    destino.parent.mkdir(exist_ok=True)
    datos = {}
    if destino.exists():
        try:
            datos = json.loads(destino.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[cerebro] {destino} no es JSON válido ({e}); no se toca nada.")
            sys.exit(1)
        respaldo = destino.with_name(f"settings.respaldo_{time.strftime('%Y%m%d_%H%M%S')}.json")
        shutil.copy2(destino, respaldo)
        print(f"[cerebro] Respaldo: {respaldo.name}")

    hooks = datos.setdefault("hooks", {})
    for ev in EVENTOS:
        grupos = [g for g in hooks.get(ev, []) if not es_del_cerebro(g)]
        if not quitar:
            grupo = {"hooks": [aviso()]}
            if ev == "PreToolUse":
                grupo = {"matcher": "*", **grupo}
            grupos.append(grupo)
        if grupos:
            hooks[ev] = grupos
        else:
            hooks.pop(ev, None)
    if not hooks:
        datos.pop("hooks")

    texto = json.dumps(datos, ensure_ascii=False, indent=2)
    json.loads(texto)  # verificación: nunca se escribe un archivo inválido
    destino.write_text(texto + "\n", encoding="utf-8")
    print(f"[cerebro] Avisos {'quitados de' if quitar else 'instalados en'} {destino}")
    if not quitar:
        print("[cerebro] Si Claude Code ya estaba abierto, escriba /hooks una vez o reinícielo para activarlos.")


if __name__ == "__main__":
    main()
