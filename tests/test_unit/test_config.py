import pytest

from config import settings


def test_config_exists():
    # проверка наличия объекта конфигурации
    assert settings is not None


def test_database_url_is_configured():
    # проверка наличия и корректности URL базы данных
    assert settings.DATABASE_URL is not None
    assert "postgresql" in settings.DATABASE_URL.lower()


def test_secret_key_is_secure():
    # проверка наличия и длины секретного ключа (минимум 10 символов)
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) >= 10


def test_jwt_algorithm_is_hs256():
    # проверка используемого алгоритма для JWT
    assert settings.ALGORITHM == "HS256"


def test_token_expiration_is_configured():
    # проверка наличия времени жизни токена (вместо отсутствующего ALLOWED_ORIGINS)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES is not None
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_yandex_api_key_exists():
    # проверка наличия ключа API Яндекс.Карт
    assert settings.YANDEX_MAPS_API_KEY is not None
    assert isinstance(settings.YANDEX_MAPS_API_KEY, str)
