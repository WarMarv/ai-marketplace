---
name: feature
description: "Implement a feature end-to-end — Plan → Implementation → Tests → ready to commit. Input: feature description or issue title."
version: 1.0.0
---

# /feature
# Input: Feature-Beschreibung oder Issue-Titel (z.B. "add user login flow")
# Output: Plan → Implementierung → Tests → bereit zum Committen

Du implementierst ein neues Feature vollständig — von der Planung bis zu grünen Tests.
Führe alle Phasen durch — keine Bestätigungen erforderlich, außer bei Blockern oder offenen Fragen.

---

## Phase 1 — Plan

**1. Planner-Rolle aktivieren**
Lese `agents/planner.md` vollständig und agiere ab jetzt als Planner-Rolle.

**2. Planung erstellen**
Input: `$ARGUMENTS`

Wenn die Beschreibung unvollständig oder mehrdeutig ist: eine gezielte Rückfrage stellen, dann weiter.
Ansonsten: direkt den Plan ausgeben.

Ausgabeformat exakt nach `agents/planner.md`:

```
### Goal
### Interfaces / Contracts Affected
### Implementation Steps
### Risks & Open Questions
### Test Strategy
```

Wenn "Risks & Open Questions" nicht leer sind: Stoppe und kläre sie mit dem User bevor weiter.
Ansonsten: **automatisch mit Phase 2 fortfahren**.

---

## Phase 2 — Implementierung

**1. Implementer-Rolle aktivieren**
Lese `agents/implementer.md` vollständig und agiere ab jetzt als Implementer-Rolle.

**2. Plan ausführen**
Führe jeden Schritt aus dem Plan in Phase 1 einzeln durch.
Nach jedem Schritt kurzen Status ausgeben:

```
[DONE] Schritt N: <was wurde gemacht>
[NEXT] Schritt N+1: <was kommt als nächstes>
```

Wenn ein Schritt unklar ist oder ein Blocker auftritt: Stoppe und melde:

```
[BLOCKER] Schritt N: <was ist unklar oder blockiert>
```

Wenn alle Schritte abgeschlossen: **automatisch mit Phase 3 fortfahren**.

---

## Phase 3 — Tests

**1. Test-Coverage prüfen**
Lese `agents/test-generator.md` vollständig und agiere als Test-Generator-Rolle.
Führe `git diff main` aus und prüfe, ob die Änderungen ausreichend Tests haben.
Liste fehlende Tests auf — format: `MISSING: test_<behavior>`

**2. Fehlende Tests schreiben**
Lese `agents/implementer.md` vollständig und wechsle in die Implementer-Rolle.
Schreibe alle in Schritt 1 identifizierten Tests direkt — nicht nur auflisten.
Ausgabe nach jedem geschriebenen Test: `WRITTEN: test_<behavior>`

**3. Abschluss**

```
Feature implementiert und getestet.
Bereit zum Committen.

Nächster Schritt:
- Wenn dieses Feature als GitHub Issue getrackt ist: `/close-issue <issue-nummer>` ausführen.
- Ansonsten: `/ship` ausführen.
```
