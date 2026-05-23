---
name: close-issue
description: Close a GitHub Issue via PR with full QA — runs Tester, Reviewer, creates PR, and auto-merges. Input: issue number.
version: 1.0.0
---

# /close-issue
# Input: GitHub Issue-Nummer (z.B. 42)
# Output: QS-Report → PR erstellen → automatisch mergen

## Issue: $ARGUMENTS

Du schließt ein GitHub Issue via PR. Führe Phase 1 und Phase 2 vollständig durch — keine Bestätigungen erforderlich, außer bei Blockern.

---

## Phase 1 — Qualitätssicherung

**1. Issue laden**
Führe `gh issue view $ARGUMENTS` aus und zeige: Titel, Beschreibung, Labels.

**2. Branch-Kontext**
Zeige den aktuellen Branch-Namen und alle Commits seit `main` (einzeilig, mit Hash).

**3. Tests ausführen**
Erkenne den Test-Runner aus dem Projekt (`package.json` → scripts.test, `pyproject.toml`, `Makefile`, etc.) und führe ihn aus.
- Wenn kein Test-Runner gefunden: explizit melden, nicht überspringen.
- Zeige Ergebnis: Anzahl Tests, Failures, relevante Fehlermeldungen.

**4. Tester**
Lese `agents/test-runner.md` vollständig und agiere als Tester-Rolle.
Führe `git diff main` aus und prüfe, ob die Änderungen ausreichend Tests haben.
Gib fehlende Tests als Liste aus — format: `MISSING: test_<behavior>`

**5. Reviewer**
Lese `agents/reviewer.md` vollständig und agiere als Reviewer-Rolle.
Reviewe `git diff main` nach den Prinzipien aus `agents/reviewer.md`.
Format: `[BLOCKING | SUGGESTION] file:line — Problem — Warum — Fix`
Wenn nichts auffällt: explizit bestätigen.

**6. Refactorer (bedingt)**
Wenn der Reviewer BLOCKING-Findings mit Code-Smells enthält:
Lese `agents/refactorer.md` vollständig und agiere als Refactorer-Rolle.
Führe den Refactor durch, dann zurück zu Schritt 5.

**7. Checkpoint-Report**
Gib einen kompakten Report aus:

```
Issue:    #$ARGUMENTS — <Titel>
Branch:   <branch-name>
Tests:    PASS / FAIL (<n> Tests, <n> Failures)
Tester:   <n> fehlende Tests / keine
Reviewer: <n> Blocking, <n> Suggestions
```

Wenn Tests fehlschlagen oder BLOCKING-Findings vorliegen: Stoppe und weise auf die offenen Punkte hin.
Ansonsten: Fahre **automatisch mit Phase 2 fort** — keine Bestätigung erforderlich.

---

## Phase 2 — PR erstellen und mergen

**1. Unstaged Changes prüfen**
Führe `git status` aus. Wenn uncommitted Changes vorhanden sind: Hinweis ausgeben und auf Commit warten, bevor weiter.

**2. Branch pushen**
`git push -u origin <branch>`

**3. PR erstellen oder existierenden nutzen**
Prüfe zuerst ob für den aktuellen Branch bereits ein offener PR existiert:

```bash
gh pr list --head <branch>
```

- Falls ja: PR-Nummer merken, keinen neuen PR erstellen.
- Falls nein: PR erstellen mit:
  - Titel: Issue-Titel übernehmen
  - Body: Änderungszusammenfassung (1–3 Stichpunkte) + `Closes #$ARGUMENTS`
  - Labels: aus dem Issue übernehmen wenn vorhanden

```bash
gh pr create --title "<issue-titel>" --body "$(cat <<'EOF'
## Was wurde geändert
- <änderung 1>
- <änderung 2>

Closes #$ARGUMENTS
EOF
)"
```

**4. PR mergen**
Merge den PR direkt — ohne Rückfrage:

```bash
gh pr merge <pr-number> --squash --delete-branch
```

**5. Abschluss**
Gib die PR-URL und Bestätigung des Merges aus.

**6. Kontext leeren**
Weise den User explizit darauf hin, jetzt `/clear` auszuführen, um den Konversationskontext zurückzusetzen:

> Issue #$ARGUMENTS ist geschlossen. Führe jetzt `/clear` aus, um den Kontext zurückzusetzen.
