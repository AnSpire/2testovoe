# Тестовое задание

Зависимости и окружение управляются через [uv](https://docs.astral.sh/uv/).

```bash
uv sync              # установить зависимости
uv run pytest        # запустить все тесты
uv run pytest task7_fastapi_jwt   # тесты одного задания
```

| № | Папка | Решение | Запуск |
|---|-------|---------|--------|
| 1 | `task1_text_wrap` | `format_text(text, width=70)` — жадный перенос по словам, абзацы сохраняются | `uv run python task1_text_wrap/wrap.py` |
| 2 | `task2_lucky_ticket` | `can_be_lucky(digits)` — ищет разбиение шести цифр на две тройки с равной суммой | `uv run python task2_lucky_ticket/lucky.py` |
| 3 | `task3_nested_get` | `get_by_path(obj, "a.b.c")` — словари и списки (по индексу), `default`, если пути нет | `uv run python task3_nested_get/nested.py` |
| 4 | `task4_json_parse` | `outData = json.loads(inData)` | `uv run python task4_json_parse/parse.py` |
| 5 | `task5_pandas` | `df3 = df1.fillna(df2).astype(int)` | `uv run python task5_pandas/fill_df.py` |
| 6 | `task6_fastapi_crud` | CRUD пользователей, хранилище в памяти | см. ниже |
| 7 | `task7_fastapi_jwt` | регистрация, вход, защищённые маршруты на JWT (pyjwt) | см. ниже |

## 6. CRUD пользователей

```bash
cd task6_fastapi_crud
uv run uvicorn users_api.main:app --reload
```

Документация: http://127.0.0.1:8000/docs

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/users` | создать (`name`, `email`) |
| GET | `/users` | список |
| GET | `/users/{id}` | получить |
| PUT | `/users/{id}` | полная замена |
| PATCH | `/users/{id}` | частичное обновление |
| DELETE | `/users/{id}` | удалить |

Email уникален (409 при повторе), несуществующий id — 404.

## 7. JWT-аутентификация

```bash
cd task7_fastapi_jwt
JWT_SECRET_KEY=$(openssl rand -hex 32) uv run uvicorn auth_api.main:app --reload
```

| Метод | Путь | Токен | Описание |
|-------|------|-------|----------|
| POST | `/auth/register` | — | `username`, `email`, `password` |
| POST | `/auth/login` | — | `username`, `password` → `access_token` |
| GET | `/public` | — | открытый маршрут |
| GET | `/users/me` | да | текущий пользователь |
| GET | `/protected` | да | пример защищённого маршрута |

Токен передаётся в заголовке `Authorization: Bearer <token>`
(в Swagger — кнопка Authorize). Пароли хранятся как PBKDF2-хеш с солью.
Настройки: `JWT_SECRET_KEY`, `JWT_TTL_MINUTES` (по умолчанию 30).

```bash
curl -X POST localhost:8000/auth/register -H 'content-type: application/json' \
  -d '{"username":"ivan","email":"ivan@example.com","password":"secret123"}'
TOKEN=$(curl -s -X POST localhost:8000/auth/login -H 'content-type: application/json' \
  -d '{"username":"ivan","password":"secret123"}' | jq -r .access_token)
curl localhost:8000/users/me -H "Authorization: Bearer $TOKEN"
```
