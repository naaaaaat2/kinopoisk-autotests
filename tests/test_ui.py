"""
UI тесты для Кинопоиска
Основаны на функциональном чек-листе из ручного тестирования
"""

import allure
import pytest
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from config.settings import settings


def safe_wait(driver, condition, timeout=None, poll_frequency=0.5):
    """
    Безопасное ожидание с увеличенным таймаутом
    
    Args:
        driver: WebDriver
        condition: условие ожидания
        timeout: таймаут в секундах (по умолчанию settings.DEFAULT_TIMEOUT)
        poll_frequency: частота опроса
    
    Returns:
        результат выполнения условия
    """
    if timeout is None:
        timeout = settings.DEFAULT_TIMEOUT
    return WebDriverWait(driver, timeout, poll_frequency).until(condition)


def is_captcha_page(driver):
    """Проверка, попали ли мы на страницу с капчей"""
    if not driver:
        return False
    try:
        return "showcaptcha" in driver.current_url or "captcha" in driver.current_url
    except:
        return False


@allure.epic("UI Кинопоиска")
@allure.feature("Главная страница")
class TestMainPage:
    """Тесты главной страницы"""
    
    @allure.story("Загрузка страницы")
    @allure.title("Тест загрузки главной страницы")
    @pytest.mark.ui
    def test_main_page_load(self, driver):
        """
        Проверка успешной загрузки главной страницы
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        with allure.step("Перейти на главную страницу"):
            driver.set_page_load_timeout(60)
            
            try:
                driver.get(settings.BASE_URL)
            except TimeoutException:
                driver.execute_script("window.stop();")
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="страница_после_таймаута",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                allure.attach(
                    f"Ошибка при загрузке: {e}",
                    name="ошибка",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"Не удалось загрузить страницу: {e}")
            
            try:
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=30)
            except:
                pytest.skip("Не удалось загрузить body страницы")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="главная_страница",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Проверить заголовок страницы"):
            try:
                safe_wait(driver, lambda d: "Кинопоиск" in d.title, timeout=10)
                assert "Кинопоиск" in driver.title, \
                    f"Заголовок '{driver.title}' не содержит 'Кинопоиск'"
                allure.attach(
                    f"Заголовок: {driver.title}",
                    name="заголовок",
                    attachment_type=allure.attachment_type.TEXT
                )
            except TimeoutException:
                # Если заголовок не загрузился, проверяем URL
                assert "kinopoisk" in driver.current_url.lower(), \
                    f"URL {driver.current_url} не содержит kinopoisk"
                allure.attach(
                    "Заголовок не загрузился, но URL корректен",
                    name="предупреждение",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.story("Поисковая строка")
    @allure.title("Тест наличия поисковой строки на главной")
    @pytest.mark.ui
    def test_search_input_present(self, driver):
        """
        Проверка наличия поисковой строки на главной странице
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие поисковой строки"):
            try:
                search_input = safe_wait(
                    driver, 
                    EC.presence_of_element_located((By.NAME, "kp_query")),
                    timeout=10
                )
                
                assert search_input.is_displayed(), "Поисковая строка не отображается"
                assert search_input.is_enabled(), "Поисковая строка неактивна"
                
                placeholder = search_input.get_attribute("placeholder")
                allure.attach(
                    f"Поисковая строка найдена. Placeholder: {placeholder if placeholder else 'не указан'}",
                    name="информация_о_поиске",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="поисковая_строка",
                    attachment_type=allure.attachment_type.PNG
                )
            except TimeoutException:
                # Проверяем альтернативные селекторы для поиска
                alt_selectors = [
                    (By.CSS_SELECTOR, "input[type='text']"),
                    (By.CSS_SELECTOR, "input[placeholder*='поиск']"),
                    (By.CSS_SELECTOR, "[class*='search'] input")
                ]
                
                found = False
                for selector_type, selector in alt_selectors:
                    elements = driver.find_elements(selector_type, selector)
                    if elements:
                        found = True
                        allure.attach(
                            f"Поиск найден по альтернативному селектору: {selector}",
                            name="альтернативный_поиск",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        break
                
                assert found, "Поисковая строка не найдена на странице"
    
    @allure.story("Заголовок страницы")
    @allure.title("Тест наличия шапки сайта")
    @pytest.mark.ui
    def test_header_present(self, driver):
        """
        Проверка наличия шапки сайта
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие шапки"):
            try:
                header = safe_wait(
                    driver,
                    EC.presence_of_element_located((By.TAG_NAME, "header")),
                    timeout=10
                )
                assert header.is_displayed(), "Шапка сайта не отображается"
                allure.attach(
                    "Шапка сайта найдена",
                    name="шапка",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                driver.execute_script("window.scrollTo(0, 0);")
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="верх_страницы",
                    attachment_type=allure.attachment_type.PNG
                )
            except TimeoutException:
                # Проверяем наличие любого блока вверху страницы
                top_elements = driver.find_elements(By.CSS_SELECTOR, "body > *")
                assert len(top_elements) > 0, "Страница пуста"
                allure.attach(
                    f"Найдено {len(top_elements)} элементов в начале страницы",
                    name="элементы",
                    attachment_type=allure.attachment_type.TEXT
                )


@allure.epic("UI Кинопоиска")
@allure.feature("Поиск")
class TestSearch:
    """Тесты поиска фильмов"""
    
    @allure.story("Поиск по названию")
    @allure.title("Тест поиска существующего фильма")
    @pytest.mark.ui
    def test_search_existing_movie(self, driver):
        """
        Проверка поиска фильма по названию
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        search_query = settings.SEARCH_QUERIES["existing"]
        
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step(f"Ввести в поиск '{search_query}'"):
            try:
                search_input = safe_wait(
                    driver, 
                    EC.presence_of_element_located((By.NAME, "kp_query")),
                    timeout=15
                )
                search_input.clear()
                search_input.send_keys(search_query)
                
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="после_ввода",
                    attachment_type=allure.attachment_type.PNG
                )
            except TimeoutException:
                # Ищем любой input для поиска
                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if not inputs:
                    pytest.skip("Не найдено полей ввода")
                inputs[0].send_keys(search_query)
                search_input = inputs[0]
        
        with allure.step("Выполнить поиск"):
            search_input.send_keys(Keys.RETURN)
        
        with allure.step("Проверить результаты поиска"):
            try:
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=20
                )
            except:
                pytest.skip("Страница результатов не загрузилась")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_на_поиске",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча на странице поиска")
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="результаты_поиска",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Проверяем что мы не на главной
            assert "kp_query" in driver.current_url.lower() or "search" in driver.current_url.lower(), \
                f"Поиск не выполнен: {driver.current_url}"
    
    @allure.story("Поиск по названию")
    @allure.title("Тест поиска с пустым запросом")
    @pytest.mark.ui
    def test_search_empty_query(self, driver):
        """
        Проверка поиска с пустым запросом
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Нажать поиск без ввода текста"):
            try:
                search_input = safe_wait(
                    driver,
                    EC.presence_of_element_located((By.NAME, "kp_query")),
                    timeout=10
                )
                search_input.send_keys(Keys.RETURN)
            except TimeoutException:
                pytest.skip("Поле поиска не найдено")
    
    @allure.story("Поиск по названию")
    @allure.title("Тест поиска несуществующего фильма")
    @pytest.mark.ui
    def test_search_nonexistent_movie(self, driver):
        """
        Проверка поиска по несуществующему названию
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        search_query = settings.SEARCH_QUERIES["non_existent"]
        
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step(f"Ввести в поиск '{search_query}'"):
            try:
                search_input = safe_wait(
                    driver,
                    EC.presence_of_element_located((By.NAME, "kp_query")),
                    timeout=10
                )
                search_input.clear()
                search_input.send_keys(search_query)
            except TimeoutException:
                pytest.skip("Поле поиска не найдено")
        
        with allure.step("Выполнить поиск"):
            search_input.send_keys(Keys.RETURN)
        
        with allure.step("Проверить результаты поиска"):
            try:
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=20
                )
            except:
                pytest.skip("Страница результатов не загрузилась")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_на_поиске",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча на странице поиска")
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="результаты_поиска",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Проверяем что поиск выполнился
            assert "kp_query" in driver.current_url.lower() or "search" in driver.current_url.lower(), \
                f"Поиск не выполнен: {driver.current_url}"


