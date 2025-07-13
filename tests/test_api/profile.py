import requests
from config import URL

def test_profile_get_initial_verified_false(token):
    """Тест получения профиля с verified=False"""
    print("=== Тест 1: Проверка verified=False при первом получении профиля ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(URL + "/profile", headers=headers)
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    
    profile = response.json()
    assert "verified" in profile, "Поле 'verified' отсутствует в ответе"
    assert profile["verified"] is False, "Поле 'verified' должно быть False при первом получении профиля"
    print("✅ Тест 1 пройден успешно")


def test_profile_verification_email_success(token):
    """Тест успешной отправки токена для верификации email"""
    print("=== Тест 2: Успешная отправка токена для верификации ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"token": "valid_token"}  # Замените на актуальный токен верификации
    response = requests.post(URL + "/email", json=data, headers=headers)
    assert response.status_code == 204, f"Ожидался статус 204, получен {response.status_code}"
    
    # Проверка, что verified=True после верификации
    response = requests.get(URL + "/profile", headers=headers)
    profile = response.json()
    assert profile["verified"] is True, "Поле 'verified' должно стать True после успешной верификации"
    print("✅ Тест 2 пройден успешно")


def test_profile_verification_email_invalid_token(token):
    """Тест отправки невалидного токена для верификации email"""
    print("=== Тест 3: Отправка невалидного токена для верификации ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"token": "invalid_token"}
    response = requests.post(URL + "/email", json=data, headers=headers)
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    assert response.json()["errors"][0]["name"] == "token", "Неверное сообщение об ошибке"
    print("✅ Тест 3 пройден успешно")


def test_profile_verification_email_missing_token(token):
    """Тест отправки запроса без токена для верификации email"""
    print("=== Тест 4: Отправка запроса без токена для верификации ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(URL + "/email", headers=headers)
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    assert response.json()["errors"][0]["name"] == "token", "Неверное сообщение об ошибке"
    print("✅ Тест 4 пройден успешно")


def test_profile_get_success(token):
    """Тест успешного получения профиля"""
    print("=== Тест 5: Получение профиля с валидным токеном ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(URL + "/profile", headers=headers)
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    
    profile = response.json()
    assert "first_name" in profile
    assert "email" in profile
    print("✅ Тест 5 пройден успешно")


def test_profile_get_unauthorized():
    """Тест получения профиля без авторизации"""
    print("=== Тест 6: Получение профиля без токена ===")
    response = requests.get(URL + "/profile")
    assert response.status_code == 401, f"Ожидался статус 401, получен {response.status_code}"
    print("✅ Тест 6 пройден успешно")


def test_profile_patch_update_fields(token):
    """Тест обновления профиля с корректными данными"""
    print("=== Тест 7: Обновление полей профиля ===")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "first_name": "Новое имя",
        "email": "new@example.com"
    }
    response = requests.patch(URL + "/profile", json=update_data, headers=headers)
    assert response.status_code == 204, f"Ожидался статус 204, получен {response.status_code}"
    
    # Проверка сохранения изменений
    response = requests.get(URL + "/profile", headers=headers)
    profile = response.json()
    assert profile["first_name"] == "Новое имя"
    assert profile["email"] == "new@example.com"
    print("✅ Тест 7 пройден успешно")


def test_profile_patch_invalid_email(token):
    """Тест обновления профиля с невалидным email"""
    print("=== Тест 8: Невалидный email ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"email": "invalid-email"}
    response = requests.patch(URL + "/profile", json=data, headers=headers)
    assert response.status_code == 422, f"Ожидался статус 422, получен {response.status_code}"
    assert response.json()['errors'][0]['name'] == 'email', "Неверное сообщение об ошибке"
    print("✅ Тест 8 пройден успешно")


def test_profile_patch_missing_old_password(token):
    """Тест смены пароля без указания старого пароля"""
    print("=== Тест 9: Смена пароля без старого пароля ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"password_new": "new_pass123"}
    response = requests.patch(URL + "/profile", json=data, headers=headers)
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    assert response.json()['errors'][0]['name'] == 'general', "Неверное сообщение об ошибке"
    print("✅ Тест 9 пройден успешно")


def test_profile_patch_password_change(token):
    """Тест успешной смены пароля"""
    print("=== Тест 10: Успешная смена пароля ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "password_old": "TestPass123!",
        "password_new": "new_secure_pass123"
    }
    response = requests.patch(URL + "/profile", json=data, headers=headers)
    assert response.status_code == 204, f"Ожидался статус 204, получен {response.status_code}"
    print("✅ Тест 10 пройден успешно")


def test_profile_patch_invalid_json(token):
    """Тест отправки невалидного JSON"""
    print("=== Тест 11: Невалидный JSON ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    invalid_json = '{"first_name": "Ошибка"'
    response = requests.patch(URL + "/profile", data=invalid_json, headers=headers)
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    print("✅ Тест 11 пройден успешно")


def test_profile_delete_success(token):
    """Тест успешного удаления профиля"""
    print("=== Тест 12: Удаление профиля ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(URL + "/profile", headers=headers)
    assert response.status_code == 204, f"Ожидался статус 204, получен {response.status_code}"
    
    # Проверка недоступности профиля после удаления
    response = requests.get(URL + "/profile", headers=headers)
    assert response.status_code == 401, "Профиль не был удален"
    print("✅ Тест 12 пройден успешно")


def test_profile_delete_unauthorized():
    """Тест удаления профиля без авторизации"""
    print("=== Тест 13: Удаление профиля без токена ===")
    response = requests.delete(URL + "/profile")
    assert response.status_code == 401, f"Ожидался статус 401, получен {response.status_code}"
    print("✅ Тест 13 пройден успешно")


def run_all_profile_tests(token):
    """Запуск всех тестов для профиля"""
    print("=== ТЕСТИРОВАНИЕ ЭНДПОИНТОВ ПРОФИЛЯ ===\n")
    
    print("Группа 1: Верификация профиля")
    test_profile_get_initial_verified_false(token)  # Проверка, что verified=False
    test_profile_verification_email_success(token)  # Успешная верификация
    
    print("\nГруппа 2: Тесты получения профиля")
    test_profile_get_success(token)
    test_profile_get_unauthorized()
    
    print("\nГруппа 3: Тесты обновления профиля")
    test_profile_patch_update_fields(token)
    test_profile_patch_invalid_email(token)
    test_profile_patch_missing_old_password(token)
    test_profile_patch_password_change(token)
    test_profile_patch_invalid_json(token)
    
    print("\nГруппа 4: Тесты удаления профиля")
    test_profile_delete_success(token)  # Важно запускать последним
    test_profile_delete_unauthorized()
    
    print("\n✅ ВСЕ ТЕСТЫ ДЛЯ ПРОФИЛЯ ПРОЙДЕНЫ УСПЕШНО")