# 🏛️ Porsche Aftersales AI Organization - CLAUDE.md

This file provides system context, build/run commands, and operating guidelines for Claude Code in this workspace.

---

## 🚀 Commands

### Run Backend Server (FastAPI)
* **Start Server:**
  ```cmd
  cd RepairInstructionReader/backend && python main.py
  ```
  *(Runs on http://localhost:8000)*

* **Check API Health:**
  ```cmd
  curl http://localhost:8000/health
  ```

### Run Frontend
* Open `RepairInstructionReader/frontend/index.html` in your browser.
* Use VS Code Live Server or python http server for local testing.

---

## 🎨 Code Style & Quality Rules
* **No Tailwind CSS:** Always write clean Vanilla CSS in `RepairInstructionReader/frontend/style.css`.
* **Porsche Brand Palette:**
  - Active/Alert: Guards Red (`#D5001C`)
  - EV/Hybrid Status: Acid Green (`#88D413`)
  - Backgrounds: Dark Chrome (`#0F0F12`, `#1C1C24`)
* **Subagents:** Specialized subagents are defined in `.claude/agents/`:
  - Run `/agent ui-ux-reviewer` for frontend quality checks.
  - Run `/agent supabase-reviewer` for backend and database checks.
  - Run `/agent glossary-verifier` for translation audits.

---

## ⏱️ Session End Archiving Hook
Every time a session ends or edits are finalized, execute the archiver hook to update Obsidian's ledger:
```cmd
python scripts/session-end-archiver.py
```
This updates the logs in `Archive Department.md`.
