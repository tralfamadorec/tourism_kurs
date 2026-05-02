from slowapi import Limiter
from slowapi.util import get_remote_address

# создаём экземпляр лимитера
limiter = Limiter(key_func=get_remote_address)