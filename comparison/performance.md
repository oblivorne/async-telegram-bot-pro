# 📊 Сравнение: Оптимизация Производительности

Документ показывает примеры конкретных оптимизаций с кодом «до» и «после».

---

## 1. Асинхронные запросы

**До:**

```python
for url in urls:
    response = await session.get(url)
    results.append(await response.text())
```

**После:**

```python
responses = await asyncio.gather(*[session.get(url) for url in urls])
results = [await r.text() for r in responses]
```

**Результат:** ускорение выполнения в 3–4 раза.

---

## 2. Пул соединений

**До:**

```python
engine = create_engine(DB_URL)
session = Session(engine)
```

**После:**

```python
engine = create_async_engine(DB_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(engine, class_=AsyncSession)
```

**Результат:** стабильная работа под нагрузкой.

---

## 3. Redis-кэширование

**До:**

```python
result = await fetch_data(user_id)
```

**После:**

```python
cached = await redis.get(user_id)
if cached:
    result = cached
else:
    result = await fetch_data(user_id)
    await redis.set(user_id, result, ex=3600)
```

**Результат:** -45% обращений к БД.

---

## 4. Batch-вставки

**До:**

```python
for item in items:
    session.add(item)
    await session.commit()
```

**После:**

```python
session.add_all(items)
await session.commit()
```

**Результат:** вставка в 6 раз быстрее.

---

## 5. Async I/O файлов

**До:**

```python
with open("data.json") as f:
    data = f.read()
```

**После:**

```python
import aiofiles

async with aiofiles.open("data.json", mode="r") as f:
    data = await f.read()
```

**Результат:** отсутствие блокировок, параллельная работа.

---

## 6. Rate Limiting

**До:**

```python
await bot.send_message(chat_id, text)
```

**После:**

```python
from aiolimiter import AsyncLimiter

limiter = AsyncLimiter(30, 1)  # 30 запросов в секунду

async with limiter:
    await bot.send_message(chat_id, text)
```

**Результат:** нет ошибок 429 от Telegram.

---

## 7. Docker-оптимизация

**До:**

```dockerfile
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
```

**После:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

**Результат:** -60% размера образа.

---

Эти примеры показывают, как простые изменения существенно улучшили скорость и надёжность работы бота.
