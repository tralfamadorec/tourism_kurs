from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas import AttractionCreate, EventCreate, FoodCreate


class TestAttractionSchemas:
    # тесты для валидации схем достопримечательностей
    def test_attraction_create_valid(self):
        # создание валидной схемы достопримечательности
        data = {
            "name": "Тестовый Парк",
            "description": "Описание парка",
            "latitude": 56.27,
            "longitude": 90.50,
        }
        attraction = AttractionCreate(**data)
        assert attraction.name == "Тестовый Парк"
        assert attraction.latitude == 56.27

    def test_attraction_create_missing_name(self):
        # ошибка при отсутствии обязательного поля name
        with pytest.raises(ValidationError):
            AttractionCreate(description="Описание", latitude=56.0, longitude=90.0)

    def test_attraction_invalid_coordinates(self):
        # ошибка при невалидных координатах (должны быть числами)
        with pytest.raises(ValidationError):
            AttractionCreate(name="Парк", latitude="invalid", longitude=90.0)


class TestFoodSchemas:
    # тесты для валидации схем заведений питания
    def test_food_create_valid(self):
        # создание валидной схемы заведения
        data = {"name": "Кафе Тест", "address": "ул. Тестовая, 1"}
        food = FoodCreate(**data)
        assert food.name == "Кафе Тест"
        assert food.address == "ул. Тестовая, 1"

    def test_food_create_missing_address(self):
        # проверка поведения при отсутствии адреса (если поле обязательное)
        data = {"name": "Кафе Тест"}
        food = FoodCreate(**data)
        assert food.name == "Кафе Тест"


class TestEventSchemas:
    # тесты для валидации схем событий
    def test_event_create_valid(self):
        # создание валидной схемы события с датой
        event_date = datetime.now()
        data = {
            "title": "Тестовое событие",
            "description": "Описание",
            "location": "Ачинск",
            "event_date": event_date,
        }
        event = EventCreate(**data)
        assert event.title == "Тестовое событие"
        assert event.event_date == event_date

    def test_event_create_missing_title(self):
        # ошибка при отсутствии названия события
        with pytest.raises(ValidationError):
            EventCreate(
                description="Описание", location="Ачинск", event_date=datetime.now()
            )


from datetime import datetime

from schemas import SafetyMemoResponse, UserResponse


class TestUserResponseSchema:
    """Покрывает сериализацию UserResponse (использует устаревший class Config)"""

    def test_user_response_from_dict(self):
        payload = {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "photo_url": None,
            "role": "admin",
            "is_approved": True,
            "is_active": True,
            "created_at": datetime.now(),
        }
        user = UserResponse(**payload)
        dumped = user.model_dump()
        assert dumped["username"] == "test_user"
        assert "id" in dumped

    def test_user_response_model_validate(self):
        """Проверяет работу from_attributes на mock-объекте"""

        class MockUser:
            id = 5
            username = "mock"
            email = "m@m.com"
            photo_url = None
            role = "user"
            is_approved = False
            is_active = True
            created_at = datetime.now()

        user = UserResponse.model_validate(MockUser())
        assert user.username == "mock"
        assert user.role == "user"


class TestSafetyMemoResponseSchema:
    """Покрывает сериализацию SafetyMemoResponse (использует устаревший class Config)"""

    def test_safety_memo_response_serialization(self):
        payload = {
            "id": 10,
            "title": "Памятка №1",
            "content": "Текст",
            "order": 2,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        memo = SafetyMemoResponse(**payload)
        dumped = memo.model_dump()
        assert dumped["title"] == "Памятка №1"
        assert dumped["order"] == 2
