# AI Development Context — СМР ПСД

> Архитектурная память для будущих AI-сессий разработки.
> Этот файл содержит всё необходимое для понимания предметной области,
> структуры проекта и принятых архитектурных решений.

---

## 1. Предметная область

### Назначение системы

Веб-приложение для управления **проектно-сметной документацией (ПСД)** и **исполнительной документацией (ИД)** при проведении **строительно-монтажных работ (СМР)** в Российской Федерации.

### Термины и сокращения

| Термин    | Расшифровка                                                        |
|-----------|--------------------------------------------------------------------|
| **ПСД**   | Проектно-сметная документация — сметы, расчёты, ведомости          |
| **ИД**    | Исполнительная документация — акты, журналы, сертификаты            |
| **СМР**   | Строительно-монтажные работы                                       |
| **ПТО**   | Производственно-технический отдел — ведёт сметы, факт, договоры    |
| **СДО**   | Строительный контроль / технадзор — предписания, контроль ИД       |
| **ССР**   | Сводный сметный расчёт (верхний уровень иерархии смет)             |
| **ОСР**   | Объектный сметный расчёт                                           |
| **ЛСР**   | Локальный сметный расчёт                                           |
| **ЛС**    | Локальная смета (основная или дополнительная)                      |
| **КС-2**  | Акт о приёмке выполненных работ (Госкомстат РФ № 100)             |
| **КС-3**  | Справка о стоимости выполненных работ и затрат                     |
| **КС-6а** | Журнал учёта выполненных работ                                     |
| **М-29**  | Отчёт о расходе основных материалов                                |
| **АОСР**  | Акт освидетельствования скрытых работ (РД-11-02-2006)              |
| **АООК**  | Акт освидетельствования ответственных конструкций                  |
| **ОЖР**   | Общий журнал работ (РД-11-05-2007)                                 |

### Нормативная база РФ

- **Постановление Госкомстата РФ № 100 от 11.11.1999** — формы КС-2, КС-3, КС-6а
- **РД-11-02-2006** — порядок ведения АОСР
- **РД-11-05-2007** — порядок ведения ОЖР
- **Приказ Минстроя № 1026/пр от 02.12.2022** — обновлённые требования к ОЖР
- **СП 48.13330.2019** — организация строительства
- **СП 543.1325800.2024** — входной контроль

### Конечные пользователи

| Роль                  | Задачи в системе                                                |
|-----------------------|-----------------------------------------------------------------|
| Инженер ПТО           | Сметы, договоры, факт выполнения (КС-2), АОСР, М-29, отчёты   |
| Инженер СДО           | Предписания, контроль ИД, готовность к сдаче                   |
| Руководитель проекта  | Управленческие отчёты, дашборды                                 |

---

## 2. Стек технологий (точные версии)

### Backend

| Пакет              | Версия   | Назначение                           |
|--------------------|----------|--------------------------------------|
| Python             | 3.11+    | Язык                                 |
| FastAPI            | 0.115.6  | Web-фреймворк (lifespan, НЕ on_event)|
| Uvicorn            | 0.34.0   | ASGI-сервер                          |
| SQLAlchemy         | 2.0.36   | Async ORM (asyncpg)                  |
| asyncpg            | 0.30.0   | PostgreSQL async-драйвер             |
| Alembic            | 1.14.1   | Миграции БД                          |
| Pydantic           | 2.10.4   | Валидация / сериализация             |
| pydantic-settings  | 2.7.1    | Настройки из .env                    |
| openpyxl           | 3.1.5    | Генерация Excel-отчётов              |
| ReportLab          | 4.2.5    | Генерация PDF (Platypus + Drawing)   |
| aiofiles           | 24.1.0   | Неблокирующее чтение файлов          |
| minio              | 7.2.12   | S3-совместимое хранилище             |
| pytest             | 8.3.4    | Тестирование                         |
| httpx              | 0.28.1   | HTTP-клиент для тестов               |

### Frontend

