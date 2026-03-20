# Руководство по развёртыванию — СМР ПСД

> Для DevOps / системного администратора.

---

## 1. Требования к серверу

| Компонент        | Минимум                     | Рекомендация               |
|------------------|-----------------------------|-----------------------------|
| ОС               | Ubuntu 22.04 LTS (x86_64)  | Ubuntu 22.04 / 24.04 LTS   |
| Docker           | 24.0+                       | Последняя stable            |
| Docker Compose   | v2 (плагин `docker compose`)| v2.20+                      |
| ОЗУ              | 4 ГБ                        | 8 ГБ+                       |
| Диск             | 20 ГБ                       | 50 ГБ+ (с учётом MinIO)    |
| Процессор        | 2 ядра                      | 4 ядра                      |
| Сеть             | Открытые порты: 3000, 8000  | + 9001 (MinIO Console)      |

### Установка Docker (если не установлен)

```bash
# Добавить официальный GPG-ключ Docker
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Добавить репозиторий
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Проверка
docker --version        # Docker 24.0+
docker compose version  # v2.x
```

---

## 2. Клонирование и настройка окружения

```bash
# Клонирование репозитория
git clone <URL_РЕПОЗИТОРИЯ> smr_psd
cd smr_psd

# Создание файла .env из шаблона
cp .env.example .env
```

### Настройка переменных окружения (.env)

Отредактируйте `.env` — **обязательно** измените пароли:

```dotenv
# ── PostgreSQL ────────────────────────────────────────────────────
POSTGRES_HOST=postgres              # Имя Docker-сервиса (не менять)
POSTGRES_PORT=5432                  # Порт PostgreSQL
POSTGRES_DB=smr_psd                 # Имя базы данных
POSTGRES_USER=smr_user              # Пользователь БД
POSTGRES_PASSWORD=<СИЛЬНЫЙ_ПАРОЛЬ>  # ⚠️ ОБЯЗАТЕЛЬНО СМЕНИТЬ!

# ── MinIO (S3-совместимое хранилище) ──────────────────────────────
MINIO_HOST=minio                    # Имя Docker-сервиса (не менять)
MINIO_PORT=9000                     # API-порт MinIO
MINIO_ROOT_USER=minioadmin          # Логин администратора MinIO
MINIO_ROOT_PASSWORD=<СИЛЬНЫЙ_ПАРОЛЬ>  # ⚠️ ОБЯЗАТЕЛЬНО СМЕНИТЬ!
MINIO_BUCKET_DRAWINGS=drawings      # Бакет для чертежей
MINIO_BUCKET_ASBUILT=asbuilt        # Бакет для актов ИД
MINIO_BUCKET_CERTIFICATES=certificates  # Бакет для сертификатов
MINIO_BUCKET_REPORTS=reports        # Бакет для кэша отчётов

# ── Backend ───────────────────────────────────────────────────────
BACKEND_HOST=0.0.0.0                # Слушать все интерфейсы
BACKEND_PORT=8000                   # Порт FastAPI
BACKEND_RELOAD=false                # В продакшене — false!
LOG_LEVEL=info                      # Уровень логирования (debug/info/warning/error)

# ── Frontend ──────────────────────────────────────────────────────
REACT_APP_API_URL=http://<IP_СЕРВЕРА>:8000/api/v1
```

> **Важно:** `REACT_APP_API_URL` должен указывать на внешний адрес сервера, доступный из браузера пользователя.

---

## 3. Сборка и запуск

```bash
# Сборка и запуск всех сервисов в фоне
docker compose up --build -d

# Проверка статуса
docker compose ps
```

Ожидаемый вывод — все 4 сервиса `running (healthy)`:

| Сервис     | Порт          | Описание                    |
|------------|---------------|-----------------------------|
| postgres   | 5432          | PostgreSQL 15               |
| minio      | 9000 / 9001   | MinIO API / Web Console     |
| backend    | 8000          | FastAPI (Python)            |
| frontend   | 3000          | React (Node.js)             |

---

## 4. Применение миграций

