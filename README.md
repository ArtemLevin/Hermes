# Hermes MVP — образовательный сервис-органайзер для частного репетитора

Минимальный рабочий продукт (MVP) на **FastAPI + React**, разворачиваемый через Docker Compose.

---

## 🚀 Возможности

- **Панель репетитора**
  - Дашборд с графиками прогресса.
  - Радар внимания (приоритизация учеников).
  - Календарь-мозаика (уроки как карточки).
- **Профиль ученика**
  - Герой-аватар, уровень = прогресс.
  - Биография, цели, тепловая карта ошибок.
  - Лента достижений.
- **Учёт уроков и материалов**
  - Трекер занятий.
  - Автобиблиотека материалов.
- **Домашка как квест**
  - Чек-листы, награды, статусы.
- **Финансовый модуль**
  - Учёт оплат, статусы, напоминания.
- **Уведомления**
  - Еженедельный дайджест родителям.
  - Напоминания о ДЗ, уроках и оплате.

---

## 📂 Структура проекта

```
.
├─ api/               # Backend (FastAPI)
│  ├─ main.py
│  ├─ models.py
│  ├─ routers/
│  ├─ alembic/
│  ├─ scripts/
│  └─ tests/
├─ web/               # Frontend (React + Vite)
│  └─ src/pages/
├─ docker-compose.yml
├─ Makefile
├─ .env.sample
└─ pyproject.toml (или requirements.txt)
```

---

## 🛠️ Установка и запуск

### 1. Клонирование и подготовка
```bash
git clone https://github.com/ArtemLevin/Hermes.git
cd Hermes
cp .env.sample .env
```

### 2. Запуск контейнеров
```bash
make up
make migrate
make seed
```

### 3. Доступы
- **Backend (Swagger/OpenAPI):** http://localhost:8000/docs  
- **Frontend (React):** http://localhost:5173/  
- **Mailhog (тест почты):** http://localhost:8025/  

Демо-логин:  
```
email: tutor@example.com
pass:  tutor
```

---

## 📊 UML-диаграммы

### Процесс: Создание урока
```mermaid
sequenceDiagram
    participant T as Tutor
    participant FE as Frontend
    participant API as FastAPI
    participant DB as PostgreSQL

    T->>FE: Заполняет форму урока
    FE->>API: POST /lessons
    API->>DB: INSERT lesson
    DB-->>API: OK
    API-->>FE: 201 Created (lesson_id)
    FE-->>T: Урок создан (карточка в календаре)
```

### Состояния задания (ДЗ)
```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> InProgress: Студент начал
    InProgress --> Submitted: Отправка решения
    Submitted --> Reviewed: Репетитор проверил
    Submitted --> Overdue: Истёк срок
    Reviewed --> Done: Принято
```

### Схема БД (ключевые таблицы)
```mermaid
erDiagram
    USER ||--o{ STUDENT_PROFILE : owns
    STUDENT_PROFILE ||--o{ LESSON : has
    STUDENT_PROFILE ||--o{ ASSIGNMENT : has
    ASSIGNMENT ||--o{ SUBMISSION : has
    STUDENT_PROFILE ||--o{ PAYMENT : has
    PAYMENT ||--o{ INVOICE : grouped_in
    STUDENT_PROFILE ||--o{ ACHIEVEMENT : earns
    STUDENT_PROFILE ||--o{ TROPHY : collects
    STUDENT_PROFILE ||--o{ ERROR_HOTSPOT : generates
    LESSON ||--o{ MATERIAL : attaches
```

### Активность: Еженедельный отчёт родителям
```mermaid
flowchart TD
    A["CRON: каждую субботу"] --> B["Сбор данных по ученикам"]
    B --> C["Генерация дайджеста: прогресс, уроки, ДЗ"]
    C --> D["Формирование письма (Jinja-шаблон)"]
    D --> E["Отправка через SMTP"]
    E --> F{"Успех?"}
    F -->|Да| G["Лог: письмо отправлено"]
    F -->|Нет| H["Повтор / DLQ в Redis"]
```

---

## 🔧 Команды Makefile

- `make up` — собрать и поднять контейнеры.  
- `make down` — остановить и удалить контейнеры/volumes.  
- `make migrate` — применить Alembic миграции.  
- `make seed` — загрузить тестовые данные.  
- `make smoke` — прогнать быстрый smoke-тест API.  

---

## ✅ Критерии приёмки (DoD)

- Поднимается `docker-compose up` → Swagger и Frontend доступны.  
- Можно: зарегистрировать ученика, создать урок, выдать ДЗ, получить письмо в Mailhog.  
- Основные API отвечают <200 мс на dev-стенде.  
- Линтер + тесты проходят:  
  ```bash
  ruff check api
  pytest -q
  ```

---

## 📌 Дальнейшая доработка

- Метрики (Prometheus/Grafana).  
- Радар внимания и прогноз экзамена.  
- Турниры, мемы и чат-бот-ассистент.  
- Экспорт PDF отчётов для родителей.  
