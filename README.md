# PeakIT 2024 Backend

Серверная часть для приложения "Ужин с пандой". Приложения для заказа еды из ресторана китайской кухни. Разработано для хакатона PeakIT 2024. Состояние на конец хакатона находится в ветке `temporary-solutions-is-always-the-best`.

## Содержание

- [Технологии](#технологии)
- [Использование](#использование)
- [Разработка](#разработка)
- [Команда](#команда)

## Технологии

### Языки программирования

- [Python](https://www.python.org/)

### Фреймворки

- [FastAPI](https://fastapi.tiangolo.com/)

### Инструменты

- [Poetry](https://python-poetry.org/) - Пакетный менеджер
- [Docker](https://www.docker.com/) - Контейнеризация
- [PostgreSQL](https://www.postgresql.org/) - База данных
- [Docker rollout](https://github.com/wowu/docker-rollout) - Обновление сервера с нулевым временем простоя
- [Github Actions](https://github.com/features/actions) - CI/CD

## Использование

### Требования

- [Ubuntu](https://ubuntu.com/) или другой дистрибутив Linux
- [Github CLI](https://cli.github.com/)
- [Docker](https://www.docker.com/)
- [Docker rollout](https://github.com/wowu/docker-rollout)

### Настройка .env файла

Скопируйте `.env.example` в новый `.env` файл и заполните нужные данные.

### Настройки для CD

```bash
# Настройте ssh ключи
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
cat .ssh/id_rsa.pub >> .ssh/authorized_keys
# Настройте Github CLI
git config --global credential.helper store
gh auth login
```

### Запуск сервера

```bash
# Клонируйте репозиторий
git clone https://github.com/toastmanager/peak_it_2024_backend.git ~/peak_it_2024_backend
cd peak_it_2024_backend
# Настройте .env файлы
cp .env.example .env
nano .env
# Запустите сервер в фоновом режиме
HOST=<your.domain> docker compose up -d
```

### Ручное обновление

```bash
# Соберите новое изображение `server` для docker compose
docker compose build server
# Запустите новое изображение через docker rollout
docker rollout -f docker-compose.yml server
# Обновите базу данных
docker compose run server alembic upgrade head
```

## Разработка

### Требования

- [Python 3](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)

### Копирование репозитория

```
# Скопируйте репозиторий в нужную директорию
git clone https://github.com/toastmanager/peak_it_2024_backend.git

# Перейдите в эту директорию
cd peak_it_2024_backend
```

### Настройка Poetry (Зависимостей)

Исполните команду `poetry config virtualenvs.in-project true`, если хотите чтобы poetry создавал папку виртуального окружения `.venv` в директории разработки.

```bash
poetry shell # используйте, если не настроили poetry на создание .venv в папке разработки
poetry install
```

### Локальная база данных для разработки

```
docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### Применение последних миграций базы данных

```
alembic upgrade head
```

### Локальное S3 хранилище для разработки

- [LocalStack](https://www.localstack.cloud/) или [Minio](https://min.io/)

### Запуск сервера для разрабтки

Сервер запустится используя `uvicorn` и будет обновляться при каждом сохранении любого файла.

```
fastapi dev src/main.py
```

### Создание миграций

`<message>` - описание изменений в базе данных

```
alembic revision --autogenerate -m "<message>"
```

## Команда

|              | Роль        |
| ------------ | ----------- |
| toastmanager | Разработчик |
