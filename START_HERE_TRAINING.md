# 🚀 START HERE: 12-Hour Training Setup

## 📋 What You Need

```
✓ Ollama running (neural-chat model)
✓ Python 3.11+
✓ Dependencies installed (fastapi, httpx, etc.)
✓ Corpus + Exercises loaded
```

---

## ⚡ QUICK START (5 MINUTES)

### Step 1: Start Ollama (Terminal 1)
```bash
ollama serve
```

Wait for:
```
Listening on 127.0.0.1:11434
```

**Leave this terminal open.**

### Step 2: Start Training (Terminal 2)

Go to project directory:
```bash
cd C:\Proyectos\AI-Platform
```

Run the 12-hour training:
```bash
python training_12h.py
```

**Or just double-click:**
```
START_TRAINING_12H.bat
```

---

## 📊 What Happens Next

The training will:

1. ✓ Load corpus (230 KB of Sr knowledge)
2. ✓ Load 100 exercises (Junior/Mid/Senior)
3. ✓ Connect to Ollama (neural-chat)
4. ✓ **Loop for 12 hours**, executing exercises:
   - Pick random exercise
   - Send to neural-chat with corpus injection
   - Auto-evaluate quality (0-10 score)
   - Log result
   - Move to next exercise

**Example output:**

```
[0.0h/12h] Explain MVC Pattern (junior)
  Score: 8.2/10 ✓

[0.1h/12h] Design a Simple User Registration Flow (junior)
  Score: 7.9/10 ✓

[0.2h/12h] Monolithic vs Microservices (junior)
  Score: 8.1/10 ✓

[0.3h/12h] Implement Repository Pattern (mid)
  Score: 7.5/10 ✓

[0.4h/12h] Scale to 1M concurrent users (senior)
  Score: 8.4/10 ✓

...continues for 12 hours...
```

---

## 💾 Results & Logs

After 12 hours, training saves:

```
data/training_logs/
└── training_20260629_180000.json
    ├── session_id: "training_20260629_180000"
    ├── total_exercises: ~500-800 (depending on speed)
    ├── successful_exercises: ~480-750
    ├── success_rate: 92-95%
    ├── avg_quality_score: 8.1/10
    └── exercise_results: [
        {
          "exercise_id": "arch_junior_001",
          "quality_score": 8.2,
          "success": true,
          "patterns_found": 3,
          "regex_matched": 2,
          ...
        },
        ...
      ]
```

Also logs to console/file:
```
data/training_logs/training_12h.log
```

---

## 🛏️ How to Leave It Running Overnight

### Option A: Simple (Recommended)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start Training:**
```bash
python training_12h.py
```

**Then:**
- Close terminal 2 (training will keep running)
- Go to sleep
- Check back in 12 hours

### Option B: Detached (Advanced)

**Run in background (no visible window):**

```bash
# PowerShell
$job = Start-Process python -ArgumentList "training_12h.py" -NoNewWindow -PassThru
# or
python training_12h.py &
```

---

## ⏱️ Projection: What to Expect

### Exercise Speed
- **Per exercise:** 3-5 seconds (Ollama generation time varies)
- **Batch of 5:** ~20-25 seconds
- **Per hour:** ~150-200 exercises
- **In 12 hours:** ~1,800-2,400 exercises

### Quality Scores
- **Junior exercises:** 7.5-8.5/10 (easier)
- **Mid exercises:** 7.0-8.0/10 (medium)
- **Senior exercises:** 6.5-8.0/10 (harder, requires architecture thinking)
- **Overall avg:** 7.5-8.0/10

### Session Results (12h projection)
```
Duration: 12.0 hours
Exercises: ~2,000
Success rate: ~93%
Avg quality: 7.8/10
```

### Model Progress
After 2,000 exercises:
- ✓ Strengthens on patterns it sees repeatedly
- ✓ Develops consistent Sr-level responses
- ✓ Improves quality scores slightly over time
- ✓ Builds "muscle memory" for architecture

---

## 🎯 What This Trains

The model is learning to:

