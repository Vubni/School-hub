from typing import Callable, Optional, TypeVar, Awaitable, Dict, Any
from functools import wraps
from pydantic import BaseModel, ValidationError
import json
from aiohttp import web
from pydantic import field_validator, model_validator
import core
from datetime import date

T = TypeVar("T", bound=BaseModel)

class EmailError(Exception):
    def __init__(self, message="Ошибка проверки email", errors=None):
        self.message = message
        self.errors = errors or []  # Добавляем атрибут errors
        super().__init__(self.message)

def validate(model: type[T]) -> Callable:
    def decorator(handler: Callable[[web.Request, Any], Awaitable[web.Response]]):
        @wraps(handler)
        async def wrapper(request: web.Request) -> web.Response:
            try:
                data = await request.json()
            except json.JSONDecodeError:
                data = {}

            all_data = dict(request.query)
            all_data.update(data)

            try:
                parsed = model(**all_data)
            except ValidationError as e:
                errors = [
                    {
                        "name": error["loc"][-1] if error["loc"] else "general",  # Проверяем, есть ли элементы в loc
                        "type": error["type"],
                        "message": error["msg"],
                        "value": all_data.get(error["loc"][-1] if error["loc"] else None),  # Аналогично проверяем loc
                    }
                    for error in e.errors()
                ]
                return web.json_response({
                    "error": "Validation failed",
                    "errors": errors,
                    "received_params": all_data,
                }, status=400)
            except EmailError as e:
                errors = [
                    {
                        "name": "email",
                        "type": "email_validation",
                        "message": e.message,
                        "value": all_data.get("email"),
                    }
                ]
                return web.json_response({
                    "error": "Email validation failed",
                    "errors": errors,
                    "received_params": all_data,
                }, status=422)

            return await handler(request, parsed)
        return wrapper
    return decorator


    
class Auth(BaseModel):
    identifier: str
    password : str
    
    @field_validator('identifier')
    def check_identifier(cls, v):
        if len(v) > 256:
            raise ValueError('Identifier cannot exceed 256 characters')
        return v
    

class Auth_telegram(BaseModel):
    token: str

    
class Login_patch(BaseModel):
    login: str
    
    @field_validator('login')
    def check_email(cls, v):
        if len(v) > 20:
            raise ValueError('Login cannot exceed 20 characters')
        return v
    
class Email_patch(BaseModel):
    email: str
    
    @field_validator('email')
    def check_email(cls, v):
        if len(v) > 256:
            raise ValueError('Email cannot exceed 256 characters')
        if not core.is_valid_email(v):
            raise EmailError('Email does not comply with email standards or dns mail servers are not found')
        return v
    
class Password_patch(BaseModel):
    password_old: str
    password_new: str
    
class Schedule_get(BaseModel):
    date: str
    
class Clubs_list(BaseModel):
    type: str = "my"
    offset: int = 0
    limit: int = 100
    
class Club_info(BaseModel):
    club_id: int
    
class Club_new(BaseModel):
    title: str
    description: str
    administration: int
    max_members_counts: Optional[int] = 0
    class_limit_min: Optional[int] = 1
    class_limit_max: Optional[int] = 11
    telegram_url: Optional[str] = None  # Явно указываем Optional
    
    @field_validator('class_limit_max')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 1 <= v <= 11:
            return v
        raise ValueError("class_limit_max in 1-11")
    
    @field_validator('class_limit_min')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 1 <= v <= 11:
            return v
        raise ValueError("class_limit_min in 1-11")
    
    @field_validator('max_members_counts')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 0 < v < 4:
            return v
        raise ValueError("max_members_counts is 4+ or 0")
        

    @field_validator('telegram_url')
    def validate_telegram_url(cls, v):
        # Если значение не указано - пропускаем проверку
        if v is None:
            return v
        
        # Проверяем, что ссылка начинается с допустимых префиксов
        valid_prefixes = (
            "https://t.me/", 
            "http://t.me/",
            "https://telegram.me/",
            "http://telegram.me/"
        )
        
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                "Telegram URL must start with: "
                "https://t.me/, http://t.me/, "
                "https://telegram.me/ or http://telegram.me/"
            )
        
        # Дополнительная проверка на минимальную длину
        if len(v) < 15:
            raise ValueError("Telegram URL is too short")
            
        return v
    
class Check_title(BaseModel):
    title: str
    
class Club_join(BaseModel):
    club_id: int

class Club_delete(BaseModel):
    club_id: int

class Achievements_local(BaseModel):
    club_id: int

class Club_edit(BaseModel):
    club_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    max_members_counts: Optional[int] = None
    class_limit_min: Optional[int] = None
    class_limit_max: Optional[int] = None
    telegram_url: Optional[str] = None

    @field_validator('class_limit_max')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 1 <= v <= 11:
            return v
        raise ValueError("class_limit_max in 1-11")
    
    @field_validator('class_limit_min')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 1 <= v <= 11:
            return v
        raise ValueError("class_limit_min in 1-11")
    
    @field_validator('max_members_counts')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        if 0 < v < 4:
            return v
        raise ValueError("max_members_counts is 4+ or 0")
        

    @field_validator('telegram_url')
    def validate_telegram_url(cls, v):
        if v is None:
            return v
        
        # Проверяем, что ссылка начинается с допустимых префиксов
        valid_prefixes = (
            "https://t.me/", 
            "http://t.me/",
            "https://telegram.me/",
            "http://telegram.me/"
        )
        
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                "Telegram URL must start with: "
                "https://t.me/, http://t.me/, "
                "https://telegram.me/ or http://telegram.me/"
            )
        
        # Дополнительная проверка на минимальную длину
        if len(v) < 15:
            raise ValueError("Telegram URL is too short")
            
        return v
    
class Forgot_password(BaseModel):
    identifier: str
    new_password: str
    
class Forgot_password_confirm(BaseModel):
    confirm: int
    
class Email_verify_confirm(BaseModel):
    token: str