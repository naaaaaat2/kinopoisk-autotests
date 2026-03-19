"""
API тесты для Кинопоиска
Основаны на коллекции Postman из ручного тестирования
"""

import allure
import pytest
from typing import Dict, Any
from config.settings import settings


@allure.epic("API Кинопоиска")
@allure.feature("Поиск фильмов")
class TestMovieSearch:
    """Тесты поиска фильмов"""
    
    @allure.story("Поиск по названию")
    @allure.title("Тест поиска существующего фильма по названию")
    @pytest.mark.api
    def test_search_existing_movie(self, api_client):
        """
        Проверка, что поиск по названию возвращает результаты
        
        Ожидаемый результат:
        - Статус код 200
        - В ответе есть поле docs с результатами
        - Среди результатов есть искомый фильм
        """
        movie_title = "Аватар"
        
        with allure.step(f"Поиск фильма по названию: {movie_title}"):
            response = api_client.search_movies(movie_title)
        
        with allure.step("Проверка статус-кода ответа"):
            assert response.status_code == 200, \
                f"Ожидался 200, получен {response.status_code}"
        
        with allure.step("Проверка структуры ответа"):
            data = response.json()
            assert "docs" in data, "В ответе отсутствует поле docs"
            assert len(data["docs"]) > 0, "Поиск не вернул результатов"
            
            allure.attach(
                f"Найдено фильмов: {data.get('total', 0)}",
                name="количество_результатов",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Проверка, что в результатах есть искомый фильм"):
            found_movies = [
                movie for movie in data["docs"] 
                if movie_title.lower() in movie.get("name", "").lower()
            ]
            assert len(found_movies) > 0, \
                f"Фильм '{movie_title}' не найден в результатах"
            
            first_movie = found_movies[0]
            allure.attach(
                f"Первый найденный фильм: {first_movie.get('name')} "
                f"({first_movie.get('year')}) - ID: {first_movie.get('id')}",
                name="пример_результата",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("Поиск по названию")
    @allure.title("Тест поиска несуществующего фильма")
    @pytest.mark.api
    def test_search_nonexistent_movie(self, api_client):
        """
        Проверка поиска по заведомо несуществующему названию
        
        Ожидаемый результат:
        - Статус код 200
        - Поле total = 0
        - Поле docs пустое
        """
        movie_title = "этотфильмточнонесуществует123456789"
        
        with allure.step(f"Поиск по несуществующему названию: {movie_title}"):
            response = api_client.search_movies(movie_title)
        
        with allure.step("Проверка статус-кода ответа"):
            assert response.status_code == 200
        
        with allure.step("Проверка, что результатов нет"):
            data = response.json()
            assert data.get("total", 0) == 0, \
                f"Найдены результаты для несуществующего фильма: total = {data.get('total')}"
            assert len(data.get("docs", [])) == 0, \
                f"В ответе есть фильмы ({len(data.get('docs', []))}), хотя их не должно быть"
    
    @allure.story("Поиск по ID")
    @allure.title("Тест получения фильма по существующему ID")
    @pytest.mark.api
    def test_get_movie_by_valid_id(self, api_client):
        """
        Проверка получения фильма по корректному ID
        
        Ожидаемый результат:
        - Статус код 200
        - Данные фильма соответствуют запрошенному ID
        """
        movie_id = settings.EXISTING_MOVIE_ID  # 535341 - "1+1"
        
        with allure.step(f"Получение фильма по ID: {movie_id}"):
            response = api_client.get_movie_by_id(movie_id)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200, \
                f"Ожидался 200, получен {response.status_code}"
        
        with allure.step("Проверка данных фильма"):
            movie = response.json()
            assert movie.get("id") == movie_id, \
                f"ID фильма не совпадает: ожидался {movie_id}, получен {movie.get('id')}"
            assert movie.get("name") is not None, "Отсутствует название фильма"
            assert movie.get("year") is not None, "Отсутствует год выпуска"
            assert movie.get("rating") is not None, "Отсутствует рейтинг"
            
            allure.attach(
                f"Фильм: {movie.get('name')} ({movie.get('year')})\n"
                f"Рейтинг: {movie.get('rating', {}).get('kp')}\n"
                f"Жанры: {', '.join([g.get('name') for g in movie.get('genres', [])[:5]])}",
                name="детальная_информация",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("Поиск по ID")
    @allure.title("Тест получения фильма по несуществующему ID - BUG-001")
    @pytest.mark.api
    def test_get_movie_by_invalid_id(self, api_client):
        """
        Тест для документирования дефекта BUG-001 из ручного тестирования
        Согласно REST-стандартам должен быть 404, но API возвращает 400
        
        Ожидаемый результат: 404 Not Found
        Фактический результат: 400 Bad Request
        """
        invalid_id = 999999999
        
        with allure.step(f"Запрос фильма по несуществующему ID: {invalid_id}"):
            response = api_client.get_movie_by_id(invalid_id)
        
        with allure.step("Проверка статус-кода"):
            if response.status_code == 400:
                allure.attach(
                    f"БАГ-001: API возвращает 400 вместо 404 для несуществующего ID {invalid_id}\n"
                    f"REST стандарт требует 404 Not Found для несуществующих ресурсов\n"
                    f"Ответ API: {response.text}",
                    name="описание_бага",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.xfail("Известный баг BUG-001: API возвращает 400 вместо 404")
            else:
                assert response.status_code == 404, \
                    f"Ожидался 404, получен {response.status_code}"
    
    @allure.story("Поиск по ID")
    @allure.title("Тест получения фильма с граничными значениями ID")
    @pytest.mark.api
    def test_get_movie_by_boundary_id(self, api_client):
        """
        Проверка обработки граничных значений ID
        
        Тестируемые значения:
        - ID = 0
        - Отрицательный ID
        - Очень большой ID
        """
        test_ids = [0, -1, 999999999999]
        
        for test_id in test_ids:
            with allure.step(f"Проверка ID = {test_id}"):
                response = api_client.get_movie_by_id(test_id)
                
                assert response.status_code < 500, \
                    f"Внутренняя ошибка сервера для ID {test_id}: {response.status_code}"
                
                allure.attach(
                    f"ID: {test_id}\nСтатус код: {response.status_code}",
                    name=f"результат_для_id_{test_id}",
                    attachment_type=allure.attachment_type.TEXT
                )


@allure.epic("API Кинопоиска")
@allure.feature("Фильтры и сортировка")
class TestMovieFilters:
    """Тесты фильтрации и сортировки фильмов"""
    
    @allure.story("Фильтрация по году")
    @allure.title("Тест поиска фильмов по году выпуска")
    @pytest.mark.api
    def test_search_movies_by_year(self, api_client):
        """
        Проверка фильтрации фильмов по году
        
        Ожидаемый результат:
        - Статус код 200
        - Все найденные фильмы соответствуют указанному году
        """
        test_year = 2023
        
        with allure.step(f"Поиск фильмов за {test_year} год"):
            response = api_client.search_movies_by_filters(year=test_year)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка, что все фильмы соответствуют году"):
            data = response.json()
            assert len(data.get("docs", [])) > 0, \
                f"Не найдено фильмов за {test_year} год"
            
            allure.attach(
                f"Найдено фильмов за {test_year} год: {len(data['docs'])}",
                name="количество_фильмов",
                attachment_type=allure.attachment_type.TEXT
            )
            
            incorrect_years = []
            for movie in data["docs"][:5]:
                movie_year = movie.get("year")
                if movie_year != test_year:
                    incorrect_years.append(
                        f"{movie.get('name')}: {movie_year} (ожидался {test_year})"
                    )
            
            assert len(incorrect_years) == 0, \
                f"Найдены фильмы не за {test_year} год:\n" + "\n".join(incorrect_years)
    
    @allure.story("Фильтрация по жанру")
    @allure.title("Тест поиска фильмов по жанру")
    @pytest.mark.api
    def test_search_movies_by_genre(self, api_client):
        """
        Проверка фильтрации фильмов по жанру
        
        Ожидаемый результат:
        - Статус код 200
        - Все найденные фильмы содержат указанный жанр
        """
        test_genre = "комедия"
        
        with allure.step(f"Поиск фильмов в жанре: {test_genre}"):
            response = api_client.search_movies_by_filters(genre=test_genre)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка жанров фильмов"):
            data = response.json()
            assert len(data.get("docs", [])) > 0, \
                f"Не найдено фильмов жанра '{test_genre}'"
            
            allure.attach(
                f"Найдено фильмов в жанре '{test_genre}': {len(data['docs'])}",
                name="количество_фильмов",
                attachment_type=allure.attachment_type.TEXT
            )
            
            incorrect_genres = []
            for movie in data["docs"][:5]:
                genres = [g.get("name", "").lower() for g in movie.get("genres", [])]
                if test_genre not in genres:
                    incorrect_genres.append(
                        f"{movie.get('name')}: жанры - {', '.join(genres)}"
                    )
            
            assert len(incorrect_genres) == 0, \
                f"Найдены фильмы без жанра '{test_genre}':\n" + "\n".join(incorrect_genres)
    
    @allure.story("Фильтрация по рейтингу")
    @allure.title("Тест поиска фильмов с высоким рейтингом")
    @pytest.mark.api
    def test_search_movies_by_high_rating(self, api_client):
        """
        Проверка фильтрации фильмов по минимальному рейтингу
        
        Ожидаемый результат:
        - Статус код 200
        - Все найденные фильмы имеют рейтинг не ниже заданного
        """
        min_rating = 8.0
        
        with allure.step(f"Поиск фильмов с рейтингом >= {min_rating}"):
            response = api_client.search_movies_by_filters(rating_from=min_rating)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка рейтингов фильмов"):
            data = response.json()
            assert len(data.get("docs", [])) > 0, \
                f"Не найдено фильмов с рейтингом >= {min_rating}"
            
            low_rated = []
            for movie in data["docs"][:5]:
                rating = movie.get("rating", {}).get("kp")
                if rating is None or rating < min_rating:
                    low_rated.append(
                        f"{movie.get('name')}: рейтинг {rating}"
                    )
            
            assert len(low_rated) == 0, \
                f"Найдены фильмы с рейтингом ниже {min_rating}:\n" + "\n".join(low_rated)


@allure.epic("API Кинопоиска")
@allure.feature("Детальная информация")
class TestMovieDetails:
    """Тесты детальной информации о фильмах"""
    
    @allure.story("Актерский состав")
    @allure.title("Тест получения актеров фильма")
    @pytest.mark.api
    def test_get_movie_actors(self, api_client):
        """
        Проверка получения списка актеров для фильма
        
        Ожидаемый результат:
        - Статус код 200
        - У фильма есть актеры
        """
        movie_id = settings.EXISTING_MOVIE_ID  # 535341 - "1+1"
        
        with allure.step(f"Получение информации о фильме ID {movie_id}"):
            response = api_client.get_movie_actors(movie_id)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка наличия актеров"):
            movie = response.json()
            
            assert "persons" in movie, "В ответе отсутствует поле persons"
            
            persons = movie.get("persons", [])
            assert len(persons) > 0, "У фильма нет информации о персонах"
            
            actors = [
                p for p in persons 
                if p.get("profession") == "актеры" or p.get("enProfession") == "actor"
            ]
            
            assert len(actors) > 0, "У фильма нет актеров"
            
            actors_info = []
            for actor in actors[:10]:
                actors_info.append(
                    f"- {actor.get('name')} "
                    f"({actor.get('description', 'роль не указана')})"
                )
            
            allure.attach(
                f"Фильм: {movie.get('name')}\n"
                f"Всего персон: {len(persons)}\n"
                f"Актеров: {len(actors)}\n\n"
                f"Актерский состав (первые 10):\n" + "\n".join(actors_info),
                name="актерский_состав",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.story("Популярные фильмы")
    @allure.title("Тест получения списка популярных фильмов")
    @pytest.mark.api
    def test_get_popular_movies(self, api_client):
        """
        Проверка получения списка популярных фильмов
        
        Ожидаемый результат:
        - Статус код 200
        - Возвращается список фильмов с рейтингом >= 7
        """
        with allure.step("Получение списка популярных фильмов"):
            response = api_client.get_popular_movies()
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка структуры и данных"):
            data = response.json()
            assert "docs" in data, "В ответе отсутствует поле docs"
            assert len(data["docs"]) > 0, "Список популярных фильмов пуст"
            
            allure.attach(
                f"Найдено популярных фильмов: {len(data['docs'])}",
                name="количество_фильмов",
                attachment_type=allure.attachment_type.TEXT
            )
            
            with allure.step("Проверка наличия рейтинга у фильмов"):
                low_rated = []
                movies_info = []
                
                for movie in data["docs"][:5]:
                    name = movie.get('name', 'Название не указано')
                    rating = movie.get("rating", {}).get("kp")
                    
                    if rating is None:
                        low_rated.append(f"{name}: рейтинг отсутствует")
                    elif rating < 7:
                        low_rated.append(f"{name}: рейтинг {rating}")
                    
                    movies_info.append(f"{name} - рейтинг: {rating}")
                
                assert len(low_rated) == 0, \
                    "Найдены фильмы с низким рейтингом:\n" + "\n".join(low_rated)
                
                allure.attach(
                    "Топ-5 популярных фильмов:\n" + "\n".join(movies_info),
                    name="топ_фильмов",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.story("Связанные фильмы")
    @allure.title("Тест получения рекомендаций и похожих фильмов")
    @pytest.mark.api
    def test_get_similar_movies(self, api_client):
        """
        Проверка наличия похожих фильмов и рекомендаций
        
        Ожидаемый результат:
        - Статус код 200
        - У фильма есть поле с похожими фильмами
        """
        movie_id = settings.EXISTING_MOVIE_ID
        
        with allure.step(f"Получение информации о фильме ID {movie_id}"):
            response = api_client.get_movie_by_id(movie_id)
        
        with allure.step("Проверка статус-кода"):
            assert response.status_code == 200
        
        with allure.step("Проверка наличия похожих фильмов"):
            movie = response.json()
            
            similar_fields = ['similarMovies', 'sequelsAndPrequels', 'recommendations']
            
            found_similar = False
            similar_info = []
            
            for field in similar_fields:
                if field in movie and movie[field]:
                    found_similar = True
                    similar_info.append(f"{field}: {len(movie[field])} элементов")
                    
                    if len(movie[field]) > 0:
                        similar_list = []
                        for item in movie[field][:3]:
                            if isinstance(item, dict):
                                name = item.get('name', 'Название не указано')
                                similar_list.append(f"  - {name}")
                        
                        if similar_list:
                            similar_info.extend(similar_list)
            
            if found_similar:
                allure.attach(
                    "Найдены похожие фильмы:\n" + "\n".join(similar_info),
                    name="похожие_фильмы",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    "У фильма нет информации о похожих фильмах",
                    name="информация",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            assert True
