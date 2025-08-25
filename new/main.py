#!/usr/bin/env python3
"""
Основной файл приложения Telegram Events Bot
"""

import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
import logfire

from events_bot.database import init_database
from events_bot.database.connection import engine
from events_bot.bot.handlers import (
    register_start_handlers,
    register_user_handlers,
    register_post_handlers,
    register_callback_handlers,
    register_moderation_handlers,
    register_feed_handlers,
)
from events_bot.bot.middleware import DatabaseMiddleware
from events_bot.database.services.post_service import PostService
from events_bot.bot.utils import get_db_session
from events_bot.storage import initialize_file_storage, set_file_storage, get_file_storage

# Настройка Logfire
logfire.configure()
logfire.info("Logfire настроен.")

async def cleanup_expired_posts_task():
    """Фоновая задача для удаления и очистки просроченных постов."""
    # Запускает периодическую задачу для удаления или архивирования просроченных постов и их изображений.
    logfire.info("🌀 Запущена фоновая задача очистки просроченных постов.")
    
    while True:
        db = None
        try:
            await asyncio.sleep(60 * 10)  # каждые 10 минут
            db = await get_db_session()
            expired_posts_info = await PostService.get_expired_posts_info(db)
            if not expired_posts_info:
                continue
            deleted_count = await PostService.delete_expired_posts(db)
            if deleted_count:
                logfire.info(f"🧹 Удалено/архивировано постов: {deleted_count}")
                for post_info in expired_posts_info:
                    image_id = post_info.get("image_id")
                    if image_id:
                        try:
                            file_storage = await get_file_storage()
                            if file_storage:
                                file_storage_instance = await file_storage
                                await file_storage_instance.delete_file(image_id)
                            else:
                                logfire.error("File storage не инициализирован, пропуск удаления файла.")
                        except Exception as file_e:
                            logfire.error(f"Ошибка удаления файла {image_id}: {file_e}")
        except asyncio.CancelledError:
            logfire.info("🌀 Фоновая задача остановлена (отмена).")
            break
        except Exception as e:
            if db:
                try:
                    await db.rollback()
                except Exception:
                    pass
            logfire.error(f"❌ Критическая ошибка в фоновой задаче: {e}", exc_info=True)
            await asyncio.sleep(60 * 30)  # при ошибке — пауза 30 минут
        finally:
            if db:
                try:
                    await db.close()
                except Exception:
                    pass

async def main():
    """Главная точка входа бота"""
    # Инициализирует и запускает Telegram-бот с необходимыми компонентами.
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logfire.info("Переменные окружения загружены из .env.")
    except ImportError:
        logfire.info(".env файл не найден, используются системные переменные окружения.")

    token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")
    moderation_group_id = os.getenv("MODERATION_GROUP_ID")
    if not token or not database_url or not moderation_group_id:
        logfire.critical(
            f"❌ КРИТИЧЕСКАЯ ОШИБКА: BOT_TOKEN: {token}, DATABASE_URL: {database_url}, "
            f"MODERATION_GROUP_ID: {moderation_group_id} не установлены!"
        )
        return

    logfire.info(f"Подключение к базе данных: {database_url}")
    try:
        await init_database()
        logfire.info("✅ База данных инициализирована.")
    except Exception as e:
        logfire.error(f"❌ Ошибка инициализации базы данных: {e}", exc_info=True)
        return

    try:
        file_storage_instance = await initialize_file_storage()
        set_file_storage(file_storage_instance)
        logfire.info(f"✅ File storage инициализирован: {type(file_storage_instance).__name__}")
    except Exception as e:
        logfire.critical(f"❌ Ошибка инициализации file storage: {e}", exc_info=True)
        raise ValueError(f"Ошибка инициализации file storage: {e}")

    try:
        bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
    except Exception as e:
        logfire.error(f"❌ Ошибка инициализации бота: {e}", exc_info=True)
        return

    try:
        dp.message.middleware(DatabaseMiddleware())
        dp.callback_query.middleware(DatabaseMiddleware())
        register_start_handlers(dp)
        register_user_handlers(dp)
        register_post_handlers(dp)
        register_callback_handlers(dp)
        register_moderation_handlers(dp)
        register_feed_handlers(dp)
        logfire.info("✅ Middleware и обработчики успешно зарегистрированы.")
    except Exception as e:
        logfire.error(f"❌ Ошибка при регистрации middleware/handlers: {e}", exc_info=True)
        return

    cleanup_task = asyncio.create_task(cleanup_expired_posts_task())
    
    logfire.info("🤖 Бот запускается...")

    try:
        await dp.start_polling(bot)
        logfire.info("✅ Бот работает.")
    except Exception as e:
        logfire.error(f"❌ Ошибка в основном цикле: {e}", exc_info=True)
    finally:
        logfire.info("🛑 Остановка бота. Завершение фоновых задач...")
        cleanup_task.cancel()
        await asyncio.gather(cleanup_task, return_exceptions=True)

        try:
            await engine.dispose()
            logfire.info("✅ Соединения с БД освобождены (engine.dispose).")
        except Exception as e:
            logfire.error(f"❌ Ошибка при закрытии соединений БД: {e}", exc_info=True)

        try:
            await bot.session.close()
            logfire.info("✅ HTTP-сессия бота закрыта.")
        except Exception as e:
            logfire.error(f"❌ Ошибка при закрытии bot.session: {e}", exc_info=True)

        logfire.info("✅ Бот остановлен.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logfire.info("Остановка по Ctrl+C.")