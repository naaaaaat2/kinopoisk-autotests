"""
Клиент для работы с API Кинопоиска
"""

import requests
import allure
from typing import Optional, Dict, Any
from config.settings import settings


class KinopoiskAPIClient:
    """Клиент для работы с API Кинопоиска"""
    
    def __init__(self):
        self.base_url = settings.API_URL
        self.headers = {
            "X-API-KEY": settings.API_TOKEN,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    @allure.step("API: Авторизация пользователя")
    def login(self, email: str, password: str) -> requests.Response:
        """
        Авторизация пользователя
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            
        Returns:
            Response объект с результатом авторизации
        """
        # Примечание: В официальном API Кинопоиска нет публичного эндпоинта авторизации
        # Это заглушка для демонстрации структуры
        # В реальном проекте нужно использовать реальный эндпоинт
        
        allure.attach(
            f"Email: {email}\nПароль: {'*' * len(password)}",
            name="учетные_данные",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # TODO: Заменить на реальный эндпоинт авторизации Кинопоиска
        # Сейчас возвращаем заглушку, так как API Кинопоиска не требует авторизации
        # для базовых запросов
        
        # Создаем заглушку ответа
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"token": "mock_token_for_testing"}'
        
        return mock_response
    
    @allure.step("API: Поиск фильмов по названию")
    def search_movies(self, query: str, page: int = 1, limit: int = 10) -> requests.Response:
        """
        Поиск фильмов по названию
        
        Args:
            query: Поисковый запрос
            page: Номер страницы
            limit: Количество результатов на странице
            
        Returns:
            Response объект с результатами поиска
        """
        params = {
            "query": query,
            "page": page,
            "limit": limit
        }
        
        allure.attach(
            f"Запрос: {query}\nСтраница: {page}\nЛимит: {limit}",
            name="параметры_поиска",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = self.session.get(
            f"{self.base_url}/movie/search",
            params=params
        )
        
        return response
    
    @allure.step("API: Получение фильма по ID")
    def get_movie_by_id(self, movie_id: int) -> requests.Response:
        """
        Получение детальной информации о фильме по ID
        
        Args:
            movie_id: ID фильма в базе Кинопоиска
            
        Returns:
            Response объект с данными фильма
        """
        allure.attach(
            f"ID фильма: {movie_id}",
            name="параметры_запроса",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = self.session.get(
            f"{self.base_url}/movie/{movie_id}"
        )
        
        return response
    
    @allure.step("API: Поиск фильмов по фильтрам")
    def search_movies_by_filters(
        self, 
        year: Optional[int] = None, 
        genre: Optional[str] = None,
        rating_from: Optional[float] = None
    ) -> requests.Response:
        """
        Поиск фильмов с применением фильтров
        
        Args:
            year: Год выпуска
            genre: Жанр (например, "комедия", "драма")
            rating_from: Минимальный рейтинг
            
        Returns:
            Response объект с результатами
        """
        params = {}
        if year:
            params["year"] = year
        if genre:
            params["genres.name"] = genre
        if rating_from:
            params["rating.kp"] = f"{rating_from}-10"
        
        allure.attach(
            f"Год: {year or 'любой'}\nЖанр: {genre or 'любой'}\nРейтинг от: {rating_from or 'любой'}",
            name="параметры_фильтрации",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = self.session.get(
            f"{self.base_url}/movie",
            params=params
        )
        
        return response
    
    @allure.step("API: Получение актеров фильма")
    def get_movie_actors(self, movie_id: int) -> requests.Response:
        """
        Получение списка актеров для конкретного фильма
        
        Args:
            movie_id: ID фильма
            
        Returns:
            Response объект с данными о персонах
        """
        allure.attach(
            f"ID фильма: {movie_id}",
            name="параметры_запроса",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Получаем фильм с расширенной информацией
        response = self.session.get(
            f"{self.base_url}/movie/{movie_id}"
        )
        
        return response
    
    @allure.step("API: Получение популярных фильмов")
    def get_popular_movies(self, page: int = 1) -> requests.Response:
        """
        Получение списка популярных фильмов
        
        Args:
            page: Номер страницы
            
        Returns:
            Response объект со списком фильмов
        """
        params = {
            "page": page,
            "limit": 20,
            "sortField": "rating.kp",
            "sortType": "-1",
            "rating.kp": "7-10"
        }
        
        allure.attach(
            f"Страница: {page}\nСортировка: по рейтингу (убывание)\nРейтинг: от 7",
            name="параметры_запроса",
            attachment_type=allure.attachment_type.TEXT
        )
        
        response = self.session.get(
            f"{self.base_url}/movie",
            params=params
        )
        
        return response
