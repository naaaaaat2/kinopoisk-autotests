"""
Page Object для главной страницы Кинопоиска
"""

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pages.base_page import BasePage


class MainPage(BasePage):
    """Класс для работы с главной страницей"""
    
    # Локаторы
    SEARCH_INPUT = (By.NAME, "kp_query")
    HEADER = (By.TAG_NAME, "header")
    LOGO = (By.CSS_SELECTOR, "a[aria-label='Кинопоиск']")
    
    @allure.step("Открыть главную страницу")
    def open(self):
        """Открыть главную страницу"""
        self.driver.get(self.base_url)
        self.wait_for_page_load()
    
    @allure.step("Ввести поисковый запрос")
    def enter_search_query(self, query):
        """Ввести текст в поисковую строку"""
        search_input = self.find_element(self.SEARCH_INPUT)
        search_input.clear()
        search_input.send_keys(query)
        return search_input
    
    @allure.step("Выполнить поиск")
    def perform_search(self, query=None):
        """Выполнить поиск (с запросом или без)"""
        search_input = self.find_element(self.SEARCH_INPUT)
        if query:
            search_input.clear()
            search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)
    
    @allure.step("Проверить наличие поисковой строки")
    def is_search_input_present(self):
        """Проверить, что поисковая строка отображается"""
        element = self.find_element(self.SEARCH_INPUT)
        return element.is_displayed() and element.is_enabled()
    
    @allure.step("Проверить наличие шапки сайта")
    def is_header_present(self):
        """Проверить, что шапка сайта отображается"""
        element = self.find_element(self.HEADER)
        return element.is_displayed()
    
    @allure.step("Кликнуть на логотип")
    def click_logo(self):
        """Кликнуть по логотипу для перехода на главную"""
        logo = self.find_element(self.LOGO)
        self.scroll_to_element(logo)
        self.safe_click(logo)
