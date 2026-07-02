"""Автоприменение SQL-миграций при старте database-core.

Прогоняет все файлы `migrations/*.sql` в лексикографическом порядке
(0001, 0002, …) на каждом запуске сервиса. Это безопасно, потому что по
соглашению проекта каждая миграция ОБЯЗАНА быть неразрушающей и идемпотентной
(`ADD COLUMN IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`,
`INSERT … ON CONFLICT DO NOTHING` и т.п.) — повторный прогон ничего не меняет.

Так изменения схемы/справочников попадают в прод сами при `deploy.sh`
(пересборка + перезапуск контейнера), без ручного `psql`.

Каждый файл исполняется на соединении в режиме AUTOCOMMIT: собственные
`BEGIN; … COMMIT;` внутри файла задают границы транзакции. При ошибке
исключение пробрасывается — контейнер не пройдёт healthcheck, и проблема
будет видна сразу, а не «наполовину применится молча».
"""

import os

from app.database import engine

MIGRATIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "migrations"
)


def run_migrations() -> None:
    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"[migrations] каталог не найден: {MIGRATIONS_DIR} — пропускаю")
        return

    files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )
    if not files:
        print("[migrations] .sql-файлов нет — пропускаю")
        return

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for name in files:
            path = os.path.join(MIGRATIONS_DIR, name)
            with open(path, "r", encoding="utf-8") as fh:
                sql = fh.read()
            try:
                conn.exec_driver_sql(sql)
                print(f"[migrations] применена {name}")
            except Exception as exc:  # noqa: BLE001 — логируем и пробрасываем
                print(f"[migrations] ОШИБКА в {name}: {exc}")
                raise

    print("[migrations] готово")
