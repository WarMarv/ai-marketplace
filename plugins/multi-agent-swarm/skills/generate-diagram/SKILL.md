---
name: generate-diagram
description: Regenerate the architecture Mermaid diagram for the current project — reads hooks, agents, and commands from live sources and writes docs/architecture/system-overview.md.
version: 1.0.0
---

# /generate-diagram
# Input: keines
# Output: docs/architecture/system-overview.md mit aktuellem Mermaid-Diagramm überschreiben

Generiert das Architekturdiagramm für dieses Repository neu und schreibt es direkt nach `docs/architecture/system-overview.md`. Der Trigger-Check des Documenter-Agenten wird dabei **übersprungen** — das Diagramm wird immer neu erzeugt.

---

## Phase 1 — Datenquellen auslesen

**1. Hooks aus `.claude/settings.json` lesen**
Lies `.claude/settings.json` und extrahiere alle Hook-Einträge. Leite für jeden Hook ab:
- **Name**: Dateiname des Hook-Skripts ohne Pfad und ohne `.py`-Suffix (z.B. `dangerous-command-blocker`)
- **Event**: Der übergeordnete JSON-Schlüssel, unter dem der Hook registriert ist (`PreToolUse`, `PostToolUse` oder `Stop`)

Niemals Namen hardcoden — ausschließlich aus der Datei ableiten.

**2. Agenten aus `agents/` lesen**
Liste alle Dateien in `agents/` auf. Extrahiere die Agentennamen: Dateiname ohne `.md`-Suffix (z.B. `documenter`, `planner`).

**3. Slash-Commands aus `.claude/commands/` lesen**
Liste alle `.md`-Dateien in `.claude/commands/` auf. Extrahiere die Command-Namen: Dateiname ohne `.md`-Suffix, mit `/`-Präfix vorangestellt (z.B. `/ship`, `/generate-diagram`).

**4. Aktuellen Commit-Hash ermitteln**
```bash
git log -1 --format=%h
```

---

## Phase 2 — Diagramm erzeugen

Schreibe `docs/architecture/system-overview.md` vollständig neu (niemals anhängen). Der Inhalt hat folgende Struktur:

````
---
date: <heutiges Datum, ISO 8601, z.B. 2026-03-06>
commit: <Hash aus git log>
tags: [architecture, diagram]
---

# System Overview

```mermaid
graph TD
    User -->|prompt| CC[Claude Code]

    CC --> PreToolUse["PreToolUse"]
    CC --> PostToolUse["PostToolUse"]
    CC --> Stop["Stop"]

    PreToolUse --> <hook-name-1>
    PreToolUse --> <hook-name-2>
    ...

    PostToolUse --> <hook-name-3>
    ...

    Stop --> <hook-name-n>
    ...

    CC --> <agent-1>
    CC --> <agent-2>
    ...

    CC --> <"/command-1">
    CC --> <"/command-2">
    ...
```
````

**Regeln für das Diagramm:**
- Alle Hook-Knoten als Kind des jeweiligen Event-Knotens gruppieren (`PreToolUse`, `PostToolUse`, `Stop`).
- Falls für einen Event-Typ (PreToolUse / PostToolUse / Stop) keine Hooks existieren, wird dieser Event-Node weggelassen.
- Alle Agenten direkt als Kind von `CC` eintragen.
- Alle Commands direkt als Kind von `CC` eintragen, mit `/`-Präfix im Label.
- Falls ein Agent namens `documenter` in `agents/` existiert, füge eine Kante hinzu: `documenter -->|schreibt| Vault[(docs/)]`
- Knoten-IDs dürfen keine Leerzeichen oder Sonderzeichen enthalten — Bindestriche sind erlaubt.
- Für Labels mit Sonderzeichen (z.B. `/ship`) die Mermaid-Syntax `id["label"]` verwenden.
- Alle Namen ausschließlich aus den ausgelesenen Quellen ableiten — niemals hardcoden.

---

## Phase 3 — Abschluss

Gib nach dem Schreiben der Datei aus:

```
[WROTE] docs/architecture/system-overview.md
```
