import requests
import time
from config import URL

def delete_user(token):
    """Удаляет пользователя по токену"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{URL}/profile", headers=headers)
    if response.status_code != 204:
        print(f"⚠️ Ошибка при удалении пользователя: {response.status_code} - {response.text}")

def test_registration_success():
    """Тест успешной регистрации пользователя"""
    print("=== Тест 1.1: Успешная регистрация ===")
    email = f"testuser_{int(time.time())}@example.com"
    data = {
        "first_name": "TestUser",
        "password": "TestPass123!",
        "email": email
    }
    response = requests.post(f"{URL}/reg", json=data)
    try:
        assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
        assert "token" in response.json(), "Токен не найден в ответе"
        print("✅ Тест 1.1 пройден успешно")
    finally:
        token = response.json().get("token")
        if token:
            delete_user(token)

def test_registration_missing_fields():
    """Тест регистрации с отсутствующими обязательными полями"""
    print("=== Тест 1.2: Регистрация без обязательных полей ===")
    data = {
        "first_name": "TestUser",
        "email": "incomplete@example.com"
    }
    response = requests.post(f"{URL}/reg", json=data)
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    errors = response.json()["errors"]
    assert any(e["name"] == "password" for e in errors), "Не обнаружена ошибка для password"
    print("✅ Тест 1.2 пройден успешно")

def test_registration_duplicate_email():
    """Тест регистрации с уже существующей почтой"""
    print("=== Тест 1.3: Регистрация с существующей почтой ===")
    email = f"duplicate_{int(time.time())}@example.com"
    data = {
        "first_name": "User1",
        "password": "Pass123!",
        "email": email
    }
    # Создаем первого пользователя
    response1 = requests.post(f"{URL}/reg", json=data)
    try:
        assert response1.status_code == 201, "Первая регистрация должна пройти успешно"
        token1 = response1.json()["token"]
        
        # Пытаемся создать дубликата
        response2 = requests.post(f"{URL}/reg", json=data)
        assert response2.status_code == 409, f"Ожидался статус 409, получен {response2.status_code}"
        print("✅ Тест 1.3 пройден успешно")
    finally:
        if 'token1' in locals():
            delete_user(token1)

def test_registration_invalid_email():
    """Тест регистрации с невалидным email"""
    print("=== Тест 1.4: Регистрация с невалидной почтой ===")
    data = {
        "first_name": "InvalidUser",
        "password": "Pass123!",
        "email": "invalid-email"
    }
    response = requests.post(f"{URL}/reg", json=data)
    assert response.status_code == 422, f"Ожидался статус 422, получен {response.status_code}"
    print("✅ Тест 1.4 пройден успешно")

def test_login_success():
    """Тест успешной авторизации"""
    print("=== Тест 2.1: Успешная авторизация ===")
    email = f"loginuser_{int(time.time())}@example.com"
    password = "LoginPass123!"
    # Регистрация пользователя
    reg_data = {
        "first_name": "LoginUser",
        "password": password,
        "email": email
    }
    reg_response = requests.post(f"{URL}/reg", json=reg_data)
    try:
        assert reg_response.status_code == 201, "Регистрация должна пройти успешно"
        token_reg = reg_response.json()["token"]
        
        # Авторизация
        auth_data = {
            "identifier": email,
            "password": password
        }
        response = requests.post(f"{URL}/auth", json=auth_data)
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        assert "token" in response.json(), "Токен не найден в ответе"
        print("✅ Тест 2.1 пройден успешно")
        return response.json()["token"]
    finally:
        if 'token_reg' in locals():
            delete_user(token_reg)

def test_login_invalid_credentials():
    """Тест авторизации с неверными данными"""
    print("=== Тест 2.2: Авторизация с неверными данными ===")
    auth_data = {
        "identifier": "nonexistent@example.com",
        "password": "wrongpass"
    }
    response = requests.post(f"{URL}/auth", json=auth_data)
    assert response.status_code == 401, f"Ожидался статус 401, получен {response.status_code}"
    print("✅ Тест 2.2 пройден успешно")

def test_login_missing_params():
    """Тест авторизации без обязательных параметров"""
    print("=== Тест 2.3: Авторизация без обязательных параметров ===")
    response = requests.post(f"{URL}/auth", json={})
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    errors = response.json()["errors"]
    assert len(errors) == 2, "Ожидались ошибки для identifier и password"
    print("✅ Тест 2.3 пройден успешно")

def get_auth_token():
    """Вспомогательная функция для получения токена"""
    email = "test_user@example.com"
    password = "TestPass123!"
    
    # Попытка авторизации существующего пользователя
    auth_data = {
        "identifier": email,
        "password": password
    }
    response = requests.post(f"{URL}/auth", json=auth_data)
    if response.status_code == 200:
        return response.json()["token"]
    
    # Если пользователь не существует - регистрируем
    reg_data = {
        "first_name": "TestUser",
        "password": password,
        "email": email
    }
    reg_response = requests.post(f"{URL}/reg", json=reg_data)
    reg_response.raise_for_status()
    return reg_response.json()["token"]

def run_auth_tests():
    """Запуск всех тестов авторизации и возврат токена"""
    print("=== ТЕСТИРОВАНИЕ ЭНДПОИНТОВ АВТОРИЗАЦИИ ===\n")
    
    print("Группа 1: Тесты регистрации")
    test_registration_success()
    test_registration_missing_fields()
    test_registration_duplicate_email()
    test_registration_invalid_email()
    
    print("\nГруппа 2: Тесты авторизации")
    test_login_success()
    test_login_invalid_credentials()
    test_login_missing_params()
    
    print("\n✅ ВСЕ ТЕСТЫ АВТОРИЗАЦИИ ПРОЙДЕНЫ УСПЕШНО")
    
    # Получение токена для последующих тестов
    token = get_auth_token()
    print(f"\nToken for other tests: {token}")
    return token