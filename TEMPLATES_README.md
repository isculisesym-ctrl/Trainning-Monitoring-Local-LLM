# Templates para Validación de Fases — Uso Reutilizable

**Tres documentos generados desde lecciones de Phase 1. Úsalos en cualquier repo, cualquier equipo.**

---

## 📄 Los 3 Documentos

### 1. **HANDOFF_TEMPLATE.md**
- **Qué es:** Guía conceptual de model selection + checklist básico
- **Cuándo usarlo:** Para entender QUÉ modelo usar y POR QUÉ
- **Audiencia:** Tech leads, project managers, cualquiera planeando fases

**Sections:**
- Model Selection Quick Guide (Haiku vs Sonnet vs Opus)
- Checklist universal de validación
- Lecciones de Phase 1 (bug patterns, what worked)
- Cómo adaptar el template

**Ejemplo:** "Necesito un smoke test rápido" → Haiku. "Necesito validar código roto" → Opus.

---

### 2. **PHASE_VALIDATION_PROMPT.md**
- **Qué es:** Prompt EJECUTABLE. Copy-paste directamente en un chat con Claude.
- **Cuándo usarlo:** Antes de cada fase. Es el "checklist vivo" que Claude ejecuta.
- **Audiencia:** Desarrolladores, ingenieros, cualquiera interactuando con Claude

**Sections:**
- Contexto + Tu rol (Haiku/Sonnet/Opus)
- Checklist universal con ejemplos
- Model-specific guidance (qué hace cada uno)
- Red flags (qué investigar antes de PASS)
- Handoff format

**Cómo usarlo:**
```
1. Copia la sección "Checklist Universal"
2. Reemplaza placeholders [tu-server], [port], etc.
3. Copia en el chat con Claude
4. Ejecuta paso a paso
5. Reporta PASS/FAIL
```

**Ejemplo:** Ejecuté Phase 1 smoke test usando este prompt.

---

### 3. **REPO_CLAUDE_PROMPT.md**
- **Qué es:** Meta-prompt. Copia la estructura, personaliza para tu repo, guarda en CLAUDE.md.
- **Cuándo usarlo:** Al iniciar un nuevo proyecto. Define expectativas para Claude permanentemente.
- **Audiencia:** Proyectos nuevos, cualquier repo que quiera instrucciones claras

**Sections:**
- Context Section template (fill-in-the-blanks)
- Phase-based workflow template
- Multi-team workflow (Haiku/Sonnet/Opus roles)
- Common patterns by project type (FastAPI, Flask, TypeScript)
- Issue/Task template
- Best practices (do's/don'ts)
- Quick decision tree (cuál modelo usar)

**Cómo usarlo:**
```
1. Abre CLAUDE.md en tu repo (o crea uno)
2. Rellena los campos de Context Section
3. Adapta los comandos de validación para tu proyecto
4. Commit y comparte con tu equipo
5. Claude (cualquier modelo) leerá esto automáticamente
```

---

## 🎯 Flujo Recomendado

### Proyecto Nuevo
```
1. Leo REPO_CLAUDE_PROMPT.md
2. Creo/edito CLAUDE.md con contexto del proyecto
3. Cada vez que hago un task, el modelo lee CLAUDE.md automáticamente
4. Cuando cierro una fase, sigo PHASE_VALIDATION_PROMPT.md
5. Documento con HANDOFF_TEMPLATE.md
```

### Proyecto Existente
```
1. Creo/edito CLAUDE.md basado en REPO_CLAUDE_PROMPT.md
2. Para la siguiente fase, copio PHASE_VALIDATION_PROMPT.md
3. Adapto checklist a mi proyecto
4. Ejecuto con el modelo (Haiku/Sonnet/Opus según escala)
5. Reporto con HANDOFF_TEMPLATE.md format
```

### Multi-Team Workflow
```
Opus → Valida todo, documenta en VALIDATION_REPORT.md, deja en rama
Sonnet → Lee VALIDATION_REPORT.md, implementa feature, ejecuta checklist
Haiku → Smoke test final, verifica, reporta PASS/FAIL
```

---

## 🔄 Relación Entre Documentos

