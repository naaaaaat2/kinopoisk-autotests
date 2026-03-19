"""
Простой тест для проверки работы браузера через Selenium Manager
Исправленная версия без предупреждений pytest
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def test_browser():
    """
    Проверка, что Selenium может открыть браузер без webdriver_manager
    """
    print("\n" + "="*50)
    print("ТЕСТ БРАУЗЕРА С SELENIUM MANAGER")
    print("="*50)
    
    driver = None
    try:
        print("1. Настраиваю опции Chrome...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-allow-origins=*")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("2. Запускаю Chrome (Selenium Manager сам скачает драйвер)...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("3. Открываю Кинопоиск...")
        driver.get("https://www.kinopoisk.ru")
        
        # Ждем загрузки страницы
        time.sleep(3)
        
        print(f"4. Заголовок страницы: {driver.title}")
        
        # Проверяем, что страница загрузилась
        assert driver.title is not None, "Заголовок страницы отсутствует"
        assert "Кинопоиск" in driver.title, f"Заголовок '{driver.title}' не содержит 'Кинопоиск'"
        
        print("✅ УСПЕХ: Браузер работает, страница загружена корректно")
        
        print("5. Жду 2 секунды...")
        time.sleep(2)
        
        print("6. Закрываю браузер...")
        driver.quit()
        driver = None
        
        print("="*50)
        print("ТЕСТ ПРОЙДЕН УСПЕШНО")
        print("="*50)
        
        # Вместо return True используем assert
        assert True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        print("="*50)
        # Вместо return False используем assert с сообщением
        assert False, f"Тест не пройден: {e}"
        
    finally:
        # Гарантированно закрываем браузер в случае ошибки
        if driver:
            try:
                driver.quit()
            except:
                pass


# Для запуска вне pytest (как обычный скрипт)
if __name__ == "__main__":
    try:
        test_browser()
    except AssertionError as e:
        print(f"Тест упал: {e}")
        exit(1)
    print("Все проверки пройдены")
    exit(0)
