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
    password: str
    
class Schedule_get(BaseModel):
    date: date
    