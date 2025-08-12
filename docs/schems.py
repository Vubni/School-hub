from marshmallow import Schema, fields

class TokenResponseSchema(Schema):
    token = fields.Str(description="Токен для взаимодействия с аккаунтом")

class UserAuthSchema(Schema):
    identifier = fields.Str(required=True)
    password = fields.Str(required=True)
    
class UserProfileSchema(Schema):
    login = fields.Str()
    email = fields.Str()
    name = fields.Str()
    surname = fields.Str()
    class_number = fields.Int()
    class_letter = fields.Str()
    telegram_name = fields.Str()
    
class LoginEditSchema(Schema):
    login = fields.Str(required=True, description="login пользователя. До 20 символов")
    
class EmailEditSchema(Schema):
    email = fields.Str(required=True, description="email пользователя. До 256 символов")
    
class PasswordEditSchema(Schema):
    password = fields.Str(required=True, description="password пользователя.")
    
class TelegramConnectSchema(Schema):
    url = fields.Str(required=True, description="Ссылка для привязки аккаунта Telegram.")
    

class ScheduleGetSchema(Schema):
    date = fields.Date(required=True, description="Дата на которую получают расписание.")
    
class ClubsListSchema(Schema):
    type = fields.Str(default="my")
    offset = fields.Int(default=0)
    limit = fields.Int(default=100)
    
class ClubGetSchema(Schema):
    club_id = fields.Int(required=True, description="id клуба")
    
class ClubNewSchema(Schema):
    title = fields.Str(required=True, description="Название клуба. До 20 символов")
    description = fields.Str(required=True, description="Описание клуба. До 200 символов")
    administration = fields.Int(required=True, description="Направление клуба (ответственное министерство)")
    max_members_counts = fields.Int(required=True, description="Максимальное количество участников клуба", default=0)
    class_limit_min = fields.Int(required=True, description="Минимальный класс для участия в клубе", default=1)
    class_limit_max = fields.Int(required=True, description="Максимальный класс для участия в клубе", default=11)
    telegram_url = fields.Str(required=True, description="URL телеграм-канала клуба")
    
class CheckTitleSchema(Schema):
    title = fields.Str(required=True, description="Название клуба")
    
class AdministrationListSchema(Schema):
    id = fields.Int()
    title = fields.Str()

class ScheduleItemSchema(Schema):
    start_time = fields.Str(required=True, description="Время начала урока в формате ЧЧ:ММ")
    stop_time = fields.Str(required=True, description="Время окончания урока в формате ЧЧ:ММ")
    lesson_number = fields.Int(required=True, description="Порядковый номер урока")
    title = fields.Str(
        required=False, 
        allow_none=True, 
        description="Название урока (присутствует только если урок запланирован)"
    )
    classrooms = fields.List(
        fields.Raw(), 
        required=False, 
        allow_none=True, 
        description="Список кабинетов (строки/числа) или None"
    )
    teachers = fields.List(
        fields.Str(), 
        required=False, 
        allow_none=True, 
        description="Список преподавателей (строки) или None"
    )
    
class ClubSchema(Schema):
    id = fields.Int(required=True, description="ID клуба")
    title = fields.Str(required=True, description="Название клуба")
    members_count = fields.Int(required=True, description="Количество участников клуба")
    max_members_counts = fields.Int(required=True, description="Максимальное количество участников клуба")
    class_limit_min = fields.Int(required=True, description="Минимальный класс для участия в клубе")
    class_limit_max = fields.Int(required=True, description="Максимальный класс для участия в клубе")
    
    
class ClubGetReturnSchema(Schema):
    id = fields.Int(required=True, description="ID клуба")
    title = fields.Str(required=True, description="Название клуба")
    description = fields.Str(required=True, description="Описание клуба")
    telegram_url = fields.Str(required=True, description="Ссылка на Telegram-канал/группу клуба")
    xp = fields.Int(required=True, description="Текущий опыт клуба")
    members_count = fields.Int(required=True, description="Количество участников клуба")
    max_members_counts = fields.Int(required=True, description="Максимальное количество участников клуба")
    administration = fields.Int(required=True, description="Направление клуба (ответственное министерство)")
    class_limit_min = fields.Int(required=True, description="Минимальный класс для участия в клубе")
    class_limit_max = fields.Int(required=True, description="Максимальный класс для участия в клубе")
    participant = fields.Bool(required=True, description="Является ли пользователь участником клуба")
    admin = fields.Bool(required=True, description="Является ли пользователь администратором клубa")

    
class ClubJoinSchema(Schema):
    club_id = fields.Int(required=True, description="id клуба")

class AchievementsLocalSchema(Schema):
    club_id = fields.Int(required=True, description="id клуба")

class ClubEditSchema(Schema):
    club_id = fields.Int(required=True, description="id клуба")
    title = fields.Str(required=True, description="Название клуба")
    description = fields.Str(required=True, description="Описание клуба")
    max_members_counts = fields.Int(required=True, description="Максимальное количество участников в клубе")
    class_limit_min = fields.Int(required=True, description="Минимальный класс для участия в клубе")
    class_limit_max = fields.Int(required=True, description="Максимальный класс для участия в клубе")
    telegram_url = fields.Str(required=True, description="Telegram ссылка на канал/группу клуба")
    

class AchievementsGlobalReturnSchema(Schema):
    title = fields.Str(description="Название достижения")
    description = fields.Str(description="Описание достижения")
    xp = fields.Str(description="Текущий набранный опыт")
    need_xp = fields.Str(description="Необходимый опыт")


    
class ErrorDetailSchema(Schema):
    """Схема для детального описания одной ошибки."""
    name = fields.Str(description="Имя параметра, вызвавшего ошибку")
    type = fields.Str(description="Тип ошибки (например, missing)")
    message = fields.Str(description="Сообщение об ошибке")
    value = fields.Raw(description="Значение параметра, если оно было передано", allow_none=True)

class Error400Schema(Schema):
    """Основная схема ответа с ошибками."""
    error = fields.Str(description="Общее сообщение об ошибке")
    errors = fields.List(fields.Nested(ErrorDetailSchema), description="Список детальных ошибок")
    received_params = fields.Dict(description="Параметры, которые были успешно получены")
    
class AlreadyBeenTaken(Schema):
    name = fields.Str(description="Название переменной, которая занята")
    error = fields.Str(description="Описание, что переменная занята")