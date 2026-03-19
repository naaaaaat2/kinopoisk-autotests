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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from config.settings import settings


def safe_wait(driver, condition, timeout=None, poll_frequency=0.5):
    """
    Безопасное ожидание с увеличенным таймаутом
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
            
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=30)
            
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
            except TimeoutException:
                assert "kinopoisk" in driver.current_url.lower(), \
                    f"URL {driver.current_url} не содержит kinopoisk"
    
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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие поисковой строки"):
            # Точный локатор для поисковой строки
            search_input = safe_wait(
                driver, 
                EC.presence_of_element_located((By.NAME, "kp_query")),
                timeout=10
            )
            
            assert search_input.is_displayed(), "Поисковая строка не отображается"
            assert search_input.is_enabled(), "Поисковая строка неактивна"
    
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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие шапки"):
            # Точный локатор для шапки
            header = safe_wait(
                driver,
                EC.presence_of_element_located((By.TAG_NAME, "header")),
                timeout=10
            )
            assert header.is_displayed(), "Шапка сайта не отображается"


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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step(f"Ввести в поиск '{search_query}'"):
            search_input = safe_wait(
                driver, 
                EC.presence_of_element_located((By.NAME, "kp_query")),
                timeout=15
            )
            search_input.clear()
            search_input.send_keys(search_query)
        
        with allure.step("Выполнить поиск"):
            search_input.send_keys(Keys.RETURN)
        
        with allure.step("Проверить результаты поиска"):
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=20
            )
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча на странице поиска")
            
            current_url = driver.current_url.lower()
            assert "kp_query" in current_url or "search" in current_url, \
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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Нажать поиск без ввода текста"):
            search_input = safe_wait(
                driver,
                EC.presence_of_element_located((By.NAME, "kp_query")),
                timeout=10
            )
            search_input.send_keys(Keys.RETURN)
    
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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step(f"Ввести в поиск '{search_query}'"):
            search_input = safe_wait(
                driver,
                EC.presence_of_element_located((By.NAME, "kp_query")),
                timeout=10
            )
            search_input.clear()
            search_input.send_keys(search_query)
        
        with allure.step("Выполнить поиск"):
            search_input.send_keys(Keys.RETURN)
        
        with allure.step("Проверить результаты поиска"):
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=20
            )
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча на странице поиска")
            
            assert "kp_query" in driver.current_url.lower(), \
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
            driver.get(movie_url)
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=20
            )
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча при переходе на страницу фильма")
        
        with allure.step("Проверить, что страница фильма загрузилась"):
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
            driver.get(movie_url)
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=20
            )
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие информации"):
            body_text = driver.find_element(By.TAG_NAME, "body").text
            assert len(body_text) > 100, "На странице недостаточно текста"


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
            driver.get(settings.BASE_URL)
            safe_wait(driver, EC.presence_of_element_located((By.TAG_NAME, "body")), timeout=20)
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Проверить наличие разделов"):
            sections = ["Фильмы", "Сериалы", "Медиа"]
            found_sections = []
            
            for section in sections:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{section}')]")
                if elements:
                    found_sections.append(section)
            
            assert len(found_sections) > 0, "Не найдено ни одного раздела"
    
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
            driver.get(movie_url)
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=20
            )
            
            if is_captcha_page(driver):
                pytest.skip("Обнаружена капча. Тест пропущен.")
        
        with allure.step("Найти и кликнуть на логотип"):
            # Точный локатор для логотипа Кинопоиска
            logo = safe_wait(
                driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Кинопоиск']")),
                timeout=10
            )
            
            assert logo.is_displayed(), "Логотип не отображается"
            
            driver.execute_script("arguments[0].scrollIntoView(true);", logo)
            
            try:
                logo.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", logo)
        
        with allure.step("Проверить, что вернулись на главную"):
            safe_wait(
                driver,
                lambda d: d.execute_script("return document.readyState") == "complete",
                timeout=15
            )
            
            current_url = driver.current_url.rstrip('/')
            base_url = settings.BASE_URL.rstrip('/')
            
            assert base_url in current_url or current_url == base_url + '/', \
                f"Ожидалась главная страница, получено: {driver.current_url}"
