# 🚀 Деплой и Запуск

Документ описывает процесс локального запуска и деплоя проекта.

---

## 1. Подготовка окружения

1. Установить **Python 3.11+**.
2. Клонировать репозиторий:

   ```bash
   git clone https://github.com/oblivorne/async-telegram-bot-pro.git
   cd async-telegram-bot-pro
   ```
3. Создать виртуальное окружение:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / Mac
   venv\Scripts\activate      # Windows
   ```
4. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Переменные окружения

Создать файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_token
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
MODERATION_GROUP_ID=-1234567890
S3_BUCKET_NAME=example-bucket
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

---

## 3. Запуск локально

```bash
python -m bot
```

Бот должен подключиться к Telegram API и начать принимать сообщения.

---

## 4. Запуск через Docker

1. Собрать контейнер:

   ```bash
   docker build -t async-telegram-bot .
   ```
2. Запустить:

   ```bash
   docker run --env-file .env async-telegram-bot
   ```

---

## 5. Docker Compose

Для запуска всей системы (Postgres + Redis + Bot):

```bash
docker-compose up -d --build
```

Файл `docker-compose.yml` содержит сервисы:

* База данных (PostgreSQL)
* Redis
* Сам бот

---

## 6. Продакшн

* Использовать **systemd** или **supervisord** для мониторинга процесса.
* Логи писать в stdout (для Docker).
* Регулярные бэкапы PostgreSQL и Redis.

---

Эти шаги позволяют быстро развернуть бота в любом окружении: локально, в контейнере или на сервере.
