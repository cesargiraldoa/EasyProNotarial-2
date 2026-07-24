#!/usr/bin/env python3
"""Valida un molde (.html + .map.json) antes de entregarlo.

Uso:
    python validate_molde.py <slug>.html <slug>.map.json

Comprueba:
  1. [[if ...]] y [[/if]] balanceados.
  2. {{ y }} balanceados.
  3. El .map.json parsea y tiene los campos mínimos.
  4. Cada token del .map.json aparece en el HTML, y viceversa (avisos).
  5. Prueba de relleno: simula el motor (resuelve [[if]] con un estado de prueba
     y quita los {{tokens}}). Al final NO deben quedar {{, [[if ni [[/if]] sueltos.
  6. La afectación (código 304 / "AFECTACIÓN A VIVIENDA FAMILIAR") aparece con
     afect="si" y desaparece con afect="no".

Sale con código 0 si todo pasa; 1 si hay errores.
"""
from __future__ import annotations

import json
import re
import sys

TOKEN_RE = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
IF_OPEN_RE = re.compile(r"\[\[if\s+([^\]]+?)\]\]")
IF_CLOSE = "[[/if]]"


def _fail(msg: str) -> None:
    print(f"  [ERROR] {msg}")


def resolve_conditionals(html: str, state: dict) -> str:
    """Imita el motor: resuelve [[if COND]]…[[/if]] de adentro hacia afuera."""
    inner = re.compile(r"\[\[if ([^\]]+?)\]\]((?:(?!\[\[if ).)*?)\[\[/if\]\]", re.DOTALL)

    def truthy(cond: str) -> bool:
        cond = cond.strip()
        m = re.match(r"^(\S+)\s+in\s+(.+)$", cond)
        if m:
            value = state.get(m.group(1))
            options = [o.strip() for o in m.group(2).split("|")]
            return isinstance(value, str) and value in options
        value = state.get(cond)
        if cond == "vis":
            return isinstance(value, str) and value not in ("no", "")
        return bool(value)

    prev = None
    while prev != html:
        prev = html
        html = inner.sub(lambda mm: mm.group(2) if truthy(mm.group(1)) else "", html)
    return html


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python validate_molde.py <slug>.html <slug>.map.json", file=sys.stderr)
        return 2
    html_path, map_path = sys.argv[1], sys.argv[2]
    html = open(html_path, encoding="utf-8").read()
    errors = 0

    # 1. Balance de condicionales.
    opens = len(IF_OPEN_RE.findall(html))
    closes = html.count(IF_CLOSE)
    print(f"Condicionales: {opens} aperturas [[if]] / {closes} cierres [[/if]]")
    if opens != closes:
        _fail("aperturas y cierres [[if]] no coinciden."); errors += 1

    # 2. Balance de llaves de token.
    o, c = html.count("{{"), html.count("}}")
    print(f"Tokens: {o} '{{{{' / {c} '}}}}'")
    if o != c:
        _fail("'{{' y '}}' no coinciden."); errors += 1

    # 3. map.json.
    try:
        meta = json.load(open(map_path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"el .map.json no parsea: {exc}"); return 1
    for field in ("name", "acto", "fuente", "tokens"):
        if field not in meta:
            _fail(f"falta '{field}' en el .map.json."); errors += 1

    # 4. Tokens declarados vs usados.
    used = {t.strip() for t in TOKEN_RE.findall(html)}
    declared = {t.get("token") for t in meta.get("tokens", [])}
    for t in sorted(used - declared):
        print(f"  [AVISO] token '{t}' usado en HTML pero no declarado en map.json")
    for t in sorted(declared - used):
        print(f"  [AVISO] token '{t}' declarado en map.json pero no usado en HTML")

    # 5. Prueba de relleno.
    demo = {
        "credito": True, "ph": True, "afect": "si", "vis": "no", "subsidio": False,
        "C.0.estado": "casado_sc", "V.0.estado": "soltero",
    }
    filled = resolve_conditionals(html, demo)
    filled = TOKEN_RE.sub("·", filled)
    leftovers = []
    if "{{" in filled or "}}" in filled:
        leftovers.append("{{…}}")
    if "[[if" in filled or IF_CLOSE in filled:
        leftovers.append("[[if…]]")
    if leftovers:
        _fail(f"tras rellenar quedaron marcadores sueltos: {', '.join(leftovers)}"); errors += 1
    else:
        print("Prueba de relleno: sin marcadores sobrantes. OK")

    # 6. Afectación aparece/desaparece con afect.
    if "AFECTACIÓN A VIVIENDA FAMILIAR" in html or "afect in si" in html:
        con = resolve_conditionals(html, {**demo, "afect": "si"})
        sin = resolve_conditionals(html, {**demo, "afect": "no"})
        aparece = "AFECTACIÓN A VIVIENDA FAMILIAR" in con
        oculta = "AFECTACIÓN A VIVIENDA FAMILIAR" not in sin
        if aparece and oculta:
            print("Afectación: aparece con afect='si' y se oculta con 'no'. OK")
        else:
            _fail("la afectación no responde bien a afect (¿usaste [[if afect in si]]?)."); errors += 1

    print()
    if errors:
        print(f"❌ {errors} error(es). Corrige y vuelve a validar.")
        return 1
    print("✅ Molde válido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
