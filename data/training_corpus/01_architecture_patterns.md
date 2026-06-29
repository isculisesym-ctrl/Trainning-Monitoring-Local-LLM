# Architectural Patterns - Sr Level

## Clean Architecture (Hexagonal)

### ¿Por qué?
- Framework independence: cambias DB, web, API sin tocar lógica de negocio
- Testeable: tests sin dependencias externas
- Escalable: evolución sin roturas

### ¿Cuándo?
- Proyectos > 6 meses
- Equipos > 3 personas
- Cambios frecuentes de requisitos
- Necesidad de múltiples integraciones

### Estructura:
```
src/
├── domain/                    # Reglas de negocio puras
│   ├── entities.py
│   ├── use_cases.py           # Orquesta lógica de negocio
│   └── interfaces.py          # Abstracciones (Repositories, Services)
├── application/               # Adaptadores de entrada
│   ├── http_handlers.py       # Controllers/API
│   └── cli_handlers.py
└── infrastructure/            # Adaptadores de salida
    ├── repositories.py        # Implementación BD
    ├── external_services.py
    └── frameworks.py          # FastAPI, Django, etc
```

### Ejemplo - Crear Usuario:
```python
# domain/entities.py
class User:
    def __init__(self, email: str, password: str):
        if not self._is_valid_email(email):
            raise InvalidEmailError()
        self.email = email
        self.password_hash = self._hash_password(password)
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return "@" in email and len(email) > 5

# domain/use_cases.py
class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def execute(self, email: str, password: str) -> User:
        if self.repository.exists(email):
            raise DuplicateUserError(f"{email} already exists")
        user = User(email, password)
        return self.repository.save(user)

# application/http_handlers.py (Framework agnostic)
class CreateUserHandler:
    def __init__(self, use_case: CreateUserUseCase):
        self.use_case = use_case
    
    async def handle(self, email: str, password: str):
        try:
            user = self.use_case.execute(email, password)
            return {"id": user.id, "email": user.email}
        except DuplicateUserError as e:
            return {"error": str(e)}, 409

# infrastructure/repositories.py
class PostgresUserRepository(UserRepository):
    async def exists(self, email: str) -> bool:
        return await self.db.query(
            "SELECT 1 FROM users WHERE email = $1", email
        ) is not None
    
    async def save(self, user: User) -> User:
        result = await self.db.query(
            "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
            user.email, user.password_hash
        )
        user.id = result.id
        return user

# FastAPI adapter
from fastapi import FastAPI
app = FastAPI()

@app.post("/users")
async def create_user(email: str, password: str):
    handler = CreateUserHandler(use_case)  # Inyección
    return await handler.handle(email, password)
```

### Anti-patterns ❌
- Lógica de negocio en controllers
- Controllers llamando directo a BD
- Mixing de concerns (HTTP + BD + lógica)
- Repositorio mock diferente a implementación real

---

## CQRS (Command Query Responsibility Segregation)

### ¿Por qué?
- Lecturas y escrituras con modelos diferentes
- Escalas independientemente (read replicas)
- Cada modelo optimizado para su propósito

### ¿Cuándo?
- Alto volumen de lecturas vs escrituras
- Modelos de lectura complejos
- Múltiples vistas del mismo dato

### Estructura:
```python
# domain/commands.py
class CreateOrderCommand:
    user_id: int
    items: List[OrderItem]
    
    async def execute(self, write_repo: OrderRepository):
        order = Order(self.user_id, self.items)
        return await write_repo.save(order)

# domain/queries.py
class GetUserOrdersQuery:
    user_id: int
    
    async def execute(self, read_db: ReadModelDB) -> List[OrderSummary]:
        # Optimizado para lectura (denormalizado)
        return await read_db.query("""
            SELECT order_id, total, status, created_at
            FROM order_summaries
            WHERE user_id = $1
            ORDER BY created_at DESC
        """, self.user_id)

# application/event_handlers.py
class OrderCreatedEventHandler:
    async def handle(self, event: OrderCreatedEvent, write_db, read_db):
        # Escribe en tabla de resumen para lecturas rápidas
        await read_db.execute("""
            INSERT INTO order_summaries (order_id, user_id, total, status)
            VALUES ($1, $2, $3, $4)
        """, event.order_id, event.user_id, event.total, "pending")
```