| Пакет              | Версия   | Назначение                           |
|--------------------|----------|--------------------------------------|
| React              | 18.3.1   | UI-фреймворк                         |
| TypeScript         | 5.7.2    | Типизация                            |
| Ant Design         | 5.22.0   | UI-библиотека                        |
| react-router-dom   | 6.28.0   | Маршрутизация                        |
| axios              | 1.7.9    | HTTP-клиент                          |
| react-window       | 1.8.10   | Виртуализация списков                |
| react-hook-form    | 7.54.0   | Формы                                |

### Инфраструктура

| Компонент    | Версия     | Назначение                  |
|--------------|------------|-----------------------------|
| PostgreSQL   | 15-alpine  | База данных                 |
| MinIO        | latest     | Файловое хранилище (S3)     |
| Docker       | 24+        | Контейнеризация             |
| docker-compose | v2       | Оркестрация                 |

---

## 3. Структура БД — 26 таблиц

### Таблицы и связи

```
projects
 ├── summary_estimates ──→ object_estimates ──→ local_estimate_bases ──→ local_estimates ──→ estimate_items
 ├── income_contracts ──┐
 ├── expense_contracts ──┤
 │    ├── ls_income_contract (M:N: local_estimates ↔ income_contracts, с percentage)
 │    └── income_expense_contract (M:N: income_contracts ↔ expense_contracts, с percentage)
 ├── drawings ──→ specifications
 │    └── ls_drawing (M:N: local_estimates ↔ drawings)
 ├── asbuilt_docs
 │    ├── asbuilt_drawing (M:N: asbuilt_docs ↔ drawings)
 │    └── asbuilt_specification (M:N: asbuilt_docs ↔ specifications, с volume)
 ├── work_journals ──→ journal_entries
 ├── material_certificates (→ specifications)
 ├── m29_reports ──→ m29_lines (→ specifications)
 ├── inspections ──→ inspection_logs
 └── documents (единое файловое хранилище)

progress (→ estimate_items) — факт выполнения (месяц/год)
report_cache — кэш сгенерированных отчётов
```

### Ассоциативные таблицы (5 штук)

| Таблица                   | Связь                                      | Дополнительные поля        |
|---------------------------|--------------------------------------------|----------------------------|
| `ls_income_contract`      | local_estimates ↔ income_contracts         | `percentage` (NUMERIC)     |
| `income_expense_contract` | income_contracts ↔ expense_contracts       | `percentage` (NUMERIC)     |
| `ls_drawing`              | local_estimates ↔ drawings                 | —                          |
| `asbuilt_drawing`         | asbuilt_docs ↔ drawings                    | —                          |
| `asbuilt_specification`   | asbuilt_docs ↔ specifications              | `volume` (NUMERIC)         |

### ORM-классы (21 штука)

| Модуль       | Классы                                                    |
|--------------|-----------------------------------------------------------|
| projects     | `Project`                                                 |
| estimates    | `SummaryEstimate`, `ObjectEstimate`, `LocalEstimateBase`, `LocalEstimate`, `EstimateItem` |
| contracts    | `IncomeContract`, `ExpenseContract`                       |
| drawings     | `Drawing`, `Specification`                                |
| asbuilt      | `AsBuiltDoc`, `WorkJournal`, `JournalEntry`               |
| progress     | `Progress`                                                |
| materials    | `MaterialCertificate`, `M29Report`, `M29Line`             |
| inspections  | `Inspection`, `InspectionLog`                             |
| documents    | `Document`                                                |
| reports      | `ReportCache`                                             |

### Ключевые CHECK constraints

- `inspections.status` — CHECK IN ('OPEN', 'IN_PROGRESS', 'FIXED', 'CLOSED')
- `projects.status` — CHECK IN ('DESIGN', 'CONSTRUCTION', 'COMMISSIONING', 'COMPLETED')
- `asbuilt_docs.type` — CHECK IN ('AOSR', 'AOOK', 'OTHER')
- `local_estimates.type` — CHECK IN ('BASIC', 'ADDITIONAL')
- `drawings.status` — CHECK IN ('DRAFT', 'ISSUED', 'SUPERSEDED')
- `ls_income_contract.percentage` — CHECK (0 < percentage AND percentage <= 100)

