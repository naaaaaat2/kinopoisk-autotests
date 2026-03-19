"""
Настройки для тестов Кинопоиска
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Settings:
    """Класс с настройками для тестов"""
    
    # URL-ы
    BASE_URL = "https://www.kinopoisk.ru"
    API_URL = "https://api.kinopoisk.dev/v1.4"
    
    # Токен API (из переменных окружения или прямой вставкой для разработки)
    API_TOKEN = os.getenv("KINOPOISK_API_TOKEN", "46YKTQS-E3FMCE0-MB6HR9Z-WTCWSVV")
    
    # Тестовые данные для UI (если потребуется авторизация)
    TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
    TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")
    
    # Таймауты (увеличены для стабильности)
    DEFAULT_TIMEOUT = 20  # секунд для WebDriverWait
    IMPLICIT_WAIT = 10    # секунд для implicit_wait
    PAGE_LOAD_TIMEOUT = 30  # секунд для загрузки страницы
    
    # Тестовые ID фильмов
    EXISTING_MOVIE_ID = 535341  # "1+1" (реальный фильм на Кинопоиске)
    NON_EXISTENT_MOVIE_ID = 999999999  # Заведомо несуществующий ID
    
    # Поисковые запросы для тестов
    SEARCH_QUERIES = {
        "existing": "Аватар",
        "partial": "ава",
        "non_existent": "этотфильмточнонесуществует123456789",
        "special_chars": "!@#$%"
    }
    
    # ID фильмов для тестов страниц
    MOVIE_IDS = {
        "popular": 535341,    # 1+1
        "classic": 326,        # Операция Ы
        "new": 1319872        # Дюна
    }


# Создаем глобальный экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Возвращает экземпляр настроек"""
    return settings
