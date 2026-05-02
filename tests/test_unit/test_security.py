import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from security import (create_access_token, get_current_user, get_password_hash,
                      verify_password)


class TestPasswordHashing:
    """Тесты для проверки хеширования и верификации паролей"""

    def test_hash_password_not_plaintext(self):
        password = "SecureTestPassword123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password_success(self):
        password = "MyPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        password = "MyPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokenSecurity:
    """Тесты для проверки создания и декодирования JWT-токенов"""

    def test_create_and_decode_token(self):
        test_data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data=test_data)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_token_contains_expiry(self):
        test_data = {"sub": "user"}
        token = create_access_token(data=test_data)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()

    def test_decode_invalid_token(self):
        with pytest.raises(JWTError):
            jwt.decode(
                "invalid.token.string",
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

    def test_decode_token_with_wrong_secret(self):
        test_data = {"sub": "user"}
        token = create_access_token(data=test_data)
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret_key_12345", algorithms=[settings.ALGORITHM])

    def test_decode_token_with_wrong_algorithm(self):
        test_data = {"sub": "user"}
        token = create_access_token(data=test_data)
        with pytest.raises(JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["RS256"])


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Тесты зависимости get_current_user с проверкой логирования и веток ошибок"""

    async def test_invalid_token_logs_warning_and_raises_401(self, caplog):
        caplog.set_level(logging.WARNING)
        mock_db = AsyncMock(spec=AsyncSession)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid.token.here", db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        # Проверяем, что ветка try/except выполнилась и записала лог
        assert "JWT" in caplog.text or "Ошибка" in caplog.text

    async def test_valid_token_user_not_found_logs_warning_and_raises_401(self, caplog):
        caplog.set_level(logging.WARNING)
        # Создаём валидный токен для несуществующего пользователя
        token = create_access_token(data={"sub": "ghost_user"})

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "не найден" in caplog.text.lower()

    async def test_user_inactive_raises_403(self, caplog):
        caplog.set_level(logging.WARNING)
        token = create_access_token(data={"sub": "inactive_user"})

        mock_user = MagicMock()
        mock_user.username = "inactive_user"
        mock_user.is_active = False
        mock_user.is_approved = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Учётная запись заблокирована"

    async def test_user_not_approved_raises_403(self, caplog):
        caplog.set_level(logging.WARNING)
        token = create_access_token(data={"sub": "pending_user"})

        mock_user = MagicMock()
        mock_user.username = "pending_user"
        mock_user.is_active = True
        mock_user.is_approved = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Учётная запись ожидает подтверждения"


# tests/test_unit/test_security.py — вариант без класса
@pytest.mark.asyncio
async def test_require_role_allows_admin():
    """Проверяет, что require_role пропускает пользователя с нужной ролью"""
    from unittest.mock import MagicMock

    from security import require_role

    mock_user = MagicMock()
    mock_user.role = "admin"

    checker = require_role("admin", "super_admin")
    result = checker(current_user=mock_user)
    assert result == mock_user


@pytest.mark.asyncio
async def test_require_role_denies_user():
    """Проверяет, что require_role отклоняет пользователя без нужной роли"""
    from unittest.mock import MagicMock

    from fastapi import HTTPException

    from security import require_role

    mock_user = MagicMock()
    mock_user.role = "user"

    checker = require_role("admin", "super_admin")
    with pytest.raises(HTTPException) as exc_info:
        checker(current_user=mock_user)
    assert exc_info.value.status_code == 403
