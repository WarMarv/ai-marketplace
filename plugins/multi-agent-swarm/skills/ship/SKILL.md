---
name: ship
description: "Ship current changes — creates branch, commits, runs QA (Tester + Reviewer), creates PR, and auto-merges. Input: optional commit message. Flag --skip-tests to skip test checks."
version: 1.0.0
---

# /ship
# Input: Commit-Message (optional, z.B. "feat(auth): add login flow")
#        Flag --skip-tests (optional): Überspringt Test-Generator und Test-Runner in Phase 2 — nur für reine Dokumentations-Änderungen.
# Output: Branch erstellen → committen → QS → PR erstellen → automatisch mergen

Du shippst aktuelle Änderungen ohne Issue-Kontext. Führe alle Phasen vollständig durch — keine Bestätigungen erforderlich, außer bei Blockern.

**Flag-Erkennung:** Prüfe ob `$ARGUMENTS` das Flag `--skip-tests` enthält.
- Falls ja: Setze intern `SKIP_TESTS=true` und entferne `--skip-tests` aus der Commit-Message.
- Falls nein: `SKIP_TESTS=false`.

---

## Phase 1 — Branch und Commit

**1. Git-Status prüfen**
Führe `git status` aus und zeige den aktuellen Branch und uncommitted Changes.

**2. Branch sicherstellen**
Wenn der aktuelle Branch `main` oder `develop` ist: Erstelle einen neuen Feature-Branch.
- Falls `$ARGUMENTS` vorhanden: Leite den Branch-Namen daraus ab (lowercase, Leerzeichen → Bindestriche, Sonderzeichen entfernen, max. 50 Zeichen).
  - Beispiel: `"feat(auth): add login"` → `feat/add-login`
- Falls kein Argument: Branch-Name aus staged/unstaged Dateipfaden oder `feat/changes-<datum>` ableiten.

```bash
git checkout -b <branch-name>
```

**3. Änderungen committen**
Wenn uncommitted Changes vorhanden sind:
- Führe `git add -A` aus.
- Commit-Message bestimmen:
  - Falls `$ARGUMENTS` vorhanden: `$ARGUMENTS` verwenden.
  - Falls kein Argument: Aus `git diff --staged --stat` eine Conventional-Commit-Message ableiten und ausgeben (damit der User sie sieht).

```bash
git commit -m "<message>"
```

Wenn keine Änderungen vorhanden sind (alles bereits committed): Melde dies und fahre direkt mit Phase 2 fort.

---

## Phase 2 — Qualitätssicherung

**1. Test Generator**
Falls `SKIP_TESTS=true`: Überspringe diesen Schritt — melde `Test Generator: SKIPPED (--skip-tests)`.
Falls `SKIP_TESTS=false`: Lese `agents/test-generator.md` vollständig und agiere als Test-Generator-Rolle.
Führe `git diff main` aus und prüfe, ob die Änderungen ausreichend Tests haben.
Gib fehlende Tests als Liste aus — format: `MISSING: [UNIT|INTEGRATION|E2E] test_<behavior>`

**2. Test Runner**
Falls `SKIP_TESTS=true`: Überspringe diesen Schritt — melde `Test Runner: SKIPPED (--skip-tests)`.
Falls `SKIP_TESTS=false`: Lese `agents/test-runner.md` vollständig und agiere als Test-Runner-Rolle.
Führe die vorhandene Test-Suite aus und berichte Ergebnis im Format aus `agents/test-runner.md`.
Wenn Tests fehlschlagen: Stoppe und weise auf die Failures hin — fahre nicht mit Schritt 3 fort.

**3. Reviewer**
Lese `agents/reviewer.md` vollständig und agiere als Reviewer-Rolle.
Reviewe `git diff main` nach den Prinzipien aus `agents/reviewer.md`.
Format: `[BLOCKING | SUGGESTION] file:line — Problem — Warum — Fix`
Wenn nichts auffällt: explizit bestätigen.

**4. Refactorer (bedingt)**
Wenn der Reviewer BLOCKING-Findings mit Code-Smells enthält:
Lese `agents/refactorer.md` vollständig und agiere als Refactorer-Rolle.
Führe den Refactor durch, dann zurück zu Schritt 3.

**5. Checkpoint-Report**

```
Branch:         <branch-name>
Commit:         <message>
Test Runner:    PASS / FAIL (<n> Tests, <n> Failures) | SKIPPED (--skip-tests)
Test Generator: <n> fehlende Tests / keine | SKIPPED (--skip-tests)
Reviewer:       <n> Blocking, <n> Suggestions
```

Wenn Tests fehlschlagen oder BLOCKING-Findings vorliegen: Stoppe und weise auf die offenen Punkte hin.
Ansonsten: Fahre **automatisch mit Phase 3 fort** — keine Bestätigung erforderlich.

---

## Phase 3 — PR erstellen und mergen

**1. Branch pushen**
```bash
git push -u origin <branch>
```

**2. PR erstellen oder existierenden nutzen**
Prüfe ob für den aktuellen Branch bereits ein offener PR existiert:

```bash
gh pr list --head <branch>
```

- Falls ja: PR-Nummer merken, keinen neuen PR erstellen.
- Falls nein: PR erstellen mit:
  - Titel: Commit-Message (ohne Conventional-Commit-Präfix falls gewünscht)
  - Body: Änderungszusammenfassung aus `git log main..HEAD --oneline`

```bash
gh pr create --title "<titel>" --body "$(cat <<'EOF'
## Was wurde geändert
- <änderung 1>
- <änderung 2>
EOF
)"
```

**3. PR mergen**
```bash
gh pr merge <pr-number> --squash --delete-branch
```

**4. Lokal auf main rebasen**
```bash
git checkout main && git pull origin main
```

**5. Abschluss**
Gib die PR-URL und Bestätigung des Merges aus.

> Änderungen geshippt. Führe jetzt `/clear` aus, um den Kontext zurückzusetzen.
