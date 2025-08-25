# 🧪 Тестирование

Документ описывает систему тестирования проекта: unit-тесты, интеграционные тесты и CI/CD.

---

## 1. Используемые инструменты

* **pytest** — основной тестовый фреймворк.
* **pytest-asyncio** — поддержка асинхронного кода.
* **httpx / respx** — моки HTTP-запросов.
* **pytest-docker** — запуск зависимостей (Postgres, Redis) в контейнерах.

---

## 2. Структура тестов

```
/tests
  ├── unit
  │   ├── test_handlers.py
  │   ├── test_utils.py
  │   └── test_middlewares.py
  ├── integration
  │   ├── test_database.py
  │   ├── test_redis.py
  │   └── test_api.py
  └── conftest.py
```

---

## 3. Unit-тесты

**Пример: тестирование обработчика сообщений**

```python
import pytest
from bot.handlers import start

@pytest.mark.asyncio
async def test_start_handler(mock_message):
    response = await start(mock_message)
    assert "Добро пожаловать" in response.text
```

---

## 4. Интеграционные тесты

**Пример: тестирование работы с базой**

```python
@pytest.mark.asyncio
async def test_user_creation(async_session):
    from bot.models import User

    user = User(id=1, name="Test")
    async_session.add(user)
    await async_session.commit()

    result = await async_session.get(User, 1)
    assert result.name == "Test"
```

---

## 5. Моки и фикстуры

* Моки для HTTP-запросов:

```python
import respx

@respx.mock
async def test_external_api_call(client):
    respx.get("https://api.example.com/data").mock(return_value={"ok": True})
    result = await client.get_data()
    assert result["ok"]
```

* Общие фикстуры находятся в `conftest.py`.

---

## 6. CI/CD (GitHub Actions)

В репозитории настроен workflow `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        ports: [5432:5432]
        env:
          POSTGRES_USER: user
          POSTGRES_PASSWORD: pass
          POSTGRES_DB: test_db
      redis:
        image: redis:7
        ports: [6379:6379]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest -v
```

---

Эта система обеспечивает надёжное тестирование проекта: быстрые unit-тесты и полные интеграционные проверки.
