#!/bin/bash

echo "🚀 Старт скрипта загрузки тестовых данных"

# Загружаем переменные окружения из .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ Файл .env не найден"
    exit 1
fi

# Отладочная информация
echo "POSTGRES_USER=$POSTGRES_USER"
echo "POSTGRES_HOST=$POSTGRES_HOST"
echo "POSTGRES_DB=$POSTGRES_DB"
echo "POSTGRES_PORT=$POSTGRES_PORT"

# Подмена host, если мы не в контейнере
if [ "$POSTGRES_HOST" = "database" ]; then
    echo "⚠️ Заменяю POSTGRES_HOST=database на localhost (не в контейнере)"
    POSTGRES_HOST=localhost
fi

echo "Загрузка тестовых данных в базу данных $POSTGRES_USER..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -p "$POSTGRES_PORT" -f test_data/test_data.sql

if [ $? -eq 0 ]; then
    echo "✅ Тестовые данные успешно загружены."
else
    echo "❌ Ошибка при загрузке данных."
    exit 1
fi
