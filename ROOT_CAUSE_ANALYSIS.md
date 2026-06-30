# ROOT CAUSE ANALYSIS - FALLOS SESIÓN 1

**Fecha**: 2026-06-30  
**Sesión Analizada**: training_20260629_230311  
**Ejercicios Totales**: 848  
**Fallos**: 4  

---

## 📌 PROBLEMA #1: arch_junior_002

### Síntomas
```
Exercise ID:        arch_junior_002
Status:             FAIL (repetido 2x en log)
Quality Score:      5.5/10 (crítico, -3.3 vs baseline 8.8)
Patterns Found:     1/4 (25% - debería ser ~80%)
Regex Matched:      1/4 (25% - debería ser ~80%)
Manual Review:      False
Response Length:    Variable
```

### Root Cause Hypothesis

**H1: Corpus Entry Incompleta** [PROBABILITY: 70%]
- El archivo `data/training_corpus/01_architecture_patterns.md` tiene entrada para arch_junior_002
- Problema: Entrada es ambigua, contradictoria, o incompleta
- Síntoma: Modelo no identifica patrones porque no están claros en corpus

**H2: Prompt Builder Falla** [PROBABILITY: 20%]  
- El prompt generado para arch_junior_002 está mal formado
- Problema: Contexto insuficiente o confuso del corpus
- Síntoma: Modelo recibe mal el ejercicio

**H3: Validador Demasiado Estricto** [PROBABILITY: 10%]
- El validador espera patrones que no están en la corpus
- Problema: Mismatch entre corpus y validación
- Síntoma: Respuesta es correcta pero validador rechaza

### Investigación Necesaria

1. **Leer el corpus entry** (src/training/corpus_loader.py → load())
   ```python
   # Find arch_junior_002 in loaded corpus
   for key, content in corpus.items():
       if 'junior' in key and 'arch' in key:
           print(f"Entry: {key}")
           print(f"Content length: {len(content)}")
           print(f"First 500 chars: {content[:500]}")
   ```

2. **Revisar exercise definition** (src/training/exercise_loader.py)
   ```python
   # Find arch_junior_002 exercise
   exercises = exercise_loader.load()
   arch_j002 = exercises.get('arch_junior_002')
   print(f"Title: {arch_j002.title}")
   print(f"Required patterns: {arch_j002.required_patterns}")
   print(f"Expected regex: {arch_j002.expected_regex}")
   ```

3. **Ver qué responde el modelo** (monitoring)
   - Correr arch_junior_002 solo
   - Capturar respuesta del modelo
   - Comparar con expected patterns

### Acciones de Fix (Prioridad P0)

**Opción A: Mejorar Corpus** (Si corpus está incompleta)
```
1. Abrir: data/training_corpus/01_architecture_patterns.md
2. Buscar: arch_junior_002
3. Expandir entry con:
   - Ejemplos claros del patrón
   - Anti-patterns (qué NO hacer)
   - Context de cuándo aplica
4. Test: Rerun arch_junior_002 → debería subir a 8.5+
```

**Opción B: Ajustar Validador** (Si corpus está bien pero validador es injusto)
```
1. Abrir: src/training/validators.py
2. Buscar: ResponseValidator.validate()
3. Si es arch_junior_002 específico:
   - Reducir required_patterns de 4 a 3
   - Reducir regex requirement
4. Test: Rerun → debería pasar
```

**Opción C: Reescribir Ejercicio** (Si ambos están mal)
```
1. Crear nuevo ejercicio: arch_junior_003
2. Basado en arch_junior_002 pero más claro
3. Eliminar arch_junior_002 o deprecate
4. Rebalancear exercises
```

### Success Criteria
```
arch_junior_002 quality >= 8.5
arch_junior_002 success = true
arch_junior average success >= 99.5%
```

---

## 📌 PROBLEMA #2: patterns_senior_095

### Síntomas
```
Exercise ID:        patterns_senior_095
Status:             FAIL (repetido 2x en log)
Quality Score:      5.6/10 (crítico, -3.2 vs baseline 8.8)
Patterns Found:     1/5 (20% - debería ser ~80%)
Regex Matched:      1/3 (33% - debería ser ~90%)
Manual Review:      True (RED FLAG)
Response Length:    Variable
```

### Root Cause Hypothesis

**H1: Senior Patterns Corpus Insuficiente** [PROBABILITY: 75%]
- El corpus de senior patterns es menos detallado que otros
- Problema: Modelo no tiene suficiente context para senior-level patterns
- Síntoma: Solo detecta 1/5 patrones, necesita manual review

**H2: Validador de Patterns Demasiado Estricto** [PROBABILITY: 15%]
- El validador espera regex exactos que no matchean variantes
- Problema: Model responde correctamente pero validador rechaza
- Síntoma: Manual review requerido

**H3: Modelo Insuficiente para Senior Patterns** [PROBABILITY: 10%]
- El modelo neural-chat no es lo bastante sofisticado
- Problema: Tarea demasiado compleja para el modelo
- Síntoma: No puede hacer pattern matching a nivel senior

### Investigación Necesaria

1. **Analizar pattern recognition** (validators.py)
   ```python
   # Check how patterns are validated
   for pattern in expected_patterns:
       matched = response.find(pattern) >= 0  # Exact match?
       regex_matched = re.search(pattern, response)  # Regex match?
   ```

