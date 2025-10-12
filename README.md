Веб-приложение на Django для управления поставщиками, контрактами, счетами и платежами.

**Структура приложения**

```
company_app/
│
├── company_app/                # Конфигурация проекта Django
│   ├── __init__.py
│   ├── asgi.py                 # Запуск проекта через ASGI
│   ├── settings.py             # Настройки: приложения, БД, статические файлы
│   ├── urls.py                 # Основные маршруты проекта
│   └── wsgi.py                 # Запуск проекта через WSGI
│
├── accounts/                   # Авторизация и управление пользователями
│   ├── __init__.py
│   ├── admin.py                # Регистрация моделей в админке
│   ├── models.py               # Модель пользователя (если есть)
│   ├── forms.py                # Формы входа и регистрации
│   ├── views.py                # Контроллеры (login, logout, регистрация)
│   ├── urls.py                 # Маршруты для авторизации
│   └── migrations/             # Миграции БД
│
├── core/                       # Основная бизнес-логика приложения
│   ├── __init__.py
│   ├── admin.py                # Админ-панель для моделей
│   ├── models.py               # Основные модели данных
│   ├── forms.py                # Формы добавления и редактирования записей
│   ├── views.py                # CRUD-операции и обработка запросов
│   ├── urls.py                 # Маршруты для core
│   ├── middleware.py           # Пользовательские middleware
│   ├── migrations/             # Файлы миграций
│   ├── static/core/            # Статические файлы 
│   └── templates/core/         # HTML-шаблоны страниц интерфейса
│
├── templates/                  # Общие шаблоны
│   ├── base.html               # Основной шаблон (структура сайта)
│   └── accounts/               # Шаблоны страниц авторизации
│
├── static/                     # Глобальные статические файлы
│
├── venv/                       # Виртуальное окружение
│
├── manage.py                   # Точка входа Django-проекта
├── .gitignore                  
└── README.md                 

```

**Запуск**


```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
