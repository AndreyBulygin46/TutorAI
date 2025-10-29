#!/usr/bin/env python3
"""
TutorAI API Test Script
Тестирование всех API endpoints
"""

import requests
import json
from datetime import date, timedelta
from typing import Dict, Any

# Конфигурация
BASE_URL = "http://localhost:8000"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

class TutorAITester:
    """Класс для тестирования TutorAI API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def test_health(self) -> bool:
        """Тест health check"""
        print("🔍 Тестирование health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_students_api(self) -> bool:
        """Тест API студентов"""
        print("\n👥 Тестирование API студентов...")
        
        try:
            # 1. Получение списка студентов
            print("  📋 Получение списка студентов...")
            response = self.session.get(f"{self.base_url}/api/v1/students/")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Студенты получены: {data.get('total', 0)} записей")
            else:
                print(f"  ❌ Ошибка получения студентов: {response.status_code}")
                return False
            
            # 2. Создание нового студента
            print("  ➕ Создание нового студента...")
            student_data = {
                "name": "Тестовый Студент",
                "phone": "+79999999999",
                "telegram_user_id": 999999999,
                "telegram_username": "test_student",
                "is_active": True
            }
            response = self.session.post(f"{self.base_url}/api/v1/students/", json=student_data)
            if response.status_code == 200:
                created_student = response.json()
                print(f"  ✅ Студент создан: ID {created_student.get('student_id')}")
                student_id = created_student.get('student_id')
            else:
                print(f"  ❌ Ошибка создания студента: {response.status_code}")
                print(f"  📝 Ответ: {response.text}")
                return False
            
            # 3. Получение студента по ID
            print("  🔍 Получение студента по ID...")
            response = self.session.get(f"{self.base_url}/api/v1/students/{student_id}")
            if response.status_code == 200:
                student = response.json()
                print(f"  ✅ Студент получен: {student.get('name')}")
            else:
                print(f"  ❌ Ошибка получения студента: {response.status_code}")
            
            # 4. Получение фактов о студенте
            print("  📊 Получение фактов о студенте...")
            week_start = date.today() - timedelta(days=7)
            week_end = date.today()
            response = self.session.get(
                f"{self.base_url}/api/v1/students/{student_id}/facts",
                params={"week_start": week_start, "week_end": week_end}
            )
            if response.status_code == 200:
                facts = response.json()
                print(f"  ✅ Факты получены: {len(facts.get('assignments', {}))} категорий")
            else:
                print(f"  ❌ Ошибка получения фактов: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка тестирования студентов: {e}")
            return False
    
    def test_materials_api(self) -> bool:
        """Тест API материалов"""
        print("\n📚 Тестирование API материалов...")
        
        try:
            # 1. Получение списка материалов
            print("  📋 Получение списка материалов...")
            response = self.session.get(f"{self.base_url}/api/v1/materials/")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Материалы получены: {data.get('total', 0)} записей")
            else:
                print(f"  ❌ Ошибка получения материалов: {response.status_code}")
                return False
            
            # 2. Получение статистики материалов
            print("  📊 Получение статистики материалов...")
            response = self.session.get(f"{self.base_url}/api/v1/materials/stats/")
            if response.status_code == 200:
                stats = response.json()
                print(f"  ✅ Статистика: {stats}")
            else:
                print(f"  ❌ Ошибка получения статистики: {response.status_code}")
            
            # 3. Поиск материалов
            print("  🔍 Поиск материалов...")
            response = self.session.get(f"{self.base_url}/api/v1/materials/search/?q=тест")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Поиск выполнен: {data.get('total', 0)} результатов")
            else:
                print(f"  ❌ Ошибка поиска: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка тестирования материалов: {e}")
            return False
    
    def test_messages_api(self) -> bool:
        """Тест API сообщений"""
        print("\n💬 Тестирование API сообщений...")
        
        try:
            # 1. Получение списка сообщений
            print("  📋 Получение списка сообщений...")
            response = self.session.get(f"{self.base_url}/api/v1/messages/")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Сообщения получены: {data.get('total', 0)} записей")
            else:
                print(f"  ❌ Ошибка получения сообщений: {response.status_code}")
                return False
            
            # 2. Создание сообщения
            print("  ➕ Создание сообщения...")
            message_data = {
                "chat_id": 123456789,
                "sender_type": "user",
                "sender_id": 1,
                "text_content": "Тестовое сообщение от API"
            }
            response = self.session.post(f"{self.base_url}/api/v1/messages/", json=message_data)
            if response.status_code == 200:
                message = response.json()
                print(f"  ✅ Сообщение создано: ID {message.get('message_id')}")
                message_id = message.get('message_id')
            else:
                print(f"  ❌ Ошибка создания сообщения: {response.status_code}")
                print(f"  📝 Ответ: {response.text}")
                return False
            
            # 3. Создание ответа бота
            print("  🤖 Создание ответа бота...")
            bot_response_data = {
                "text_content": "Это тестовый ответ бота"
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/messages/{message_id}/bot-response",
                json=bot_response_data
            )
            if response.status_code == 200:
                bot_response = response.json()
                print(f"  ✅ Ответ бота создан: ID {bot_response.get('response_id')}")
            else:
                print(f"  ❌ Ошибка создания ответа бота: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка тестирования сообщений: {e}")
            return False
    
    def test_rating_api(self) -> bool:
        """Тест API рейтинга"""
        print("\n📊 Тестирование API рейтинга...")
        
        try:
            # 1. Получение конфигурации потоков
            print("  📋 Получение конфигурации потоков...")
            response = self.session.get(f"{self.base_url}/api/v1/rating/streams")
            if response.status_code == 200:
                streams = response.json()
                print(f"  ✅ Потоки получены: {len(streams)} записей")
            else:
                print(f"  ❌ Ошибка получения потоков: {response.status_code}")
                return False
            
            # 2. Получение студентов потока (если есть потоки)
            if streams:
                stream_id = streams[0].get('stream_id')
                print(f"  👥 Получение студентов потока {stream_id}...")
                response = self.session.get(f"{self.base_url}/api/v1/rating/streams/{stream_id}/students")
                if response.status_code == 200:
                    students_data = response.json()
                    print(f"  ✅ Студенты потока: {students_data.get('total_count', 0)} записей")
                else:
                    print(f"  ❌ Ошибка получения студентов потока: {response.status_code}")
            
            # 3. Получение еженедельного отчета
            if streams:
                stream_id = streams[0].get('stream_id')
                print(f"  📈 Получение еженедельного отчета для потока {stream_id}...")
                week_start = date.today() - timedelta(days=7)
                week_end = date.today()
                response = self.session.get(
                    f"{self.base_url}/api/v1/rating/streams/{stream_id}/weekly-report",
                    params={"week_start": week_start, "week_end": week_end}
                )
                if response.status_code == 200:
                    report = response.json()
                    print(f"  ✅ Отчет получен: {report.get('active_students', 0)} активных студентов")
                else:
                    print(f"  ❌ Ошибка получения отчета: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка тестирования рейтинга: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Запуск всех тестов"""
        print("🚀 Запуск тестирования TutorAI API")
        print("=" * 50)
        
        results = {}
        
        # Тест health check
        results['health'] = self.test_health()
        
        # Тест API студентов
        results['students'] = self.test_students_api()
        
        # Тест API материалов
        results['materials'] = self.test_materials_api()
        
        # Тест API сообщений
        results['messages'] = self.test_messages_api()
        
        # Тест API рейтинга
        results['rating'] = self.test_rating_api()
        
        # Итоги
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{test_name.upper()}: {status}")
        
        print(f"\nИтого: {passed}/{total} тестов пройдено")
        
        if passed == total:
            print("🎉 Все тесты пройдены успешно!")
        else:
            print("⚠️  Некоторые тесты провалены. Проверьте настройки.")
        
        return results

def main():
    """Главная функция"""
    print("TutorAI API Test Suite")
    print("Убедитесь, что приложение запущено на http://localhost:8000")
    print()
    
    # Создание тестера
    tester = TutorAITester()
    
    # Запуск тестов
    results = tester.run_all_tests()
    
    # Возврат кода выхода
    if all(results.values()):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()

