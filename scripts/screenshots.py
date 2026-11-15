"""Render a preview PNG of each theme into images/, using the theme JSON's own colours.

Needs google-chrome-stable on PATH. Run: python3 scripts/screenshots.py
"""
import html
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = {
    "dark": "matcha-latte-color-theme.json",
    "light": "matcha-latte-light-color-theme.json",
    "oled": "matcha-latte-oled-color-theme.json",
}

KW, ST, CM, TY, FN, PR, PA, NU, OP, PU = (
    "keyword.control", "string.quoted", "comment.line", "entity.name.type", "entity.name.function",
    "variable.other.property", "variable.parameter", "constant.numeric", "keyword.operator", "punctuation",
)
SAMPLE = [
    [("import", KW), (" { ", PU), ("useState", None), (" } ", PU), ("from", KW), (" ", None), ('"react"', ST), (";", PU)],
    [],
    [("// Every tracker that has been opened at least once", CM)],
    [("interface", KW), (" ", None), ("Tracker", TY), (" {", PU)],
    [("  ", None), ("id", PR), (": ", PU), ("number", "support.type"), (";", PU)],
    [("  ", None), ("name", PR), (": ", PU), ("string", "support.type"), (";", PU)],
    [("  ", None), ("lastChecked", PR), (": ", PU), ("Date", TY), (" ", None), ("|", OP), (" ", None), ("null", "constant.language"), (";", PU)],
    [("}", PU)],
    [],
    [("export", KW), (" ", None), ("async", KW), (" ", None), ("function", KW), (" ", None), ("loadTrackers", FN), ("(", PU), ("limit", PA), (" ", None), ("=", OP), (" ", None), ("20", NU), ("): ", PU), ("Promise", TY), ("<", PU), ("Tracker", TY), ("[]> {", PU)],
    [("  ", None), ("const", KW), (" res ", None), ("=", OP), (" ", None), ("await", KW), (" ", None), ("fetch", FN), ("(", PU), ("`/api/trackers/?limit=", ST), ("${", KW), ("limit", None), ("}", KW), ("`", ST), (");", PU)],
    [("  ", None), ("if", KW), (" (", PU), ("!", OP), ("res", None), (".", PU), ("ok", PR), (") ", PU), ("throw", KW), (" ", None), ("new", KW), (" ", None), ("Error", TY), ("(", PU), ('"backend unreachable"', ST), (");", PU)],
    [("  ", None), ("const", KW), (" data", None), (": ", PU), ("Tracker", TY), ("[] ", PU), ("=", OP), (" ", None), ("await", KW), (" res", None), (".", PU), ("json", FN), ("();", PU)],
    [("  ", None), ("return", KW), (" data", None), (".", PU), ("filter", FN), ("((", PU), ("t", PA), (") ", PU), ("=>", KW), (" t", None), (".", PU), ("lastChecked", PR), (" ", None), ("!==", OP), (" ", None), ("null", "constant.language"), (");", PU)],
    [("}", PU)],
]


def style_for(theme, scope):
    if scope is None:
        return {}
    best, best_len = {}, -1
    for rule in theme["tokenColors"]:
        scopes = rule["scope"] if isinstance(rule["scope"], list) else [rule["scope"]]
        for s in scopes:
            if (scope == s or scope.startswith(s + ".")) and len(s) > best_len:
                best, best_len = rule["settings"], len(s)
    return best


def css_for(settings):
    out = []
    if "foreground" in settings:
        out.append(f"color:{settings['foreground']}")
    fs = settings.get("fontStyle", "")
    out.append("font-weight:700" if "bold" in fs else "")
    out.append("font-style:italic" if "italic" in fs else "")
    return ";".join(o for o in out if o)


def render_html(theme):
    c = theme["colors"]
    lines = []
    for i, line in enumerate(SAMPLE, 1):
        spans = "".join(f'<span style="{css_for(style_for(theme, sc))}">{html.escape(t)}</span>' for t, sc in line)
        hl = f"background:{c['editor.lineHighlightBackground']};" if i == 11 else ""
        num = c["editorLineNumber.activeForeground"] if i == 11 else c["editorLineNumber.foreground"]
        lines.append(f'<div class="ln" style="{hl}"><span class="num" style="color:{num}">{i}</span>{spans}</div>')
    return f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;font:14px/1.6 'JetBrainsMono Nerd Font','JetBrains Mono','DejaVu Sans Mono',monospace}}
.win{{width:900px;height:520px;display:flex;flex-direction:column;background:{c['editor.background']};color:{c['editor.foreground']}}}
.title{{height:30px;background:{c['titleBar.activeBackground']};color:{c['titleBar.activeForeground']};display:flex;align-items:center;justify-content:center;font:12px sans-serif}}
.mid{{flex:1;display:flex;min-height:0}}
.act{{width:44px;background:{c['activityBar.background']};border-left:2px solid {c['activityBar.activeBorder']};box-sizing:border-box}}
.side{{width:170px;background:{c['sideBar.background']};color:{c['sideBar.foreground']};font:12px sans-serif;padding:10px 12px;box-sizing:border-box}}
.side .sel{{background:{c['list.activeSelectionBackground']};color:{c['list.activeSelectionForeground']};margin:0 -12px;padding:2px 12px}}
.side div{{padding:2px 0}}
.ed{{flex:1;display:flex;flex-direction:column;min-width:0}}
.tabs{{height:34px;background:{c['editorGroupHeader.tabsBackground']};display:flex;font:12px sans-serif}}
.tab{{padding:0 16px;display:flex;align-items:center;color:{c['tab.inactiveForeground']}}}
.tab.on{{background:{c['tab.activeBackground']};color:{c['tab.activeForeground']};border-top:2px solid {c['tab.activeBorderTop']}}}
.code{{padding:8px 0;font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0;white-space:pre;overflow:hidden}}
.num{{display:inline-block;width:44px;text-align:right;padding-right:18px}}
.status{{height:24px;background:{c['statusBar.background']};color:{c['statusBar.foreground']};font:12px sans-serif;display:flex;align-items:center;padding:0 12px;gap:18px}}
</style><div class="win"><div class="title">{html.escape(theme['name'])}</div><div class="mid"><div class="act"></div>
<div class="side"><div style="opacity:.7;font-size:11px;letter-spacing:.06em">EXPLORER</div><div>api.ts</div><div class="sel">trackers.ts</div><div>App.tsx</div><div>index.css</div></div>
<div class="ed"><div class="tabs"><div class="tab on">trackers.ts</div><div class="tab">App.tsx</div></div><div class="code">{''.join(lines)}</div></div></div>
<div class="status"><span>beta</span><span>TypeScript</span><span style="margin-left:auto">Ln 11, Col 42</span></div></div>"""


for key, filename in THEMES.items():
    theme = json.loads((ROOT / "themes" / filename).read_text())
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(render_html(theme))
    out = ROOT / "images" / f"preview-{key}.png"
    subprocess.run(
        ["google-chrome-stable", "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=2", "--window-size=900,520", f"--screenshot={out}", f"file://{f.name}"],
        check=True, capture_output=True,
    )
    Path(f.name).unlink()
    print("wrote", out.relative_to(ROOT))
