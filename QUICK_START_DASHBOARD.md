# ⚡ QUICK START - Dashboard + Training (3 Terminals)

## Setup Rápido (5 minutos)

### Terminal 1: Ollama Server
```bash
ollama serve
```
Expected output:
```
listening on 127.0.0.1:11434
```

### Terminal 2: Dashboard Server (nueva ventana)
```bash
python serve_dashboard.py
```
Expected output:
```
Training Dashboard Server
Server running at: http://localhost:8000/dashboard.html
```
✅ **Se abre el navegador automáticamente con el dashboard**

### Terminal 3: Training (nueva ventana)
```bash
python training_12h.py
```
Expected output:
```
================================================================================
PHASE 2: STARTING 12-HOUR TRAINING LOOP
Session: training_20260630_113000
Mode: continuous
================================================================================
Loading corpus...
✓ Loaded 85 corpus files
Loading exercises...
✓ Loaded 848 exercises
✓ Connected to Ollama: neural-chat

Starting loop at 2026-06-30 11:30:00
Will run until 2026-07-01 11:30:00 (12h)
Training in progress...

[0.0h/12.0h] arch_junior_001
  Score: 8.4/10 [OK]
[0.1h/12.0h] patterns_mid_042
  Score: 8.6/10 [OK]
...
```

---

## 📊 Dashboard En Vivo

**URL**: http://localhost:8000/dashboard.html

### Lo que ves:
- ✅ Progress bar (0% → 100%)
- ✅ Success Rate (vs Session 1: 99.53%)
- ✅ Quality Score (vs Session 1: 8.79)
- ✅ Failures count (idealmente 0)
- ✅ Real-time graphs
- ✅ Latest 20 exercises table
- ✅ Performance by type

### Auto-refresh: Cada 2 segundos

---

## 🎯 Monitoreo

### Cada 30 minutos:
1. Abre el dashboard (debería tener nuevos datos)
2. Verifica:
   - Success Rate > 99%
   - Quality Score > 8.7
   - Failures = 0 (idealmente)
   - Gráficos no bajando

### Si todo está bien:
→ Déjalo correr, vuelve en 2-3 horas

### Si algo baja:
→ Pause entrenamiento (Ctrl+C en Terminal 3)
→ Debug según ROOT_CAUSE_ANALYSIS.md
→ Reinicia cuando esté listo

---

## 📈 Esperado Ver en Dashboard

### Primeras 2 horas:
```
Exercises: 150-200 (75-100 ex/h)
Success: 99%+
Quality: 8.7+
Failures: 0-2
```

### Horas 2-6:
```
Exercises: 450-600
Success: 99.5%+
Quality: 8.8+
Failures: 0-1 (arch_junior_002, patterns_senior_095 idealmente FIXED)
```

### Horas 6-12:
```
Exercises: 900+
Success: 99.6%+
Quality: 8.85+
Failures: 0 (si los fixes funcionaron)
```

---

## 🏁 Cuando Termine (12 horas después)

Deberías ver en el dashboard:
```
✅ Success Rate: 99.60%+ (vs 99.53% en S1)
✅ Quality: 8.85+ (vs 8.79 en S1)
✅ Total: 900+ ejercicios
✅ Failures: 0-1
```

Y en Terminal 3 (training_12h.py):
```
================================================================================
TRAINING SESSION COMPLETE
================================================================================
Duration: 12.0 hours
Exercises: 900+
Success rate: 99.6%+
Avg quality: 8.85+/10
Saved to: data/training_logs/training_[DATE].json
================================================================================
```

---

## 🔧 Resolver Problemas Comunes

### "Dashboard blank/loading forever"
```
1. Verifica serve_dashboard.py está corriendo
2. Ctrl+Shift+I en browser → Network tab
3. live_metrics.json debe tener status 200
4. Si error 404: training_12h.py no ha creado aún el archivo
```

### "Training muy lento"
```
1. Normal si es < 75 ex/h
2. Verifica que Ollama está respondiendo
3. Revisa recursos (CPU/RAM)
```

### "Success rate bajando"
```
1. PAUSE inmediatamente (Ctrl+C)
2. Revisa última línea del log: tail -f data/training_logs/training_12h.log
3. Ver ROOT_CAUSE_ANALYSIS.md para diagnóstico
```

### "arch_junior_002 o patterns_senior_095 aparecen en Failures"
```
1. Normal si ocurre 1-2 veces en 12h
2. Si se repiten: Pause y debug Phase 1 fixes
```

---

## 📊 Dashboard Files

```
dashboard.html              ← Interfaz visual
serve_dashboard.py          ← Servidor HTTP
src/training/live_metrics.py ← Collector de datos
```

Datos guardados en:
```
data/training_logs/live_metrics.json    ← Actualiza cada ejercicio (en vivo)
data/training_logs/training_[DATE].json ← Resultado final (al completar)
```

---

## ✨ Resumen

| Tarea | Terminal | Comando |
|-------|----------|---------|
| Ollama | 1 | `ollama serve` |
| Dashboard | 2 | `python serve_dashboard.py` |
| Training | 3 | `python training_12h.py` |
| Monitoreo | Browser | http://localhost:8000/dashboard.html |

**Tiempo total**: 12 horas (hands-off después de setup)

---

**STATUS**: 🟢 LISTO PARA EJECUTAR  
**Expected Improvement**: +0.07% success, +0.06 quality  
**Next Step**: Abrir 3 terminales y ejecutar los comandos arriba
