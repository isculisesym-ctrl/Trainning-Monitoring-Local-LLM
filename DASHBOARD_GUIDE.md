# 📊 Training Dashboard - Guía Completa

**En vivo durante Session 2** - Trackea cada ejercicio, métrica y comparación con Session 1.

---

## 🚀 CÓMO USAR

### Setup (3 pasos simples)

**Terminal 1: Iniciar el servidor de Ollama**
```bash
ollama serve
# Output esperado: listening on 127.0.0.1:11434
```

**Terminal 2: Levantar el Dashboard**
```bash
python serve_dashboard.py
# Output:
# Training Dashboard Server
# Server running at: http://localhost:8000/dashboard.html
# (Se abre el navegador automáticamente)
```

**Terminal 3: Iniciar el entrenamiento**
```bash
python training_12h.py
# Output:
# [0.0h/12.0h] arch_junior_001
# [0.2h/12.0h] patterns_mid_042
# ...
```

---

## 📈 QUÉ VES EN EL DASHBOARD

### 1. **Session Progress** (Progress Bar)
```
Elapsed Time: 2.5h
Progress: 20% (2.5h / 12.0h)
```
- Barra visual del progreso
- Tiempo transcurrido actualizado en vivo

### 2. **Success Rate** (Métrica crítica)
```
Current: 99.54%
Target: 99.60%+
Delta: +0.01%
```
- Compara con Session 1 (99.53%)
- Verde si mejora, rojo si baja
- Barrita visual de progreso

### 3. **Quality Score** (Métrica crítica)
```
Average: 8.81/10
Target: 8.85+
Delta: +0.02
```
- Compara con Session 1 (8.79)
- Barra visual del score
- Delta verde si mejora

### 4. **Exercises Completed**
```
Total: 250
Rate: 100 ex/h
Target: 900+
```
- Contador total de ejercicios
- Velocidad de entrenamiento (ejercicios/hora)

### 5. **Failures Detected** (⚠️ CRÍTICO)
```
Failed Exercises: 2
- arch_junior_002
- patterns_senior_095
```
- Rojo si hay fallos
- Lista de ejercicios fallidos
- Tabla con detalles de cada fallo

### 6. **S1 vs S2 Comparison**
```
Success (S1): 99.53%    Success (S2): 99.54%
Quality (S1): 8.79      Quality (S2): 8.81
Improvement: +0.03 (improving)
```
- Comparativa lado a lado
- Verde si mejora

---

## 📊 GRÁFICOS EN VIVO

### 1. **Success Rate Trend**
- Línea azul: Tu sesión 2 en vivo
- Línea punteada: Baseline de Session 1 (99.53%)
- Y-axis: 98% a 100%
- X-axis: Horas de entrenamiento

**Qué buscar:**
- ✅ Línea subiendo o igual → bueno
- ❌ Línea bajando → problema

### 2. **Quality Score Trend**
- Línea azul: Tu sesión 2 en vivo
- Línea punteada: Baseline de Session 1 (8.79)
- Y-axis: 8.0 a 10.0
- X-axis: Horas de entrenamiento

**Qué buscar:**
- ✅ Línea arriba de 8.8 → excelente
- ⚠️ Línea bajando → necesita atención
- ❌ Línea abajo de 8.5 → problema crítico

### 3. **Performance by Exercise Type**
- Barra por tipo (arch_junior, patterns_senior, etc)
- Altura = success rate
- Color indica calidad

**Qué buscar:**
- arch_junior debe estar al 100% (fijo de S1: 98.1%)
- patterns_senior debe estar al 97%+ (fijo de S1: 94.3%)
- Resto en 100%

---

## 📋 TABLAS

### Latest Exercises (Last 20)
```
Exercise ID          Quality  Status   Patterns  Regex  Time
arch_junior_001      8.4      ✓ PASS   4/5      2/3    11:35:00
patterns_mid_042     8.6      ✓ PASS   5/5      4/4    11:36:30
arch_junior_002      8.5      ✓ PASS   4/4      4/4    11:38:00  ← FIXED!
```

- Muestra los últimos 20 ejercicios en orden inverso (más recientes arriba)
- Green checkmark = PASS
- Red X = FAIL
- Time = hora exacta del ejercicio

### Failed Exercises (si hay)
```
Exercise ID          Quality  Patterns  Regex
arch_junior_002      5.5      1/4       1/4
patterns_senior_095  5.6      1/5       1/3
```

- Solo aparece si hay fallos
- Útil para identificar problemas rápidamente

---

## 🎯 CÓMO INTERPRETAR LOS DATOS

### Escenario 1: Todo Verde ✅
```
Success Rate: 99.60%+ → En target
Quality: 8.85+ → En target
Failures: 0 → Perfecto
Graphs: Líneas arriba de baseline → Mejorando
```
**Acción**: Continúa, todo está bien.

### Escenario 2: Bajando ⚠️
```
Success Rate: 99.40% (baja de 99.53%) → Problema
Quality: 8.65 (baja de 8.79) → Problema
Graphs: Líneas bajando
```
**Acción**: Pause el entrenamiento, debug. Ver ROOT_CAUSE_ANALYSIS.md