### GENERATED COLUMN

- `m29_lines.deviation` = `actual_consumption - norm_consumption` (STORED)

---

## 4. Ключевые архитектурные решения

### 4.1. Уровень договора — ЛС, а не сметная статья

**Решение:** Привязка договора к ЛС (локальной смете), а не к отдельной сметной статье.

**Обоснование:**
- В реальной практике РФ договор заключается на выполнение работ по ЛС целиком
- Привязка к статьям создала бы N×M связей (тысячи записей) без практической пользы
- Процент распределения (`percentage`) логичнее на уровне сметы
- Бизнес-правило: `SUM(percentage) <= 100%` контролируется на уровне ЛС

### 4.2. М-29 — две таблицы (Report + Line)

**Решение:** `m29_reports` (заголовок) + `m29_lines` (строки).

**Обоснование:**
- Форма М-29 — ежемесячный отчёт прораба
- Заголовок содержит метаданные (период, прораб, статус)
- Строки — нормативы и факт по каждой спецификации
- `deviation` — GENERATED COLUMN (actual - norm), автоматический пересчёт

### 4.3. ReportCache — отдельная таблица

**Решение:** Кэш отчётов хранится в `report_cache` + файлы в MinIO bucket `reports`.

**Обоснование:**
- Отчёты генерируются долго (Excel/PDF с агрегацией по всей иерархии)
- При повторном запросе с теми же параметрами — отдаётся кэш
- `params_hash` — SHA256 от JSON параметров → быстрый поиск
- Отчёт не привязан к одному документу — он может агрегировать данные всего проекта

### 4.4. Recursive CTE вместо Python-агрегации

**Решение:** Иерархическая агрегация смет реализована через PostgreSQL Recursive CTE.

**Обоснование:**
- Сметная иерархия: ССР → ОСР → ЛСР → ЛС → Статья → Progress (факт)
- Python-агрегация потребовала бы загрузки всего дерева в память
- CTE выполняется на стороне PostgreSQL — быстрее и масштабируемее
- Используется для: budget_summary, estimate_tree, промежуточных итогов отчётов

---

## 5. Архитектура бэкенда

### Модульная структура (10 модулей)

Каждый модуль содержит 5 файлов:

```
module/
├── models.py       # SQLAlchemy ORM-классы
├── schemas.py      # Pydantic v2 схемы (Create, Update, Read)
├── repository.py   # Доступ к данным (CRUD + сложные запросы)
├── service.py      # Бизнес-логика
└── router.py       # FastAPI endpoints
```

**Исключение:** модуль `reports/` содержит дополнительно `excel_builder.py` и `pdf_builder.py`.

### Слой репозитория — `_CrudMixin`

Базовый mixin `_CrudMixin` в каждом `repository.py` предоставляет стандартные CRUD-операции. Конкретные репозитории наследуют его и добавляют специфичные методы (CTE-запросы, агрегация).

### Бизнес-правила в сервисном слое

- **Валидация SUM(percentage) ≤ 100** — `contracts/service.py` при добавлении `ls_income_contract`
- **Агрегация alerts** — `projects/service.py` → endpoint `GET /projects/{id}/alerts`
- **Кэширование отчётов** — `reports/service.py` → проверка `params_hash` → MinIO

### Основные эндпоинты

| Метод  | Путь                                    | Модуль       | Описание                        |
|--------|-----------------------------------------|--------------|---------------------------------|
| GET    | `/projects`                             | projects     | Список проектов                 |
| GET    | `/projects/{id}/tree`                   | projects     | Дерево смет (CTE)               |
| GET    | `/projects/{id}/budget-summary`         | projects     | Сводка бюджета                  |
| GET    | `/projects/{id}/alerts`                 | projects     | Агрегированные уведомления      |
| GET    | `/projects/{id}/id-readiness`           | projects     | Готовность ИД по маркам         |
| POST   | `/inspections/{id}/change-status`       | inspections  | Смена статуса + лог             |
| GET    | `/reports/generate`                     | reports      | Генерация отчёта (streaming)    |
| GET    | `/reports/list`                         | reports      | Список кэшированных отчётов    |

