# PeakIT 2024 backend

## Содержание
- [Технологии](#технологии)
- [Использование](#использование)
- [Разработка](#разработка)
- [Команда](#команда)

## Технологии
- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/)
- [PostgreSQL](https://www.postgresql.org/)

## Использование

### Требования
- [Docker](https://www.docker.com/)

### Настройка .env файла

1. Скопируйте `.env.example` в новый `.env` файл и заполните нужные данные кроме `DB_HOST`, он не будет иметь роли во время запуска.

### Запуск сервера

```
# Скопируйте репозиторий в нужную директорию
git clone https://github.com/toastmanager/peak_it_2024_backend.git

# Перейдите в эту директорию
cd peak_it_2024_backend

# Запустите docker compose в фоновом режиме
docker compose up -d
```

### Обновление сервера

Если вы хотите обновить приложение с нулевым временем простоя используйте [docker-rollout](https://github.com/wowu/docker-rollout), стандартный `docker compose up -d <service-name>` не даёт нужного результата.

## Разработка

### Требования
- [Python 3](https://www.python.org/)
- [Docker](https://www.docker.com/)

### Копирование репозитория

```
# Скопируйте репозиторий в нужную директорию
git clone https://github.com/toastmanager/peak_it_2024_backend.git

# Перейдите в эту директорию
cd peak_it_2024_backend
```

### Создание и активация виртуального окружения

С помощью виртуального окружения можно установить и использовать различные версии пакетов и зависимостей для каждого проекта, изолируя их друг от друга и предотвращая конфликты или несовместимости.

- **Windows**
```
# Создание виртуального окружения
python -m venv venv
# Активация виртуального окружения
venv/Scripts/activate
```
- **Linux**
```
# Создание виртуального окружения
python3 -m venv venv
# Активация виртуального окружения
source venv/bin/activate
```

### Установка pip зависимостей
```
pip install -r requirements.txt
```

### Локальная база данных для разработки

```
docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### Применение миграций

`<latest-revision>` - это значение переменной `revision` в последнем созданном файле по пути `alembic/versions/`

```
alembic upgrade <latest-revision>
```

### Запуск сервера для разрабтки

Сервер запустится использую `uvicorn` и будет обновляться при каждом сохранении любого файла.

```
fastapi dev src/main.py
```


### Создание миграций

`<message>` - описание изменений в базе данных

```
alembic revision --autogenerate -m "<message>"
```

## Команда
