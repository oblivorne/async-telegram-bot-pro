# 🔍 Сравнение: Исправления Ошибок

Документ демонстрирует конкретные примеры критических багов и их решений. Каждое исправление содержит: исходный код, анализ проблемы и исправленный вариант.

---

## 1. Асинхронные контексты БД

**До:**

```python
async with get_db_session() as session:
    await session.execute(query)
```

**Проблема:** `get_db_session` возвращал корутину, из-за чего возникал `TypeError`.

**После:**

```python
async with await get_db_session() as session:
    await session.execute(query)
```

**Результат:** корректная работа контекста, отсутствие ошибок.

---

## 2. Утечки aiohttp

**До:**

```python
session = aiohttp.ClientSession()
response = await session.get(url)
```

**Проблема:** `session` не закрывался, оставались открытые соединения.

**После:**

```python
async with aiohttp.ClientSession() as session:
    response = await session.get(url)
```

**Результат:** освобождение ресурсов, отсутствие утечек.

---

## 3. Блокировка цикла событий

**До:**

```python
def heavy_task():
    ... # CPU-bound работа

async def handler():
    heavy_task()  # блокирует event loop
```

**После:**

```python
loop = asyncio.get_running_loop()
await loop.run_in_executor(None, heavy_task)
```

**Результат:** UI не зависает, бот продолжает реагировать.

---

## 4. Ошибки сериализации JSON

**До:**

```python
return {"created": datetime.utcnow()}
```

**Проблема:** `TypeError: Object of type datetime is not JSON serializable`.

**После:**

```python
return {"created": datetime.utcnow().isoformat()}
```

**Результат:** успешная сериализация ответа.

---

## 5. Завершение приложения

**До:**

```python
# при выходе ресурсы не освобождаются
```

**После:**

```python
async def on_shutdown():
    await session.close()
    await redis.close()
```

**Результат:** корректное завершение, отсутствие висящих соединений.

---

## 6. Работа с транзакциями

**До:**

```python
session.commit()
```

**Проблема:** при ошибке изменения сохранялись частично.

**После:**

```python
try:
    session.commit()
except Exception:
    session.rollback()
    raise
```

**Результат:** консистентность данных в БД.

---

## 7. Таймауты HTTP-запросов

**До:**

```python
await session.get(url)
```

**После:**

```python
await session.get(url, timeout=10)
```

**Результат:** бот не зависает на медленных внешних сервисах.

---

## 8. Кэш Redis

**До:**

```python
await redis.set(key, value)
```

**После:**

```python
await redis.set(key, value, ex=3600)
```

**Результат:** ключи автоматически истекают, память не переполняется.

---

## 9. Локализация сообщений

**До:**

```python
await bot.send_message(chat_id, "Hello!")
```

**После:**

```python
await bot.send_message(chat_id, _("Привет!"))
```

**Результат:** пользователи получают сообщения на нужном языке.

---

## 10. Логирование

**До:**

```python
print("Error happened")
```

**После:**

```python
logger.error("Ошибка", extra={"context": "db_query"})
```

**Результат:** структурированные JSON-логи, легко искать.

---

Эти исправления обеспечили стабильность, устранили критические баги и подготовили проект к промышленному использованию.
