from sqladmin import Admin, ModelView
from app.core.database import engine
from app.models.education import (
    Student, CourseProgram, Stream, Module, Lesson,
    CourseMaterial, Schedule, Assignment, Message, BotResponse
)

class StudentAdmin(ModelView, model=Student):
    name = "Студент"
    name_plural = "Студенты"
    column_list = [Student.student_id, Student.name, Student.phone, Student.telegram_username, Student.is_active]
    column_details_list = [Student.student_id, Student.name, Student.phone, Student.telegram_username, Student.telegram_user_id, Student.is_active, Student.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить студента"
    edit_text = "Редактировать студента"
    delete_text = "Удалить студента"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    # Иконка и русские подписи
    icon = "fa-solid fa-user"
    column_labels = {
        Student.student_id: "ID",
        Student.name: "Имя",
        Student.phone: "Телефон",
        Student.telegram_username: "Telegram",
        Student.is_active: "Активен",
        Student.created_at: "Создан"
    }
    
    # Русские названия для кнопок
    form_columns = [Student.student_id, Student.name, Student.phone, Student.telegram_user_id, Student.telegram_username, Student.is_active]
    form_widget_args = {
        "name": {"placeholder": "Введите имя студента"},
        "phone": {"placeholder": "+7XXXXXXXXXX"},
        "telegram_username": {"placeholder": "username"}
    }

class CourseProgramAdmin(ModelView, model=CourseProgram):
    name = "Программа курса"
    name_plural = "Программы курсов"
    column_list = [CourseProgram.program_id, CourseProgram.name, CourseProgram.total_hours]
    column_details_list = [CourseProgram.program_id, CourseProgram.name, CourseProgram.description, CourseProgram.total_hours, CourseProgram.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить программу"
    edit_text = "Редактировать программу"
    delete_text = "Удалить программу"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-graduation-cap"
    column_labels = {
        CourseProgram.program_id: "ID",
        CourseProgram.name: "Название",
        CourseProgram.description: "Описание",
        CourseProgram.total_hours: "Часов",
        CourseProgram.created_at: "Создана"
    }
    
    # Русские настройки для форм
    form_columns = [CourseProgram.program_id, CourseProgram.name, CourseProgram.description, CourseProgram.total_hours]
    form_widget_args = {
        "name": {"placeholder": "Введите название программы"},
        "description": {"placeholder": "Введите описание программы"},
        "total_hours": {"placeholder": "Введите количество часов"}
    }

class StreamAdmin(ModelView, model=Stream):
    name = "Поток"
    name_plural = "Потоки"
    column_list = [Stream.stream_id, Stream.name, Stream.start_date, Stream.end_date]
    column_details_list = [Stream.stream_id, Stream.name, Stream.start_date, Stream.end_date, Stream.description, Stream.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить поток"
    edit_text = "Редактировать поток"
    delete_text = "Удалить поток"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-users"
    column_labels = {
        Stream.stream_id: "ID",
        Stream.name: "Название",
        Stream.start_date: "Начало",
        Stream.end_date: "Окончание",
        Stream.description: "Описание",
        Stream.created_at: "Создан"
    }
    
    # Русские настройки для форм
    form_columns = [Stream.stream_id, Stream.name, Stream.start_date, Stream.end_date, Stream.description]
    form_widget_args = {
        "name": {"placeholder": "Введите название потока"},
        "description": {"placeholder": "Введите описание потока"},
        "start_date": {"placeholder": "Выберите дату начала"},
        "end_date": {"placeholder": "Выберите дату окончания"}
    }

class ModuleAdmin(ModelView, model=Module):
    name = "Модуль"
    name_plural = "Модули"
    column_list = [Module.module_id, Module.name, Module.order_num, Module.duration_hours]
    column_details_list = [Module.module_id, Module.name, Module.order_num, Module.description, Module.duration_hours, Module.lecture_hours, Module.practice_hours, Module.independent_hours, Module.is_intermediate_attestation, Module.is_final_attestation, Module.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить модуль"
    edit_text = "Редактировать модуль"
    delete_text = "Удалить модуль"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-book"
    column_labels = {
        Module.module_id: "ID",
        Module.name: "Название",
        Module.order_num: "Порядок",
        Module.description: "Описание",
        Module.duration_hours: "Часов",
        Module.lecture_hours: "Лекции",
        Module.practice_hours: "Практика",
        Module.independent_hours: "Самостоятельно",
        Module.is_intermediate_attestation: "Промежуточная аттестация",
        Module.is_final_attestation: "Финальная аттестация",
        Module.created_at: "Создан"
    }
    
    # Русские настройки для форм
    form_columns = [Module.module_id, Module.name, Module.order_num, Module.description, Module.duration_hours, Module.lecture_hours, Module.practice_hours, Module.independent_hours, Module.is_intermediate_attestation, Module.is_final_attestation]
    form_widget_args = {
        "name": {"placeholder": "Введите название модуля"},
        "description": {"placeholder": "Введите описание модуля"},
        "order_num": {"placeholder": "Введите порядковый номер"},
        "duration_hours": {"placeholder": "Введите общее количество часов"},
        "lecture_hours": {"placeholder": "Введите количество лекционных часов"},
        "practice_hours": {"placeholder": "Введите количество практических часов"},
        "independent_hours": {"placeholder": "Введите количество часов самостоятельной работы"}
    }

class LessonAdmin(ModelView, model=Lesson):
    name = "Урок"
    name_plural = "Уроки"
    column_list = [Lesson.lesson_id, Lesson.name, Lesson.order_num, Lesson.duration_hours]
    column_details_list = [Lesson.lesson_id, Lesson.name, Lesson.order_num, Lesson.description, Lesson.duration_hours, Lesson.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить урок"
    edit_text = "Редактировать урок"
    delete_text = "Удалить урок"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-chalkboard-teacher"
    column_labels = {
        Lesson.lesson_id: "ID",
        Lesson.name: "Название",
        Lesson.order_num: "Порядок",
        Lesson.description: "Описание",
        Lesson.duration_hours: "Часов",
        Lesson.created_at: "Создан"
    }
    
    # Русские настройки для форм
    form_columns = [Lesson.lesson_id, Lesson.name, Lesson.order_num, Lesson.description, Lesson.duration_hours]
    form_widget_args = {
        "name": {"placeholder": "Введите название урока"},
        "description": {"placeholder": "Введите описание урока"},
        "order_num": {"placeholder": "Введите порядковый номер"},
        "duration_hours": {"placeholder": "Введите количество часов"}
    }

class CourseMaterialAdmin(ModelView, model=CourseMaterial):
    name = "Материал курса"
    name_plural = "Материалы курса"
    column_list = [CourseMaterial.material_id, CourseMaterial.title, CourseMaterial.material_type, CourseMaterial.material_category, CourseMaterial.is_public]
    column_details_list = [CourseMaterial.material_id, CourseMaterial.title, CourseMaterial.content, CourseMaterial.file_path, CourseMaterial.material_type, CourseMaterial.material_category, CourseMaterial.is_public, CourseMaterial.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить материал"
    edit_text = "Редактировать материал"
    delete_text = "Удалить материал"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-file-alt"
    column_labels = {
        CourseMaterial.material_id: "ID",
        CourseMaterial.title: "Название",
        CourseMaterial.content: "Содержимое",
        CourseMaterial.file_path: "Файл",
        CourseMaterial.material_type: "Тип",
        CourseMaterial.material_category: "Категория",
        CourseMaterial.is_public: "Публичный",
        CourseMaterial.created_at: "Создан"
    }
    
    # Русские настройки для форм
    form_columns = [CourseMaterial.material_id, CourseMaterial.title, CourseMaterial.content, CourseMaterial.file_path, CourseMaterial.material_type, CourseMaterial.material_category, CourseMaterial.is_public]
    form_widget_args = {
        "title": {"placeholder": "Введите название материала"},
        "content": {"placeholder": "Введите содержимое материала"},
        "file_path": {"placeholder": "Введите путь к файлу"},
        "material_type": {"placeholder": "Выберите тип материала"},
        "material_category": {"placeholder": "Выберите категорию материала"}
    }

class ScheduleAdmin(ModelView, model=Schedule):
    name = "Расписание"
    name_plural = "Расписания"
    column_list = [Schedule.schedule_id, Schedule.scheduled_date, Schedule.is_completed]
    column_details_list = [Schedule.schedule_id, Schedule.scheduled_date, Schedule.is_completed, Schedule.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить расписание"
    edit_text = "Редактировать расписание"
    delete_text = "Удалить расписание"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-calendar"
    column_labels = {
        Schedule.schedule_id: "ID",
        Schedule.scheduled_date: "Дата",
        Schedule.is_completed: "Завершено",
        Schedule.created_at: "Создано"
    }
    
    # Русские настройки для форм
    form_columns = [Schedule.schedule_id, Schedule.scheduled_date, Schedule.is_completed]
    form_widget_args = {
        "scheduled_date": {"placeholder": "Выберите дату занятия"},
        "is_completed": {"placeholder": "Отметьте, если занятие завершено"}
    }

class AssignmentAdmin(ModelView, model=Assignment):
    name = "Задание"
    name_plural = "Задания"
    column_list = [Assignment.assignment_id, Assignment.name, Assignment.status, Assignment.deadline, Assignment.grade]
    column_details_list = [Assignment.assignment_id, Assignment.name, Assignment.description, Assignment.status, Assignment.deadline, Assignment.submitted_at, Assignment.checked_at, Assignment.feedback, Assignment.grade, Assignment.created_at]
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    # Кастомные тексты для кнопок
    create_text = "Добавить задание"
    edit_text = "Редактировать задание"
    delete_text = "Удалить задание"
    save_text = "Сохранить"
    cancel_text = "Отмена"
    
    icon = "fa-solid fa-tasks"
    column_labels = {
        Assignment.assignment_id: "ID",
        Assignment.name: "Название",
        Assignment.description: "Описание",
        Assignment.status: "Статус",
        Assignment.deadline: "Дедлайн",
        Assignment.submitted_at: "Сдано",
        Assignment.checked_at: "Проверено",
        Assignment.feedback: "Отзыв",
        Assignment.grade: "Оценка",
        Assignment.created_at: "Создано"
    }
    
    # Русские настройки для форм
    form_columns = [Assignment.assignment_id, Assignment.name, Assignment.description, Assignment.status, Assignment.deadline, Assignment.submitted_at, Assignment.checked_at, Assignment.feedback, Assignment.grade]
    form_widget_args = {
        "name": {"placeholder": "Введите название задания"},
        "description": {"placeholder": "Введите описание задания"},
        "deadline": {"placeholder": "Выберите дедлайн"},
        "feedback": {"placeholder": "Введите отзыв по заданию"},
        "grade": {"placeholder": "Введите оценку (0-100)"}
    }

class MessageAdmin(ModelView, model=Message):
    name = "Сообщение"
    name_plural = "Сообщения"
    column_list = [Message.message_id, Message.sender_type, Message.text_content, Message.created_at]
    column_details_list = [Message.message_id, Message.telegram_message_id, Message.chat_id, Message.sender_type, Message.sender_id, Message.text_content, Message.attachment_url, Message.created_at]
    can_create = False
    can_edit = False
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    icon = "fa-solid fa-comment"
    column_labels = {
        Message.message_id: "ID",
        Message.telegram_message_id: "Telegram ID",
        Message.chat_id: "Чат ID",
        Message.sender_type: "Тип отправителя",
        Message.sender_id: "ID отправителя",
        Message.text_content: "Текст",
        Message.attachment_url: "Вложение",
        Message.created_at: "Создано"
    }
    
    # Русские настройки для форм (только для просмотра, так как can_create = False)
    form_columns = [Message.message_id, Message.telegram_message_id, Message.chat_id, Message.sender_type, Message.sender_id, Message.text_content, Message.attachment_url]
    form_widget_args = {
        "text_content": {"placeholder": "Текст сообщения"},
        "attachment_url": {"placeholder": "Ссылка на вложение"}
    }

class BotResponseAdmin(ModelView, model=BotResponse):
    name = "Ответ бота"
    name_plural = "Ответы бота"
    column_list = [BotResponse.response_id, BotResponse.text_content, BotResponse.created_at]
    column_details_list = [BotResponse.response_id, BotResponse.message_id, BotResponse.text_content, BotResponse.attachment_url, BotResponse.created_at]
    can_create = False
    can_edit = False
    can_export = False
    can_delete = False
    can_bulk_delete = False
    can_bulk_export = False
    
    icon = "fa-solid fa-robot"
    column_labels = {
        BotResponse.response_id: "ID",
        BotResponse.message_id: "ID сообщения",
        BotResponse.text_content: "Текст",
        BotResponse.attachment_url: "Вложение",
        BotResponse.created_at: "Создано"
    }
    
    # Русские настройки для форм (только для просмотра, так как can_create = False)
    form_columns = [BotResponse.response_id, BotResponse.message_id, BotResponse.text_content, BotResponse.attachment_url]
    form_widget_args = {
        "text_content": {"placeholder": "Текст ответа бота"},
        "attachment_url": {"placeholder": "Ссылка на вложение"}
    }

def setup_admin(app):
    admin = Admin(app, engine, title="AI Tutor Admin")
    
    # Добавляем кастомный CSS для переводов
    @app.get("/static/admin_translations.css")
    def get_translations_css():
        from fastapi.responses import FileResponse
        return FileResponse("app/static/admin_translations.css", media_type="text/css")
    
    # Добавляем middleware для вставки CSS и JavaScript
    @app.middleware("http")
    async def add_translations_css(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/admin") and "text/html" in response.headers.get("content-type", ""):
            if hasattr(response, 'body'):
                body = response.body.decode() if isinstance(response.body, bytes) else response.body
                css_link = '<link rel="stylesheet" href="/static/admin_translations.css">'
                js_script = '''
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Функция для замены текста
                    function replaceText() {
                        // Заменяем текст кнопок
                        const buttons = document.querySelectorAll('a.btn, button.btn');
                        buttons.forEach(btn => {
                            if (btn.textContent.includes('New')) {
                                btn.textContent = btn.textContent.replace('New', 'Добавить');
                            }
                            if (btn.textContent.includes('Edit')) {
                                btn.textContent = btn.textContent.replace('Edit', 'Редактировать');
                            }
                            if (btn.textContent.includes('Delete')) {
                                btn.textContent = btn.textContent.replace('Delete', 'Удалить');
                            }
                            if (btn.textContent.includes('Save')) {
                                btn.textContent = btn.textContent.replace('Save', 'Сохранить');
                            }
                            if (btn.textContent.includes('Cancel')) {
                                btn.textContent = btn.textContent.replace('Cancel', 'Отмена');
                            }
                        });
                        
                        // Заменяем кнопки форм редактирования
                        const submitButtons = document.querySelectorAll('input[type="submit"]');
                        submitButtons.forEach(btn => {
                            if (btn.value === 'Save') {
                                btn.value = 'Сохранить';
                            }
                            if (btn.value === 'Save and continue editing') {
                                btn.value = 'Сохранить и продолжить редактирование';
                            }
                            if (btn.value === 'Save and add another') {
                                btn.value = 'Сохранить и добавить еще';
                            }
                        });
                        
                        // Заменяем ссылки Cancel
                        const cancelLinks = document.querySelectorAll('a.btn[href*="/list"]');
                        cancelLinks.forEach(link => {
                            if (link.textContent.includes('Cancel')) {
                                link.textContent = link.textContent.replace('Cancel', 'Отмена');
                            }
                        });
                        
                        // Заменяем текст пагинации - более агрессивно
                        const allElements = document.querySelectorAll('*');
                        allElements.forEach(el => {
                            if (el.textContent && el.textContent.includes('Showing')) {
                                el.textContent = el.textContent.replace(/Showing \\d+ to \\d+ of \\d+ items/g, 'Показано элементов');
                            }
                            if (el.textContent && el.textContent.includes('prev')) {
                                el.textContent = el.textContent.replace('prev', 'Предыдущая');
                            }
                            if (el.textContent && el.textContent.includes('next')) {
                                el.textContent = el.textContent.replace('next', 'Следующая');
                            }
                            if (el.textContent && el.textContent.includes('Show')) {
                                el.textContent = el.textContent.replace('Show', 'Показать');
                            }
                            if (el.textContent && el.textContent.includes('/ Page')) {
                                el.textContent = el.textContent.replace('/ Page', '/ Страница');
                            }
                        });
                        
                        // Специально для пагинации
                        const paginationTexts = document.querySelectorAll('p.text-muted');
                        paginationTexts.forEach(p => {
                            if (p.textContent.includes('Showing')) {
                                p.innerHTML = p.innerHTML.replace(/Showing <span>\\d+<\\/span> to <span>\\d+<\\/span> of <span>\\d+<\\/span> items/g, 'Показано элементов');
                            }
                        });
                        
                        // Кнопки пагинации
                        const paginationLinks = document.querySelectorAll('.pagination a');
                        paginationLinks.forEach(link => {
                            if (link.textContent.includes('prev')) {
                                link.innerHTML = link.innerHTML.replace('prev', 'Предыдущая');
                            }
                            if (link.textContent.includes('next')) {
                                link.innerHTML = link.innerHTML.replace('next', 'Следующая');
                            }
                        });
                        
                        // Dropdown элементы
                        const dropdownItems = document.querySelectorAll('.dropdown-item');
                        dropdownItems.forEach(item => {
                            if (item.textContent.includes('/ Page')) {
                                item.textContent = item.textContent.replace('/ Page', '/ Страница');
                            }
                        });
                        
                        const dropdownToggle = document.querySelectorAll('.dropdown-toggle');
                        dropdownToggle.forEach(toggle => {
                            if (toggle.textContent.includes('/ Page')) {
                                toggle.textContent = toggle.textContent.replace('/ Page', '/ Страница');
                            }
                        });
                    }
                    
                    // Запускаем сразу
                    replaceText();
                    
                    // Запускаем через небольшую задержку (на случай если контент загружается асинхронно)
                    setTimeout(replaceText, 100);
                    setTimeout(replaceText, 500);
                    setTimeout(replaceText, 1000);
                });
                </script>
                '''
                body = body.replace("</head>", css_link + "</head>")
                body = body.replace("</body>", js_script + "</body>")
                response.body = body.encode() if isinstance(body, str) else body
        return response
    
    # Регистрация моделей
    admin.add_view(StudentAdmin)
    admin.add_view(CourseProgramAdmin)
    admin.add_view(StreamAdmin)
    admin.add_view(ModuleAdmin)
    admin.add_view(LessonAdmin)
    admin.add_view(CourseMaterialAdmin)
    admin.add_view(ScheduleAdmin)
    admin.add_view(AssignmentAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(BotResponseAdmin)
    
    return admin
