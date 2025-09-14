import re
import asyncio
from openpyxl import load_workbook
from datetime import time
from database.database import Database  # Импортируйте ваш класс Database

async def parse_excel_and_save_to_db(file_path: str):
    # Загрузка workbook
    wb = load_workbook(filename=file_path, data_only=True)
    sheet = wb['Временное с 8-13 сентября ']
    
    # Загрузка списка всех возможных предметов из листа "pred"
    pred_sheet = wb['pred']
    subjects = set()
    for row in range(1, pred_sheet.max_row + 1):
        subject = pred_sheet.cell(row=row, column=1).value
        if subject:
            subjects.add(str(subject).strip())
    
    # Словарь для преобразования дней недели в числовой формат
    days_map = {
        'ПОНЕДЕЛЬНИК': 1,
        'ВТОРНИК': 2,
        'СРЕДА': 3,
        'ЧЕТВЕРГ': 4,
        'ПЯТНИЦА': 5,
        'СУББОТА': 6
    }
    
    current_day = None
    lessons_data = []
    processed_lessons = set()  # Для отслеживания уже обработанных уроков
    
    # Сначала соберем информацию о классах и их колонках
    class_columns = {}
    for col in range(3, sheet.max_column + 1, 2):
        class_name = sheet.cell(row=3, column=col).value
        if class_name and class_name not in ['№', 'Каб/Предмет']:
            # Извлекаем номер и букву класса
            match = re.match(r'(\d+)([А-Я]+)', str(class_name))
            if match:
                class_number = int(match.group(1))
                class_letter = match.group(2)
                class_columns[col] = (class_number, class_letter)
    
    # Проходим по всем строкам в листе
    for row in range(1, sheet.max_row + 1):
        # Проверяем ячейку в колонке A на наличие названия дня
        day_cell = sheet.cell(row=row, column=1).value
        if day_cell and day_cell in days_map:
            current_day = days_map[day_cell]
            continue
        
        if not current_day:
            continue
        
        # Получаем время из колонки B
        time_value = sheet.cell(row=row, column=2).value
        if not time_value:
            continue
        
        # Обрабатываем все классы
        for col, (class_number, class_letter) in class_columns.items():
            # Получаем номер урока
            lesson_number_cell = sheet.cell(row=row, column=col).value
            
            # Пропускаем если нет номера урока или это не число
            if not lesson_number_cell or not isinstance(lesson_number_cell, (int, float)):
                continue
            
            lesson_number = int(lesson_number_cell)
            
            # Создаем уникальный идентификатор урока
            lesson_id = f"{class_number}_{class_letter}_{current_day}_{lesson_number}"
            
            # Пропускаем если уже обработали этот урок
            if lesson_id in processed_lessons:
                continue
            
            # Пытаемся найти предмет в разных местах
            title = None
            
            # 1. Попробуем найти в следующей колонке той же строки
            title_cell = sheet.cell(row=row, column=col + 1).value
            if title_cell and any(subject in str(title_cell) for subject in subjects):
                title = str(title_cell).strip()
            
            # 2. Если не нашли, попробуем в следующей строке, той же колонки+1
            if not title and row + 1 <= sheet.max_row:
                title_cell = sheet.cell(row=row + 1, column=col + 1).value
                if title_cell and any(subject in str(title_cell) for subject in subjects):
                    title = str(title_cell).strip()
            
            # 3. Если все еще не нашли, попробуем в строке ниже, но той же колонки
            if not title and row + 1 <= sheet.max_row:
                title_cell = sheet.cell(row=row + 1, column=col).value
                if title_cell and any(subject in str(title_cell) for subject in subjects):
                    title = str(title_cell).strip()
            
            # 4. Если все еще не нашли, попробуем в строке выше, следующей колонки
            if not title and row - 1 >= 1:
                title_cell = sheet.cell(row=row - 1, column=col + 1).value
                if title_cell and any(subject in str(title_cell) for subject in subjects):
                    title = str(title_cell).strip()
            
            # Пропускаем если не нашли название предмета
            if not title:
                continue
            
            # Добавляем данные урока
            lessons_data.append((
                class_number,
                class_letter,
                current_day,
                title,
                lesson_number
            ))
            
            # Помечаем урок как обработанный
            processed_lessons.add(lesson_id)
    
    # Сохранение в базу данных
    async with Database() as db:
        await db.execute("DELETE FROM lessons")
        insert_sql = """
            INSERT INTO lessons (class_number, class_letter, day_number, title, lesson_number)
            VALUES ($1, $2, $3, $4, $5)"""
        
        await db.executemany(insert_sql, lessons_data)

# Запуск парсинга
async def main():
    await parse_excel_and_save_to_db('Временное расписание уроков 2025-2026.xlsx')

if __name__ == '__main__':
    asyncio.run(main())