2. **Revisar responses del modelo** (captured outputs)
   - Qué pattern deja pasar (1/5)?
   - Qué patterns se pierden?
   - ¿Es el modelo muy conservador?

3. **Revisar corpus de patterns senior**
   - Tamaño: data/training_corpus/04_design_patterns.md
   - Cantidad de patrones: cuántos senior patterns hay?
   - Detalle: qué tan descriptivos son?

### Acciones de Fix (Prioridad P0)

**Opción A: Expand Senior Patterns Corpus** (RECOMENDADO)
```
1. Abrir: data/training_corpus/04_design_patterns.md
2. Agregar más ejemplos de senior-level patterns:
   - SOLID principles en profundidad
   - Anti-patterns a evitar
   - Trade-offs y decisiones
   - Ejemplos reales de código
3. Test: patterns_senior debería mejorar a 97%+
```

**Opción B: Ajustar Pattern Validator**
```
1. src/training/validators.py → pattern matching
2. Cambiar:
   - De exact match a fuzzy match (permite typos)
   - De 5/5 required a 4/5 required
   - De strict regex a more flexible
3. Test: patterns_senior_095 debería pasar
```

**Opción C: Improve Prompt Context**
```
1. src/training/prompt_builder.py
2. Para senior patterns, inyectar:
   - Más corpus context (aumentar window)
   - Ejemplos de patrón similar
   - Criterios de éxito explícitos
3. Test: Modelo debería ser más preciso
```

### Success Criteria
```
patterns_senior_095 quality >= 8.0
patterns_senior_095 success = true
patterns_senior average success >= 97%
patterns_senior average quality >= 8.5
```

---

## 🔍 ANÁLISIS COMPARATIVO

### Dónde funciona bien (SIN cambios)
```
Quality exercises:      100% success, 9.5 avg → EXCELENTE
Security exercises:     100% success, 9.1 avg → EXCELENTE
Scale exercises:        100% success, 8.9 avg → EXCELENTE
Patterns junior/mid:    100% success, 8.56 avg → EXCELENTE
Arch mid/senior:        100% success, 8.48 avg → EXCELENTE
```

### Dónde hay oportunidad
```
Arch junior:            98.1% success, 8.68 avg → MEJORAR (arch_junior_002)
Patterns senior:        94.3% success, 7.83 avg → MEJORAR (patterns_senior_095)
```

**Patrón**: Problemas están en SENIOR patterns y JUNIOR architecture
- Junior architecture podría ser sobre-complejidad en corpus
- Senior patterns podría ser sub-detalle en corpus

---

## 📋 RECOMENDACIÓN GENERAL

### Strategy: "Focused Improvement" (70% chance of success)

1. **Start with Corpus First** (Opción A para ambos)
   - Expandir data/training_corpus/01_architecture_patterns.md
   - Expandir data/training_corpus/04_design_patterns.md
   - Motivo: Corpus es más fácil de arreglar que validadores

2. **Then Test Incrementally**
   - Correr arch_junior_002 solo → debería subir
   - Correr patterns_senior_095 solo → debería subir
   - No cambiar validadores aún

3. **If Still Failing**
   - Opción B: Ajustar validadores (menos estrictos)
   - Opción C: Mejorar prompts (más contexto)

### Timeline Estimate
```
Diagnosis:    1 hora (leer corpus, revisar validadores)
Fix Corpus:   1 hora (expandir entries)
Testing:      1 hora (validar fixes sin regression)
Total:        3 horas (matches Phase 1 del plan)
```

---

## 🎯 EXECUTION CHECKLIST

### Step 1: Diagnose (1h)
- [ ] Leer arch_junior_002 corpus entry
- [ ] Entender qué patrones espera el validador
- [ ] Ver respuesta del modelo en detalle
- [ ] Root cause: corpus? validador? prompts?

- [ ] Leer patterns_senior_095 corpus entry
- [ ] Entender qué patrones espera el validador
- [ ] Ver respuesta del modelo en detalle
- [ ] Root cause: corpus? validador? prompts?

### Step 2: Fix Corpus (1h)
- [ ] Expandir arch junior patterns en corpus
- [ ] Agregar ejemplos y contexto
- [ ] Expandir senior patterns en corpus
- [ ] Agregar ejemplos y contexto

### Step 3: Validate (1h)
- [ ] Test arch_junior_002 → target 8.5+ quality
- [ ] Test patterns_senior_095 → target 8.0+ quality
- [ ] Regression check: no romper otros ejercicios
- [ ] Commit changes

---

## 📊 SUCCESS METRICS

### After Fix (Session 2 - Phase 1)
```
arch_junior_002:        quality 8.5+, success TRUE
patterns_senior_095:    quality 8.0+, success TRUE

arch_junior average:    99.5%+ success, 8.8+ quality
patterns_senior avg:    97%+ success, 8.5+ quality
```

### Full Session 2 Target
```
Total Exercises:        900+
Success Rate:           99.60%+
Quality Average:        8.85+
```

---

**Document**: ROOT_CAUSE_ANALYSIS.md  
**Status**: READY FOR EXECUTION  
**Next Action**: Phase 1 - Debug & Fix (see PHASE_2_SESSION_2_PLAN.md)