После первого запуска необходимо создать структуру БД:

```bash
docker compose exec backend alembic upgrade head
```

Миграция `001_initial_schema` создаёт 26 таблиц:
- `projects`, `summary_estimates`, `object_estimates`, `local_estimate_bases`, `local_estimates`, `estimate_items`
- `income_contracts`, `expense_contracts`, `ls_income_contract`, `income_expense_contract`
- `drawings`, `specifications`, `ls_drawing`
- `documents`, `progress`
- `asbuilt_docs`, `asbuilt_drawing`, `asbuilt_specification`
- `work_journals`, `journal_entries`
- `material_certificates`, `m29_reports`, `m29_lines`
- `inspections`, `inspection_logs`
- `report_cache`

Проверка применения миграции:

```bash
docker compose exec backend alembic current
# Ожидается: 001_initial_schema (head)
```

---

## 5. Настройка MinIO — создание бакетов

### Вариант A: через MinIO Console (веб-интерфейс)

1. Откройте `http://<IP_СЕРВЕРА>:9001` в браузере
2. Авторизуйтесь с `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`
3. Перейдите в **Buckets** → **Create Bucket**
4. Создайте 4 бакета:
   - `drawings`
   - `asbuilt`
   - `certificates`
   - `reports`

### Вариант B: через MinIO Client (CLI)

```bash
# Установка mc (если не установлен)
docker compose exec minio mc alias set local http://localhost:9000 \
  $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD

# Создание бакетов
docker compose exec minio mc mb local/drawings
docker compose exec minio mc mb local/asbuilt
docker compose exec minio mc mb local/certificates
docker compose exec minio mc mb local/reports

# Проверка
docker compose exec minio mc ls local/
```

---

## 6. Проверка работоспособности

### Health-check бэкенда

```bash
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
# Ожидается: {"status": "ok"}
```

### Health-check фронтенда

Откройте `http://<IP_СЕРВЕРА>:3000` в браузере — должна загрузиться страница «Проекты».

### Health-check PostgreSQL

```bash
docker compose exec postgres pg_isready -U smr_user -d smr_psd
# Ожидается: accepting connections
```

### Health-check MinIO

```bash
curl -s http://localhost:9000/minio/health/live
# Ожидается: HTTP 200
```

---

## 7. Резервное копирование

### PostgreSQL — pg_dump

```bash
# Создание дампа
docker compose exec postgres pg_dump -U smr_user -d smr_psd \
  --format=custom --compress=9 \
  -f /tmp/smr_psd_backup_$(date +%Y%m%d_%H%M%S).dump

# Копирование дампа на хост
docker compose cp postgres:/tmp/smr_psd_backup_*.dump ./backups/

# Восстановление из дампа
docker compose exec postgres pg_restore -U smr_user -d smr_psd \
  --clean --if-exists /tmp/smr_psd_backup_YYYYMMDD_HHMMSS.dump
```

### Рекомендация: автоматизация через cron

```bash
# /etc/cron.d/smr_psd_backup
0 3 * * * root docker compose -f /path/to/smr_psd/docker-compose.yml \
  exec -T postgres pg_dump -U smr_user -d smr_psd --format=custom --compress=9 \
  > /backups/smr_psd_$(date +\%Y\%m\%d).dump 2>/dev/null
```

### MinIO — бэкап файлов

```bash
# Зеркальное копирование всех бакетов
docker compose exec minio mc mirror local/ /backup/minio/ --overwrite
```

---

## 8. Обновление

```bash
cd smr_psd

# Получить обновления
git pull origin main

# Пересобрать и перезапустить
docker compose up --build -d

# Применить новые миграции (если есть)
docker compose exec backend alembic upgrade head
```

---

## 9. Логирование и мониторинг

```bash
# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f backend

# Последние 100 строк
docker compose logs --tail=100 backend
```

---

## 10. Остановка и удаление

```bash
# Остановка (данные сохраняются в volumes)
docker compose down

# Полное удаление (⚠️ данные будут потеряны!)
docker compose down -v
```
