# Design Patterns - Sr Level (Gang of Four + Modern)

## Creational

### Factory Pattern
```python
# Problem: Creating objects is complex, varies by type
# Solution: Centralize creation logic

class UserRepository:
    pass

class PostgresUserRepository(UserRepository):
    def __init__(self, connection_string):
        self.db = connect(connection_string)

class MongoUserRepository(UserRepository):
    def __init__(self, connection_string):
        self.mongo = MongoClient(connection_string)

class RepositoryFactory:
    @staticmethod
    def create(db_type: str, connection_string: str) -> UserRepository:
        if db_type == "postgres":
            return PostgresUserRepository(connection_string)
        elif db_type == "mongo":
            return MongoUserRepository(connection_string)
        else:
            raise ValueError(f"Unknown db: {db_type}")

# Usage:
repo = RepositoryFactory.create("postgres", "postgresql://...")
# Cambiar BD: 1 línea, cero cambios en aplicación
```

### Builder Pattern
```python
# Problem: Constructor con 10+ parámetros
# Solution: Fluent interface

class QueryBuilder:
    def __init__(self):
        self.filters = []
        self.limit_value = None
        self.offset_value = 0
    
    def where(self, column: str, op: str, value) -> "QueryBuilder":
        self.filters.append((column, op, value))
        return self  # Enable chaining
    
    def limit(self, n: int) -> "QueryBuilder":
        self.limit_value = n
        return self
    
    def offset(self, n: int) -> "QueryBuilder":
        self.offset_value = n
        return self
    
    def build(self) -> str:
        sql = "SELECT * FROM table WHERE "
        sql += " AND ".join(f"{c} {op} ?" for c, op, _ in self.filters)
        if self.limit_value:
            sql += f" LIMIT {self.limit_value}"
        if self.offset_value:
            sql += f" OFFSET {self.offset_value}"
        return sql

# Usage (fluent, readable):
query = (QueryBuilder()
    .where("age", ">=", 18)
    .where("status", "=", "active")
    .limit(10)
    .offset(20)
    .build())
```

### Singleton (Cautious)
```python
# Problem: Database connection must be shared (not recreate each time)
# Solution: One instance globally

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connect()
        return cls._instance
    
    def connect(self):
        self.connection = create_connection()

# Usage:
db1 = Database()
db2 = Database()
assert db1 is db2  # Same object

# Better in FastAPI: Dependency Injection
app = FastAPI()

async def get_db():
    return Database()  # FastAPI caches this per request

@app.get("/users")
async def list_users(db: Database = Depends(get_db)):
    return db.query("SELECT * FROM users")
```

---

## Structural

### Decorator Pattern (Aspect-Oriented)
```python
# Problem: Want to add behavior without modifying class
# Solution: Wrap with decorator

def measure_performance(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

def log_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

# Stack decorators (order matters)
@log_errors
@measure_performance
async def expensive_operation():
    await asyncio.sleep(2)
    return "done"

# Execution order: log_errors → measure_performance → expensive_operation
```

### Adapter Pattern
```python
# Problem: 3rd party library has incompatible interface
# Solution: Adapter wraps and translates

# Old system
class OldPaymentGateway:
    def process(self, amount, card):
        return {"status": "ok", "id": "12345"}

# New system expects different interface
class PaymentProcessor:
    async def charge(self, amount: Decimal) -> PaymentResult:
        raise NotImplementedError

# Adapter
class OldGatewayAdapter(PaymentProcessor):
    def __init__(self, old_gateway: OldPaymentGateway):
        self.gateway = old_gateway
    
    async def charge(self, amount: Decimal) -> PaymentResult:
        result = self.gateway.process(float(amount), ...)
        return PaymentResult(
            success=result["status"] == "ok",
            transaction_id=result["id"]
        )

# Usage: Just plug in adapter
processor: PaymentProcessor = OldGatewayAdapter(old_gateway)
await processor.charge(Decimal("99.99"))
```

### Proxy Pattern
```python
# Problem: Lazy load expensive resource
# Solution: Proxy controls access

class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self._connection = None  # Lazy
    
    @property
    def connection(self):
        if self._connection is None:
            print("Connecting to DB...")
            self._connection = create_connection(self.connection_string)
        return self._connection
    
    def query(self, sql):
        return self.connection.execute(sql)

# Usage:
db = DatabaseConnection("postgresql://...")
# Connection not created yet

result = db.query("SELECT 1")  # NOW it connects
```

---

## Behavioral

