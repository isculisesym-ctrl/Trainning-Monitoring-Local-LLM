# Code Quality & Excellence - Sr Level

## Testing Pyramid

```
        △
       △ △  Unit Tests (70%)
      △ △ △  
     ▁▁▁▁▁▁  Integration Tests (20%)
    ▔▔▔▔▔▔▔▔
     E2E Tests (10%)
```

### Unit Tests (Fast, Isolated)
```python
# Test ONLY the function, mock dependencies

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def create_user(self, email: str) -> User:
        if not email:
            raise ValueError("Email required")
        if await self.repo.exists(email):
            raise DuplicateUserError()
        return await self.repo.save(User(email))

# Test (mock repository)
@pytest.mark.asyncio
async def test_create_user_success():
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.exists.return_value = False
    mock_repo.save.return_value = User(email="test@example.com")
    
    service = UserService(mock_repo)
    user = await service.create_user("test@example.com")
    
    assert user.email == "test@example.com"
    mock_repo.save.assert_called_once()

async def test_create_user_duplicate_email():
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.exists.return_value = True  # Already exists
    
    service = UserService(mock_repo)
    
    with pytest.raises(DuplicateUserError):
        await service.create_user("test@example.com")

async def test_create_user_missing_email():
    mock_repo = AsyncMock(spec=UserRepository)
    service = UserService(mock_repo)
    
    with pytest.raises(ValueError, match="Email required"):
        await service.create_user("")
```

### Integration Tests
```python
# Real database, real external services (or test double)

async def test_create_and_retrieve_user(db):
    # Real DB transaction
    service = UserService(PostgresUserRepository(db))
    
    user = await service.create_user("test@example.com")
    retrieved = await service.get_user(user.id)
    
    assert retrieved.email == user.email

async def test_order_flow_with_payment(db, payment_service_mock):
    # Full flow: create order → charge payment → update inventory
    order_service = OrderService(
        repo=PostgresOrderRepository(db),
        payment=payment_service_mock,
        inventory=PostgresInventoryRepository(db)
    )
    
    order = await order_service.create_order(
        user_id=1,
        items=[{"sku": "BOOK001", "qty": 2}]
    )
    
    assert order.status == "pending"
    payment_service_mock.charge.assert_called_once()
```

### E2E Tests
```python
# Full application flow via HTTP

async def test_create_order_api(client: TestClient):
    response = client.post("/orders", json={
        "user_id": 1,
        "items": [{"sku": "BOOK001", "qty": 2}]
    })
    
    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "pending"
    
    # Verify in DB
    db_order = await db.query("SELECT * FROM orders WHERE id = ?", order["id"])
    assert db_order is not None
```

### Coverage Target
```bash
# Sr standard: > 80% coverage
# Critical paths (auth, payments, data): 100%
# Utilities: 70%

pytest --cov=src --cov-report=term-missing
```

---

## Code Review (Sr must do this well)

### What to Look For

1. **Correctness**
   - Does it handle errors?
   - Off-by-one errors?
   - Null pointer exceptions?
   - Race conditions?

2. **Performance**
   - N+1 queries?
   - Unnecessary loops?
   - Blocking operations?
   - Memory leaks?

3. **Maintainability**
   - Clear variable names?
   - Single responsibility?
   - Duplicated logic?
   - Documentation needed?

4. **Security**
   - Input validation?
   - SQL injection risk?
   - XSS vulnerability?
   - Hard-coded secrets?

### Review Template
```markdown
## PR Review: Add Order API

### ✅ Good
- Clear separation of concerns (service/repository)
- Good test coverage (95%)
- Proper error handling

### ⚠️ Suggestions
1. Query optimization: Add index on `orders(user_id, status)`
   - Current: 2s for 100K rows
   - After: 50ms
   
2. Performance: Use async context manager
   ```python
   # Before
   session = get_session()
   user = session.query(User).filter_by(id=1).first()
   session.close()
   
   # After
   async with get_session() as session:
       user = await session.get(User, 1)
   ```

3. Security: Validate user owns order before returning
   ```python
   order = await repo.get_order(order_id)
   if order.user_id != request.user.id:  # Missing!
       raise Forbidden()
   ```

### ❌ Issues
1. N+1 query: Fetching user for each order
   - Current: 1 order query + 100 user queries
   - Fix: Use JOIN or eager loading
   ```python
   # Slow
   orders = await repo.get_orders()
   for order in orders:
       order.user = await repo.get_user(order.user_id)
   
   # Fast
   orders = await repo.get_orders_with_users()  # One query
   ```

2. Race condition: Between check and use
   ```python
   # ❌ Unsafe
   if user.balance >= amount:  # Check
       user.balance -= amount  # Use (another thread changed it)
       await save(user)
   
   # ✅ Safe (atomic)
   await db.execute(
       "UPDATE users SET balance = balance - ? WHERE id = ? AND balance >= ?",
       amount, user.id, amount
   )
   ```

### Verdict: ✅ Approve with suggested changes
```
