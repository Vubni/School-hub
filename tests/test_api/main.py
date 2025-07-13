import requests, os, time
from config import URL


    
if __name__ == "__main__":
    import auth, profile, psychologist, university, schedule, specialization

    token = auth.get_auth_token()
    profile.test_profile_delete_success(token)
    
    # Регистрация и авторизация
    token = auth.run_auth_tests()
    
    # Профиль
    profile.run_all_profile_tests(token)
    
    token = auth.get_auth_token()
    
    psychologist.run_all_psychologist_tests(token)
    
    university.run_all_university_tests(token)
    
    schedule.run_all_schedule_tests(token)
    
    specialization.run_all_specialization_tests(token)
    
    # Очистка
    profile.test_profile_delete_success(token)