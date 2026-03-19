"""
Фикстуры pytest для тестов
"""

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from api.client import KinopoiskAPIClient
from config.settings import settings


@pytest.fixture
def driver():
    """
    Фикстура для WebDriver с использованием встроенного Selenium Manager
    """
    driver_instance = None
    with allure.step("Настройка и запуск браузера"):
        chrome_options = Options()
        
        # Добавляем аргументы для стабильности
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-allow-origins=*")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        # Добавляем user-agent чтобы не выглядеть как бот
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Пробуем использовать Selenium Manager
            driver_instance = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            allure.attach(
                f"Ошибка при запуске Chrome: {e}\nПробуем с webdriver-manager...",
                name="ошибка_драйвера",
                attachment_type=allure.attachment_type.TEXT
            )
            # Fallback на webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver_instance = webdriver.Chrome(service=service, options=chrome_options)
        
        driver_instance.implicitly_wait(settings.IMPLICIT_WAIT)
        
        # Пробуем максимизировать окно, но не падаем если не получается
        try:
            driver_instance.maximize_window()
        except Exception:
            driver_instance.set_window_size(1920, 1080)
        
        yield driver_instance
        
        with allure.step("Закрытие браузера"):
            try:
                driver_instance.quit()
            except:
                pass  # Игнорируем ошибки при закрытии


@pytest.fixture
def api_client():
    """
    Фикстура для API клиента
    Возвращает экземпляр KinopoiskAPIClient
    """
    client = KinopoiskAPIClient()
    return client