### Strategy Pattern
```python
# Problem: Multiple ways to do same thing (pricing, payment, sorting)
# Solution: Encapsulate algorithms as strategies

class PricingStrategy:
    def calculate(self, base_price: Decimal) -> Decimal:
        raise NotImplementedError

class RegularPricing(PricingStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        return base_price

class PremiumPricing(PricingStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        return base_price * Decimal("0.8")  # 20% discount

class VIPPricing(PricingStrategy):
    def calculate(self, base_price: Decimal) -> Decimal:
        return base_price * Decimal("0.5")  # 50% discount

class ShoppingCart:
    def __init__(self, pricing_strategy: PricingStrategy):
        self.strategy = pricing_strategy
        self.items = []
    
    def add_item(self, item, price):
        self.items.append(price)
    
    def total(self) -> Decimal:
        base = sum(self.items)
        return self.strategy.calculate(base)

# Usage:
user_tier = get_user_tier(user_id)  # "regular", "premium", "vip"

strategy = {
    "regular": RegularPricing(),
    "premium": PremiumPricing(),
    "vip": VIPPricing()
}[user_tier]

cart = ShoppingCart(strategy)
cart.add_item("book", Decimal("20"))
print(cart.total())  # Correct price based on tier
```

### Observer Pattern (Event-Driven)
```python
# Problem: Multiple subsystems need to react to event
# Solution: Observer listens and reacts

class EventBus:
    def __init__(self):
        self.observers = {}
    
    def subscribe(self, event_type: str, handler):
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(handler)
    
    async def publish(self, event_type: str, data):
        if event_type in self.observers:
            for handler in self.observers[event_type]:
                await handler(data)

# Observers
class PaymentObserver:
    async def on_order_created(self, order_data):
        await payment_service.charge(order_data["user_id"], order_data["total"])

class NotificationObserver:
    async def on_order_created(self, order_data):
        await email_service.send(order_data["email"], "Order confirmed")

class AnalyticsObserver:
    async def on_order_created(self, order_data):
        await analytics.track("order_created", order_data)

# Setup
event_bus = EventBus()
event_bus.subscribe("order_created", PaymentObserver().on_order_created)
event_bus.subscribe("order_created", NotificationObserver().on_order_created)
event_bus.subscribe("order_created", AnalyticsObserver().on_order_created)

# Trigger
await event_bus.publish("order_created", {
    "user_id": 123,
    "total": Decimal("99.99"),
    "email": "user@example.com"
})
```

### Template Method Pattern
```python
# Problem: Algorithm has common steps, variations in some
# Solution: Define template, let subclasses override

class DataProcessor:
    async def process_file(self, filepath):
        # Template
        data = await self.read(filepath)
        data = await self.validate(data)
        data = await self.transform(data)
        await self.save(data)
    
    async def read(self, filepath):
        raise NotImplementedError
    
    async def validate(self, data):
        raise NotImplementedError
    
    async def transform(self, data):
        raise NotImplementedError
    
    async def save(self, data):
        raise NotImplementedError

class CSVProcessor(DataProcessor):
    async def read(self, filepath):
        return pd.read_csv(filepath)
    
    async def validate(self, data):
        # CSV-specific validation
        return data.dropna()
    
    async def transform(self, data):
        return data.astype({"age": int})
    
    async def save(self, data):
        await db.save_csv_data(data)

class JSONProcessor(DataProcessor):
    async def read(self, filepath):
        with open(filepath) as f:
            return json.load(f)
    
    async def validate(self, data):
        # JSON-specific validation
        return data
    
    async def transform(self, data):
        return data
    
    async def save(self, data):
        await db.save_json_data(data)
```

---

## Architectural Patterns

### Repository Pattern (Sr must know)
```python
# Abstraction over data source (BD, cache, API)

class UserRepository:
    async def get_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError
    
    async def save(self, user: User) -> User:
        raise NotImplementedError
    
    async def delete(self, user_id: str) -> bool:
        raise NotImplementedError

# Implementation agnostic (could be BD, mock, API)
class PostgresUserRepository(UserRepository):
    async def get_by_id(self, user_id: str):
        return await self.db.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )

# Business logic works with abstraction
class CreateUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo  # Agnostic!
    
    async def execute(self, email: str, password: str):
        user = User(email, password)
        return await self.repo.save(user)
```

### Dependency Injection
```python
# ❌ Tight coupling
class OrderService:
    def __init__(self):
        self.repo = PostgresUserRepository()  # Hard-coded
    
    async def get_user_orders(self, user_id):
        return await self.repo.get_orders(user_id)

# ✅ Loose coupling (injected)
class OrderService:
    def __init__(self, repo: UserRepository):
        self.repo = repo  # Abstraction
    
    async def get_user_orders(self, user_id):
        return await self.repo.get_orders(user_id)

# In FastAPI (automatic)
@app.get("/orders")
async def get_orders(
    user_id: str,
    repo: UserRepository = Depends(get_user_repository)
):
    service = OrderService(repo)
    return await service.get_user_orders(user_id)
```
