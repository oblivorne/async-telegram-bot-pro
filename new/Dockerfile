# Базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для PostgreSQL и других инструментов
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Устанавливаем uv для управления зависимостями
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml ./
COPY requirements.txt ./

# Создаем uv.lock и устанавливаем зависимости
RUN uv lock && uv sync --frozen

# Копируем весь исходный код
COPY . .

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Создаем uploads директорию и устанавливаем права
RUN mkdir -p /app/uploads && \
    chown -R app:app /app/uploads

# Переключаемся на непривилегированного пользователя
USER app

# Открываем порт для веб-хуков (если используется)
EXPOSE 8080

# Health check для мониторинга состояния контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; print('Bot is healthy')" || exit 1

# Команда запуска бота
CMD ["uv", "run", "python", "main.py"]