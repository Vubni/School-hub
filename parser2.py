import pandas as pd
from database.database import Database
import asyncio

async def export_users_to_excel(db: Database, filename: str = "users.xlsx"):
    """
    Экспортирует данные пользователей в Excel с разделением по классам
    """
    # Получаем все данные из таблицы users (без переименования в SQL)
    users = await db.execute_all("""
        SELECT name, surname, login, password, class_number, class_letter 
        FROM users 
        ORDER BY class_number, class_letter
    """)

    if not users:
        print("Не найдено пользователей для экспорта")
        return False

    # Создаем DataFrame из всех пользователей
    df = pd.DataFrame(users)
    
    # Переименовываем столбцы на русский язык
    df = df.rename(columns={
        'name': 'Имя',
        'surname': 'Фамилия',
        'login': 'Логин',
        'password': 'Пароль',
        'class_number': 'Класс',
        'class_letter': 'Буква'
    })
    
    # Создаем Excel-файл
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Группируем по классу и записываем каждый класс на отдельный лист
        nmb = 0
        for (class_num, class_letter), group in df.groupby(['Класс', 'Буква']):
            class_str = f"{class_num}{class_letter}"
            nmb += 1
            # Записываем данные на лист
            group.to_excel(
                writer,
                sheet_name=class_str,
                index=False
            )
        print(nmb)

    print(f"Данные успешно экспортированы в файл {filename}")
    return True

async def main():
    db = Database()
    async with db:
        await export_users_to_excel(db, "users1.xlsx")

asyncio.run(main())