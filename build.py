"""Generate the Light and OLED variants from themes/matcha-latte-color-theme.json.

Edit the dark theme, then run: python3 build.py
"""
import json
import re
from pathlib import Path

THEMES = Path(__file__).parent / "themes"
SOURCE = THEMES / "matcha-latte-color-theme.json"

LIGHT_MAP = {
    # backgrounds
    "26221C": "F8F4EC",
    "201D18": "ECE4D5",
    "191612": "E3D9C6",
    "2F2A22": "EAE1CF",
    "2A261F": "E6DCC9",
    "3B352C": "D6CAB3",
    "34302A": "DED3BF",
    "463F35": "CFC2AA",
    "5A5145": "A8998A",
    "685E51": "6E6356",
    "5A4A38": "8A6248",
    # text
    "EADFCF": "211D18",
    "F5EDE1": "15120E",
    "D8CBB8": "3B352C",
    "A39A8D": "564C41",
    "8B7F6E": "6E6355",
    "E6CBAE": "6A4A30",
    # syntax
    "9FC48A": "2B721B",
    "C9E0B4": "245F17",
    "7FB59A": "1F6E5A",
    "D9AE82": "9A4F10",
    "E8C27A": "1A6A82",
    "E3A07C": "B0341C",
    "C9B3D6": "7A3DA8",
    "E58B7A": "B02A1A",
    # terminal
    "F2D49A": "8A6A10",
    "F0A495": "C25A45",
    "DDB9CE": "9C5E8A",
    "C8A0B8": "8A4F78",
    "A9C6D8": "4E7E9E",
    "9ACDB3": "3E8A6A",
    "8FB0C4": "3D6A8A",
}

LIGHT_OVERRIDES = {
    "statusBar.foreground": "#191612",
    "statusBar.debuggingForeground": "#191612",
    "statusBarItem.hoverBackground": "#19161222",
    "statusBarItem.remoteForeground": "#F8F4EC",
    "activityBarBadge.background": "#8DB37C",
    "activityBarBadge.foreground": "#191612",
    "button.foreground": "#191612",
    "button.hoverBackground": "#9FC48A",
    "button.secondaryForeground": "#F8F4EC",
    "badge.foreground": "#191612",
    "editorWarning.foreground": "#9A6A00",
    "terminal.ansiBlack": "#33271F",
    "terminal.ansiWhite": "#8F7F6E",
    "terminal.ansiBrightWhite": "#6E5F51",
}

OLED_MAP = {
    "26221C": "000000",
    "201D18": "000000",
    "191612": "000000",
    "2F2A22": "13110E",
    "2A261F": "110F0C",
    "3B352C": "26221C",
    "34302A": "1C1915",
    "463F35": "2A261F",
}

OLED_OVERRIDES = {
    "sideBar.border": "#1C1915",
    "editorGroup.border": "#1C1915",
    "tab.border": "#1C1915",
    "titleBar.border": "#1C1915",
    "editorWidget.background": "#0C0B09",
    "editorSuggestWidget.background": "#0C0B09",
    "editorHoverWidget.background": "#0C0B09",
}

HEX = re.compile(r"#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?")


def recolor(value, mapping):
    if isinstance(value, str):
        return HEX.sub(lambda m: "#" + mapping.get(m[1].upper(), m[1].upper()) + (m[2] or ""), value)
    if isinstance(value, list):
        return [recolor(v, mapping) for v in value]
    if isinstance(value, dict):
        return {k: recolor(v, mapping) for k, v in value.items()}
    return value


def build(name, kind, mapping, overrides, out):
    theme = json.loads(SOURCE.read_text())
    theme = recolor(theme, mapping)
    theme["name"] = name
    theme["type"] = kind
    theme["colors"].update(overrides)
    (THEMES / out).write_text(json.dumps(theme, indent=2) + "\n")
    print("wrote", out)


build("Matcha Latte Light", "light", LIGHT_MAP, LIGHT_OVERRIDES, "matcha-latte-light-color-theme.json")
build("Matcha Latte OLED", "dark", OLED_MAP, OLED_OVERRIDES, "matcha-latte-oled-color-theme.json")
