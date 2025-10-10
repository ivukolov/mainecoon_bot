import datetime as dt
from logging import getLogger

from jose import JWTError, jwt
import jose.exceptions as jose_exec
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from config import settings
from database import User
from utils.cache import RedisCache

logger = getLogger(__name__)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> (bool, dict):
        session: AsyncSession = request.state.db
        redis_cash: RedisCache = request.state.cash
        context = {}
        form = await request.form()
        username, password = form["username"], form["password"]
        context["error"] = "Неверный логин или пароль!"
        if await self.is_brootforce(redis_cash=redis_cash, username=username):
            context["error"] = "Превышено число попыток авторизации"
        user: User = await User.one_or_none(session, username=username)
        if user and user.authenticate_user(password):
            access_token = self.generate_jwt_token(str(user.id))
            request.session.update({"token": access_token})
            return True
        logger.warning(f"Неудачная попытка войти в админ панель - пользователь: {username} ")
        return False, context

    async def is_brootforce(self, redis_cash: RedisCache, username: str) -> bool:
        key = 'failed_attempts'
        user_attempts_dict = await redis_cash.get_json(username)
        if user_attempts_dict:
            failed_attempts: int = user_attempts_dict.get(key)
            if failed_attempts >= settings.MAX_FAILED_ATTEMPTS:
                logger.error(f'Превышено число попыток авторизации пользователя {username}')
                return True
            else:
                failed_attempts+=1
                await redis_cash.set_json(username, {key: failed_attempts}, ttl=settings.USER_BLOCK_TIMEOUT)
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        session: AsyncSession = request.state.db
        token = request.session.get("token")
        if not token:
            return False
        payload = self.encode_jwt_token(token)
        if payload:
            user_id = payload.get("sub")
            try:
                user_id = int(user_id)
            except Exception:
                logger.error(f"Ошибка преобразования {user_id=} в int во время аутентификации пользователя")
                return False
            else:
                user: User | None = await User.one_or_none(session=session, id=int(user_id))
                if user:
                    return True
        return False

    def generate_jwt_token(self, user_id: str) -> str:
        """
        Генерирует JWT токен для реферальной ссылки
        """
        payload = {
            'sub': user_id,
            'exp': (dt.datetime.now(dt.UTC) + dt.timedelta(hours=settings.JWT_EXPIRES_HOURS)).timestamp(),
            'iat': dt.datetime.now(dt.UTC).timestamp(),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def encode_jwt_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jose_exec.ExpiredSignatureError as e:
            logger.info(f"Срок жизни токена истек {e}")
        except jose_exec.JWSAlgorithmError as e:
            logger.warning(f"Ошибка расшифровки токена! {e}")
        except jose_exec.JWTClaimsError as e:
            logger.error(f"Ошибка содержания токена {e}")
        except JWTError as e:
            print(f"Неопознанная ошибка при расшифровывании JWT токена: {e}")
        else:
            return payload
        return None