---

## 6. Архитектура фронтенда

### Компоненты (Раздел 8 ТЗ)

| Компонент              | Файл                          | Описание                                    |
|------------------------|-------------------------------|---------------------------------------------|
| BudgetTree             | components/BudgetTree/        | Иерархическая таблица смет, expandable + react-window |
| ContractDistribution   | components/ContractDistribution/ | Привязка ЛС→договоры, progress bar, SUM≤100% |
| AsBuiltRegistry        | components/AsBuiltRegistry/   | Таблица АОСР/АООК с фильтрами              |
| IDReadinessDashboard   | components/IDReadinessDashboard/ | Прогресс по разделам (маркам)             |
| InspectionBoard        | components/InspectionBoard/   | Предписания + Timeline + смена статуса      |
| QuickProgressForm      | components/QuickProgressForm/ | Быстрый ввод факта (ЛС→статья→период)      |
| AlertsPanel            | components/AlertsPanel/       | Уведомления: просрочки, сертификаты, бюджет |
| ReportsPage            | pages/reports/                | Генерация 21 типа отчётов, динамическая форма |

### Маршрутизация

```
/                           → redirect → /projects
/projects                   → ProjectsPage (список проектов)
/projects/:id               → ProjectLayout с боковым меню
/projects/:id/estimates     → EstimatesPage (BudgetTree + QuickProgressForm)
/projects/:id/contracts     → ContractsPage (ContractDistribution + таблицы)
/projects/:id/drawings      → DrawingsPage (CRUD чертежей)
/projects/:id/asbuilt       → AsBuiltPage (AsBuiltRegistry + IDReadinessDashboard)
/projects/:id/inspections   → InspectionsPage (InspectionBoard + AlertsPanel)
/projects/:id/reports       → ReportsPage (генерация отчётов)
```

### Ключевые паттерны

- **Form.useWatch + onValuesChange** в ReportsPage (НЕ getFieldValue)
- **Barrel exports** — каждый компонент имеет `index.ts`
- **TypeScript strict** — все типы в `types/index.ts` (46 типов)
- **Типизированный API-клиент** — `api/client.ts` (9 модулей API)
- **ConfigProvider с ruRU** — русская локализация Ant Design

---

## 7. Соглашения

| Контекст          | Соглашение               | Пример                     |
|-------------------|--------------------------|-----------------------------|
| БД (таблицы)      | snake_case               | `summary_estimates`         |
| БД (колонки)      | snake_case               | `total_amount`              |
| Python (модели)   | PascalCase               | `SummaryEstimate`           |
| Python (поля)     | snake_case               | `total_amount`              |
| TypeScript        | camelCase                | `totalAmount`               |
| TypeScript (типы) | PascalCase               | `SummaryEstimate`           |
| ID                | UUID v4 повсюду          | `uuid.uuid4()`              |
| Даты              | ISO 8601 в API           | `2024-01-15`                |
| Денежные суммы     | NUMERIC(18,2) в БД       | `1234567.89`                |

---

## 8. Полный список отчётов (21 тип)

### Группа 1: Финансовые (Excel)

| Тип                  | Название                                  | Параметры                       |
|----------------------|-------------------------------------------|---------------------------------|
| BUDGET_BALANCE       | Остатки сметного лимита                   | project_id, level, date_to      |
| BUDGET_BY_CONTRACTS  | Остатки лимитов в разрезе договоров       | project_id, contract_type       |
| MONTHLY_PROGRESS     | Помесячное выполнение (сводная)           | project_id, year, month_from, month_to |
| QUARTERLY_PROGRESS   | Освоение нарастающим итогом               | project_id, year                |

### Группа 2: Приёмочные формы (PDF)