### Ventajas
- Modelo de lectura totalmente desnormalizado (1 query)
- Writes en forma normalizada (3NF)
- Cada uno escala por separado

---

## Event-Driven Architecture

### ¿Por qué?
- Sistemas desacoplados: cambios en un servicio ≠ cambios en otros
- Asincronía natural: no esperas respuesta de cada operación
- Auditabilidad: event log = histórico perfecto
- Escalabilidad: procesa eventos en paralelo

### ¿Cuándo?
- Múltiples subsistemas
- Flujos asincronos (correos, notificaciones, reportes)
- Necesidad de auditoria completa
- Escalabilidad crítica

### Ejemplo - Order Service:
```python
# domain/events.py
class OrderCreatedEvent:
    order_id: str
    user_id: str
    total: Decimal
    items: List[OrderItem]
    timestamp: datetime

# domain/order_aggregate.py
class Order:
    def __init__(self, user_id: str, items: List[OrderItem]):
        self.id = generate_id()
        self.user_id = user_id
        self.items = items
        self.total = sum(item.price for item in items)
        
        # Publica evento (no persiste aún)
        self._events = [
            OrderCreatedEvent(
                order_id=self.id,
                user_id=user_id,
                total=self.total,
                items=items,
                timestamp=datetime.now()
            )
        ]
    
    def get_uncommitted_events(self):
        return self._events

# application/order_service.py
class OrderService:
    def __init__(self, repo: OrderRepository, event_bus: EventBus):
        self.repo = repo
        self.event_bus = event_bus
    
    async def create_order(self, user_id: str, items: List[OrderItem]) -> Order:
        order = Order(user_id, items)
        
        # 1. Persiste orden
        await self.repo.save(order)
        
        # 2. Publica eventos
        for event in order.get_uncommitted_events():
            await self.event_bus.publish(event)
        
        return order

# Infrastructure Event Handlers (desacoplados)
class PaymentEventHandler:
    async def on_order_created(self, event: OrderCreatedEvent):
        # Inicia pago asincronamente
        await self.payment_service.charge(event.user_id, event.total)

class NotificationEventHandler:
    async def on_order_created(self, event: OrderCreatedEvent):
        # Envía email asincronamente
        await self.email_service.send(
            to=event.user_id,
            subject=f"Order #{event.order_id} confirmed"
        )

class AnalyticsEventHandler:
    async def on_order_created(self, event: OrderCreatedEvent):
        # Registra en analytics
        await self.analytics.track("order_created", {
            "order_id": event.order_id,
            "total": float(event.total)
        })
```

### Ventajas:
- Payment, Notification, Analytics NO conocen OrderService
- Cada handler procesa eventos independientemente
- Nuevo handler = agregar listener, cero cambios existentes
- Si Notification falla, Order y Payment siguen (resiliente)

---

## Layered Architecture (N-tier)

### Cuándo EVITAR:
- Equipos < 3 personas (overkill)
- Proyectos < 3 meses
- CRUD simple (RAG, tabla única)

### Cuándo SÍ usar:
- Múltiples equipos
- Código de vida larga
- Compleji dad de negocio real

---

## Microservicios

### ¿Por qué?
- Equipos independientes
- Deploys independientes
- Escala selectiva (solo servicio lento)

### ¿Cuándo?
- Equipos > 10 personas
- Servicios distintos con ciclos distintos
- Alto volumen distribuido

### Desventajas (reales):
- Complejidad operacional (tracing, logs distribuidos)
- Consistencia eventual (bugs sutiles)
- Network latency (no es gratis)

### Solo si:
- Tu problema lo requiere
- Tienes DevOps/SRE
- Puedes monitorear distribuido
