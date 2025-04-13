# Официальный образ python
FROM python:3.10

# Рабочая директория
WORKDIR /code

# Копируем requirements в рабочую директорию
COPY ./requirements/requirements.txt /code/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Копируем весь код в рабочую директорию
COPY ./scripts /code/scripts
COPY ./app /code/app

CMD ["./scripts/start-dev.sh"]