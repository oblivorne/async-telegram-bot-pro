# 📑 Примеры Кода «До» и «После» (Детализированная Версия)

В этом документе представлены ключевые технические проблемы оригинального проекта и их исправления. Для каждой ситуации приведён детализированный анализ: **что происходило до**, **какая ошибка возникала**, и **как было исправлено**.

---

## 1. Проблема: Неправильная работа с пулом соединений БД

**До (сломанный):**

```python
engine = create_async_engine(DB_URL)
session_maker = sessionmaker(engine)

async def get_user(user_id: int):
    async with session_maker() as session:  # ❌ sessionmaker без expire_on_commit и async
        return await session.get(User, user_id)
```

**Ошибка:** соединения зависали, в пуле накапливались «висящие» сессии, нагрузка на PostgreSQL увеличивалась.

**После (исправлено):**

```python
engine = create_async_engine(DB_URL, pool_size=10, max_overflow=20)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_user(user_id: int):
    async with async_session_maker() as session:  # ✅ правильный async session
        return await session.get(User, user_id)
```

**Результат:**

* Сессии корректно закрываются
* Нет утечек соединений
* Производительность увеличилась при нагрузочных тестах

---

## 2. Проблема: Ошибки в обработчиках Telegram (aiogram)

**До (сломанный):**

```python
@dp.message_handler(lambda message: message.text.startswith("/add"))
async def add_command(message: types.Message):
    parts = message.text.split()
    item = parts[1]  # ❌ IndexError, если аргумент не передан
    await db.add_item(item)
    await message.answer("Добавлено!")
```

**Ошибка:** при вводе команды `/add` без аргументов бот падал с `IndexError`.

**После (исправлено):**

```python
@dp.message_handler(lambda message: message.text.startswith("/add"))
async def add_command(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Укажите элемент для добавления!")
        return
    item = parts[1]
    await db.add_item(item)
    await message.answer("✅ Добавлено!")
```

**Результат:**

* Исключена возможность `IndexError`
* Пользователь получает понятное сообщение об ошибке

---

## 3. Проблема: Блокирующие вызовы внутри асинхронного кода

**До (сломанный):**

```python
import requests

@dp.message_handler(commands=["weather"])
async def weather_handler(message: types.Message):
    data = requests.get("https://api.weather.com/data")  # ❌ блокирует event loop
    await message.answer(data.json()["temp"])
```

**Ошибка:** event loop полностью блокировался, бот переставал отвечать.

**После (исправлено):**

```python
import aiohttp

@dp.message_handler(commands=["weather"])
async def weather_handler(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.weather.com/data") as resp:
            data = await resp.json()
    await message.answer(data["temp"])
```

**Результат:**

* Event loop не блокируется
* Ответы приходят в реальном времени

---

## 4. Проблема: Некорректная сериализация объектов

**До (сломанный):**

```python
class User(BaseModel):
    id: int
    created_at: datetime

async def get_user_json(user_id: int):
    user = await db.get_user(user_id)
    return json.dumps(user.__dict__)  # ❌ datetime не сериализуется
```

**Ошибка:** `TypeError: Object of type datetime is not JSON serializable`

**После (исправлено):**

```python
from fastapi.encoders import jsonable_encoder

class User(BaseModel):
    id: int
    created_at: datetime

async def get_user_json(user_id: int):
    user = await db.get_user(user_id)
    return json.dumps(jsonable_encoder(user))  # ✅ datetime → str
```

**Результат:**

* Объекты корректно сериализуются
* JSON-ответы валидны и удобны для клиентов

---

## 5. Проблема: Неправильная конфигурация переменных окружения

**До (сломанный):**

```python
TOKEN = os.getenv("BOT_TOKEN")  # ❌ если переменной нет → None

bot = Bot(token=TOKEN)
```

**Ошибка:** бот падал на старте при отсутствии переменной.

**После (исправлено):**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
bot = Bot(token=settings.BOT_TOKEN)  # ✅ гарантированная валидация
```

**Результат:**

* Строгая проверка конфигурации
* Ошибки выявляются на старте, а не в рантайме

---

Эти исправления обеспечили стабильность, отказоустойчивость и готовность бота к продакшен-среде.