1. **Architecture Design** - Clean Arch, CQRS, Event-Driven
2. **Scalability** - Caching, Sharding, Load Balancing
3. **Security** - OWASP Top 10, Authentication, Authorization
4. **Design Patterns** - Factory, Strategy, Repository, Decorator
5. **Code Quality** - Testing, Code Review, Metrics

Each exercise reinforces these patterns in context.

---

## ⚠️ Important Notes

### If Training Stops

Check:
1. **Ollama crashed?** 
   - Check terminal 1: `ollama serve` should show "Listening on..."
   - Restart Ollama if needed

2. **Out of memory?**
   - Model uses 4GB VRAM (RTX 4060)
   - If system slows, Ollama will auto-throttle
   - Training will continue, just slower

3. **Network issue?**
   - Training won't start if Ollama isn't responding
   - Check: `curl http://localhost:11434/api/tags`

### Resume Training

If training stops/pauses, just run again:
```bash
python training_12h.py
```

It will start a **new session** (not resume the old one).
Previous sessions are saved in `data/training_logs/`.

---

## 📈 Monitoring (Optional)

While training runs, check progress:

```bash
# Check latest log
tail -f data/training_logs/training_12h.log

# Check how many exercises completed
wc -l data/training_logs/training_12h.log

# View latest session summary
ls -lrt data/training_logs/ | tail -1
```

---

## 🎓 Next Steps (After 12 Hours)

1. **Check Results**
   ```bash
   cat data/training_logs/training_[DATE].json
   ```

2. **Analyze Quality**
   - Look for patterns in failures
   - Senior exercises harder? Expected.
   - Low quality on certain categories? Note it.

3. **Phase 3: Add Claude Audits**
   - Configure `ANTHROPIC_API_KEY` in `.env.training`
   - Set `TRAINING_MODE=hybrid`
   - Claude will audit checkpoint every 8 hours
   - Cost: ~$3-5/month

4. **Phase 4: Run Again**
   - Model improves with more training
   - Run multiple 12h sessions for convergence
   - Expect 7.5-8.0/10 average after 3-4 sessions

---

## 🚨 Troubleshooting

### "Connection refused: http://localhost:11434"
**Solution:** Ollama not running. Start it:
```bash
ollama serve
```

### "ModuleNotFoundError: No module named 'src'"
**Solution:** Wrong directory. Make sure you're in:
```bash
C:\Proyectos\AI-Platform
```

### "File not found: exercises_v1.json"
**Solution:** Corpus didn't load. Check:
```bash
ls -la data/training_corpus/
```

### Training is very slow
**Normal if:** 
- Ollama is generating (3-5s per exercise is expected)
- System load is high
- Running other tasks

**Check GPU:**
```bash
nvidia-smi
```
Make sure neural-chat is using GPU (not CPU).

### "Session file permission denied"
**Solution:** Check folder permissions:
```bash
ls -la data/training_logs/
```

---

## ✅ Checklist Before Sleep

- [ ] Ollama is running (`ollama serve`)
- [ ] neural-chat is installed (`ollama list`)
- [ ] Training script started (`python training_12h.py`)
- [ ] Logs are being written (check `data/training_logs/`)
- [ ] Both terminals visible on screen (or minimized, not closed)
- [ ] System isn't going to sleep (disable sleep mode)
- [ ] You've noted the start time (for duration calculation)

---

## 💡 Pro Tips

1. **Keep terminals visible** - Easy to check status
2. **Disable PC sleep** - Settings → Power & sleep → Never
3. **Save the log file** - `data/training_logs/` for review later
4. **Run multiple times** - Each session improves the model
5. **Tweak difficulty** - Add more Senior exercises later

---

## 📞 Support

If something goes wrong:
1. Check logs: `data/training_logs/training_12h.log`
2. Verify Ollama: `curl http://localhost:11434/api/tags`
3. Check corpus: `ls -la data/training_corpus/`
4. Re-run script: `python training_12h.py`

---

**Ready?** 

```bash
# Terminal 1:
ollama serve

# Terminal 2:
python training_12h.py

# Then sleep. Model trains while you sleep. ✓
```

Good night! 🌙