| Тип   | Название                              | Параметры                                        |
|-------|---------------------------------------|--------------------------------------------------|
| KS2   | Акт КС-2                             | project_id, income_contract_id, period_month, period_year |
| KS3   | Справка КС-3                         | project_id, income_contract_id, period_month, period_year |
| KS6A  | Журнал КС-6а (Excel)                 | project_id, ls_id                                |

### Группа 3: Материальная отчётность

| Тип              | Название                              | Параметры                       |
|------------------|---------------------------------------|---------------------------------|
| M29_REPORT       | Форма М-29 (Excel + PDF)             | project_id, report_id / period  |
| MATERIAL_DEMAND  | Потребность в материалах              | project_id, ls_id (опц.)       |

### Группа 4: Статусы документации (Excel)

| Тип                  | Название                              | Параметры                        |
|----------------------|---------------------------------------|----------------------------------|
| ID_REGISTRY          | Реестр ИД                             | project_id, type, status (опц.) |
| ID_READINESS         | Дашборд готовности ИД                 | project_id                       |
| INSPECTION_REPORT    | Отчёт по предписаниям СДО            | project_id, status, date_from, date_to |
| CERTIFICATE_STATUS   | Реестр сертификатов                   | project_id, status (опц.)       |

### Группа 5: Сроки (Excel)

| Тип                  | Название                              | Параметры                       |
|----------------------|---------------------------------------|---------------------------------|
| SCHEDULE_DEVIATION   | Отклонение от графика                 | project_id, date_to             |

### Группа 6: Журналы СДО (PDF)

| Тип                    | Название                            | Параметры                       |
|------------------------|-------------------------------------|---------------------------------|
| WORK_JOURNAL_PRINT     | Общий журнал работ                  | journal_id, date_from, date_to  |
| INPUT_CONTROL_JOURNAL  | Журнал входного контроля            | project_id, date_from, date_to  |

### Группа 7: Договорные (Excel)

| Тип                | Название                              | Параметры                       |
|--------------------|---------------------------------------|---------------------------------|
| CONTRACT_REGISTRY  | Реестр договоров                      | project_id, contract_type       |
| MARGIN_REPORT      | Маржа генподрядчика                   | project_id, ls_id (опц.)       |
| UNCOVERED_LS       | ЛС с незакрытыми объёмами             | project_id                      |

### Группа 8: Управленческие (PDF)

| Тип                    | Название                            | Параметры       |
|------------------------|-------------------------------------|-----------------|
| EXECUTIVE_DASHBOARD    | Управленческий отчёт (1 стр.)       | project_id      |
| MULTI_PROJECT_SUMMARY  | Сводная по всем проектам            | (нет)           |

---

## 9. Roadmap будущих функций

| Функция                                           | Приоритет | Описание                                                       |
|---------------------------------------------------|-----------|----------------------------------------------------------------|
| **RBAC** (роли)                                   | Высокий   | Администратор, Инженер ПТО, Инженер СДО, Руководитель          |
| **Интеграция с 1С:УСО**                           | Высокий   | REST API для обмена данными со сметными программами             |
| **Мобильное приложение**                          | Средний   | React Native для прораба: ввод факта, фото предписаний         |
| **Генерация АОСР в PDF**                          | Средний   | По шаблону РД-11-02-2006 с автозаполнением                     |
| **Электронная подпись (КЭП)**                     | Средний   | Подписание актов квалифицированной электронной подписью         |
| **Импорт из XML-смет**                            | Средний   | Загрузка из Grand Smeta, Турбосметчик                          |
| **Push-уведомления**                              | Низкий    | Уведомления о просрочках предписаний и сертификатов            |

---

## 10. Ограничения текущей версии

- Нет аутентификации и авторизации (RBAC не реализован)
- Нет интеграции с ERP / 1С
- Весь ввод данных — вручную через веб-интерфейс
- Генерация АОСР в PDF не реализована (только реестр)
- Нет мобильного приложения
- Нет электронной подписи
