# Blokadamap

Чтобы запустить у себя:

####  Напрямую (консоль bash)

У вас должен быть локально поднят postgres. Если вам не хочется этого делать, советую запускать через Docker

1. Создайте файл .env скопировав .env.example,
2. Определите переменные окружения

```
    # На данный момент версия Python 3.10
    # Создание виртуального окружения
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements/requirements.txt

    # Запуск
    ./scripts/start-dev.sh

    # Тесты
    ./scripts/tests/test-mock-ping.sh
```

#### Через Docker (теперь это удобно)
    
1. Устанавливаете докер 
2. Создайте файл .env
2. Копируете .env.example в .env и определяете переменные окружения (можно оставить как есть)

``` bash
    # build
    docker compose build
    # up
    docker compose up   
```
    
На 8080 порту запустится приложение fastapi, на 5432 postgres, 
на 1000 adminer (супер легковесный веб интерфейс для взаимодействия с базой)

#### Про adminer:
Если запуск получится, то на localhost:1000 будет запущен adminer \
Если вы не меняли .env.example при копировании, то credentials для доступа такие:

    System: PostgreSQL
    Server: database
    Username: root
    Password: root
    Database: db

P.s. Неочевидный нюанс в том, что server это database, а не localhost,
это связано с тем, что контейнеры для себя создают свою сеть, и в этой сети нету localhost.
Вместо этого в качестве адресов контейнеров выступают названия их как сервисов (как прописано в docker-compose.yaml) 
P.p.s На самом деле вроде можно и localhost, можете проверить

---

## Загрузка тестовых данных в базу данных

После запуска базы данных вы можете загрузить тестовые данные из файла `test_data/test_data.sql`.

### Если вы запускаете напрямую (без Docker):

Используйте готовый скрипт для загрузки данных (убедитесь, что он находится в папке `scripts/`):

```bash
# Для настроек по умолчанию
./scripts/load-test-data.sh
```

### Если вы запускаете через Docker
#### Вариант 1: Использование готового скрипта внутри контейнера

[//]: # (```bash )

[//]: # (# Копируем файл данных в контейнер)

[//]: # (docker cp ./test_data/test_data.sql database-core-database-1:/tmp/test_data.sql)

[//]: # (```)
```bash
# Выполняем напрямую
docker exec -i database-core-database-1 psql -U root -d db -f /tmp/test_data.sql
```

#### Вариант 2: Прямая загрузка через psql в контейнере
Используя строку bash, запустите из папки с проектом:
```bash 
docker exec -i database-core-database-1 psql -U root -d db < ./test_data/test_data.sql
```

#### Вариант 3: Через Adminer (web-интерфейс)
1) Откройте http://localhost:1000

2) Авторизуйтесь
```bash
    # (по умолчанию)
    System: PostgreSQL
    Server: database
    Username: root
    Password: root
    Database: db
```

3) Нажмите "SQL-запрос"

4) Вставьте содержимое test_data.sql

5) Нажмите "Выполнить"

### Проверка, что тестовые данные загрузились в database:
```bash
# Подключаемся к БД
docker compose exec database psql -U root -d db

# В интерактивной консоли psql:
db=# \dt                 # Список таблиц
db=# SELECT * FROM users LIMIT 1;  # Пример запроса

# Вывод: 
# author_id	first_name	middle_name	last_name	sex	birth_date	family_status_id	has_children	biography
# 1             Ivan            Ivanovich	 Ivanov	          M	  1910-01-01	      1	                      1	       Test biography

db=# \q                 # Выход
```