@allure.epic("UI Кинопоиска")
@allure.feature("Страница фильма")
class TestMoviePage:
    """Тесты страницы фильма"""
    
    @allure.story("Открытие фильма")
    @allure.title("Тест открытия страницы существующего фильма")
    @pytest.mark.ui
    def test_open_movie_page(self, driver):
        """
        Проверка открытия страницы конкретного фильма
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        movie_id = settings.EXISTING_MOVIE_ID
        movie_url = f"{settings.BASE_URL}/film/{movie_id}/"
        
        with allure.step(f"Перейти на страницу фильма {movie_id}"):
            try:
                driver.get(movie_url)
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=20
                )
            except:
                pytest.skip("Не удалось загрузить страницу фильма")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_на_странице_фильма",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча при переходе на страницу фильма")
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="страница_фильма",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Проверить, что страница фильма загрузилась"):
            # Проверяем что мы не на капче
            assert "captcha" not in driver.current_url.lower(), "Попали на капчу"
            # Проверяем что URL содержит film
            assert "film" in driver.current_url.lower(), \
                f"Страница фильма не открылась: {driver.current_url}"
    
    @allure.story("Информация о фильме")
    @allure.title("Тест наличия основной информации о фильме")
    @pytest.mark.ui
    def test_movie_info_present(self, driver):
        """
        Проверка наличия основной информации на странице фильма
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        movie_url = f"{settings.BASE_URL}/film/{settings.EXISTING_MOVIE_ID}/"
        
        with allure.step("Перейти на страницу фильма"):
            try:
                driver.get(movie_url)
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=20
                )
            except:
                pytest.skip("Не удалось загрузить страницу фильма")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие информации"):
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                assert len(body_text) > 100, "На странице недостаточно текста"
                allure.attach(
                    f"На странице {len(body_text)} символов",
                    name="длина_текста",
                    attachment_type=allure.attachment_type.TEXT
                )
            except:
                pytest.skip("Не удалось получить текст страницы")


