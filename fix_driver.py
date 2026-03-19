"""
Исправление проблемы с ChromeDriver
"""

import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager

def fix_chromedriver():
    """
    Исправляет проблему с загрузкой chromedriver
    Когда webdriver_manager скачивает THIRD_PARTY_NOTICES вместо chromedriver.exe
    """
    print("=" * 50)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМЫ CHROMEDRIVER")
    print("=" * 50)
    
    try:
        # Шаг 1: Очищаем кэш webdriver_manager
        print("\n1. Очищаю кэш webdriver_manager...")
        cache_dir = os.path.expanduser("~/.wdm")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("   ✅ Кэш очищен")
        else:
            print("   ⏭️ Кэш не найден")
        
        # Шаг 2: Скачиваем драйвер через webdriver_manager
        print("\n2. Скачиваю драйвер через webdriver_manager...")
        driver_path = ChromeDriverManager().install()
        print(f"   ✅ Драйвер скачан: {driver_path}")
        
        # Шаг 3: Проверяем, что скачался правильный файл
        print("\n3. Проверяю скачанный файл...")
        folder = os.path.dirname(driver_path)
        
        # Ищем chromedriver.exe в папке
        possible_paths = [
            os.path.join(folder, "chromedriver.exe"),
            os.path.join(folder, "chromedriver-win32", "chromedriver.exe"),
            os.path.join(folder, "chromedriver")
        ]
        
        correct_path = None
        for path in possible_paths:
            if os.path.exists(path):
                correct_path = path
                print(f"   ✅ Найден chromedriver: {path}")
                break
        
        if correct_path:
            print("\n✅ ИСПРАВЛЕНИЕ УСПЕШНО!")
            print(f"\nПуть к драйверу: {correct_path}")
            
            # Шаг 4: Создаем символическую ссылку или копируем файл
            print("\n4. Создаю резервную копию в папке проекта...")
            project_dir = os.getcwd()
            backup_path = os.path.join(project_dir, "chromedriver.exe")
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            shutil.copy2(correct_path, backup_path)
            print(f"   ✅ Драйвер скопирован в: {backup_path}")
            
            return correct_path
        else:
            print("\n❌ Не удалось найти chromedriver.exe в скачанной папке")
            print(f"Содержимое папки {folder}:")
            for file in os.listdir(folder):
                print(f"   - {file}")
            return None
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return None

def test_driver():
    """Тестирует работу драйвера"""
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ДРАЙВЕРА")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        import time
        
        # Пробуем использовать драйвер из папки проекта
        project_dir = os.getcwd()
        driver_path = os.path.join(project_dir, "chromedriver.exe")
        
        if not os.path.exists(driver_path):
            print("❌ Драйвер не найден в папке проекта")
            return False
        
        print(f"\n1. Использую драйвер: {driver_path}")
        service = Service(driver_path)
        
        print("2. Запускаю браузер...")
        driver = webdriver.Chrome(service=service)
        
        print("3. Открываю страницу...")
        driver.get("https://www.kinopoisk.ru")
        
        print(f"4. Заголовок страницы: {driver.title}")
        
        if "Кинопоиск" in driver.title:
            print("5. ✅ Тест пройден успешно!")
        else:
            print("5. ⚠️ Странный заголовок, но браузер работает")
        
        time.sleep(2)
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    driver_path = fix_chromedriver()
    if driver_path:
        test_driver()