### Escenario 3: Stuck en arch_junior_002 o patterns_senior_095 🔴
```
Failures: 2+
Latest table muestra fallos repetidos en esos ejercicios
```
**Acción**: Pause y revisa el corpus. Ver PHASE_2_SESSION_2_PLAN.md Phase 1.

### Escenario 4: Lento pero Mejorando 📈
```
Success Rate: 99.55% (mejorando lentamente)
Quality: 8.81 (mejorando)
Graphs: Líneas suavemente arriba
Velocidad: 70 ex/h (normal)
```
**Acción**: Continúa, va bien. Espera a completar las 12 horas.

---

## 🔍 MONITOREO RECOMENDADO

### Cada 30 minutos:
- [ ] Revisar Success Rate (debe mantener >99%)
- [ ] Revisar Quality Score (debe mantener >8.7)
- [ ] Ver Latest Exercises para confirmar progreso
- [ ] Check Failures - ¿aparecen arch_junior_002 o patterns_senior_095?

### Cada 2 horas:
- [ ] Revisar tendencias en gráficos
- [ ] Comparar S1 vs S2 - ¿Mejorando?
- [ ] Verificar velocidad (ex/h) - ¿Constante?

### Si ves problema:
```
1. Anota la hora exacta
2. Screenshot del dashboard
3. Revisa ROOT_CAUSE_ANALYSIS.md
4. Pausa el training (Ctrl+C)
5. Debug y fixes
6. Reinicia desde el checkpoint
```

---

## 💾 ARCHIVOS INVOLUCRADOS

```
dashboard.html              ← El dashboard (abre en navegador)
serve_dashboard.py          ← Servidor HTTP local
src/training/live_metrics.py ← Collector de métricas
training_12h.py             ← Script principal (integrado)
data/training_logs/live_metrics.json ← Datos en vivo (actualiza cada ejercicio)
data/training_logs/training_[DATE].json ← Resultado final
```

---

## 🚨 TROUBLESHOOTING

### Dashboard no carga
```
1. Verifica que serve_dashboard.py está corriendo
2. Abre browser en: http://localhost:8000/dashboard.html
3. Revisa en console: Ctrl+Shift+I → Network tab
   - live_metrics.json debe tener status 200
```

### live_metrics.json no existe
```
1. Verifica que training_12h.py está corriendo
2. Espera a que se complete el primer ejercicio
3. File será creado en: data/training_logs/live_metrics.json
```

### Dashboard no actualiza
```
1. Revisa que live_metrics.json está siendo actualizado
   - Terminal: ls -la data/training_logs/live_metrics.json
2. Recarga el página del browser (F5)
3. Si sigue no actualizando, reinicia serve_dashboard.py
```

### Datos se ven congelados
```
1. El training puede estar pausado
2. Revisa Terminal 3 - ¿training_12h.py sigue corriendo?
3. Mira el log: tail -f data/training_logs/training_12h.log
```

---

## 📊 MÉTRICAS GUARDADAS

Cada ejercicio registra:
```json
{
  "exercise_id": "arch_junior_001",
  "quality_score": 8.4,
  "success": true,
  "timestamp": "2026-06-30T11:35:00",
  "patterns_found": 4,
  "patterns_total": 5,
  "regex_matched": 2,
  "regex_total": 3
}
```

**Historial**: Últimos 20 ejercicios en `latest_exercises`  
**Fallos**: Todos los fallos en `failures`  
**Tipos**: Desglosa por tipo (arch_junior, patterns_senior, etc)

---

## 🎯 OBJETIVOS EN EL DASHBOARD

### Session 2 Targets (Esperado Ver)

| Métrica | Target | Dashboard Location |
|---------|--------|-------------------|
| **Total Ejercicios** | 900+ | "Exercises Completed" card |
| **Success Rate** | 99.60%+ | "Success Rate" card |
| **Quality Score** | 8.85+ | "Quality Score" card |
| **Arch Junior** | 100% | "Performance by Exercise Type" chart |
| **Patterns Senior** | 97%+ | "Performance by Exercise Type" chart |
| **Failures** | 0 | "Failures Detected" card |

**Si ves todo en verde y en target, Session 2 será exitosa.**

---

## 🔗 QUICK LINKS

- **Training Plan**: PHASE_2_SESSION_2_PLAN.md
- **Root Causes**: ROOT_CAUSE_ANALYSIS.md
- **Executive Summary**: BATUTA_SESION2.md
- **Getting Started**: README_SESION2.md

---

## 💡 TIPS PRO

1. **Mantén el dashboard abierto** en una pantalla/ventana
2. **Monitorea cada 30-60 min** durante el entrenamiento
3. **Captura screenshots** si ves anomalías para después revisar
4. **Usa los gráficos** para entender tendencias, no valores puntuales
5. **Si todo está verde**, confía en el proceso y deja correr las 12 horas
6. **Si hay problema**, pausa inmediatamente y debug según ROOT_CAUSE_ANALYSIS.md

---

**Dashboard Ready**: ✅  
**Last Updated**: 2026-06-30  
**Created For**: Session 2 Real-time Tracking  
**Auto-refresh**: Every 2 seconds