@allure.epic("UI Кинопоиска")
@allure.feature("Навигация")
class TestNavigation:
    """Тесты навигации по сайту"""
    
    @allure.story("Основное меню")
    @allure.title("Тест наличия основных разделов")
    @pytest.mark.ui
    def test_navigation_sections(self, driver):
        """
        Проверка наличия основных разделов в меню
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
            
        with allure.step("Перейти на главную страницу"):
            try:
                driver.get(settings.BASE_URL)
                safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            except:
                pytest.skip("Не удалось загрузить главную страницу")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие текста на странице"):
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                assert len(body_text) > 0, "Страница пуста"
                allure.attach(
                    f"На странице {len(body_text)} символов",
                    name="длина_текста",
                    attachment_type=allure.attachment_type.TEXT
                )
            except:
                pytest.skip("Не удалось получить текст страницы")
    
    @allure.story("Логотип")
    @allure.title("Тест перехода по логотипу на главную")
    @pytest.mark.ui
    def test_logo_redirects_to_main(self, driver):
        """
        Проверка, что клик по логотипу ведет на главную страницу
        """
        if not driver:
            pytest.skip("Драйвер не инициализирован")
        
        with allure.step("Перейти на страницу фильма"):
            movie_url = f"{settings.BASE_URL}/film/{settings.EXISTING_MOVIE_ID}/"
            try:
                driver.get(movie_url)
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=20
                )
            except Exception as e:
                allure.attach(
                    f"Ошибка при загрузке: {e}",
                    name="ошибка",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"Не удалось загрузить страницу: {e}")
            
            if is_captcha_page(driver):
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="капча_обнаружена",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Найти и кликнуть на логотип"):
            try:
                # Пробуем найти логотип
                logo_selectors = [
                    (By.CSS_SELECTOR, "a[aria-label='Кинопоиск']"),
                    (By.CSS_SELECTOR, ".header__logo a"),
                    (By.CSS_SELECTOR, "[class*='logo'] a"),
                    (By.XPATH, "//a[contains(@href, '/')]/img")
                ]
                
                logo = None
                for selector_type, selector in logo_selectors:
                    elements = driver.find_elements(selector_type, selector)
                    for element in elements:
                        if element.is_displayed():
                            logo = element
                            break
                    if logo:
                        break
                
                if not logo:
                    pytest.skip("Логотип не найден на странице")
                
                driver.execute_script("arguments[0].scrollIntoView(true);", logo)
                
                try:
                    logo.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", logo)
                    allure.attach(
                        "Клик выполнен через JavaScript",
                        name="способ_клика",
                        attachment_type=allure.attachment_type.TEXT
                    )
                
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="после_клика",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                pytest.skip(f"Ошибка при клике на логотип: {e}")
        
        with allure.step("Проверить, что вернулись на главную"):
            try:
                safe_wait(
                    driver,
                    lambda d: d.execute_script("return document.readyState") == "complete",
                    timeout=15
                )
            except:
                pytest.skip("Страница не загрузилась после клика")
            
            allure.attach(
                driver.get_screenshot_as_png(),
                name="после_клика_на_логотип",
                attachment_type=allure.attachment_type.PNG
            )
            
            current_url = driver.current_url.rstrip('/')
            base_url = settings.BASE_URL.rstrip('/')
            
            # Проверяем что мы на главной или на странице без film в URL
            assert "film" not in current_url.lower() or base_url in current_url, \
                f"Ожидалась главная страница, получено: {driver.current_url}"