```
REPO_CLAUDE_PROMPT.md  ← El "contexto permanente" del proyecto
    ↓
Cada vez que trabajas, el modelo lee esto
    ↓
PHASE_VALIDATION_PROMPT.md ← El "checklist ejecutable" para cada fase
    ↓
Adaptas este prompt para tu proyecto específico
    ↓
HANDOFF_TEMPLATE.md ← Referencia de cómo documentar + model selection
    ↓
Generas VALIDATION_REPORT.md (project-specific)
    ↓
Próxima fase empieza leyendo VALIDATION_REPORT.md + CLAUDE.md
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Smoke Test Phase 1 (AI-Platform)
```
1. Copié el checklist de PHASE_VALIDATION_PROMPT.md
2. Adapté para FastAPI/pytest/Ollama
3. Ejecuté con Haiku en 3 minutos
4. Reporté: "PASS: 37 tests, gates green, cache verified"
5. Referencia: VALIDATION_REPORT.md (Opus validación previa)
```

### Ejemplo 2: Setup nuevo repo Python
```
1. Leí REPO_CLAUDE_PROMPT.md
2. Copié la sección "FastAPI + pytest + black + mypy"
3. Personalicé paths y ports
4. Commit a CLAUDE.md
5. Ahora cada chat con Claude ve esto automáticamente
```

### Ejemplo 3: Feature work + handoff
```
1. Sonnet implementa feature, sigue PHASE_VALIDATION_PROMPT.md
2. Tests pass, gates pass, endpoints work
3. Commit con mensaje: "Feature X: phase-ready"
4. Haiku ejecuta smoke test final
5. Si PASS → merges to dev
```

---

## ✅ Checklist: Cómo Usar Estos Templates

### Setup (Una sola vez por proyecto)
- [ ] Leí REPO_CLAUDE_PROMPT.md
- [ ] Creé/edité CLAUDE.md en mi repo con contexto específico
- [ ] Commit CLAUDE.md
- [ ] Equipo/modelo ahora ve instrucciones automáticamente

### Para Cada Fase
- [ ] Leí PHASE_VALIDATION_PROMPT.md
- [ ] Copié checklist y adapté para mi proyecto
- [ ] Ejecuté paso a paso (tests → gates → server → logs)
- [ ] Reporté PASS/FAIL
- [ ] Documenté en VALIDATION_REPORT.md (o equivalent)

### Al Handoff
- [ ] Seguí format de HANDOFF_TEMPLATE.md
- [ ] Documenté qué se arregló + por qué
- [ ] Verifiqué blockers/recommendations
- [ ] Next phase puede leer todo y continuar

---

## 📚 Quick Links

- **Model selection guide:** HANDOFF_TEMPLATE.md → "Model Selection Quick Guide"
- **Execution checklist:** PHASE_VALIDATION_PROMPT.md → "Checklist Universal"
- **Project setup:** REPO_CLAUDE_PROMPT.md → "Context Section"
- **Example validation:** VALIDATION_REPORT.md (Phase 1)
- **Example handoff:** HAIKU_HANDOFF.md (Phase 1 smoke test)

---

## 🚀 How to Share With Your Team

**Option 1: Copy templates to your repo**
```bash
# Assume you have AI-Platform cloned
cp AI-Platform/HANDOFF_TEMPLATE.md your-repo/
cp AI-Platform/PHASE_VALIDATION_PROMPT.md your-repo/
cp AI-Platform/REPO_CLAUDE_PROMPT.md your-repo/
cd your-repo
git add *.md
git commit -m "Add phase validation templates (from AI-Platform)"
```

**Option 2: Reference from AI-Platform**
```markdown
# In your repo README.md:

## Validation Process

We follow the phase-based validation process documented in [AI-Platform](link).

Key templates:
- [Model selection](link/HANDOFF_TEMPLATE.md)
- [Validation checklist](link/PHASE_VALIDATION_PROMPT.md)
- [Project setup](link/REPO_CLAUDE_PROMPT.md)
```

**Option 3: Generate for your repo**
```markdown
Use REPO_CLAUDE_PROMPT.md as a template to create your own CLAUDE.md
with project-specific paths, commands, gates.
```

---

## 🎓 What We Learned (Phase 1 → All Projects)

### ✅ What Worked
- Layered validation (unit tests + offline paths + live server)
- Conservative thresholds (0.95 similarity, not 0.5)
- Graceful degradation (503 for unavailable services, no crash)
- Type hints + clear gates (mypy found bugs tests missed)
- Cache hit verification (2x identical request)
- Clean logs (UTF-8, no corruption)
- Full documentation in handoff

### 🔴 What Failed First, Then Fixed
- Fake semantic cache (lookup was exact-hash only)
- Cache never served (mode check blocked default path)
- Type errors on None (used `or` with booleans, snapped 0.0)
- Log encoding (non-ASCII chars corrupted)
- Missing docstrings (harder to debug)
- Unlinked gates (black passed, mypy failed)

### 💼 Process Learnings
- Smoke tests save time (5 min verification vs debugging in prod)
- Handoff documentation is critical (next person needs context)
- Model selection matters (Haiku for smoke, Opus for deep fixes)
- Offline paths must work (services fail; graceful degradation required)
- Gates are not just lint (type hints, coverage catch real bugs)

---

## 🔗 Related Files (This Repo)

- `dev` branch commit `65c4595`: Phase 1 complete (semantic cache real, all gates green)
- `VALIDATION_REPORT.md`: Deep validation by Opus (found + fixed 4+ bugs)
- `HAIKU_HANDOFF.md`: Smoke test checklist
- `CLAUDE.md`: (if exists) Project-specific instructions

---

**Generated:** 2026-06-28  
**Source:** Phase 1 Validation Learnings (AI-Platform)  
**Applicable to:** Any project, any team, any model  
**License:** Use freely in your own repos
