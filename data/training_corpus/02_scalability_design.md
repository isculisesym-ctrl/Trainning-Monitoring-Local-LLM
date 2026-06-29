# Scalability Design - Sr Level

## Caching Strategy

### L1: In-Memory (Application)
```python
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def get_user_by_id(user_id: int):
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

# Problema: cache muere con restart
# Solución: invalidación explícita
@lru_cache.clear()
```

### L2: Redis (Shared)
```python
import redis
import json
from datetime import timedelta

class UserRepository:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def get_user(self, user_id: int):
        # Intenta cache primero (Hot path)
        cache_key = f"user:{user_id}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Cache miss: BD
        user = await self.db.query(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        
        # Repoblate cache (TTL = 1 hora)
        await self.redis.setex(
            cache_key,
            timedelta(hours=1),
            json.dumps(user)
        )
        return user
    
    async def update_user(self, user_id: int, data: dict):
        # Actualiza BD
        updated = await self.db.update(
            "UPDATE users SET ... WHERE id = $1", user_id
        )
        
        # Invalida cache inmediatamente
        await self.redis.delete(f"user:{user_id}")
        return updated
```

### L3: CDN (Static Assets)
```
CloudFront / Cloudflare
├─ HTML, CSS, JS (cache 7 días)
├─ Images (cache 30 días)
└─ API responses (cache 5 min si cacheable)
```

### Cache Invalidation Strategies
```
1. TTL (Time-to-Live): Natural expiry
   - Pros: Simple
   - Cons: Stale data hasta TTL

2. Event-based: Invalida cuando cambio
   - Pros: Siempre fresco
   - Cons: Complejo (need event bus)

3. Hybrid: TTL corto (5 min) + Event-based
   - Mejor balance
```

---

## Database Optimization

### Query Performance
```sql
-- ❌ Slow: N+1 problem
SELECT * FROM users;  -- 1000 users
for user in users:
    orders = SELECT * FROM orders WHERE user_id = user.id;  -- 1000 queries

-- ✅ Fast: JOIN
SELECT u.*, o.* FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- ✅ Fast: Subquery
SELECT * FROM users u
WHERE id IN (SELECT DISTINCT user_id FROM orders);
```

### Indexing
```sql
-- Slow (full table scan)
SELECT * FROM orders WHERE user_id = 123 AND status = 'completed';

-- Fast (with index)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Rule: Index WHERE columns + ORDER BY + JOIN
-- Composite index: (user_id, status) better than separate indexes
```

### Database Partitioning (Sharding)
```python
# By user_id (most common)
def get_shard_id(user_id: int) -> int:
    return user_id % NUM_SHARDS  # Consistent hashing better

# Connection routing
async def query_user(user_id: int):
    shard = get_shard_id(user_id)
    db = shard_connections[shard]  # 0-9
    return await db.query("SELECT * FROM users WHERE id = ?", user_id)

# Benefits:
# - Escalabilidad horizontal (cada shard en servidor distinto)
# - Queries rápidas (menor dataset por shard)
# Desventajas:
# - Joins entre shards complicados
# - Rebalancing es pesado
```

### Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Bad: Nueva conexión por request
engine = create_engine("postgresql://...")

# Good: Pool de conexiones
engine = create_engine(
    "postgresql://...",
    poolclass=QueuePool,
    pool_size=20,           # Conexiones abiertas
    max_overflow=10,        # Conexiones extras si necesita
    pool_recycle=3600       # Recicla cada hora
)

# Benefits:
# - Reutiliza conexiones (caro crear)
# - Evita "too many connections"
# - Automático en FastAPI/Django
```

---

## Load Balancing

### Round Robin (Básico)
```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1 (cicla)
```
Problema: No considera carga actual.

### Least Connections
```
Request → Servidor con menos conexiones activas
```
Mejor para sesiones largas (WebSocket).

### Weighted Round Robin
```
Server 1 (10GB RAM) → 50% traffic
Server 2 (5GB RAM)  → 25% traffic
Server 3 (5GB RAM)  → 25% traffic
```

### NGINX Config:
```nginx
upstream api_servers {
    server api1.local:8000 weight=2;
    server api2.local:8000 weight=1;
    server api3.local:8000 weight=1;
}

server {
    listen 80;
    location /api {
        proxy_pass http://api_servers;
    }
}
```

---

## Rate Limiting

### Token Bucket (Sr-level)
```python
from aioredis import Redis

class RateLimiter:
    def __init__(self, redis: Redis, rate: int, period: int):
        self.redis = redis
        self.rate = rate          # max requests
        self.period = period      # seconds
    
    async def is_allowed(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        
        # Lua script (atomic in Redis)
        result = await self.redis.eval("""
            local current = redis.call('incr', KEYS[1])
            if current == 1 then
                redis.call('expire', KEYS[1], ARGV[1])
            end
            return current <= tonumber(ARGV[2])
        """, 1, key, self.period, self.rate)
        
        return result

# Usage:
limiter = RateLimiter(redis, rate=100, period=60)

@app.post("/api/expensive")
async def expensive_operation(user_id: str):
    if not await limiter.is_allowed(user_id):
        raise HTTPException(429, "Rate limit exceeded")
    
    return await do_expensive_work()
```

### DDoS Protection (Infrastructure)
```
Cloudflare / AWS Shield
├─ Geo-blocking (bloquea países)
├─ Rate limiting automático
├─ CAPTCHA challenges
└─ WAF rules
```

---

## Async/Await (Critical for scale)

### ❌ Blocking (Serial)
```python
import time

@app.post("/orders")
def create_order(request):
    # Secuencial: 1s + 2s + 0.5s = 3.5s total
    payment_result = payment_service.charge(1)  # 1s blocking
    inventory_update = inventory_service.update(1)  # 2s blocking
    email_sent = email_service.send(0.5)  # 0.5s blocking
    return {"status": "ok"}
```

### ✅ Async (Parallel)
```python
import asyncio

@app.post("/orders")
async def create_order(request):
    # Concurrente: max(1s, 2s, 0.5s) = 2s total
    results = await asyncio.gather(
        payment_service.charge_async(1),        # 1s
        inventory_service.update_async(1),      # 2s (blocks here)
        email_service.send_async(0.5)           # 0.5s
    )
    return {"status": "ok"}
```

**Sin async:** 100 requests × 3.5s = 350s
**Con async:** 100 requests × 2s = 200s (43% improvement)

---

## Monitoring for Scale

```python
import prometheus_client as pc

# Latency buckets
request_duration = pc.Histogram(
    'request_duration_seconds',
    'Request latency',
    buckets=[0.1, 0.5, 1, 5, 10]
)

# Track cache hits/misses
cache_hits = pc.Counter('cache_hits_total', 'Cache hits')
cache_misses = pc.Counter('cache_misses_total', 'Cache misses')

# Database queries
db_queries = pc.Gauge('db_connections_active', 'Active DB connections')

# Alert thresholds:
# - P99 latency > 1s → scale out
# - Cache miss rate > 20% → increase cache
# - Error rate > 1% → investigate
```
