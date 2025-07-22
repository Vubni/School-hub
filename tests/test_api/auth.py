import requests
import time
from config import URL

def delete_user(token):
    """Удаляет пользователя по токену"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{URL}/profile", headers=headers)
    if response.status_code != 204:
        print(f"⚠️ Ошибка при удалении пользователя: {response.status_code} - {response.text}")

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

def run_auth_tests():
    """Запуск всех тестов авторизации и возврат токена"""
    print("=== ТЕСТИРОВАНИЕ ЭНДПОИНТОВ АВТОРИЗАЦИИ ===\n")
    
    print("\nГруппа 2: Тесты авторизации")
    test_login_invalid_credentials()
    test_login_missing_params()
    
    print("\n✅ ВСЕ ТЕСТЫ АВТОРИЗАЦИИ ПРОЙДЕНЫ УСПЕШНО")
    
    # Получение токена для последующих тестов
    token = get_auth_token()
    print(f"\nToken for other tests: {token}")
    return token