---
name: issue
description: "Create a GitHub Issue from a free-text description — derives title, body, and labels automatically. Input: issue description."
version: 1.0.0
---

# /issue
# Input: Freitext-Beschreibung des Issues (z.B. "Login schlägt bei leerem Token fehl")
# Output: GitHub Issue anlegen und URL ausgeben

## Issue: $ARGUMENTS

Du legst ein GitHub Issue an. Führe alle Phasen vollständig durch — keine Bestätigungen erforderlich.

---

## Phase 1 — Kontext laden

**1. Repo-Labels abrufen**

Führe aus:

```bash
gh label list
```

Merke alle Label-Namen für Phase 2.

**2. Repo ermitteln**

Führe aus:

```bash
gh repo view --json name,owner
```

---

## Phase 2 — Issue ableiten

Leite aus `$ARGUMENTS` folgende Felder ab:

- **Titel**: prägnant, max. 72 Zeichen, Imperativ oder Substantiv-Phrase
- **Beschreibung**: 2–4 Sätze — Kontext + erwartetes vs. tatsächliches Verhalten
- **Labels**: 1–3 aus der in Phase 1 abgerufenen Label-Liste, inhaltlich passend; keine Labels wenn nichts passt

---

## Phase 3 — Issue anlegen

Falls Labels passen:

```bash
gh issue create --title "<titel>" --body "<beschreibung>" --label "<label1>,<label2>"
```

Falls keine Labels passen:

```bash
gh issue create --title "<titel>" --body "<beschreibung>"
```

**Ausgabe:**

```
Issue angelegt: #<n> — <titel>
<url>
```
