# Order test case

# Стек технологий
<div id="badges" align="center">
  <img src="https://img.shields.io/badge/Python%203.11-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/>
  <img src="https://img.shields.io/badge/Django%20-green?style=for-the-badge&logo=django&"/>
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white"/>

  <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"/>
</div>

# Описание проекта
Приложение которое принимает данные о заказах в формате JSON, сохраняет их в базу, и формирует простую агрегированную статистику по пользователю.

В проекте реализовано:
* Панель администратора с таблицей товаров.

* Celery-таска для подсчёта статистики.

* Управление Celery-таской через панель администратора: настройка периодичности, времени старта и окончания.

* Логирование метода upload.

# Установка проекта.
Перед установкой проекта необходимо в корне проекта создать файл .env с переменными окруженя. Пример:
```.dotenv
DEBUG=True
SECRET_KEY=django-insecure-emd
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=order_analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
``` 
DB_HOST=localhost для запуска в ручном режиме.
## Установка проекта из репозитория  GitHub.
### Установить Python 3.10
- Для Windows https://www.python.org/downloads/
- Для Linux 
```
sudo apt update
sudo apt -y install python3-pip
sudo apt install python3.10
``` 
### Клонировать репозиторий и перейти в него в командной строке.
```
https://github.com/Rashid-creator-droid/order_analytics.git
``` 
###  Развернуть виртуальное окружение.
```
python -m venv venv

``` 
 - для Windows;
```
venv\Scripts\activate.bat
``` 
 - для Linux и MacOS.
``` 
source venv/bin/activate

```
### Установить систему контроля зависимостей Poetry
```
pip install poetry
``` 
### Установить зависимости
```
poetry install
```
### Команда для применения миграций
```
python manage.py migrate
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```
### Создание суперюзера
```
python manage.py createsuperuser
```
### Запуск проекта
```
python manage.py runserver
```
### Проект будет доступен по адресу.
```
http://127.0.0.1:8000/
```
## Установка контейнера Docker
### Склонировать репозиторий
```
https://github.com/Rashid-creator-droid/order_analytics.git
```
### Запустить сборку контейнера
```
sudo docker-compose up -d
``` 
### Создать суперюзера
```
docker exec -it order_analytics_web_1 python manage.py createsuperuser

```
### Проект будет доступен по адресу
```
http://localhost:8000/
```

## Эндпоинты
```/admin``` панель администратора.

```POST /api/orders/upload```
принмает JSON вида:
```Json
{
  "user": "test_seller",
  "orders": [
    {
      "order_number": "12345",
      "created_at": "2025-11-12T10:00:00Z",
      "total_amount": 2500.00,
      "status": "delivered",
      "items": [
        {"sku": "tea01", "name": "Чай зелёный", "quantity": 2, "price": 500},
        {"sku": "cup01", "name": "Чашка фарфоровая", "quantity": 1, "price": 1500}
      ]
    }
  ]
}

``` 
```GET /api/orders/stats?user=test_seller``` Возвращает JSON статистику:
```Json
{
  "user": "test_seller",
  "orders_count": 10,
  "total_revenue": 12345.67,
  "avg_order_value": 1234.56
}
``` 